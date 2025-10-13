"""
Banker's Algorithm Implementation for Deadlock Prevention
Author: Ritika
Module: SafeBox Resource Management System

This module implements the Banker's Algorithm for deadlock avoidance in 
resource allocation systems. The algorithm ensures the system remains in 
a safe state by checking if resource allocation will lead to deadlock.
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import copy


@dataclass
class ProcessState:
    """Represents the resource state of a single process"""
    pid: int
    name: str
    max_resources: List[int]  # Maximum resources needed
    allocated: List[int]       # Currently allocated resources
    need: List[int]            # Still needed resources (max - allocated)


class BankerAlgorithm:
    """
    Implementation of Banker's Algorithm for deadlock avoidance.
    
    The algorithm maintains system state and determines if resource 
    allocation requests can be safely granted without causing deadlock.
    """
    
    def __init__(self, total_resources: List[int], resource_names: Optional[List[str]] = None):
        """
        Initialize the Banker's Algorithm system.
        
        Args:
            total_resources: List of total available resources in the system
            resource_names: Optional names for resources (e.g., ['CPU', 'Memory', 'Disk'])
        """
        self.total_resources = total_resources
        self.num_resources = len(total_resources)
        self.resource_names = resource_names or [f"R{i}" for i in range(self.num_resources)]
        self.processes: Dict[int, ProcessState] = {}
        self.available = total_resources.copy()
        self.history: List[Dict] = []
        
    def add_process(self, pid: int, name: str, max_resources: List[int]) -> bool:
        """
        Add a new process to the system.
        
        Args:
            pid: Process ID
            name: Process name
            max_resources: Maximum resources the process may need
            
        Returns:
            True if process added successfully, False otherwise
        """
        if len(max_resources) != self.num_resources:
            return False
            
        # Check if max_resources exceeds total available
        for i in range(self.num_resources):
            if max_resources[i] > self.total_resources[i]:
                return False
        
        self.processes[pid] = ProcessState(
            pid=pid,
            name=name,
            max_resources=max_resources,
            allocated=[0] * self.num_resources,
            need=max_resources.copy()
        )
        return True
    
    def request_resources(self, pid: int, request: List[int]) -> Tuple[bool, str]:
        """
        Process a resource request from a process.
        
        Args:
            pid: Process ID requesting resources
            request: List of resources requested
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if pid not in self.processes:
            return False, f"Process {pid} not found"
        
        process = self.processes[pid]
        
        # Check if request exceeds need
        for i in range(self.num_resources):
            if request[i] > process.need[i]:
                return False, f"Request exceeds maximum need for {self.resource_names[i]}"
        
        # Check if request exceeds available
        for i in range(self.num_resources):
            if request[i] > self.available[i]:
                return False, f"Request exceeds available {self.resource_names[i]}"
        
        # Tentatively allocate resources
        for i in range(self.num_resources):
            self.available[i] -= request[i]
            process.allocated[i] += request[i]
            process.need[i] -= request[i]
        
        # Check if system is in safe state
        is_safe, safe_sequence = self.is_safe_state()
        
        if is_safe:
            self.history.append({
                'action': 'allocate',
                'pid': pid,
                'request': request.copy(),
                'safe_sequence': safe_sequence
            })
            return True, f"Request granted. Safe sequence: {safe_sequence}"
        else:
            # Rollback allocation
            for i in range(self.num_resources):
                self.available[i] += request[i]
                process.allocated[i] -= request[i]
                process.need[i] += request[i]
            return False, "Request denied: Would lead to unsafe state (potential deadlock)"
    
    def release_resources(self, pid: int, release: List[int]) -> Tuple[bool, str]:
        """
        Release resources from a process.
        
        Args:
            pid: Process ID releasing resources
            release: List of resources to release
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if pid not in self.processes:
            return False, f"Process {pid} not found"
        
        process = self.processes[pid]
        
        # Check if release exceeds allocated
        for i in range(self.num_resources):
            if release[i] > process.allocated[i]:
                return False, f"Cannot release more {self.resource_names[i]} than allocated"
        
        # Release resources
        for i in range(self.num_resources):
            self.available[i] += release[i]
            process.allocated[i] -= release[i]
            process.need[i] += release[i]
        
        self.history.append({
            'action': 'release',
            'pid': pid,
            'release': release.copy()
        })
        
        return True, "Resources released successfully"
    
    def is_safe_state(self) -> Tuple[bool, List[int]]:
        """
        Check if the system is in a safe state using safety algorithm.
        
        Returns:
            Tuple of (is_safe: bool, safe_sequence: List[int])
        """
        work = self.available.copy()
        finish = {pid: False for pid in self.processes}
        safe_sequence = []
        
        while len(safe_sequence) < len(self.processes):
            found = False
            
            for pid, process in self.processes.items():
                if finish[pid]:
                    continue
                
                # Check if process can finish with available resources
                can_finish = all(
                    process.need[i] <= work[i] 
                    for i in range(self.num_resources)
                )
                
                if can_finish:
                    # Process can finish, add its allocated resources to work
                    for i in range(self.num_resources):
                        work[i] += process.allocated[i]
                    finish[pid] = True
                    safe_sequence.append(pid)
                    found = True
                    break
            
            if not found:
                # No process can finish, unsafe state
                return False, []
        
        return True, safe_sequence
    
    def get_system_state(self) -> Dict:
        """
        Get current system state snapshot.
        
        Returns:
            Dictionary containing complete system state
        """
        is_safe, safe_seq = self.is_safe_state()
        
        return {
            'total_resources': self.total_resources,
            'available': self.available,
            'resource_names': self.resource_names,
            'processes': {
                pid: {
                    'name': p.name,
                    'max': p.max_resources,
                    'allocated': p.allocated,
                    'need': p.need
                }
                for pid, p in self.processes.items()
            },
            'is_safe': is_safe,
            'safe_sequence': safe_seq,
            'total_processes': len(self.processes)
        }
    
    def remove_process(self, pid: int) -> bool:
        """
        Remove a process and release all its resources.
        
        Args:
            pid: Process ID to remove
            
        Returns:
            True if process removed successfully
        """
        if pid not in self.processes:
            return False
        
        process = self.processes[pid]
        
        # Release all allocated resources
        for i in range(self.num_resources):
            self.available[i] += process.allocated[i]
        
        del self.processes[pid]
        self.history.append({
            'action': 'remove',
            'pid': pid
        })
        
        return True
    
    def simulate_scenario(self, scenario: List[Tuple[int, List[int]]]) -> List[Dict]:
        """
        Simulate a sequence of resource requests.
        
        Args:
            scenario: List of (pid, request) tuples
            
        Returns:
            List of simulation results
        """
        results = []
        
        for pid, request in scenario:
            success, message = self.request_resources(pid, request)
            state = self.get_system_state()
            
            results.append({
                'pid': pid,
                'request': request,
                'success': success,
                'message': message,
                'state_after': state
            })
            
            if not success:
                break
        
        return results
    
    def detect_deadlock(self) -> Tuple[bool, List[int]]:
        """
        Detect if system is currently in deadlock.
        
        Returns:
            Tuple of (is_deadlock: bool, deadlocked_processes: List[int])
        """
        is_safe, _ = self.is_safe_state()
        
        if is_safe:
            return False, []
        
        # Find processes that cannot proceed
        deadlocked = []
        for pid, process in self.processes.items():
            can_proceed = all(
                process.need[i] <= self.available[i]
                for i in range(self.num_resources)
            )
            if not can_proceed and any(n > 0 for n in process.need):
                deadlocked.append(pid)
        
        return len(deadlocked) > 0, deadlocked


def create_example_scenario() -> BankerAlgorithm:
    """
    Create an example scenario for demonstration.
    
    Returns:
        Configured BankerAlgorithm instance
    """
    # System with 3 resource types: CPU cores, Memory GB, Disk GB
    banker = BankerAlgorithm(
        total_resources=[10, 5, 7],
        resource_names=['CPU', 'Memory', 'Disk']
    )
    
    # Add processes with their maximum needs
    banker.add_process(0, "WebServer", [7, 5, 3])
    banker.add_process(1, "Database", [3, 2, 2])
    banker.add_process(2, "Cache", [9, 0, 2])
    banker.add_process(3, "Worker", [2, 2, 2])
    banker.add_process(4, "Monitor", [4, 3, 3])
    
    # Initial allocation
    banker.request_resources(0, [0, 1, 0])  # WebServer
    banker.request_resources(1, [2, 0, 0])  # Database
    banker.request_resources(2, [3, 0, 2])  # Cache
    banker.request_resources(3, [2, 1, 1])  # Worker
    banker.request_resources(4, [0, 0, 2])  # Monitor
    
    return banker


if __name__ == "__main__":
    # Demo execution
    print("=" * 60)
    print("Banker's Algorithm - Deadlock Prevention Demo")
    print("=" * 60)
    
    banker = create_example_scenario()
    state = banker.get_system_state()
    
    print(f"\n✅ System State: {'SAFE' if state['is_safe'] else 'UNSAFE'}")
    print(f"Safe Sequence: {state['safe_sequence']}")
    print(f"\nAvailable Resources: {dict(zip(state['resource_names'], state['available']))}")
    
    print("\n" + "=" * 60)
    print("Testing Resource Request")
    print("=" * 60)
    
    success, msg = banker.request_resources(1, [1, 0, 2])
    print(f"\nRequest: P1 needs [1, 0, 2]")
    print(f"Result: {'✅ GRANTED' if success else '❌ DENIED'}")
    print(f"Message: {msg}")
