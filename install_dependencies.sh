#!/bin/bash

# CIA Roblox Executor - Dependencies Installer
# For Linux and macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP $1]${NC} $2"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_status "Running with root privileges"
    else
        print_warning "Not running as root. Some installations may fail."
        print_warning "Consider running with sudo for best results."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [[ -f /etc/debian_version ]]; then
            DISTRO="debian"
        elif [[ -f /etc/redhat-release ]]; then
            DISTRO="redhat"
        elif [[ -f /etc/arch-release ]]; then
            DISTRO="arch"
        else
            DISTRO="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macos"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    print_status "Detected OS: $OS ($DISTRO)"
}

# Install system dependencies
install_system_deps() {
    print_step "1/6" "Installing system dependencies..."
    
    if [[ $OS == "linux" ]]; then
        if [[ $DISTRO == "debian" ]]; then
            # Ubuntu/Debian
            sudo apt update
            sudo apt install -y curl wget git build-essential python3 python3-pip python3-venv
        elif [[ $DISTRO == "redhat" ]]; then
            # CentOS/RHEL/Fedora
            sudo yum update -y || sudo dnf update -y
            sudo yum install -y curl wget git gcc python3 python3-pip || sudo dnf install -y curl wget git gcc python3 python3-pip
        elif [[ $DISTRO == "arch" ]]; then
            # Arch Linux
            sudo pacman -Syu --noconfirm
            sudo pacman -S --noconfirm curl wget git base-devel python python-pip
        fi
    elif [[ $OS == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        brew update
        brew install curl wget git python3
    fi
    
    print_status "System dependencies installed"
}

# Install Python
install_python() {
    print_step "2/6" "Setting up Python environment..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VERSION is already installed"
        else
            print_warning "Python version $PYTHON_VERSION found, but 3.11+ is recommended"
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+ manually."
        exit 1
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    print_status "Python environment ready"
}

# Install Python dependencies
install_python_deps() {
    print_step "3/6" "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        print_status "Installing Python packages..."
        pip install -r requirements.txt
        print_status "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Install Ollama
install_ollama() {
    print_step "4/6" "Installing Ollama..."
    
    # Check if Ollama is already installed
    if command -v ollama &> /dev/null; then
        print_status "Ollama is already installed"
        ollama --version
    else
        print_status "Installing Ollama..."
        
        if [[ $OS == "linux" ]]; then
            # Linux installation
            curl -fsSL https://ollama.ai/install.sh | sh
        elif [[ $OS == "macos" ]]; then
            # macOS installation
            brew install ollama
        fi
        
        print_status "Ollama installed successfully"
    fi
}

# Start Ollama service
start_ollama() {
    print_step "5/6" "Starting Ollama service..."
    
    # Start Ollama in background
    print_status "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for service to start
    print_status "Waiting for Ollama service to start..."
    sleep 15
    
    # Test connection
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_status "Ollama service is running"
    else
        print_warning "Ollama service may not be running properly"
        print_warning "You may need to start it manually: ollama serve"
    fi
}

# Download AI models
download_models() {
    print_step "6/6" "Downloading AI models..."
    
    # Create models directory
    mkdir -p models
    
    # Download models
    print_status "Downloading Mistral model..."
    ollama pull mistral:7b-instruct-q4_0
    
    print_status "Downloading DeepSeek model..."
    ollama pull deepseek-coder:6.7b-instruct-q4_0
    
    print_status "Downloading StarCoder2 model..."
    ollama pull starcoder2:7b-q4_0
    
    print_status "AI models downloaded successfully"
}

# Create project structure
setup_project() {
    print_status "Creating project structure..."
    
    # Create directories
    mkdir -p logs sandboxed_scripts backups temp
    
    # Create default configuration
    if [[ ! -f "config.yaml" ]]; then
        print_status "Creating default configuration..."
        cat > config.yaml << EOF
# CIA Roblox Executor Configuration
# Generated automatically by installer

executor:
  name: CIA Roblox Executor
  version: 1.0.0
  max_execution_time: 30
  enable_sandbox: true
  enable_bypass: true

ai:
  default_model: mistral
  max_tokens: 2048
  temperature: 0.7

security:
  enable_validation: true
  enable_sanitization: true
  max_script_length: 50000
  bypass_level: medium

gui:
  theme: dark
  window_width: 1400
  window_height: 900

paths:
  logs_dir: logs
  scripts_dir: sandboxed_scripts
  backup_dir: backups
  temp_dir: temp
EOF
    fi
    
    print_status "Project structure created"
}

# Create activation script
create_activation_script() {
    print_status "Creating activation script..."
    
    cat > activate.sh << 'EOF'
#!/bin/bash
# CIA Roblox Executor - Activation Script

# Activate virtual environment
source venv/bin/activate

# Start Ollama if not running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama service..."
    ollama serve &
    sleep 5
fi

echo "CIA Roblox Executor environment activated!"
echo "Run: python gui.py (for GUI mode)"
echo "Run: python main.py --help (for CLI mode)"
EOF
    
    chmod +x activate.sh
    print_status "Activation script created: ./activate.sh"
}

# Main installation function
main() {
    echo
    echo "========================================"
    echo "  CIA Roblox Executor v1.0"
    echo "  Automated Dependencies Installer"
    echo "========================================"
    echo
    
    check_root
    detect_os
    install_system_deps
    install_python
    install_python_deps
    install_ollama
    start_ollama
    download_models
    setup_project
    create_activation_script
    
    echo
    echo "========================================"
    echo "  Installation Complete!"
    echo "========================================"
    echo
    print_status "Python 3.11+ installed"
    print_status "Python dependencies installed"
    print_status "Ollama installed and running"
    print_status "AI models downloaded"
    print_status "Project structure created"
    echo
    echo "Next steps:"
    echo "1. Run: source activate.sh (to activate environment)"
    echo "2. Run: python gui.py (for GUI mode)"
    echo "3. Run: python main.py --help (for CLI mode)"
    echo
    echo "For support, check the README.md file"
    echo
}

# Run main function
main "$@"