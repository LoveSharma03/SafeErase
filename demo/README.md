# SafeErase Demo

This demo showcases the SafeErase functionality without requiring Rust or Flutter installation.

## Features Demonstrated

- **Device Discovery**: Simulates detection of storage devices
- **Algorithm Selection**: Shows available wiping algorithms
- **Wipe Simulation**: Demonstrates the wiping process with progress
- **Certificate Generation**: Creates tamper-proof certificates
- **Certificate Verification**: Validates certificate integrity

## Running the Demo

### Prerequisites
- Python 3.6 or higher

### Quick Start
```bash
# Navigate to the SafeErase directory
cd SafeErase

# Run the demo
python demo/run_demo.py
```

### Demo Menu Options

1. **Discover Devices** - Shows simulated storage devices
2. **View Available Algorithms** - Lists wiping algorithms and compliance standards
3. **Start Wipe Operation** - Simulates secure data wiping with progress
4. **View System Status** - Shows current system information
5. **Verify Certificate** - Validates generated certificates
6. **Exit Demo** - Closes the demonstration

## Safety Features Demonstrated

- **System Disk Warnings**: Clear warnings for system drives
- **Multiple Confirmations**: Several confirmation steps before wiping
- **Progress Monitoring**: Real-time progress updates
- **Certificate Generation**: Automatic certificate creation
- **Digital Signatures**: Cryptographic verification

## Simulated Devices

The demo includes three simulated devices:
- Samsung SSD 980 PRO 1TB (NVMe, System Disk)
- SanDisk Ultra USB 3.0 32GB (USB, Removable)
- Western Digital Blue 2TB (SATA HDD)

## Wiping Algorithms

- **NIST SP 800-88**: Single pass, recommended for SSDs
- **DoD 5220.22-M**: Three-pass, high security
- **Gutmann Algorithm**: 35-pass, maximum security
- **ATA Secure Erase**: Hardware-level, very fast

## Certificate Features

Generated certificates include:
- Unique certificate ID
- Device information and serial number
- Wipe algorithm and completion details
- Digital signature for tamper detection
- Compliance information
- Organization details

## Note

This is a demonstration only. No actual data wiping occurs. For real device wiping:

1. Install Rust: https://rustup.rs/
2. Install Flutter: https://flutter.dev/docs/get-started/install
3. Run: `./scripts/build.sh`
4. Launch the full SafeErase application
