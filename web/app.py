"""
SafeBox Web UI - Flask Application
Author: Ritika
Purpose: Interactive web dashboard for banker's algorithm visualization

Features:
- Real-time system state visualization
- Interactive resource allocation
- Process management
- Historical tracking
- Export capabilities
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.banker import BankerAlgorithm, create_example_scenario

app = Flask(__name__)
CORS(app)

# Global banker instance
banker = None
history = []


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def api_init():
    """Initialize banker system"""
    global banker, history
    
    data = request.json
    num_resources = data.get('num_resources', 3)
    available = data.get('available', [10, 5, 7])
    
    # Generate resource names
    names = [f'R{i}' for i in range(num_resources)]
    
    banker = BankerAlgorithm(available, names)
    history = [{
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': 'System initialized with {} resources'.format(num_resources)
    }]
    
    return jsonify({
        'success': True,
        'message': 'System initialized successfully'
    })


@app.route('/api/load-example', methods=['POST'])
def api_load_example():
    """Load example scenario"""
    global banker, history
    
    banker = create_example_scenario()
    history = [{
        'timestamp': datetime.now().isoformat(),
        'action': 'load_example',
        'message': 'Example scenario loaded',
        'state': banker.get_system_state()
    }]
    
    return jsonify({
        'success': True,
        'message': 'Example scenario loaded',
        'state': banker.get_system_state()
    })


@app.route('/api/state', methods=['GET'])
def api_state():
    """Get current system state"""
    if not banker:
        # Return uninitialized state instead of error
        return jsonify({
            'initialized': False,
            'is_safe': False,
            'num_processes': 0,
            'processes': [],
            'available': [],
            'total_resources': [],
            'safe_sequence': [],
            'history': [],
            'stats': {
                'total_requests': 0,
                'successful_requests': 0,
                'denied_requests': 0,
                'success_rate': 0
            }
        })
    
    state = banker.get_system_state()
    state['initialized'] = True
    state['history'] = history[-10:] if len(history) > 0 else []
    
    # Add utilization metrics
    utilization = []
    for i, name in enumerate(state['resource_names']):
        total = state['total_resources'][i]
        available = state['available'][i]
        used = total - available
        utilization.append({
            'name': name,
            'total': total,
            'used': used,
            'available': available,
            'percentage': (used / total * 100) if total > 0 else 0
        })
    
    state['utilization'] = utilization
    
    # Add stats
    if not hasattr(api_state, 'stats'):
        api_state.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'denied_requests': 0,
            'success_rate': 0
        }
    state['stats'] = api_state.stats
    
    return jsonify(state)


@app.route('/api/add-process', methods=['POST'])
def api_add_process():
    """Add a new process"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json
    process_name = data.get('process_name')
    max_resources = data.get('max_resources')
    allocated = data.get('allocated', [0] * len(max_resources))
    
    # Generate PID
    pid = len(banker.processes) + 1
    
    success = banker.add_process(pid, process_name, max_resources)
    
    # Set allocated resources if provided
    if success and allocated and any(x > 0 for x in allocated):
        for i in range(len(allocated)):
            if allocated[i] > 0:
                banker.processes[pid].allocated[i] = allocated[i]
                banker.processes[pid].need[i] = max_resources[i] - allocated[i]
                banker.available[i] -= allocated[i]
    
    if success:
        history.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action': f'Process {process_name} added successfully'
        })
    
    return jsonify({
        'success': success,
        'message': f'Process {process_name} added successfully' if success else 'Failed to add process'
    })


@app.route('/api/request', methods=['POST'])
def api_request():
    """Request resources for a process"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json
    process_name = data.get('process_name')
    request_resources = data.get('request')
    
    # Find process by name
    pid = None
    for p_id, process in banker.processes.items():
        if process.name == process_name:
            pid = p_id
            break
    
    if pid is None:
        return jsonify({'error': f'Process {process_name} not found'}), 404
    
    success, message = banker.request_resources(pid, request_resources)
    
    # Update stats
    if not hasattr(api_state, 'stats'):
        api_state.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'denied_requests': 0,
            'success_rate': 0
        }
    
    api_state.stats['total_requests'] += 1
    if success:
        api_state.stats['successful_requests'] += 1
    else:
        api_state.stats['denied_requests'] += 1
    
    if api_state.stats['total_requests'] > 0:
        api_state.stats['success_rate'] = (api_state.stats['successful_requests'] / api_state.stats['total_requests']) * 100
    
    history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': f'{process_name}: {message}'
    })
    
    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/release', methods=['POST'])
def api_release():
    """Release resources from a process"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json
    process_name = data.get('process_name')
    release_resources = data.get('release')
    
    # Find process by name
    pid = None
    for p_id, process in banker.processes.items():
        if process.name == process_name:
            pid = p_id
            break
    
    if pid is None:
        return jsonify({'error': f'Process {process_name} not found'}), 404
    
    success, message = banker.release_resources(pid, release_resources)
    
    history.append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'action': f'{process_name}: Released resources {release_resources}'
    })
    
    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/remove-process', methods=['POST'])
def api_remove_process():
    """Remove a process"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json
    pid = data.get('pid')
    
    success = banker.remove_process(pid)
    
    if success:
        history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'remove_process',
            'pid': pid,
            'message': f'Process {pid} removed'
        })
    
    return jsonify({
        'success': success,
        'message': f'Process {pid} removed' if success else 'Failed to remove process',
        'state': banker.get_system_state()
    })


@app.route('/api/check-deadlock', methods=['GET'])
def api_check_deadlock():
    """Check for deadlock"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    is_deadlock, deadlocked_processes = banker.detect_deadlock()
    
    # Get process names instead of PIDs
    deadlocked_names = [banker.processes[pid].name for pid in deadlocked_processes if pid in banker.processes]
    
    return jsonify({
        'has_deadlock': is_deadlock,
        'deadlocked_processes': deadlocked_names,
        'message': 'Deadlock detected!' if is_deadlock else 'No deadlock detected'
    })


@app.route('/api/history', methods=['GET'])
def api_history():
    """Get action history"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'history': history[-limit:],
        'total': len(history)
    })


@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    """Simulate a sequence of requests"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    data = request.json
    scenario = data.get('scenario', [])
    
    results = banker.simulate_scenario(scenario)
    
    history.append({
        'timestamp': datetime.now().isoformat(),
        'action': 'simulate',
        'scenario': scenario,
        'results': results
    })
    
    return jsonify({
        'success': True,
        'results': results,
        'state': banker.get_system_state()
    })


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Get system statistics"""
    if not banker:
        return jsonify({'error': 'System not initialized'}), 400
    
    state = banker.get_system_state()
    
    # Calculate statistics
    total_requests = sum(1 for h in history if h.get('action') == 'request')
    successful_requests = sum(1 for h in history if h.get('action') == 'request' and h.get('success'))
    failed_requests = total_requests - successful_requests
    
    total_allocated = [0] * len(state['total_resources'])
    for proc_data in state['processes'].values():
        for i, alloc in enumerate(proc_data['allocated']):
            total_allocated[i] += alloc
    
    return jsonify({
        'total_processes': state['total_processes'],
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'failed_requests': failed_requests,
        'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        'total_allocated': total_allocated,
        'is_safe': state['is_safe'],
        'safe_sequence': state['safe_sequence']
    })


@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset the system"""
    global banker, history
    banker = None
    history = []
    
    # Reset stats
    if hasattr(api_state, 'stats'):
        api_state.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'denied_requests': 0,
            'success_rate': 0
        }
    
    return jsonify({
        'success': True,
        'message': 'System reset successfully'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("SafeBox Web UI - Starting...")
    print("=" * 60)
    print("\nAccess the dashboard at: http://localhost:5000")
    print("\nDeveloped by: Ritika")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
