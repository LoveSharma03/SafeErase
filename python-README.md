# SafeErase Python Components

This document describes the comprehensive Python implementation of SafeErase, including the GUI application, API library, and command-line tools.

## 🐍 Python Components Overview

SafeErase includes a complete Python ecosystem that provides:

- **Professional GUI Application** - CustomTkinter-based cross-platform interface
- **High-Level API Library** - Easy-to-use Python API for SafeErase functionality
- **Command-Line Tools** - Powerful CLI utilities for automation and batch operations
- **Interactive Demos** - Comprehensive demonstrations of all features

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install from Source
```bash
# Clone the repository
git clone https://github.com/safeerase/SafeErase.git
cd SafeErase

# Install Python dependencies
pip install -r python-ui/requirements.txt

# Install the package in development mode
pip install -e .
```

### Install from PyPI (Future)
```bash
pip install safeerase
```

## 🖥️ Python GUI Application

### Features
- **Modern Interface** - Built with CustomTkinter for a professional look
- **Device Discovery** - Automatic detection and analysis of storage devices
- **Real-Time Monitoring** - Live progress updates during wipe operations
- **Certificate Management** - Generate and verify tamper-proof certificates
- **Cross-Platform** - Works on Windows, macOS, and Linux

### Running the GUI
```bash
# From source
python python-ui/main.py

# After installation
safeerase-ui
```

### GUI Components
- `MainWindow` - Primary application window with navigation
- `DevicePanel` - Device discovery and selection interface
- `OperationPanel` - Wipe operation monitoring and control
- `CertificatePanel` - Certificate generation and verification
- `SettingsPanel` - Application configuration

## 🔧 Python API Library

### Quick Start
```python
import asyncio
from python_api.safeerase_api import SafeEraseAPI, WipeAlgorithm

async def main():
    api = SafeEraseAPI()
    await api.initialize()
    
    # Discover devices
    devices = await api.discover_devices()
    print(f"Found {len(devices)} devices")
    
    # Start wipe operation
    if devices:
        operation_id = await api.start_wipe(
            devices[0].id,
            WipeAlgorithm.NIST_800_88
        )
        print(f"Started operation: {operation_id}")
    
    api.cleanup()

asyncio.run(main())
```

### API Features
- **Async/Await Support** - Modern asynchronous programming
- **Type Hints** - Full type annotations for better IDE support
- **Comprehensive Models** - Rich data models for devices, operations, and certificates
- **Progress Callbacks** - Real-time progress monitoring
- **Error Handling** - Robust error handling and recovery

### Core Classes
- `SafeEraseAPI` - Main API interface
- `DeviceInfo` - Storage device information
- `WipeOptions` - Wipe operation configuration
- `WipeProgress` - Real-time progress information
- `WipeResult` - Operation results and statistics
- `CertificateInfo` - Certificate data and metadata

## ⚡ Command-Line Tools

### Device Scanner
Discover and analyze storage devices:

```bash
# Basic device scan
safeerase-scan

# Include system disks and detailed analysis
safeerase-scan --include-system --verbose

# JSON output for automation
safeerase-scan --json > devices.json

# Analyze specific device
safeerase-scan --analyze dev_001
```

### Certificate Validator
Validate SafeErase certificates:

```bash
# Validate single certificate
safeerase-validate certificate.json

# Validate multiple certificates
safeerase-validate cert1.json cert2.json cert3.json

# JSON output
safeerase-validate --json certificate.json

# Use trusted keys directory
safeerase-validate --trusted-keys ./keys certificate.json
```

### Wipe Scheduler
Schedule and manage batch operations:

```bash
# Create job from configuration
safeerase-schedule create job_config.yaml

# Start job
safeerase-schedule start job_12345678

# Check job status
safeerase-schedule status job_12345678

# List all jobs
safeerase-schedule list

# Cancel running job
safeerase-schedule cancel job_12345678
```

## 📋 Configuration Files

### Job Configuration (YAML)
```yaml
name: "Batch Wipe Operation"
description: "Wipe multiple USB devices"
algorithm: "nist_800_88"
devices:
  - "dev_002"
  - "dev_003"
options:
  verify_wipe: true
  clear_hpa: true
  clear_dco: true
  verification_samples: 1000
```

### Scheduler Configuration
```yaml
default_algorithm: "nist_800_88"
max_concurrent_operations: 2
auto_generate_certificates: true
certificate_output_dir: "./certificates"
log_level: "INFO"
```

## 🎯 Examples and Demos

### Interactive Python Demo
```bash
python python-examples/run_python_demo.py
```

Features:
- Device discovery demonstration
- Algorithm information display
- Wipe operation simulation
- Certificate generation
- UI component showcase
- Command-line tools overview

### Basic Usage Examples
```bash
python python-examples/basic_usage.py
```

Includes:
- Device discovery
- Wipe operations
- Certificate handling
- Batch operations
- Error handling

## 🏗️ Architecture

### Component Structure
```
python-ui/              # GUI Application
├── main.py            # Application entry point
├── core/              # Core application logic
├── ui/                # UI components
└── utils/             # Utility modules

python-api/            # API Library
├── safeerase_api.py   # Main API interface
└── models/            # Data models

python-tools/          # Command-Line Tools
├── device_scanner.py  # Device discovery tool
├── certificate_validator.py  # Certificate validation
└── wipe_scheduler.py  # Batch operation scheduler

python-examples/       # Examples and Demos
├── basic_usage.py     # API usage examples
└── run_python_demo.py # Interactive demo
```

### Dependencies
- **CustomTkinter** - Modern GUI framework
- **asyncio** - Asynchronous programming
- **cryptography** - Certificate validation
- **psutil** - System information
- **pyyaml** - Configuration files
- **rich** - Enhanced terminal output

## 🔒 Security Features

### Certificate Validation
- **Digital Signatures** - RSA/ECDSA signature verification
- **Tamper Detection** - Cryptographic integrity checking
- **Chain of Trust** - Trusted key management
- **Compliance Validation** - Standards compliance verification

### Secure Operations
- **Memory Safety** - Secure memory handling
- **Privilege Checking** - Administrator privilege validation
- **Input Validation** - Comprehensive input sanitization
- **Error Handling** - Secure error reporting

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=python_ui --cov=python_api --cov=python_tools

# Run specific test categories
pytest tests/test_api.py
pytest tests/test_ui.py
pytest tests/test_tools.py
```

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Cross-component testing
- **UI Tests** - GUI component testing
- **API Tests** - API functionality testing
- **Tool Tests** - Command-line tool testing

## 📚 Documentation

### API Documentation
- **Type Hints** - Full type annotations
- **Docstrings** - Comprehensive function documentation
- **Examples** - Usage examples for all features
- **Error Codes** - Detailed error documentation

### User Documentation
- **User Manual** - Complete user guide
- **Technical Specs** - Detailed technical specifications
- **Installation Guide** - Step-by-step installation
- **Troubleshooting** - Common issues and solutions

## 🚀 Getting Started

1. **Install Python 3.8+** from python.org
2. **Clone the repository** or download the source
3. **Install dependencies** with `pip install -r python-ui/requirements.txt`
4. **Run the demo** with `python python-examples/run_python_demo.py`
5. **Launch the GUI** with `python python-ui/main.py`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

### Development Setup
```bash
# Clone repository
git clone https://github.com/safeerase/SafeErase.git
cd SafeErase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black python-ui python-api python-tools python-examples

# Lint code
flake8 python-ui python-api python-tools python-examples
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the user manual and technical specifications
- **Issues**: Report bugs on GitHub Issues
- **Email**: contact@safeerase.com
- **Community**: Join our discussions on GitHub

---

**SafeErase Python Components** - Professional secure data wiping with Python power! 🐍🔒
