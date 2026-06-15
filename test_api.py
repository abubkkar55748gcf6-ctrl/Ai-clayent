#!/usr/bin/env python3
"""
Test script for AI Clayent API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("[*] Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_parse_command():
    """Test command parsing"""
    print("[*] Testing parse endpoint...")
    
    test_inputs = [
        "scan 192.168.1.1",
        "find open ports on example.com",
        "list network interfaces",
        "check disk space"
    ]
    
    for user_input in test_inputs:
        payload = {"input": user_input}
        response = requests.post(f"{BASE_URL}/api/parse", json=payload)
        print(f"Input: {user_input}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_execute_command():
    """Test command execution"""
    print("[*] Testing execute endpoint...")
    
    commands = [
        "whoami",
        "pwd",
        "id"
    ]
    
    for cmd in commands:
        payload = {"command": cmd}
        response = requests.post(f"{BASE_URL}/api/execute", json=payload)
        print(f"Command: {cmd}")
        result = response.json()
        print(f"Success: {result.get('success')}")
        if result.get('output'):
            print(f"Output: {result.get('output')[:100]}")
        print()


def test_async_execution():
    """Test async execution"""
    print("[*] Testing async execution...")
    
    payload = {"command": "sleep 2 && whoami"}
    response = requests.post(f"{BASE_URL}/api/execute/async", json=payload)
    
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 202:
        task_id = response.json().get('task_id')
        print(f"\nWaiting for task {task_id}...")
        
        # Check status multiple times
        for i in range(5):
            time.sleep(1)
            result_response = requests.get(f"{BASE_URL}/api/task/{task_id}")
            result = result_response.json()
            print(f"Check {i+1}: Complete = {result.get('complete')}")
            if result.get('complete'):
                print(f"Result: {json.dumps(result, indent=2)}")
                break


def test_parallel_execution():
    """Test parallel execution"""
    print("[*] Testing parallel execution...")
    
    payload = {
        "commands": [
            "id",
            "whoami",
            "pwd"
        ]
    }
    
    response = requests.post(f"{BASE_URL}/api/parallel", json=payload)
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_history():
    """Test history endpoint"""
    print("[*] Testing history endpoint...")
    
    response = requests.get(f"{BASE_URL}/api/history?limit=5")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")


def test_safe_mode():
    """Test safe mode endpoints"""
    print("[*] Testing safe mode endpoints...")
    
    # Get current status
    response = requests.get(f"{BASE_URL}/api/safe-mode")
    print(f"Current safe mode: {json.dumps(response.json(), indent=2)}")
    
    # Set safe mode
    payload = {"enabled": False}
    response = requests.post(f"{BASE_URL}/api/safe-mode", json=payload)
    print(f"After setting: {json.dumps(response.json(), indent=2)}\n")


def main():
    """Run all tests"""
    print("="*60)
    print("AI Clayent API Test Suite")
    print("="*60 + "\n")
    
    try:
        test_health()
        test_parse_command()
        test_execute_command()
        test_async_execution()
        test_parallel_execution()
        test_history()
        test_safe_mode()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server")
        print("Make sure the server is running: python3 api_server.py")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
