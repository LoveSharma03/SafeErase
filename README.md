# SafeErase

A comprehensive, cross-platform secure data wiping solution designed for trustworthy IT asset recyclers. SafeErase provides military-grade data destruction with tamper-proof certification for smartphones, laptops, and other storage devices.

## 🔒 Key Features

- **Comprehensive Data Destruction**: Securely erases data from all storage areas including HPA/DCO and SSD sectors
- **Tamper-Proof Certificates**: Generates cryptographically signed wipe certificates in PDF and JSON formats
- **One-Click Operation**: Simple interface suitable for non-technical users
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Offline Capability**: Bootable USB/ISO for air-gapped environments
- **Industry Compliance**: Meets NIST 800-88, DoD 5220.22-M, and other standards

## 🏗️ Architecture

SafeErase is built with a modular architecture:

- **Core Engine** (C++/Rust): Low-level disk operations and wiping algorithms
- **UI Layer** (Flutter/.NET): Cross-platform user interface
- **Certificate System**: OpenSSL-based cryptographic certificate generation
- **Bootable Environment**: Minimal Linux distribution for offline use

## 🚀 Quick Start

### Prerequisites
- Administrative/root privileges required for disk access
- Supported platforms: Windows 10+, macOS 10.15+, Ubuntu 20.04+

### Installation
```bash
# Download the latest release
# Or build from source (see Building section)
```

### Usage
1. Launch SafeErase with administrator privileges
2. Select target device(s)
3. Choose wipe standard (automatic selection available)
4. Click "Start Secure Wipe"
5. Receive tamper-proof certificate upon completion

## 🔧 Building from Source

### Core Engine (Rust)
```bash
cd core-engine
cargo build --release
```

### UI (Flutter)
```bash
cd ui-flutter
flutter build
```

### Bootable ISO
```bash
cd bootable-iso
./build-iso.sh
```

## 📋 Supported Wipe Standards

- **NIST 800-88**: Single pass with cryptographic erase for SSDs
- **DoD 5220.22-M**: Three-pass overwrite pattern
- **Gutmann**: 35-pass algorithm for maximum security
- **Random**: Cryptographically secure random data
- **Zero Fill**: Single pass with zeros
- **Custom**: User-defined patterns

## 🛡️ Security Features

- **ATA Secure Erase**: Hardware-level SSD wiping
- **HPA/DCO Detection**: Identifies and clears hidden areas
- **Cryptographic Verification**: SHA-256 verification of wipe completion
- **Digital Signatures**: JSON Web Signatures for certificate authenticity
- **Audit Trail**: Comprehensive logging of all operations

## 📁 Project Structure

```
SafeErase/
├── core-engine/          # Rust-based wiping engine
├── ui-flutter/           # Flutter cross-platform UI
├── ui-dotnet/           # .NET alternative UI
├── certificate-gen/     # Certificate generation system
├── bootable-iso/        # Linux ISO creation tools
├── tests/              # Test suites and validation
├── docs/               # Documentation
└── scripts/            # Build and deployment scripts
```

## 🧪 Testing

SafeErase includes comprehensive testing:
- Unit tests for all core components
- Integration tests with virtual disks
- Compliance validation against industry standards
- Performance benchmarks

## 📖 Documentation

- [User Manual](docs/user-manual.md)
- [Technical Specifications](docs/technical-specs.md)
- [API Documentation](docs/api.md)
- [Compliance Guide](docs/compliance.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

SafeErase is designed for legitimate data destruction purposes. Users are responsible for ensuring compliance with local laws and regulations. The authors are not liable for any misuse of this software.
