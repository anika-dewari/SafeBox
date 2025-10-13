"""
Unit Tests for Banker's Algorithm
Author: Ritika
Testing Framework: pytest

Comprehensive test suite covering:
- Basic functionality
- Edge cases
- Safety algorithm
- Deadlock detection
- Resource allocation/release
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.banker import BankerAlgorithm, ProcessState, create_example_scenario


class TestBankerAlgorithmBasics:
    """Test basic banker algorithm initialization and setup"""
    
    def test_initialization(self):
        """Test banker system initialization"""
        banker = BankerAlgorithm([10, 5, 7], ['CPU', 'Memory', 'Disk'])
        assert banker.total_resources == [10, 5, 7]
        assert banker.available == [10, 5, 7]
        assert banker.resource_names == ['CPU', 'Memory', 'Disk']
        assert len(banker.processes) == 0
    
    def test_add_process_valid(self):
        """Test adding valid process"""
        banker = BankerAlgorithm([10, 5, 7])
        result = banker.add_process(0, "TestProcess", [7, 5, 3])
        assert result is True
        assert 0 in banker.processes
        assert banker.processes[0].name == "TestProcess"
        assert banker.processes[0].max_resources == [7, 5, 3]
        assert banker.processes[0].allocated == [0, 0, 0]
        assert banker.processes[0].need == [7, 5, 3]
    
    def test_add_process_exceeds_total(self):
        """Test adding process with max > total resources"""
        banker = BankerAlgorithm([10, 5, 7])
        result = banker.add_process(0, "InvalidProcess", [15, 5, 3])
        assert result is False
        assert 0 not in banker.processes
    
    def test_add_process_wrong_dimensions(self):
        """Test adding process with wrong resource dimensions"""
        banker = BankerAlgorithm([10, 5, 7])
        result = banker.add_process(0, "InvalidProcess", [7, 5])  # Only 2 resources
        assert result is False


class TestResourceAllocation:
    """Test resource allocation and request handling"""
    
    def test_simple_allocation(self):
        """Test simple resource allocation"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        
        success, msg = banker.request_resources(0, [0, 1, 0])
        assert success is True
        assert banker.processes[0].allocated == [0, 1, 0]
        assert banker.processes[0].need == [7, 4, 3]
        assert banker.available == [10, 4, 7]
    
    def test_request_exceeds_need(self):
        """Test request exceeding process need"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        
        success, msg = banker.request_resources(0, [8, 0, 0])
        assert success is False
        assert "exceeds maximum need" in msg.lower()
    
    def test_request_exceeds_available(self):
        """Test request exceeding available resources"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [15, 10, 10])
        
        success, msg = banker.request_resources(0, [11, 0, 0])
        assert success is False
        assert "exceeds available" in msg.lower()
    
    def test_request_nonexistent_process(self):
        """Test request from non-existent process"""
        banker = BankerAlgorithm([10, 5, 7])
        success, msg = banker.request_resources(99, [1, 1, 1])
        assert success is False
        assert "not found" in msg.lower()
    
    def test_unsafe_allocation_rejected(self):
        """Test that unsafe allocation is rejected"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.add_process(1, "P1", [3, 2, 2])
        
        # Allocate resources
        banker.request_resources(0, [7, 4, 3])
        
        # This should be rejected as it would lead to unsafe state
        success, msg = banker.request_resources(1, [3, 2, 2])
        assert success is False
        assert "unsafe state" in msg.lower() or "deadlock" in msg.lower()


class TestResourceRelease:
    """Test resource release functionality"""
    
    def test_release_resources(self):
        """Test releasing allocated resources"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.request_resources(0, [2, 2, 2])
        
        success, msg = banker.release_resources(0, [1, 1, 1])
        assert success is True
        assert banker.processes[0].allocated == [1, 1, 1]
        assert banker.processes[0].need == [6, 4, 2]
        assert banker.available == [9, 4, 6]
    
    def test_release_exceeds_allocated(self):
        """Test releasing more than allocated"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.request_resources(0, [2, 2, 2])
        
        success, msg = banker.release_resources(0, [3, 0, 0])
        assert success is False
        assert "cannot release more" in msg.lower()


class TestSafetyAlgorithm:
    """Test safety algorithm and safe state detection"""
    
    def test_safe_state_detection(self):
        """Test detection of safe state"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.add_process(1, "P1", [3, 2, 2])
        banker.add_process(2, "P2", [9, 0, 2])
        
        # Initial allocations
        banker.request_resources(0, [0, 1, 0])
        banker.request_resources(1, [2, 0, 0])
        banker.request_resources(2, [3, 0, 2])
        
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
        assert len(sequence) == 3
        assert set(sequence) == {0, 1, 2}
    
    def test_unsafe_state_detection(self):
        """Test detection of unsafe state"""
        banker = BankerAlgorithm([5, 3, 3])
        banker.add_process(0, "P0", [5, 3, 3])
        banker.add_process(1, "P1", [5, 3, 3])
        
        # Allocate all resources to P0
        banker.request_resources(0, [5, 3, 3])
        
        # Now system is unsafe as P1 needs [5,3,3] but none available
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is False
        assert sequence == []
    
    def test_empty_system_is_safe(self):
        """Test that empty system is safe"""
        banker = BankerAlgorithm([10, 5, 7])
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
        assert sequence == []


class TestProcessManagement:
    """Test process lifecycle management"""
    
    def test_remove_process(self):
        """Test removing a process"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.request_resources(0, [2, 2, 2])
        
        initial_available = banker.available.copy()
        success = banker.remove_process(0)
        
        assert success is True
        assert 0 not in banker.processes
        # Resources should be returned
        assert banker.available == [initial_available[0] + 2, 
                                   initial_available[1] + 2, 
                                   initial_available[2] + 2]
    
    def test_remove_nonexistent_process(self):
        """Test removing non-existent process"""
        banker = BankerAlgorithm([10, 5, 7])
        success = banker.remove_process(99)
        assert success is False


class TestSystemState:
    """Test system state reporting"""
    
    def test_get_system_state(self):
        """Test getting complete system state"""
        banker = BankerAlgorithm([10, 5, 7], ['CPU', 'Memory', 'Disk'])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.request_resources(0, [2, 2, 2])
        
        state = banker.get_system_state()
        
        assert 'total_resources' in state
        assert 'available' in state
        assert 'processes' in state
        assert 'is_safe' in state
        assert 'safe_sequence' in state
        assert state['total_processes'] == 1
        assert state['resource_names'] == ['CPU', 'Memory', 'Disk']


class TestScenarioSimulation:
    """Test scenario simulation"""
    
    def test_simulate_scenario(self):
        """Test simulating a sequence of requests"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        banker.add_process(1, "P1", [3, 2, 2])
        
        scenario = [
            (0, [2, 2, 2]),
            (1, [1, 1, 1])
        ]
        
        results = banker.simulate_scenario(scenario)
        assert len(results) == 2
        assert all('success' in r for r in results)
        assert all('message' in r for r in results)
        assert all('state_after' in r for r in results)


class TestDeadlockDetection:
    """Test deadlock detection"""
    
    def test_no_deadlock_in_safe_state(self):
        """Test no deadlock in safe state"""
        banker = create_example_scenario()
        is_deadlock, deadlocked = banker.detect_deadlock()
        assert is_deadlock is False
        assert deadlocked == []
    
    def test_deadlock_detection_in_unsafe_state(self):
        """Test deadlock detection in unsafe state"""
        banker = BankerAlgorithm([3, 3, 3])
        banker.add_process(0, "P0", [3, 3, 3])
        banker.add_process(1, "P1", [3, 3, 3])
        
        # Allocate resources creating potential deadlock
        banker.request_resources(0, [2, 2, 2])
        banker.request_resources(1, [2, 2, 2])
        
        # Now both processes need [1,1,1] but none available - deadlock
        is_deadlock, deadlocked = banker.detect_deadlock()
        # System should detect this as problematic
        assert is_deadlock is True or len(deadlocked) > 0


class TestExampleScenario:
    """Test the example scenario"""
    
    def test_example_scenario_creation(self):
        """Test that example scenario creates valid state"""
        banker = create_example_scenario()
        assert len(banker.processes) == 5
        
        state = banker.get_system_state()
        assert state['is_safe'] is True
        assert len(state['safe_sequence']) == 5
    
    def test_example_scenario_is_safe(self):
        """Test that example scenario is in safe state"""
        banker = create_example_scenario()
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
        assert len(sequence) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_zero_resources(self):
        """Test system with zero resources"""
        banker = BankerAlgorithm([0, 0, 0])
        banker.add_process(0, "P0", [0, 0, 0])
        
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
    
    def test_single_resource_type(self):
        """Test system with single resource type"""
        banker = BankerAlgorithm([10])
        banker.add_process(0, "P0", [5])
        banker.add_process(1, "P1", [5])
        
        banker.request_resources(0, [3])
        banker.request_resources(1, [2])
        
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
    
    def test_request_zero_resources(self):
        """Test requesting zero resources"""
        banker = BankerAlgorithm([10, 5, 7])
        banker.add_process(0, "P0", [7, 5, 3])
        
        success, msg = banker.request_resources(0, [0, 0, 0])
        assert success is True


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_complete_workflow(self):
        """Test complete allocation and release workflow"""
        banker = BankerAlgorithm([10, 5, 7], ['CPU', 'Memory', 'Disk'])
        
        # Add processes
        banker.add_process(0, "WebServer", [7, 5, 3])
        banker.add_process(1, "Database", [3, 2, 2])
        
        # Allocate resources
        success1, _ = banker.request_resources(0, [2, 2, 2])
        success2, _ = banker.request_resources(1, [1, 1, 1])
        
        assert success1 and success2
        
        # Check safe state
        is_safe, sequence = banker.is_safe_state()
        assert is_safe is True
        
        # Release and reallocate
        banker.release_resources(0, [1, 1, 1])
        success3, _ = banker.request_resources(1, [1, 1, 1])
        
        assert success3 is True
        
        # Remove process
        banker.remove_process(0)
        assert 0 not in banker.processes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
