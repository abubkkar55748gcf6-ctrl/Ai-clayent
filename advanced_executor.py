#!/usr/bin/env python3
"""
Advanced Command Executor
Handles complex command execution scenarios including threading and remote execution
"""

import threading
import json
import time
from typing import Dict, List, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import paramiko
from datetime import datetime

class AdvancedCommandExecutor:
    """Advanced command execution with threading and remote support"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_results = {}
        self.active_tasks = {}
    
    def execute_async(self, command: str, callback: Optional[Callable] = None) -> str:
        """Execute command asynchronously"""
        task_id = f"task_{int(time.time() * 1000)}"
        
        def async_execution():
            try:
                from main import KaliLinuxController
                controller = KaliLinuxController()
                result = controller.execute_command(command)
                self.task_results[task_id] = result
                
                if callback:
                    callback(result)
                
                return result
            except Exception as e:
                error_result = {
                    "success": False,
                    "error": str(e),
                    "command": command
                }
                self.task_results[task_id] = error_result
                if callback:
                    callback(error_result)
                return error_result
        
        future = self.executor.submit(async_execution)
        self.active_tasks[task_id] = future
        return task_id
    
    def execute_parallel(self, commands: List[str]) -> Dict[str, Dict]:
        """Execute multiple commands in parallel"""
        results = {}
        futures = {}
        
        from main import KaliLinuxController
        controller = KaliLinuxController()
        
        for i, command in enumerate(commands):
            task_id = f"parallel_task_{i}_{int(time.time() * 1000)}"
            future = self.executor.submit(controller.execute_command, command)
            futures[task_id] = future
        
        for task_id, future in as_completed(futures):
            try:
                results[task_id] = future.result()
            except Exception as e:
                results[task_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def get_task_result(self, task_id: str) -> Optional[Dict]:
        """Retrieve result of async task"""
        return self.task_results.get(task_id)
    
    def is_task_complete(self, task_id: str) -> bool:
        """Check if task is complete"""
        if task_id not in self.active_tasks:
            return task_id in self.task_results
        
        return self.active_tasks[task_id].done()
    
    def wait_for_task(self, task_id: str, timeout: int = 60) -> Optional[Dict]:
        """Wait for task completion"""
        if task_id in self.task_results:
            return self.task_results[task_id]
        
        if task_id not in self.active_tasks:
            return None
        
        try:
            self.active_tasks[task_id].result(timeout=timeout)
            return self.task_results.get(task_id)
        except Exception as e:
            return {"success": False, "error": str(e)}


class RemoteCommandExecutor:
    """Execute commands on remote Kali Linux systems via SSH"""
    
    def __init__(self, host: str, port: int = 22, username: str = "root", password: str = None, key_file: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_file = key_file
        self.client = None
    
    def connect(self) -> bool:
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_file:
                self.client.connect(self.host, self.port, self.username, key_filename=self.key_file)
            else:
                self.client.connect(self.host, self.port, self.username, self.password)
            
            return True
        except Exception as e:
            print(f"[ERROR] SSH Connection failed: {e}")
            return False
    
    def execute_command(self, command: str) -> Dict:
        """Execute command on remote system"""
        if not self.client:
            return {"success": False, "error": "Not connected"}
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=30)
            
            return {
                "success": True,
                "command": command,
                "stdout": stdout.read().decode('utf-8'),
                "stderr": stderr.read().decode('utf-8'),
                "return_code": stdout.channel.recv_exit_status(),
                "host": self.host,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "host": self.host
            }
    
    def execute_file(self, local_file: str, remote_path: str = "/tmp") -> Dict:
        """Transfer and execute file on remote system"""
        try:
            sftp = self.client.open_sftp()
            remote_file = f"{remote_path}/{local_file.split('/')[-1]}"
            sftp.put(local_file, remote_file)
            sftp.chmod(remote_file, 0o755)
            sftp.close()
            
            # Execute the file
            return self.execute_command(f"python3 {remote_file}")
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class CommandOrchestrator:
    """Orchestrate complex command workflows"""
    
    def __init__(self):
        self.advanced_executor = AdvancedCommandExecutor()
        self.workflows = {}
    
    def create_workflow(self, workflow_name: str, commands: List[Dict]) -> str:
        """
        Create a workflow of commands
        commands format: [{"cmd": "command", "wait": True, "timeout": 30}, ...]
        """
        self.workflows[workflow_name] = {
            "commands": commands,
            "status": "created",
            "results": [],
            "created_at": datetime.now().isoformat()
        }
        return workflow_name
    
    def execute_workflow(self, workflow_name: str) -> Dict:
        """Execute a complete workflow"""
        if workflow_name not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_name]
        workflow["status"] = "running"
        workflow["results"] = []
        
        from main import KaliLinuxController
        controller = KaliLinuxController()
        
        for i, step in enumerate(workflow["commands"]):
            cmd = step.get("cmd")
            wait = step.get("wait", True)
            timeout = step.get("timeout", 30)
            
            print(f"[*] Executing step {i+1}: {cmd}")
            
            try:
                result = controller.execute_command(cmd)
                workflow["results"].append(result)
                
                if not result["success"] and step.get("fail_stop", False):
                    workflow["status"] = "failed"
                    break
                
                if wait:
                    time.sleep(step.get("wait_time", 1))
            
            except Exception as e:
                workflow["results"].append({"success": False, "error": str(e)})
        
        workflow["status"] = "completed"
        return {
            "success": True,
            "workflow": workflow_name,
            "results": workflow["results"]
        }
    
    def get_workflow_status(self, workflow_name: str) -> Dict:
        """Get status of a workflow"""
        if workflow_name not in self.workflows:
            return {"error": "Workflow not found"}
        
        return self.workflows[workflow_name]


if __name__ == "__main__":
    # Example usage
    executor = AdvancedCommandExecutor()
    
    # Async execution example
    task_id = executor.execute_async("whoami")
    print(f"Task ID: {task_id}")
    
    time.sleep(2)
    result = executor.get_task_result(task_id)
    print(f"Result: {result}")
    
    # Parallel execution example
    commands = ["id", "pwd", "whoami"]
    results = executor.execute_parallel(commands)
    print(f"Parallel results: {json.dumps(results, indent=2)}")
