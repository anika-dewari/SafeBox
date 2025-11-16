#!/usr/bin/env python3
"""
SafeBox Real System CLI
Author: Ritika

Interactive CLI for running real applications with Banker's Algorithm safety checks,
cgroup resource limits, and SafeBox sandboxing.

Usage:
    sudo python3 real_safebox_cli.py
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich import box

# ============================================================================
# SETUP: Import the system executor (connects to Banker's Algorithm backend)
# ============================================================================
# This handles the import in a way that works even when running with sudo,
# which sometimes messes up Python's module paths.

# Add backend to path robustly
backend_path = Path(__file__).resolve().parent.parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    from app.system_executor import SystemExecutor
except Exception:
    # Fallback: directly load the module file if package import fails (useful under sudo)
    import importlib.util
    se_path = backend_path / 'app' / 'system_executor.py'
    if se_path.exists():
        spec = importlib.util.spec_from_file_location('app.system_executor', str(se_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SystemExecutor = getattr(module, 'SystemExecutor')
    else:
        raise


console = Console()


# ============================================================================
# BANNER & UI DISPLAY
# ============================================================================
# Beautiful ASCII art and styling to make the CLI look professional.
# Using Rich library for colors, tables, and formatted output.

def print_banner():
    """Print SafeBox banner with beautiful ASCII art."""
    from rich.panel import Panel
    from rich.align import Align
    
    # ASCII Art Title
    title = """
███████╗ █████╗ ███████╗███████╗██████╗  ██████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔════╝██╔══██╗██╔═══██╗╚██╗██╔╝
███████╗███████║█████╗  █████╗  ██████╔╝██║   ██║ ╚███╔╝ 
╚════██║██╔══██║██╔══╝  ██╔══╝  ██╔══██╗██║   ██║ ██╔██╗ 
███████║██║  ██║██║     ███████╗██████╔╝╚██████╔╝██╔╝ ██╗
╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝
"""
    
    subtitle = Text()
    subtitle.append("R E S O U R C E   M A N A G E R", style="bold bright_white")
    
    flow = Text()
    flow.append("Banker's Algorithm", style="bold yellow")
    flow.append(" ➜ ", style="bold bright_white")
    flow.append("cgroups", style="bold green")
    flow.append(" ➜ ", style="bold bright_white")
    flow.append("Sandbox", style="bold magenta")
    flow.append(" ➜ ", style="bold bright_white")
    flow.append("Safe Execution", style="bold cyan")
    
    console.print(Panel(
        Align.center(Text(title, style="bold bright_cyan") + "\n" + subtitle + "\n\n" + flow),
        border_style="bright_cyan",
        padding=(1, 2)
    ))


def check_prerequisites():
    """Check and display prerequisites."""
    console.print("\n[bold yellow]» Checking Prerequisites...[/bold yellow]")
    
    executor = SystemExecutor()
    ok, msg = executor.check_prerequisites()
    
    if ok:
        console.print(msg, style="bold green")
        return executor
    else:
        console.print(msg, style="bold red")
        console.print("\n[yellow]→ To fix:[/yellow]")
        console.print("   1. Run on Linux or WSL")
        console.print("   2. Execute with sudo: [cyan]sudo python3 real_safebox_cli.py[/cyan]")
        console.print("   3. Build binaries: [cyan]make real-system[/cyan]")
        return None


# ============================================================================
# SYSTEM STATE DISPLAY
# ============================================================================
# Shows what's happening right now: how many resources are available,
# which jobs are running, and whether the system is in a safe state.

def show_system_state(executor: 'SystemExecutor'):
    """Display current system state."""
    console.print("\n[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    console.print("[bold bright_cyan]                        SYSTEM STATE                           [/bold bright_cyan]")
    console.print("[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    
    state = executor.get_system_state()
    banker = state['banker']
    
    # System status table
    table = Table(box=box.DOUBLE_EDGE, show_header=True, header_style="bold bright_white")
    table.add_column("Resource Metric", style="cyan", width=25)
    table.add_column("Value", style="green", width=30)
    
    table.add_row("Total CPU", f"{banker['total_resources'][0]}%")
    table.add_row("Available CPU", f"{banker['available'][0]}%")
    table.add_row("Total Memory", f"{banker['total_resources'][1]}MB")
    table.add_row("Available Memory", f"{banker['available'][1]}MB")
    
    console.print(table)
    
    # Safety status
    if banker['is_safe']:
        console.print("\n[bold green]▸ System State: SAFE[/bold green]")
        if banker['safe_sequence']:
            console.print(f"[dim]Safe Sequence: {' → '.join(banker['safe_sequence'])}[/dim]")
    else:
        console.print("\n[bold red]▸ System State: UNSAFE (Deadlock possible!)[/bold red]")
    
    # Active jobs
    if state['jobs']:
        jobs_table = Table(title="Active Jobs", box=box.SIMPLE)
        jobs_table.add_column("Job ID", style="yellow")
        jobs_table.add_column("App", style="cyan")
        jobs_table.add_column("CPU", style="green")
        jobs_table.add_column("Memory", style="green")
        
        for job_id, job in state['jobs'].items():
            jobs_table.add_row(
                str(job_id),
                job['app'],
                f"{job['cpu']}%",
                f"{job['memory']}MB"
            )
        console.print("\n", jobs_table)
    else:
        console.print("\n[dim]No active jobs[/dim]")


# ============================================================================
# APPLICATION LISTING
# ============================================================================
# Shows the test programs that can be run. These are real compiled C programs
# that will execute with actual resource limits.

def show_available_apps(executor: 'SystemExecutor') -> list:
    """Display available applications."""
    console.print("\n[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    console.print("[bold bright_cyan]                   AVAILABLE APPLICATIONS                      [/bold bright_cyan]")
    console.print("[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    
    apps = [
        {
            'name': 'calc_with_selftest',
            'path': './src/calc_with_selftest',
            'description': 'Calculator with memory stress test'
        },
        {
            'name': 'test',
            'path': './src/test',
            'description': 'Simple test program'
        }
    ]
    
    table = Table(box=box.DOUBLE_EDGE)
    table.add_column("#", style="yellow", width=5)
    table.add_column("Application", style="cyan", width=25)
    table.add_column("Description", style="white", width=35)
    
    for idx, app in enumerate(apps, 1):
        table.add_row(str(idx), app['name'], app['description'])
    
    console.print(table)
    return apps


# ============================================================================
# JOB SUBMISSION - THE MAIN FEATURE!
# ============================================================================
# This is where users submit jobs. The system will:
# 1. Ask what program to run
# 2. Ask for CPU and memory limits
# 3. Check with Banker's Algorithm if it's safe
# 4. If safe, create real cgroups and run the program!

def run_job_interactive(executor: 'SystemExecutor'):
    """Interactive job submission."""
    console.print("\n[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    console.print("[bold bright_cyan]                       RUN NEW JOB                             [/bold bright_cyan]")
    console.print("[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    
    # Show available apps
    apps = show_available_apps(executor)
    
    # Select app
    try:
        app_choice = IntPrompt.ask(
            "\n[bold]Select application[/bold]",
            choices=[str(i) for i in range(1, len(apps) + 1)]
        )
        selected_app = apps[app_choice - 1]
        app_name = selected_app['name']
        app_path = selected_app['path']
        
        # Get resource limits
        console.print(f"\n[bold]Resource Limits for [cyan]{app_name}[/cyan][/bold]")
        cpu_limit = IntPrompt.ask("  CPU limit (%)", default=30)
        mem_limit = IntPrompt.ask("  Memory limit (MB)", default=100)
        
        # Confirm
        console.print(f"\n[yellow]» Job Configuration:[/yellow]")
        console.print(f"  Application: [cyan]{app_name}[/cyan]")
        console.print(f"  CPU Limit: [cyan]{cpu_limit}%[/cyan]")
        console.print(f"  Memory Limit: [cyan]{mem_limit}MB[/cyan]")
        
        if not Confirm.ask("\n[bold]Submit job?[/bold]", default=True):
            console.print("[yellow]Job cancelled[/yellow]")
            return
        
        # Submit job
        console.print("\n[bold green]» Submitting Job...[/bold green]")
        success, message, job_id = executor.request_job(
            job_name=app_name,
            app_path=app_path,
            app_args=[],
            cpu_percent=cpu_limit,
            memory_mb=mem_limit
        )
        
        if success:
            console.print(f"\n[bold green]✅ Job Completed Successfully[/bold green]")
            console.print(f"[dim]Job ID: {job_id}[/dim]")
            console.print(f"\n[green]{message}[/green]")
        else:
            console.print(f"\n[bold red]❌ Job Failed[/bold red]")
            console.print(f"[red]{message}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Job submission cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")


# ============================================================================
# MAIN MENU - THE CONTROL CENTER
# ============================================================================
# The main loop that shows options and handles user input.
# Users can check system state, run jobs, or exit.

def main_menu(executor: 'SystemExecutor'):
    """Main interactive menu."""
    while True:
        console.print("\n[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
        console.print("[bold bright_cyan]                         MAIN MENU                             [/bold bright_cyan]")
        console.print("[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
        console.print("[bold white]1.[/bold white] [cyan]Show System State[/cyan]")
        console.print("[bold white]2.[/bold white] [green]Run New Job[/green]")
        console.print("[bold white]3.[/bold white] [yellow]List Available Apps[/yellow]")
        console.print("[bold white]4.[/bold white] [magenta]Refresh Prerequisites[/magenta]")
        console.print("[bold white]5.[/bold white] [red]Exit[/red]")
        
        try:
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=['1', '2', '3', '4', '5'],
                default='1'
            )
            
            if choice == '1':
                show_system_state(executor)
            elif choice == '2':
                run_job_interactive(executor)
            elif choice == '3':
                show_available_apps(executor)
            elif choice == '4':
                executor = check_prerequisites()
                if not executor:
                    break
            elif choice == '5':
                console.print("\n[bold cyan]» Exiting SafeBox. Goodbye![/bold cyan]")
                break
            else:
                console.print("[bold red]▸ Invalid choice. Please select 1-5.[/bold red]")
        
        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]» Exiting SafeBox. Goodbye![/bold cyan]")
            break
        except EOFError:
            console.print("\n\n[bold cyan]» Exiting SafeBox. Goodbye![/bold cyan]")
            break
        except Exception as e:
            console.print(f"[bold red]▸ Error: {e}[/bold red]")


# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================
# This is where the program starts. It shows the banner, checks if everything
# is ready (Linux, root access, binaries built), then launches the main menu.

def main():
    """Main entry point."""
    try:
        print_banner()
        executor = check_prerequisites()
        
        if not executor:
            console.print("\n[bold red]Prerequisites check failed. Exiting.[/bold red]")
            sys.exit(1)
        
        main_menu(executor)
        
    except KeyboardInterrupt:
        console.print("\n\n[bold cyan]» Interrupted. Exiting...[/bold cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == '__main__':
    main()
