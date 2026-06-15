#!/usr/bin/env python3
"""
REST API Server for AI Clayent
Provides HTTP endpoints for command execution
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
from main import KaliLinuxController
from advanced_executor import RemoteCommandExecutor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize controller
controller = KaliLinuxController()

# Store active sessions
sessions = {}


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Clayent",
        "version": "1.0"
    }), 200


@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute command endpoint"""
    try:
        data = request.get_json()
        user_input = data.get('command', '').strip()
        
        if not user_input:
            return jsonify({"error": "Command cannot be empty"}), 400
        
        result = controller.execute_command(user_input)
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/execute/async', methods=['POST'])
def execute_async():
    """Execute command asynchronously"""
    try:
        data = request.get_json()
        user_input = data.get('command', '').strip()
        
        if not user_input:
            return jsonify({"error": "Command cannot be empty"}), 400
        
        # Parse command
        command, params = controller.parser.parse(user_input)
        
        # Execute async
        task_id = controller.executor.execute_async(command)
        
        return jsonify({
            "task_id": task_id,
            "command": command,
            "status": "pending"
        }), 202
    
    except Exception as e:
        logger.error(f"Error executing async command: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/task/<task_id>', methods=['GET'])
def get_task_result(task_id):
    """Get result of async task"""
    try:
        is_complete = controller.executor.is_task_complete(task_id)
        result = controller.executor.get_task_result(task_id)
        
        return jsonify({
            "task_id": task_id,
            "complete": is_complete,
            "result": result
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting task result: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/execute/remote', methods=['POST'])
def execute_remote():
    """Execute command on remote system"""
    try:
        data = request.get_json()
        host = data.get('host')
        command = data.get('command')
        username = data.get('username', 'root')
        password = data.get('password')
        key_file = data.get('key_file')
        
        if not host or not command:
            return jsonify({"error": "Host and command are required"}), 400
        
        result = controller.execute_remote(
            host=host,
            command=command,
            username=username,
            password=password,
            key_file=key_file
        )
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error executing remote command: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/parse', methods=['POST'])
def parse_command():
    """Parse natural language to command"""
    try:
        data = request.get_json()
        user_input = data.get('input', '').strip()
        
        if not user_input:
            return jsonify({"error": "Input cannot be empty"}), 400
        
        command, params = controller.parser.parse(user_input)
        
        return jsonify({
            "input": user_input,
            "command": command,
            "params": params
        }), 200
    
    except Exception as e:
        logger.error(f"Error parsing command: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/workflow', methods=['POST'])
def create_workflow():
    """Create and execute workflow"""
    try:
        data = request.get_json()
        workflow_name = data.get('name', 'workflow')
        commands = data.get('commands', [])
        
        if not commands:
            return jsonify({"error": "Commands array is required"}), 400
        
        result = controller.execute_workflow(workflow_name, commands)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get command history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = controller.get_history(limit)
        
        return jsonify({
            "history": history,
            "total": len(history)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/safe-mode', methods=['GET', 'POST'])
def safe_mode():
    """Get or set safe mode"""
    try:
        if request.method == 'GET':
            return jsonify({
                "safe_mode": controller.safe_mode
            }), 200
        
        else:  # POST
            data = request.get_json()
            enabled = data.get('enabled', True)
            controller.set_safe_mode(enabled)
            
            return jsonify({
                "safe_mode": controller.safe_mode,
                "message": f"Safe mode {'enabled' if enabled else 'disabled'}"
            }), 200
    
    except Exception as e:
        logger.error(f"Error with safe mode: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/parallel', methods=['POST'])
def execute_parallel():
    """Execute multiple commands in parallel"""
    try:
        data = request.get_json()
        commands = data.get('commands', [])
        
        if not commands:
            return jsonify({"error": "Commands array is required"}), 400
        
        results = controller.executor.execute_parallel(commands)
        
        return jsonify({
            "commands_count": len(commands),
            "results": results
        }), 200
    
    except Exception as e:
        logger.error(f"Error executing parallel commands: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and info"""
    return jsonify({
        "status": "running",
        "service": "AI Clayent API",
        "version": "1.0",
        "safe_mode": controller.safe_mode,
        "command_count": len(controller.command_history)
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == "__main__":
    print("Starting AI Clayent API Server...")
    print("API available at http://localhost:5000")
    print("Documentation:")
    print("  POST /api/execute - Execute command")
    print("  POST /api/execute/async - Execute async")
    print("  GET /api/task/<id> - Get async result")
    print("  POST /api/parse - Parse natural language")
    app.run(host='0.0.0.0', port=5000, debug=True)
