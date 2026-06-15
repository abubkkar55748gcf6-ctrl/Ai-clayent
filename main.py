#!/usr/bin/env python3
"""
AI Clayent - Advanced AI Controller for Kali Linux
Understands human commands and Kali Linux commands
"""

import subprocess
import os
import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from advanced_executor import AdvancedCommandExecutor, RemoteCommandExecutor, CommandOrchestrator


class NaturalLanguageParser:
    """Parse natural language commands and map to Kali Linux commands"""
    
    # Command mappings from natural language to Kali Linux
    COMMAND_MAPPINGS = {
        # Reconnaissance
        r"(scan|enumerate|discover).*(host|server|ip|target)": "nmap -sV {target}",
        r"(find|search|locate).*(port|open)": "nmap -p- {target}",
        r"(check|find).*(dns|domain)": "nslookup {target}",
        r"(lookup|resolve).*(dns)": "dig {target}",
        r"(reverse|lookup).*(ip)": "host {target}",
        r"(whois|check).*(domain|owner)": "whois {target}",
        
        # Network Analysis
        r"(network|traffic).*(capture|sniff)": "tcpdump -i eth0 -n",
        r"(monitor|watch).*(network|traffic)": "tshark -i eth0",
        r"(check|list).*(interface|adapter)": "ip addr show",
        r"(get|show).*(route|routing)": "ip route show",
        r"(scan|check).*(subnet|network)": "nmap -sn {target}",
        
        # Wireless
        r"(scan|find).*(wifi|wireless|network)": "airmon-ng",
        r"(list|show).*(wireless|wifi).*(interface)": "iwconfig",
        r"(monitor).*(mode)": "airmon-ng start wlan0",
        
        # Exploitation
        r"(exploit|test).*(sql|injection)": "sqlmap -u '{url}' --batch",
        r"(brute|force).*(password|login)": "hydra -l {user} -P rockyou.txt {target}",
        r"(crack|break).*(hash)": "hashcat -m 0 -a 0 {hashfile} rockyou.txt",
        r"(password).*(crack)": "john --wordlist=rockyou.txt {file}",
        
        # Web Testing
        r"(web|http).*(crawl|spider)": "zaproxy",
        r"(scan|test).*(vulnerability|vuln)": "nikto -h {target}",
        r"(check|test).*(ssl|certificate)": "testssl.sh {target}",
        r"(proxy|intercept).*(traffic)": "burp",
        
        # Reverse Engineering
        r"(analyze|decompile|reverse).*(binary|exe|apk)": "ghidra {file}",
        r"(debug|analyze).*(binary)": "gdb {file}",
        r"(disassemble|analyze).*(code)": "objdump -d {file}",
        
        # Social Engineering
        r"(phishing|generate).*(payload)": "msfvenom -p windows/meterpreter/reverse_tcp",
        r"(create|generate).*(wordlist)": "crunch",
        r"(mask|create).*(password|wordlist)": "maskprocessor",
        
        # System & Utilities
        r"(list|show).*(file|directory)": "ls -la",
        r"(show|display).*(current).*(directory)": "pwd",
        r"(change|navigate).*(directory)": "cd {path}",
        r"(create|make).*(directory|folder)": "mkdir {path}",
        r"(delete|remove).*(file|folder)": "rm -rf {path}",
        r"(copy).*(file)": "cp {source} {dest}",
        r"(move|rename).*(file)": "mv {source} {dest}",
        r"(search|find).*(file)": "find / -name '{name}'",
        r"(view|cat|read).*(file|content)": "cat {file}",
        r"(edit|modify).*(file)": "nano {file}",
        r"(check|show).*(permission)": "ls -l {path}",
        r"(change).*(permission)": "chmod 755 {path}",
        
        # System Info
        r"(system|machine).*(info)": "uname -a",
        r"(show|get).*(system|os)": "cat /etc/os-release",
        r"(list|show).*(process|running)": "ps aux",
        r"(check|show).*(disk|space|storage)": "df -h",
        r"(show|get).*(memory|ram)": "free -h",
        r"(check|show).*(user|account)": "id",
        r"(list|show).*(user|account)": "cat /etc/passwd",
        
        # Network Utilities
        r"(ping|check).*(host|server|target)": "ping -c 4 {target}",
        r"(trace|traceroute).*(path)": "traceroute {target}",
        r"(check|test).*(connection|connectivity)": "ping -c 4 8.8.8.8",
        r"(get|show).*(ip|address)": "ip addr show",
        r"(check|show).*(port).*listening": "ss -tlnp",
        r"(listen|check).*(port)": "netstat -tlnp",
        
        # Tools
        r"(metasploit|msfconsole)": "msfconsole",
        r"(burp|burpsuite)": "burp",
        r"(wireshark|network|monitor)": "wireshark",
        r"(terminal|console)": "xterm",
        
        # Package Management
        r"(install|add).*(package)": "apt-get install {package}",
        r"(remove|uninstall).*(package)": "apt-get remove {package}",
        r"(update|refresh).*(packages)": "apt-get update",
        r"(upgrade).*(system)": "apt-get upgrade -y",
    }
    
    def __init__(self):
        self.last_target = None
        self.last_user = None
        self.command_history = []
    
    def parse(self, user_input: str) -> Tuple[str, Dict]:
        """Parse natural language input and return command with parameters"""
        user_input = user_input.lower().strip()
        self.command_history.append(user_input)
        
        # Extract potential target, URL, user, path, file
        target = self._extract_target(user_input)
        url = self._extract_url(user_input)
        user = self._extract_user(user_input)
        path = self._extract_path(user_input)
        filename = self._extract_filename(user_input)
        
        # Try to match patterns
        for pattern, command_template in self.COMMAND_MAPPINGS.items():
            if re.search(pattern, user_input):
                command = command_template
                
                # Substitute parameters
                if "{target}" in command:
                    command = command.replace("{target}", target or "192.168.1.1")
                if "{url}" in command:
                    command = command.replace("{url}", url or "http://example.com")
                if "{user}" in command:
                    command = command.replace("{user}", user or "admin")
                if "{path}" in command:
                    command = command.replace("{path}", path or "/tmp")
                if "{file}" in command:
                    command = command.replace("{file}", filename or "binary")
                if "{name}" in command:
                    command = command.replace("{name}", filename or "*")
                if "{package}" in command:
                    command = command.replace("{package}", target or "curl")
                if "{source}" in command:
                    command = command.replace("{source}", path or "source.txt")
                if "{dest}" in command:
                    command = command.replace("{dest}", target or "destination.txt")
                if "{hashfile}" in command:
                    command = command.replace("{hashfile}", filename or "hashes.txt")
                
                return command, {
                    "target": target,
                    "url": url,
                    "user": user,
                    "path": path,
                    "filename": filename,
                    "matched_pattern": pattern
                }
        
        # If no pattern matches, treat as direct command
        return user_input, {"direct_command": True}
    
    def _extract_target(self, text: str) -> Optional[str]:
        """Extract IP address or hostname"""
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_match = re.search(ip_pattern, text)
        if ip_match:
            self.last_target = ip_match.group(0)
            return ip_match.group(0)
        
        hostname_pattern = r'(?:host|target|server|ip|address)?[\s:]+([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,}))'
        hostname_match = re.search(hostname_pattern, text)
        if hostname_match:
            self.last_target = hostname_match.group(1)
            return hostname_match.group(1)
        
        return self.last_target
    
    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL"""
        url_pattern = r'https?://[^\s]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None
    
    def _extract_user(self, text: str) -> Optional[str]:
        """Extract username"""
        user_pattern = r'(?:user|username)?[\s:]+([a-zA-Z0-9_]+)'
        match = re.search(user_pattern, text)
        if match:
            self.last_user = match.group(1)
            return match.group(1)
        return self.last_user
    
    def _extract_path(self, text: str) -> Optional[str]:
        """Extract file path"""
        path_pattern = r'(?:path|file|directory)?[\s:]+(/[^\s]*|~[^\s]*)'
        match = re.search(path_pattern, text)
        return match.group(1) if match else None
    
    def _extract_filename(self, text: str) -> Optional[str]:
        """Extract filename or file reference"""
        filename_pattern = r'(?:file|name)?[\s:]+([a-zA-Z0-9._-]+)'
        match = re.search(filename_pattern, text)
        return match.group(1) if match else None


class KaliLinuxController:
    """Main controller for Kali Linux command execution"""
    
    def __init__(self):
        self.parser = NaturalLanguageParser()
        self.executor = AdvancedCommandExecutor()
        self.orchestrator = CommandOrchestrator()
        self.command_history = []
        self.safe_mode = True  # Prevent dangerous commands
        self.dangerous_commands = [
            "rm -rf /",
            "dd if=/dev/zero",
            ":(){ :|:& };:",  # Fork bomb
            "mkfs",
            "format C:",
        ]
    
    def execute_command(self, user_input: str) -> Dict:
        """Execute command from natural language or direct command"""
        try:
            # Parse the input
            command, params = self.parser.parse(user_input)
            
            # Check safety
            if self.safe_mode and self._is_dangerous(command):
                return {
                    "success": False,
                    "error": "Command blocked by safety mode",
                    "command": command,
                    "reason": "This command is potentially dangerous"
                }
            
            # Log command
            self.command_history.append({
                "input": user_input,
                "command": command,
                "timestamp": datetime.now().isoformat(),
                "params": params
            })
            
            # Execute command
            result = self._execute_local(command)
            
            return {
                "success": True,
                "command": command,
                "user_input": user_input,
                "output": result["output"],
                "error": result["error"],
                "return_code": result["return_code"],
                "params": params,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "input": user_input,
                "timestamp": datetime.now().isoformat()
            }
    
    def execute_remote(self, host: str, command: str, username: str = "root", 
                      password: str = None, key_file: str = None) -> Dict:
        """Execute command on remote Kali Linux system"""
        try:
            with RemoteCommandExecutor(host, username=username, password=password, 
                                      key_file=key_file) as executor:
                result = executor.execute_command(command)
                return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "host": host
            }
    
    def execute_workflow(self, workflow_name: str, commands: List[Dict]) -> Dict:
        """Execute a workflow of commands"""
        self.orchestrator.create_workflow(workflow_name, commands)
        return self.orchestrator.execute_workflow(workflow_name)
    
    def _execute_local(self, command: str) -> Dict:
        """Execute command locally"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": "Command timeout (30 seconds)",
                "return_code": -1
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "return_code": -1
            }
    
    def _is_dangerous(self, command: str) -> bool:
        """Check if command is potentially dangerous"""
        for dangerous_cmd in self.dangerous_commands:
            if dangerous_cmd in command:
                return True
        return False
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get command history"""
        return self.command_history[-limit:]
    
    def set_safe_mode(self, enabled: bool):
        """Enable or disable safe mode"""
        self.safe_mode = enabled
    
    def interactive_mode(self):
        """Start interactive mode"""
        print("\n" + "="*60)
        print("AI CLAYENT - Kali Linux AI Controller")
        print("="*60)
        print("Type commands in natural language or direct Kali Linux commands")
        print("Examples:")
        print("  - 'scan 192.168.1.1'")
        print("  - 'find open ports on example.com'")
        print("  - 'list network interfaces'")
        print("  - 'nmap -sV 192.168.1.100'")
        print("Type 'help' for more options, 'exit' to quit")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("AI-CLAYENT> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    print("Exiting AI CLAYENT...")
                    break
                
                if user_input.lower() == "help":
                    self._show_help()
                    continue
                
                if user_input.lower() == "history":
                    self._show_history()
                    continue
                
                if user_input.lower() == "safe":
                    self.safe_mode = not self.safe_mode
                    print(f"Safe mode: {'ENABLED' if self.safe_mode else 'DISABLED'}")
                    continue
                
                # Execute command
                result = self.execute_command(user_input)
                
                print("\n" + "-"*60)
                if result["success"]:
                    print(f"Command: {result['command']}")
                    if result["output"]:
                        print(f"Output:\n{result['output']}")
                    if result["error"]:
                        print(f"Error:\n{result['error']}")
                else:
                    print(f"ERROR: {result['error']}")
                print("-"*60 + "\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                print(f"Error: {e}\n")
    
    def _show_help(self):
        """Show help menu"""
        print("\n" + "="*60)
        print("HELP - Available Commands")
        print("="*60)
        print("\nNatural Language Examples:")
        print("  - 'scan 192.168.1.1' → nmap -sV 192.168.1.1")
        print("  - 'find open ports on target' → nmap -p- target")
        print("  - 'check dns example.com' → nslookup example.com")
        print("  - 'list network interfaces' → ip addr show")
        print("  - 'list running processes' → ps aux")
        print("  - 'check disk space' → df -h")
        print("\nDirect Commands:")
        print("  - Any standard Kali Linux command")
        print("\nSpecial Commands:")
        print("  - 'history' → Show command history")
        print("  - 'safe' → Toggle safe mode")
        print("  - 'exit' → Exit program")
        print("="*60 + "\n")
    
    def _show_history(self):
        """Show command history"""
        print("\n" + "="*60)
        print("COMMAND HISTORY")
        print("="*60)
        for i, cmd in enumerate(self.get_history(20), 1):
            print(f"{i}. {cmd['input']}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    controller = KaliLinuxController()
    controller.interactive_mode()


if __name__ == "__main__":
    main()
