# AI Clayent - Advanced AI Controller for Kali Linux

A sophisticated AI client that understands natural human language commands and translates them to Kali Linux commands. Full control of Kali Linux system through natural language processing.

## Features

✅ **Natural Language Processing** - Understand human commands and convert to Kali Linux commands  
✅ **Command Execution** - Execute commands locally or remotely  
✅ **Async Execution** - Non-blocking command execution with task tracking  
✅ **Parallel Execution** - Execute multiple commands simultaneously  
✅ **Remote SSH Execution** - Control remote Kali Linux systems  
✅ **Workflow Orchestration** - Create and execute complex command workflows  
✅ **Safety Mode** - Prevent execution of dangerous commands  
✅ **REST API** - HTTP API for integration  
✅ **Interactive Shell** - Real-time command interface  
✅ **Command History** - Track all executed commands  

## Installation

### Prerequisites
- Python 3.8+
- Kali Linux (or compatible Linux distribution)
- pip

### Setup

```bash
# Clone repository
git clone https://github.com/abubkkar55748gcf6-ctrl/Ai-clayent.git
cd Ai-clayent

# Install dependencies
pip install -r requirements.txt

# Make scripts executable
chmod +x main.py api_server.py
```

## Usage

### 1. Interactive Mode

```bash
python3 main.py
```

**Examples:**
```
AI-CLAYENT> scan 192.168.1.1
AI-CLAYENT> find open ports on example.com
AI-CLAYENT> list network interfaces
AI-CLAYENT> check dns records for google.com
AI-CLAYENT> test ssl certificate example.com
AI-CLAYENT> find all .txt files
```

### 2. REST API Server

```bash
python3 api_server.py
```

Server runs on `http://localhost:5000`

**Execute Command:**
```bash
curl -X POST http://localhost:5000/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "scan 192.168.1.1"}'
```

**Parse Command:**
```bash
curl -X POST http://localhost:5000/api/parse \
  -H "Content-Type: application/json" \
  -d '{"input": "find open ports on target.com"}'
```

**Async Execution:**
```bash
# Submit command
curl -X POST http://localhost:5000/api/execute/async \
  -H "Content-Type: application/json" \
  -d '{"command": "nmap -sV 192.168.1.1"}'

# Check result (use task_id from response)
curl http://localhost:5000/api/task/task_1719823456789
```

**Remote Execution:**
```bash
curl -X POST http://localhost:5000/api/execute/remote \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.100",
    "command": "nmap -sV 192.168.1.1",
    "username": "root",
    "password": "password"
  }'
```

### 3. Python API

```python
from main import KaliLinuxController

controller = KaliLinuxController()

# Execute natural language command
result = controller.execute_command("scan 192.168.1.1")
print(result)

# Execute remote command
remote_result = controller.execute_remote(
    host="192.168.1.100",
    command="nmap -sV 192.168.1.1",
    username="root",
    password="password"
)

# Execute workflow
commands = [
    {"cmd": "nmap -sV 192.168.1.1", "wait": True},
    {"cmd": "netstat -tlnp", "wait": False}
]
workflow_result = controller.execute_workflow("scan_workflow", commands)
```

## Natural Language Commands

### Reconnaissance
- "scan 192.168.1.1" → `nmap -sV 192.168.1.1`
- "find open ports on example.com" → `nmap -p- example.com`
- "check dns example.com" → `nslookup example.com`
- "lookup dns google.com" → `dig google.com`
- "whois example.com" → `whois example.com`

### Network Analysis
- "capture network traffic" → `tcpdump -i eth0 -n`
- "list network interfaces" → `ip addr show`
- "show routing table" → `ip route show`
- "scan subnet 192.168.1.0" → `nmap -sn 192.168.1.0`

### Wireless
- "scan wifi networks" → `airmon-ng`
- "list wireless interfaces" → `iwconfig`
- "start monitor mode" → `airmon-ng start wlan0`

### Web Testing
- "test sql injection on http://example.com" → `sqlmap -u 'http://example.com' --batch`
- "scan vulnerability" → `nikto -h example.com`
- "check ssl certificate" → `testssl.sh example.com`

### System Information
- "system info" → `uname -a`
- "show os info" → `cat /etc/os-release`
- "list processes" → `ps aux`
- "check disk space" → `df -h`
- "show memory" → `free -h`

### File Operations
- "list files" → `ls -la`
- "show current directory" → `pwd`
- "find all .txt files" → `find / -name '.txt'`
- "read file.txt" → `cat file.txt`
- "create directory /tmp/test" → `mkdir /tmp/test`

### Direct Commands
Execute any Kali Linux command directly:
```
AI-CLAYENT> nmap -A -T4 192.168.1.0/24
AI-CLAYENT> aircrack-ng capture.cap
AI-CLAYENT> metasploit
```

## API Endpoints

### Health & Status
- `GET /api/health` - Health check
- `GET /api/status` - API status

### Command Execution
- `POST /api/execute` - Execute command (sync)
- `POST /api/execute/async` - Execute command (async)
- `GET /api/task/<task_id>` - Get async task result
- `POST /api/execute/remote` - Execute on remote system
- `POST /api/execute/parallel` - Execute multiple commands

### Command Management
- `POST /api/parse` - Parse natural language to command
- `GET /api/history` - Get command history
- `GET /api/safe-mode` - Get safe mode status
- `POST /api/safe-mode` - Set safe mode

### Workflows
- `POST /api/workflow` - Create and execute workflow

## Configuration

### Safe Mode
Prevents execution of dangerous commands (default: enabled)

```python
controller.set_safe_mode(False)  # Disable
controller.set_safe_mode(True)   # Enable
```

### Command History Limit
```python
controller.get_history(limit=20)
```

## Architecture

### Components

1. **NaturalLanguageParser** - Parses human input and extracts parameters
2. **KaliLinuxController** - Main controller for command execution
3. **AdvancedCommandExecutor** - Handles async and parallel execution
4. **RemoteCommandExecutor** - SSH execution on remote systems
5. **CommandOrchestrator** - Manages complex workflows
6. **API Server** - Flask REST API

### Data Flow
```
User Input
    ↓
Natural Language Parser
    ↓
Command Extraction & Parameter Detection
    ↓
Safety Check
    ↓
Command Execution (Local/Remote/Async)
    ↓
Result Formatting & Return
```

## Examples

### Reconnaissance Workflow
```bash
python3 -c "
from main import KaliLinuxController

controller = KaliLinuxController()

# 1. Scan network
result = controller.execute_command('scan 192.168.1.0')
print('Network scan:', result)

# 2. Find open ports
result = controller.execute_command('find open ports on 192.168.1.100')
print('Port scan:', result)

# 3. Get service info
result = controller.execute_command('check services on 192.168.1.100')
print('Service check:', result)
"
```

### Parallel Execution
```bash
curl -X POST http://localhost:5000/api/parallel \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      "nmap -sV 192.168.1.1",
      "netstat -tlnp",
      "ps aux"
    ]
  }'
```

### Async Workflow
```bash
# Start scan
TASK_ID=$(curl -X POST http://localhost:5000/api/execute/async \
  -H "Content-Type: application/json" \
  -d '{"command": "nmap -sV 192.168.1.0/24"}' \
  | jq -r '.task_id')

# Check progress
sleep 5
curl http://localhost:5000/api/task/$TASK_ID
```

## Security Considerations

⚠️ **Important Security Notes:**
- This tool is designed for authorized security testing only
- Always ensure you have permission before testing any systems
- Use strong authentication for remote connections
- Keep safe mode enabled in untrusted environments
- Review command history for audit trails
- Use SSH keys instead of passwords when possible

## Troubleshooting

### Command not found
- Ensure Kali Linux tools are installed
- Check tool is in PATH

### Remote connection failed
- Verify SSH credentials
- Check network connectivity
- Ensure target allows SSH connections

### Timeout errors
- Increase timeout value
- Check command complexity
- Verify system resources

## Development

### Adding Custom Command Patterns

Edit `main.py` - `NaturalLanguageParser.COMMAND_MAPPINGS`:

```python
COMMAND_MAPPINGS = {
    r"(your|pattern)": "command {target}",
    # ... more patterns
}
```

### Extending Functionality

```python
class CustomController(KaliLinuxController):
    def custom_method(self):
        # Your custom logic
        pass
```

## License

This project is provided for educational and authorized security testing purposes only.

## Author

AI Clayent Development Team

## Support

For issues and questions, please open an issue on GitHub.

---

**Remember:** Always use this tool responsibly and ethically!
