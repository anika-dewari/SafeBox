"""
SafeBox Real System Executor
Author: Ritika, Ayush, Anika

Integrates Banker's Algorithm → cgroups → SafeBox Sandbox → Real Application Execution
This module makes SafeBox actually run real programs with real resource limits.
"""

import subprocess
import os
import sys
import json
import psutil
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from .banker import BankerAlgorithm


# ============================================================================
# SYSTEM EXECUTOR - THE INTEGRATION LAYER
# ============================================================================
# This class brings together all three team members' work:
# - Ritika's Banker's Algorithm (decides if request is safe)
# - Ayush's cgroup agent (enforces resource limits)
# - Anika's SafeBox sandbox (provides security isolation)
#
# It's like a project manager coordinating different departments!

class SystemExecutor:
    """
    Real system executor that integrates all SafeBox components:
    1. Banker's Algorithm for safety checking
    2. cgroup creation and resource limiting
    3. SafeBox sandbox for secure execution
    4. Real application execution
    """
    
    def __init__(self, total_cpu_percent: int = 100, total_memory_mb: int = 1024):
        """
        Initialize the system executor.
        
        Args:
            total_cpu_percent: Total CPU percentage available (0-100)
            total_memory_mb: Total memory in MB available
        """
        # Initialize Banker's Algorithm with [CPU%, Memory MB]
        self.banker = BankerAlgorithm(
            total_resources=[total_cpu_percent, total_memory_mb],
            resource_names=['CPU%', 'Memory_MB']
        )
        
        self.project_root = Path(__file__).parent.parent.parent
        self.safebox_bin = self.project_root / "src" / "safebox"
        self.cgroup_agent_bin = self.project_root / "build" / "safebox_cgroup"
        
        self.job_counter = 0
        self.active_jobs: Dict[int, Dict] = {}
    
    # ========================================================================
    # PREREQUISITES CHECK
    # ========================================================================
    # Before running anything, we need to verify the system is ready:
    # - Running on Linux (cgroups are Linux-only)
    # - Running as root (needed for cgroup operations)
    # - All binaries are built and available
        
    def check_prerequisites(self) -> Tuple[bool, str]:
        """Check if all required components are available."""
        errors = []
        
        # Check if running on Linux
        if sys.platform != "linux":
            errors.append("❌ Must run on Linux (use WSL on Windows)")
        
        # Check for root/sudo
        if os.geteuid() != 0:
            errors.append("❌ Must run as root (use sudo)")
        
        # Check cgroup v2 support
        if not os.path.exists("/sys/fs/cgroup/cgroup.controllers"):
            errors.append("❌ cgroup v2 not available")
        
        # Check if SafeBox binary exists
        if not self.safebox_bin.exists():
            errors.append(f"❌ SafeBox binary not found at {self.safebox_bin}")
        
        # Check if cgroup agent exists
        if not self.cgroup_agent_bin.exists():
            errors.append(f"❌ cgroup agent not found at {self.cgroup_agent_bin}")
        
        if errors:
            return False, "\n".join(errors)
        
        return True, "✅ All prerequisites met"
    
    # ========================================================================
    # JOB EXECUTION - THE MAIN WORKFLOW
    # ========================================================================
    # This is where everything comes together! When a user wants to run a job:
    # 1. First, ask Banker's Algorithm: "Is this safe?"
    # 2. If yes, create a cgroup (Ayush's code)
    # 3. Apply resource limits (Ayush's code)
    # 4. Run in SafeBox sandbox (Anika's code)
    # 5. Return the output to the user
    
    def request_job(
        self,
        job_name: str,
        app_path: str,
        app_args: List[str],
        cpu_percent: int,
        memory_mb: int
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Request to run a job with specified resource limits.
        
        Flow:
        1. Check safety using Banker's Algorithm
        2. If safe, allocate resources
        3. Create cgroup
        4. Apply resource limits
        5. Launch SafeBox sandbox
        6. Run application
        
        Args:
            job_name: Human-readable job name
            app_path: Path to application binary
            app_args: Arguments for the application
            cpu_percent: CPU percentage limit (0-100)
            memory_mb: Memory limit in MB
            
        Returns:
            (success, message, job_id)
        """
        # Validate application exists
        if not os.path.exists(app_path):
            return False, f"❌ Application not found: {app_path}", None
        
        # Validate resource limits
        if cpu_percent < 1 or cpu_percent > 100:
            return False, f"❌ Invalid CPU percentage: {cpu_percent}", None
        if memory_mb < 1:
            return False, f"❌ Invalid memory limit: {memory_mb}MB", None
        
        # STEP 3: Check safety with Banker's Algorithm
        self.job_counter += 1
        job_id = self.job_counter
        
        # Add process to banker
        max_resources = [cpu_percent, memory_mb]
        if not self.banker.add_process(job_id, job_name, max_resources):
            return False, f"❌ Failed to add process to banker", None
        
        # Request resources
        success, msg = self.banker.request_resources(job_id, max_resources)
        
        if not success:
            # Unsafe state - reject
            self.banker.processes.pop(job_id, None)  # Remove process
            return False, f"🚫 UNSAFE: {msg}\n❌ Request REJECTED by Banker's Algorithm", None
        
        # SAFE! Proceed with execution
        cgroup_name = f"safebox_job_{job_id}"
        
        try:
            # STEP 4: Create cgroup
            result = self._create_cgroup(cgroup_name)
            if not result:
                raise Exception("Failed to create cgroup")
            
            # STEP 5: Apply resource limits
            self._apply_cpu_limit(cgroup_name, cpu_percent)
            self._apply_memory_limit(cgroup_name, memory_mb)
            
            # STEP 6 & 7: Launch SafeBox sandbox with application
            output = self._run_in_sandbox(cgroup_name, app_path, app_args)
            
            # Store job info
            self.active_jobs[job_id] = {
                'name': job_name,
                'app': app_path,
                'args': app_args,
                'cpu': cpu_percent,
                'memory': memory_mb,
                'cgroup': cgroup_name,
                'output': output
            }
            
            # STEP 8: Return results
            return True, f"✅ SUCCESS: {msg}\n📊 Output:\n{output}", job_id
            
        except Exception as e:
            # Cleanup on failure
            self.banker.release_resources(job_id, max_resources)
            self.banker.processes.pop(job_id, None)
            self._cleanup_cgroup(cgroup_name)
            return False, f"❌ Execution failed: {str(e)}", None
    
    # ========================================================================
    # CGROUP OPERATIONS - AYUSH'S CODE INTEGRATION
    # ========================================================================
    # These functions call the C++ cgroup agent binary to create groups
    # and apply resource limits. The cgroup agent writes to actual kernel
    # files at /sys/fs/cgroup/
    
    def _create_cgroup(self, cgroup_name: str) -> bool:
        """Create a new cgroup."""
        try:
            result = subprocess.run(
                [str(self.cgroup_agent_bin), "create", cgroup_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Created cgroup: {cgroup_name}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create cgroup: {e.stderr}")
            return False
    
    def _apply_cpu_limit(self, cgroup_name: str, cpu_percent: int) -> bool:
        """Apply CPU limit to cgroup."""
        try:
            # CPU quota/period: 100000us period, quota = percent * 1000
            quota = cpu_percent * 1000
            period = 100000
            
            result = subprocess.run(
                [str(self.cgroup_agent_bin), "cpu.set", cgroup_name, str(quota), str(period)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Applied CPU limit: {cpu_percent}%")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to apply CPU limit: {e.stderr}")
            return False
    
    def _apply_memory_limit(self, cgroup_name: str, memory_mb: int) -> bool:
        """Apply memory limit to cgroup."""
        try:
            memory_bytes = memory_mb * 1024 * 1024
            
            result = subprocess.run(
                [str(self.cgroup_agent_bin), "mem.set", cgroup_name, str(memory_bytes)],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Applied memory limit: {memory_mb}MB")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to apply memory limit: {e.stderr}")
            return False
    
    # ========================================================================
    # SANDBOX EXECUTION - ANIKA'S CODE INTEGRATION
    # ========================================================================
    # This runs the application inside SafeBox sandbox, which provides:
    # - Namespace isolation (can't see other processes)
    # - Seccomp filtering (can only use safe system calls)
    # - Security boundaries (can't escape the sandbox)
    
    def _run_in_sandbox(self, cgroup_name: str, app_path: str, app_args: List[str]) -> str:
        """Run application in SafeBox sandbox."""
        try:
            # Build command: safebox <app> <args>
            cmd = [str(self.safebox_bin), app_path] + app_args
            
            print(f"🚀 Launching: {' '.join(cmd)}")
            
            # Run in sandbox
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=str(self.project_root)
            )
            
            output = result.stdout if result.stdout else result.stderr
            print(f"✅ Execution completed")
            return output
            
        except subprocess.TimeoutExpired:
            return "❌ Execution timed out (30s limit)"
        except Exception as e:
            return f"❌ Execution error: {str(e)}"
    
    def _cleanup_cgroup(self, cgroup_name: str):
        """Remove cgroup."""
        try:
            cgroup_path = Path(f"/sys/fs/cgroup/{cgroup_name}")
            if cgroup_path.exists():
                cgroup_path.rmdir()
                print(f"🗑️  Cleaned up cgroup: {cgroup_name}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to cleanup cgroup: {e}")
    
    # ========================================================================
    # RESOURCE CLEANUP
    # ========================================================================
    # After a job completes, we need to clean up:
    # - Tell Banker's Algorithm to free up the resources
    # - Delete the cgroup directory
    # - Remove job from our tracking
    
    def release_job(self, job_id: int) -> Tuple[bool, str]:
        """Release resources for a completed job."""
        if job_id not in self.active_jobs:
            return False, f"❌ Job {job_id} not found"
        
        job = self.active_jobs[job_id]
        
        # Release resources in Banker's Algorithm
        resources = [job['cpu'], job['memory']]
        success, msg = self.banker.release_resources(job_id, resources)
        
        # Cleanup cgroup
        self._cleanup_cgroup(job['cgroup'])
        
        # Remove from active jobs
        del self.active_jobs[job_id]
        
        return success, f"✅ Released job {job_id}: {msg}"
    
    # ========================================================================
    # SYSTEM MONITORING & REPORTING
    # ========================================================================
    # Functions to get information about what's currently happening:
    # - How many resources are available?
    # - Which jobs are running?
    # - Is the system in a safe state?
    
    def get_system_state(self) -> Dict:
        """Get current system state."""
        banker_state = self.banker.get_system_state()
        
        return {
            'banker': banker_state,
            'active_jobs': len(self.active_jobs),
            'jobs': self.active_jobs,
            'total_cpu': self.banker.total_resources[0],
            'total_memory': self.banker.total_resources[1],
            'available_cpu': self.banker.available[0],
            'available_memory': self.banker.available[1]
        }
    
    def list_available_apps(self) -> List[Dict]:
        """List available test applications."""
        apps = []
        
        # Check for calc_with_selftest
        calc_path = self.project_root / "src" / "calc_with_selftest"
        if calc_path.exists():
            apps.append({
                'name': 'Calculator with Self-Test',
                'path': str(calc_path),
                'description': 'Simple calculator with built-in tests',
                'suggested_cpu': 20,
                'suggested_memory': 50
            })
        
        # Check for test binary
        test_path = self.project_root / "src" / "test"
        if test_path.exists():
            apps.append({
                'name': 'Test Program',
                'path': str(test_path),
                'description': 'Basic test program',
                'suggested_cpu': 10,
                'suggested_memory': 30
            })
        
        return apps


# Example usage function
def example_usage():
    """Example of how to use SystemExecutor."""
    executor = SystemExecutor(total_cpu_percent=100, total_memory_mb=1024)
    
    # Check prerequisites
    ok, msg = executor.check_prerequisites()
    print(msg)
    if not ok:
        print("\n⚠️  Run with sudo on Linux/WSL:")
        print("   sudo python3 -m backend.app.system_executor")
        return
    
    # List available apps
    apps = executor.list_available_apps()
    print(f"\n📱 Available applications: {len(apps)}")
    for app in apps:
        print(f"   - {app['name']}: {app['path']}")
    
    if not apps:
        print("❌ No test applications found. Build them first:")
        print("   cd src && make")
        return
    
    # Request job
    app = apps[0]
    success, msg, job_id = executor.request_job(
        job_name="Test Job 1",
        app_path=app['path'],
        app_args=[],
        cpu_percent=app['suggested_cpu'],
        memory_mb=app['suggested_memory']
    )
    
    print(f"\n{msg}")
    
    if success:
        # Show system state
        state = executor.get_system_state()
        print(f"\n📊 System State:")
        print(f"   Safe: {state['banker']['is_safe']}")
        print(f"   Safe Sequence: {state['banker']['safe_sequence']}")
        print(f"   Available: CPU={state['available_cpu']}%, Memory={state['available_memory']}MB")
        
        # Release job
        success, msg = executor.release_job(job_id)
        print(f"\n{msg}")


if __name__ == "__main__":
    example_usage()
