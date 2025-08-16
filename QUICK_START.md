# 🚀 Quick Start Guide

Get the CIA Roblox Executor running in minutes!

## 📋 Prerequisites

- **Windows 10/11, Linux, or macOS**
- **Git** (download from https://git-scm.com/)
- **Internet connection** (for downloading dependencies)

## ⚡ Quick Installation

### Windows Users

1. **Clone the repository**
   ```cmd
   git clone <repository-url>
   cd cia-roblox-executor
   ```

2. **Run the installer**
   ```cmd
   "Exec dependencies installer.bat"
   ```
   
   *Just double-click the installer file!*

3. **Start the application**
   ```cmd
   python gui.py
   ```

### Linux/macOS Users

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cia-roblox-executor
   ```

2. **Run the installer**
   ```bash
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

3. **Activate environment and start**
   ```bash
   source activate.sh
   python gui.py
   ```

## 🎮 First Steps

1. **Launch the GUI**
   - The application will open with a dark theme
   - You'll see the main interface with script editor and AI panel

2. **Generate your first script**
   - Type a prompt like: *"Create a script that prints hello world"*
   - Click "🚀 Generate Script"
   - The AI will create a Lua script for you

3. **Execute the script**
   - Click "▶ Execute Script" to run it in the sandbox
   - Watch the execution logs in real-time

## 🤖 AI Script Generation

### Example Prompts

- *"Create a script that makes players fly when they press F"*
- *"Generate a teleportation system with GUI"*
- *"Build a weapon system with damage calculation"*
- *"Create an anti-cheat detection script for educational purposes"*

### AI Models Available

- **Mistral**: Best for general scripts
- **DeepSeek**: Best for complex programming
- **StarCoder2**: Best for multi-file projects

## 🔧 CLI Mode (Power Users)

```bash
# Generate a script
python main.py --generate --prompt "Create a teleportation script"

# Execute a script
python main.py --execute --script my_script.lua

# Validate a script
python main.py --validate --script my_script.lua --detailed

# Show logs
python main.py --log --log-type execution --limit 20
```

## 📁 Project Structure

```
cia-roblox-executor/
├── gui.py                     # Main GUI application
├── main.py                    # CLI interface
├── Exec dependencies installer.bat  # Windows installer
├── install_dependencies.sh    # Linux/macOS installer
├── requirements.txt           # Python dependencies
├── config.yaml               # Configuration file
├── logs/                     # Execution logs
├── sandboxed_scripts/        # Generated scripts
├── backups/                  # Script backups
└── temp/                     # Temporary files
```

## ⚙️ Configuration

The installer creates a default `config.yaml` file. You can customize:

- **AI Models**: Change default model and settings
- **Security**: Adjust validation and bypass levels
- **GUI**: Modify theme and window settings
- **Execution**: Set timeouts and resource limits

## 🔒 Security Features

- **Sandboxed Execution**: Scripts run in isolated environment
- **Script Validation**: Automatic security checks
- **Resource Monitoring**: Memory and CPU limits
- **Audit Logging**: Complete activity tracking

## 🆘 Troubleshooting

### Common Issues

**Installer fails:**
- Run as administrator (Windows)
- Use sudo (Linux/macOS)
- Check internet connection

**AI models not responding:**
- Ensure Ollama is running: `ollama serve`
- Check model installation: `ollama list`

**GUI won't start:**
- Verify Python installation: `python --version`
- Check PyQt6: `pip install PyQt6`

### Getting Help

1. Check the logs in the `logs/` directory
2. Review the full README.md
3. Use the CLI for debugging: `python main.py --info`

## 🎯 Next Steps

1. **Explore the GUI**: Try different AI prompts
2. **Learn Lua**: Study generated scripts
3. **Customize**: Modify configuration settings
4. **Experiment**: Test different script types
5. **Document**: Keep notes of your findings

## 📚 Educational Use

This tool is perfect for:
- Learning Lua programming
- Understanding game security
- Practicing cybersecurity
- Teaching intelligence operations
- Research and development

---

**Remember**: This tool is for educational and internal testing purposes only. Use responsibly and ethically!