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
    
    # Get actual system resources
    import psutil
    total_ram_mb = int(psutil.virtual_memory().total / (1024 * 1024))
    
    # Use 80% of system RAM as pool (leave 20% for OS)
    pool_ram_mb = int(total_ram_mb * 0.8)
    
    console.print(f"[dim]Detected system RAM: {total_ram_mb}MB[/dim]")
    console.print(f"[dim]Using resource pool: 100% CPU, {pool_ram_mb}MB RAM[/dim]")
    
    executor = SystemExecutor(total_cpu_percent=100, total_memory_mb=pool_ram_mb)
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
            # Convert PIDs to process names for display
            process_dict = banker.get('processes', {})
            safe_names = []
            for pid in banker['safe_sequence']:
                if pid in process_dict:
                    safe_names.append(process_dict[pid]['name'])
                else:
                    safe_names.append(f"P{pid}")
            if safe_names:
                console.print(f"[dim]Safe Sequence: {' → '.join(safe_names)}[/dim]")
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
# DEADLOCK PREVENTION DEMO - REAL SYSTEM
# ============================================================================
# This demonstrates REAL deadlock prevention using actual running programs.
# It shows how Banker's Algorithm rejects unsafe resource requests.

def demo_deadlock_prevention(executor: 'SystemExecutor'):
    """Demonstrate real deadlock prevention with actual programs."""
    console.print("\n[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    console.print("[bold red]              DEADLOCK PREVENTION DEMONSTRATION                [/bold red]")
    console.print("[bold bright_white]═══════════════════════════════════════════════════════════════[/bold bright_white]")
    
    console.print("\n[yellow]This demo uses REAL programs with resource requirements YOU specify.[/yellow]")
    console.print("[yellow]The Banker's Algorithm will REJECT unsafe requests in REAL-TIME.[/yellow]\n")
    
    # Get available apps
    apps = show_available_apps(executor)
    if not apps:
        console.print("[bold red]No applications available![/bold red]")
        return
    
    console.print("[bold cyan]Step 1: Check initial system state[/bold cyan]")
    state = executor.get_system_state()
    total_cpu = state['banker']['total_resources'][0]
    total_mem = state['banker']['total_resources'][1]
    show_system_state(executor)
    
    input("\n[Press Enter to continue...]")
    
    # Job 1: User selects app and resources
    console.print("\n[bold cyan]Step 2: Submit Job1 - YOU choose the resources![/bold cyan]")
    
    try:
        app_choice = IntPrompt.ask(
            "\n[bold]Select application for Job1[/bold]",
            choices=[str(i) for i in range(1, len(apps) + 1)]
        )
        app1 = apps[app_choice - 1]
        
        console.print(f"\n[bold]Resource requirements for Job1 ({app1['name']}):[/bold]")
        cpu1 = IntPrompt.ask("  CPU percentage (1-100)", default=30)
        mem1 = IntPrompt.ask("  Memory MB", default=200)
        
        console.print(f"\n[yellow]  → Submitting Job1: {app1['name']}[/yellow]")
        console.print(f"[yellow]  → Resources: {cpu1}% CPU, {mem1}MB RAM[/yellow]")
        console.print(f"[yellow]  → Available: {total_cpu}% CPU, {total_mem}MB RAM[/yellow]\n")
        
        success1, msg1, job_id1 = executor.request_job(
            job_name=f"Job1_{app1['name']}",
            app_path=app1['path'],
            app_args=[],
            cpu_percent=cpu1,
            memory_mb=mem1
        )
        
        if success1:
            console.print(f"[bold green]✅ Job1 GRANTED[/bold green] - {msg1}")
            console.print(f"[dim]Job ID: {job_id1}[/dim]")
        else:
            console.print(f"[bold red]❌ Job1 REJECTED[/bold red] - {msg1}")
            return
        
        console.print("\n[bold cyan]System state after Job1:[/bold cyan]")
        show_system_state(executor)
        
        input("\n[Press Enter to continue...]")
        
        # Job 2: User tries another job
        avail_cpu = total_cpu - cpu1
        avail_mem = total_mem - mem1
        
        console.print("\n[bold cyan]Step 3: Submit Job2 - Try to allocate more resources![/bold cyan]")
        console.print(f"[yellow]Available NOW: {avail_cpu}% CPU, {avail_mem}MB RAM[/yellow]")
        console.print("[yellow]TIP: Try requesting MORE than available to see deadlock prevention![/yellow]\n")
        
        app_choice2 = IntPrompt.ask(
            "[bold]Select application for Job2[/bold]",
            choices=[str(i) for i in range(1, len(apps) + 1)]
        )
        app2 = apps[app_choice2 - 1]
        
        console.print(f"\n[bold]Resource requirements for Job2 ({app2['name']}):[/bold]")
        cpu2 = IntPrompt.ask("  CPU percentage (1-100)", default=min(avail_cpu + 20, 100))  # Suggest exceeding
        mem2 = IntPrompt.ask("  Memory MB", default=avail_mem + 100)
        
        console.print(f"\n[yellow]  → Submitting Job2: {app2['name']}[/yellow]")
        console.print(f"[yellow]  → Requested: {cpu2}% CPU, {mem2}MB RAM[/yellow]")
        console.print(f"[yellow]  → Available: {avail_cpu}% CPU, {avail_mem}MB RAM[/yellow]")
        
        if cpu2 > avail_cpu or mem2 > avail_mem:
            console.print("[red]  ⚠️  Requesting MORE than available - will likely be REJECTED![/red]\n")
        
        success2, msg2, job_id2 = executor.request_job(
            job_name=f"Job2_{app2['name']}",
            app_path=app2['path'],
            app_args=[],
            cpu_percent=cpu2,
            memory_mb=mem2
        )
        
        if success2:
            console.print(f"[bold yellow]⚠️  Job2 was GRANTED[/bold yellow] - {msg2}")
            console.print("[yellow]The system still found a safe sequence.[/yellow]")
        else:
            console.print(f"[bold green]✅ DEADLOCK PREVENTED![/bold green]")
            console.print(f"[bold red]❌ Job2 REJECTED[/bold red] - {msg2}")
            console.print("\n[bold green]Why was it rejected?[/bold green]")
            console.print("[cyan]Banker's Algorithm Analysis:[/cyan]")
            console.print(f"[cyan]  • Job1 holds: {cpu1}% CPU, {mem1}MB RAM[/cyan]")
            console.print(f"[cyan]  • Job2 requested: {cpu2}% CPU, {mem2}MB RAM[/cyan]")
            console.print(f"[cyan]  • Total needed: {cpu1+cpu2}% CPU, {mem1+mem2}MB RAM[/cyan]")
            console.print(f"[cyan]  • System has: {total_cpu}% CPU, {total_mem}MB RAM[/cyan]")
            console.print(f"[cyan]  • Would exceed limits → UNSAFE STATE → DEADLOCK![/cyan]")
            console.print("\n[bold green]✓ Banker's Algorithm successfully prevented deadlock on REAL system![/bold green]")
        
        console.print("\n[bold cyan]Final system state:[/bold cyan]")
        show_system_state(executor)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
    
    input("\n[Press Enter to return to main menu...]")


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
        console.print("[bold white]4.[/bold white] [red]Demo: Deadlock Prevention[/red]")
        console.print("[bold white]5.[/bold white] [magenta]Refresh Prerequisites[/magenta]")
        console.print("[bold white]6.[/bold white] [red]Exit[/red]")
        
        try:
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=['1', '2', '3', '4', '5', '6'],
                default='1'
            )
            
            if choice == '1':
                show_system_state(executor)
            elif choice == '2':
                run_job_interactive(executor)
            elif choice == '3':
                show_available_apps(executor)
            elif choice == '4':
                demo_deadlock_prevention(executor)
            elif choice == '5':
                executor = check_prerequisites()
                if not executor:
                    break
            elif choice == '6':
                console.print("\n[bold cyan]» Exiting SafeBox. Goodbye![/bold cyan]")
                break
            else:
                console.print("[bold red]▸ Invalid choice. Please select 1-6.[/bold red]")
        
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
