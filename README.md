# CIA Roblox Executor v1.0

A secure, AI-powered Roblox script executor for internal testing and development purposes. This project integrates advanced AI capabilities with a robust execution engine to provide a comprehensive development environment for Roblox Lua scripts.

## 🚨 **IMPORTANT DISCLAIMER**

This software is designed for **INTERNAL USE ONLY** within controlled environments. It is intended for:
- Educational purposes
- Internal testing and development
- Security research in controlled environments
- Professional development workflows

**DO NOT** use this software for:
- Unauthorized access to systems
- Malicious activities
- Distribution of exploits
- Any illegal activities

## 🎯 Features

### 🤖 AI-Powered Script Generation
- **Multiple AI Models**: Support for Mistral, DeepSeek, and StarCoder2
- **Intelligent Prompt Routing**: Automatically selects the best AI model for your request
- **Context-Aware Generation**: Different prompt templates for various use cases
- **Real-time Generation**: Instant script creation from natural language descriptions

### 🔒 Security & Safety
- **Sandboxed Execution**: Isolated Lua environment for safe script execution
- **Anti-Cheat Bypass**: Advanced bypass techniques for internal testing
- **Script Validation**: Comprehensive security checks before execution
- **Resource Monitoring**: Memory and CPU usage tracking
- **Audit Logging**: Complete audit trail of all operations

### 🖥️ Modern GUI Interface
- **Dark Theme**: Professional dark interface with neon highlights
- **Real-time Logging**: Live execution logs and AI interaction history
- **Script Management**: Load, save, and organize your scripts
- **Progress Tracking**: Visual progress indicators for long operations
- **Tabbed Interface**: Organized workspace with multiple panels

### ⚡ Advanced Execution Engine
- **Lua Sandbox**: Secure Lua runtime with restricted access
- **Timeout Protection**: Prevents infinite loops and resource exhaustion
- **Error Handling**: Comprehensive error reporting and recovery
- **Performance Monitoring**: Execution time and resource usage tracking

### 📊 Comprehensive Logging
- **Execution Logs**: Detailed logs of all script executions
- **AI Interaction Logs**: Complete history of AI-generated scripts
- **Security Events**: Audit trail of security-related activities
- **Performance Metrics**: Resource usage and timing information

## 🏗️ Architecture

```
cia-roblox-executor/
├── gui.py                     # Main desktop GUI entry point
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── executor/                  # Core execution engine
│   ├── __init__.py
│   ├── core.py                # Main execution loop and VM management
│   ├── sandbox.py             # Isolated execution environment
│   ├── anti_cheat_bypass.py   # Anti-cheat bypass logic
│   └── logger.py              # Comprehensive logging system
├── ai_module/                 # AI script generation
│   ├── __init__.py
│   ├── ai_interface.py        # AI model communication
│   ├── script_builder.py      # Script formatting and building
│   └── validation.py          # Script safety validation
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── file_manager.py        # File I/O operations
│   └── helpers.py             # Miscellaneous utilities
├── logs/                      # Execution and audit logs
├── sandboxed_scripts/         # Generated and saved scripts
├── backups/                   # Script backups
└── temp/                      # Temporary files
```

## 🚀 Installation

### Prerequisites

- **Windows 10/11, Linux, or macOS**
- **Git**
- **Internet connection** (for downloading dependencies)

### Automated Installation (Recommended)

#### Windows Users

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd cia-roblox-executor
   ```

2. **Run the Installer**
   ```bash
   # Double-click the installer or run from command prompt
   "Exec dependencies installer.bat"
   ```

   The installer will automatically:
   - Install Python 3.11+ (if not present)
   - Install all Python dependencies
   - Download and install Ollama
   - Download AI models (Mistral, DeepSeek, StarCoder2)
   - Create project structure
   - Configure the environment

#### Linux/macOS Users

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd cia-roblox-executor
   ```

2. **Run the Installer**
   ```bash
   # Make script executable (first time only)
   chmod +x install_dependencies.sh
   
   # Run the installer
   ./install_dependencies.sh
   ```

   The installer will automatically:
   - Install system dependencies
   - Set up Python virtual environment
   - Install all Python packages
   - Download and install Ollama
   - Download AI models
   - Create project structure
   - Generate activation script

3. **Activate Environment** (Linux/macOS only)
   ```bash
   source activate.sh
   ```

### Manual Installation (Advanced Users)

If you prefer manual installation:

#### Prerequisites

- **Python 3.11+**
- **Ollama** (for AI models)
- **Git**

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd cia-roblox-executor
```

#### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Set Up AI Models

Install and configure Ollama with the required models:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required AI models
ollama pull mistral:7b-instruct-q4_0
ollama pull deepseek-coder:6.7b-instruct-q4_0
ollama pull starcoder2:7b-q4_0

# Start Ollama service
ollama serve
```

#### Step 4: Configuration

The application will create a default configuration file (`config.yaml`) on first run. You can customize settings for:

- AI model preferences
- Security settings
- GUI appearance
- File paths
- Execution limits

## 🎮 Usage

### GUI Mode (Recommended)

Launch the graphical interface:

```bash
python gui.py
```

**Features:**
- 🤖 AI script generation with natural language prompts
- 📝 Script editor with syntax highlighting
- 🚀 One-click script execution
- 📊 Real-time execution logs
- 💾 Script management and organization

### CLI Mode (Power Users)

Use the command-line interface for automation and scripting:

```bash
# Generate a script using AI
python main.py --generate --prompt "Create a script that teleports players"

# Execute a script
python main.py --execute --script my_script.lua

# Validate a script for safety
python main.py --validate --script my_script.lua --detailed

# Show execution logs
python main.py --log --log-type execution --limit 20

# List available scripts
python main.py --list

# Show system information
python main.py --info
```

### AI Script Generation

The AI system supports various prompt types:

- **Basic**: General Roblox scripts
- **Advanced**: Complex, production-ready scripts
- **Security**: Security-focused scripts with extra validation
- **Game-Specific**: Scripts tailored for specific game scenarios

**Example Prompts:**
```
"Create a script that makes players fly when they press F"
"Generate a teleportation system with GUI"
"Build a weapon system with damage calculation"
"Create an anti-cheat detection script"
```

## 🔧 Configuration

### AI Models

Configure AI models in `config.yaml`:

```yaml
ai:
  default_model: "mistral"
  models:
    mistral:
      name: "mistral:7b-instruct-q4_0"
      api_url: "http://localhost:11434/api/generate"
      max_tokens: 2048
      temperature: 0.7
```

### Security Settings

```yaml
security:
  enable_validation: true
  enable_sanitization: true
  max_script_length: 50000
  bypass_level: "medium"  # low, medium, high
```

### Execution Limits

```yaml
executor:
  max_execution_time: 30
  max_memory_usage_mb: 100
  enable_sandbox: true
  enable_bypass: true
```

## 📊 Monitoring & Logging

### Log Types

- **Execution Logs**: Script execution details and results
- **AI Logs**: AI interaction history and generated scripts
- **Error Logs**: Error tracking and debugging information
- **Audit Logs**: Security events and compliance tracking

### Log Management

```bash
# Export logs
python main.py --log --log-type execution --limit 1000 > execution_logs.json

# View real-time logs
tail -f logs/execution.log
```

## 🛡️ Security Features

### Sandbox Environment
- Isolated Lua runtime
- Restricted API access
- Resource usage limits
- Timeout protection

### Script Validation
- Dangerous pattern detection
- Infinite loop prevention
- Malicious code identification
- Syntax validation

### Anti-Cheat Bypass
- VM detection obfuscation
- Function wrapping
- String encryption
- Control flow obfuscation

## 🔍 Troubleshooting

### Common Issues

**AI Models Not Responding:**
```bash
# Check Ollama service
ollama list
ollama serve

# Test model connection
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "mistral:7b-instruct-q4_0", "prompt": "Hello"}'
```

**Script Execution Fails:**
- Check script validation results
- Review execution logs
- Verify sandbox configuration
- Check resource limits

**GUI Not Starting:**
- Verify PyQt6 installation
- Check Python version (3.11+)
- Review system dependencies

### Debug Mode

Enable debug logging:

```python
# In config.yaml
executor:
  log_level: "DEBUG"
```

## 📈 Performance

### Optimization Tips

1. **AI Model Selection**: Use appropriate models for different tasks
2. **Script Validation**: Enable validation only when needed
3. **Log Management**: Regular log rotation and cleanup
4. **Resource Limits**: Adjust based on system capabilities

### Benchmarks

- **Script Generation**: 2-10 seconds (depending on model)
- **Script Execution**: <1 second (simple scripts)
- **Validation**: <100ms per script
- **Memory Usage**: 50-200MB (depending on configuration)

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Run tests
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add comprehensive docstrings
- Include unit tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚖️ Legal Notice

This software is provided "as is" without warranty. Users are responsible for ensuring compliance with applicable laws and regulations. The authors are not liable for any misuse of this software.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs for error details
3. Search existing issues
4. Create a new issue with detailed information

---

**Remember**: This tool is for educational and internal testing purposes only. Always use responsibly and ethically.
