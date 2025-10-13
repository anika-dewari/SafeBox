#!/usr/bin/env python3
"""
SafeBox CLI - Command Line Interface
Author: Ritika
Purpose: Interactive CLI for deadlock prevention simulation and testing

Features:
- Run banker's algorithm simulations
- Check system state
- Load/save scenarios
- Generate reports
- Interactive and batch modes
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.progress import Progress
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.banker import BankerAlgorithm, create_example_scenario


console = Console()


class SafeBoxCLI:
    """Command-line interface for SafeBox banker's algorithm"""
    
    def __init__(self):
        self.banker = None
        self.scenarios_dir = Path(__file__).parent.parent / 'scenarios'
        self.scenarios_dir.mkdir(exist_ok=True)
    
    def cmd_init(self, args):
        """Initialize a new banker system"""
        resources = args.resources
        names = args.names.split(',') if args.names else [f"R{i}" for i in range(len(resources))]
        
        self.banker = BankerAlgorithm(resources, names)
        
        console.print(Panel.fit(
            f"✅ Banker system initialized\n"
            f"Resources: {dict(zip(names, resources))}",
            title="System Initialized",
            border_style="green"
        ))
    
    def cmd_add_process(self, args):
        """Add a process to the system"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first (use 'init' command)[/red]")
            return
        
        success = self.banker.add_process(args.pid, args.name, args.max_resources)
        
        if success:
            console.print(f"[green]✅ Process {args.name} (PID: {args.pid}) added successfully[/green]")
        else:
            console.print(f"[red]❌ Failed to add process {args.name}[/red]")
    
    def cmd_request(self, args):
        """Request resources for a process"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first[/red]")
            return
        
        success, message = self.banker.request_resources(args.pid, args.request)
        
        if success:
            console.print(f"[green]✅ {message}[/green]")
        else:
            console.print(f"[red]❌ {message}[/red]")
        
        self.show_state()
    
    def cmd_release(self, args):
        """Release resources from a process"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first[/red]")
            return
        
        success, message = self.banker.release_resources(args.pid, args.release)
        
        if success:
            console.print(f"[green]✅ {message}[/green]")
        else:
            console.print(f"[red]❌ {message}[/red]")
        
        self.show_state()
    
    def cmd_check_state(self, args):
        """Check current system state"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first[/red]")
            return
        
        self.show_state()
    
    def show_state(self):
        """Display current system state"""
        state = self.banker.get_system_state()
        
        # Status header
        status = "SAFE ✅" if state['is_safe'] else "UNSAFE ⚠️"
        console.print(f"\n[bold]System State: {status}[/bold]")
        
        if state['is_safe']:
            console.print(f"Safe Sequence: {' → '.join(f'P{pid}' for pid in state['safe_sequence'])}\n")
        else:
            console.print("[yellow]⚠️ System is in UNSAFE state - Deadlock possible![/yellow]\n")
        
        # Resources table
        resources_table = Table(title="Available Resources", box=box.ROUNDED)
        resources_table.add_column("Resource", style="cyan")
        resources_table.add_column("Available", style="green")
        resources_table.add_column("Total", style="blue")
        
        for i, name in enumerate(state['resource_names']):
            resources_table.add_row(
                name,
                str(state['available'][i]),
                str(state['total_resources'][i])
            )
        
        console.print(resources_table)
        
        # Processes table
        if state['processes']:
            processes_table = Table(title="Process Allocation State", box=box.ROUNDED)
            processes_table.add_column("PID", style="cyan")
            processes_table.add_column("Name", style="yellow")
            
            for rname in state['resource_names']:
                processes_table.add_column(f"{rname}\nMax", style="blue")
                processes_table.add_column(f"{rname}\nAlloc", style="green")
                processes_table.add_column(f"{rname}\nNeed", style="magenta")
            
            for pid, pdata in state['processes'].items():
                row = [str(pid), pdata['name']]
                for i in range(len(state['resource_names'])):
                    row.extend([
                        str(pdata['max'][i]),
                        str(pdata['allocated'][i]),
                        str(pdata['need'][i])
                    ])
                processes_table.add_row(*row)
            
            console.print(processes_table)
    
    def cmd_simulate(self, args):
        """Run a simulation scenario"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first[/red]")
            return
        
        scenario_file = self.scenarios_dir / f"{args.scenario}.json"
        
        if not scenario_file.exists():
            console.print(f"[red]❌ Scenario '{args.scenario}' not found[/red]")
            return
        
        with open(scenario_file) as f:
            scenario_data = json.load(f)
        
        console.print(Panel.fit(
            f"Running scenario: {scenario_data.get('name', args.scenario)}",
            border_style="blue"
        ))
        
        # Execute scenario steps
        for step in scenario_data['steps']:
            action = step['action']
            
            if action == 'request':
                console.print(f"\n[cyan]→ P{step['pid']} requests {step['resources']}[/cyan]")
                success, msg = self.banker.request_resources(step['pid'], step['resources'])
                
                if success:
                    console.print(f"[green]  ✅ {msg}[/green]")
                else:
                    console.print(f"[red]  ❌ {msg}[/red]")
            
            elif action == 'release':
                console.print(f"\n[cyan]→ P{step['pid']} releases {step['resources']}[/cyan]")
                success, msg = self.banker.release_resources(step['pid'], step['resources'])
                console.print(f"[green]  ✅ {msg}[/green]" if success else f"[red]  ❌ {msg}[/red]")
            
            if args.step_by_step:
                input("Press Enter to continue...")
        
        self.show_state()
    
    def cmd_load_example(self, args):
        """Load the example scenario"""
        self.banker = create_example_scenario()
        console.print(Panel.fit(
            "✅ Example scenario loaded\n"
            "5 processes with pre-allocated resources",
            title="Example Loaded",
            border_style="green"
        ))
        self.show_state()
    
    def cmd_save(self, args):
        """Save current state to file"""
        if not self.banker:
            console.print("[red]❌ Error: No system to save[/red]")
            return
        
        state = self.banker.get_system_state()
        output_file = Path(args.output)
        
        with open(output_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        console.print(f"[green]✅ State saved to {output_file}[/green]")
    
    def cmd_export_report(self, args):
        """Export detailed report"""
        if not self.banker:
            console.print("[red]❌ Error: Initialize system first[/red]")
            return
        
        state = self.banker.get_system_state()
        output_file = Path(args.output)
        
        report = []
        report.append("=" * 60)
        report.append("SafeBox Banker's Algorithm Report")
        report.append("=" * 60)
        report.append(f"\nSystem Status: {'SAFE' if state['is_safe'] else 'UNSAFE'}")
        
        if state['is_safe']:
            report.append(f"Safe Sequence: {' → '.join(f'P{pid}' for pid in state['safe_sequence'])}")
        
        report.append(f"\nTotal Processes: {state['total_processes']}")
        report.append(f"\nResource Configuration:")
        for i, name in enumerate(state['resource_names']):
            report.append(f"  {name}: {state['available'][i]}/{state['total_resources'][i]} available")
        
        report.append("\nProcess Details:")
        for pid, pdata in state['processes'].items():
            report.append(f"\n  Process {pid} ({pdata['name']}):")
            report.append(f"    Maximum:   {pdata['max']}")
            report.append(f"    Allocated: {pdata['allocated']}")
            report.append(f"    Need:      {pdata['need']}")
        
        report.append("\n" + "=" * 60)
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        console.print(f"[green]✅ Report exported to {output_file}[/green]")
    
    def cmd_test_suite(self, args):
        """Run comprehensive test suite"""
        console.print(Panel.fit(
            "Running SafeBox Test Suite",
            border_style="blue"
        ))
        
        tests = [
            ("Basic Allocation", self.test_basic_allocation),
            ("Safe State Detection", self.test_safe_state),
            ("Unsafe Request Rejection", self.test_unsafe_rejection),
            ("Resource Release", self.test_resource_release),
            ("Deadlock Detection", self.test_deadlock_detection)
        ]
        
        results = []
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Running tests...", total=len(tests))
            
            for test_name, test_func in tests:
                try:
                    test_func()
                    results.append((test_name, "PASS", "✅"))
                except Exception as e:
                    results.append((test_name, "FAIL", f"❌ {str(e)}"))
                
                progress.update(task, advance=1)
                time.sleep(0.2)
        
        # Display results
        results_table = Table(title="Test Results", box=box.ROUNDED)
        results_table.add_column("Test", style="cyan")
        results_table.add_column("Status", style="bold")
        results_table.add_column("Result")
        
        for name, status, result in results:
            style = "green" if status == "PASS" else "red"
            results_table.add_row(name, f"[{style}]{status}[/{style}]", result)
        
        console.print(results_table)
    
    # Test methods
    def test_basic_allocation(self):
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        success, _ = banker.request_resources(0, [2, 2, 2])
        assert success, "Basic allocation failed"
    
    def test_safe_state(self):
        banker = create_example_scenario()
        is_safe, _ = banker.is_safe_state()
        assert is_safe, "Example scenario should be safe"
    
    def test_unsafe_rejection(self):
        banker = BankerAlgorithm([5, 3, 3])
        banker.add_process(0, "P0", [5, 3, 3])
        banker.add_process(1, "P1", [5, 3, 3])
        banker.request_resources(0, [5, 3, 3])
        success, _ = banker.request_resources(1, [5, 3, 3])
        assert not success, "Unsafe request should be rejected"
    
    def test_resource_release(self):
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.request_resources(0, [2, 2, 2])
        success, _ = banker.release_resources(0, [1, 1, 1])
        assert success, "Resource release failed"
    
    def test_deadlock_detection(self):
        banker = create_example_scenario()
        is_deadlock, _ = banker.detect_deadlock()
        assert not is_deadlock, "Should not detect deadlock in safe state"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SafeBox - Banker's Algorithm CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize banker system')
    init_parser.add_argument('resources', type=int, nargs='+', help='Total resources (e.g., 10 5 7)')
    init_parser.add_argument('--names', help='Resource names (comma-separated)')
    
    # add-process command
    add_parser = subparsers.add_parser('add-process', help='Add a process')
    add_parser.add_argument('pid', type=int, help='Process ID')
    add_parser.add_argument('name', help='Process name')
    add_parser.add_argument('max_resources', type=int, nargs='+', help='Maximum resources needed')
    
    # request command
    req_parser = subparsers.add_parser('request', help='Request resources')
    req_parser.add_argument('pid', type=int, help='Process ID')
    req_parser.add_argument('request', type=int, nargs='+', help='Resources to request')
    
    # release command
    rel_parser = subparsers.add_parser('release', help='Release resources')
    rel_parser.add_argument('pid', type=int, help='Process ID')
    rel_parser.add_argument('release', type=int, nargs='+', help='Resources to release')
    
    # check-state command
    subparsers.add_parser('check-state', help='Check system state')
    
    # simulate command
    sim_parser = subparsers.add_parser('simulate', help='Run scenario simulation')
    sim_parser.add_argument('scenario', help='Scenario name')
    sim_parser.add_argument('--step-by-step', action='store_true', help='Step through scenario')
    
    # load-example command
    subparsers.add_parser('load-example', help='Load example scenario')
    
    # save command
    save_parser = subparsers.add_parser('save', help='Save current state')
    save_parser.add_argument('output', help='Output file path')
    
    # export-report command
    exp_parser = subparsers.add_parser('export-report', help='Export detailed report')
    exp_parser.add_argument('output', help='Output file path')
    
    # test-suite command
    subparsers.add_parser('test-suite', help='Run comprehensive tests')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SafeBoxCLI()
    command_method = getattr(cli, f'cmd_{args.command.replace("-", "_")}', None)
    
    if command_method:
        try:
            command_method(args)
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
    else:
        console.print(f"[red]❌ Unknown command: {args.command}[/red]")


if __name__ == "__main__":
    main()
