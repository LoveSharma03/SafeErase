# SafeErase User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Device Selection](#device-selection)
5. [Wipe Configuration](#wipe-configuration)
6. [Monitoring Progress](#monitoring-progress)
7. [Certificate Management](#certificate-management)
8. [Settings](#settings)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

## Introduction

SafeErase is a professional-grade secure data wiping solution designed for IT asset recyclers, data centers, and organizations requiring certified data destruction. It provides military-grade data sanitization with tamper-proof certification, ensuring complete data destruction that meets industry standards.

### Key Features
- **Comprehensive Data Destruction**: Securely erases data from all storage areas including HPA/DCO and SSD sectors
- **Tamper-Proof Certificates**: Generates cryptographically signed wipe certificates in PDF and JSON formats
- **One-Click Operation**: Simple interface suitable for non-technical users
- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Offline Capability**: Bootable USB/ISO for air-gapped environments
- **Industry Compliance**: Meets NIST 800-88, DoD 5220.22-M, and other standards

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Ubuntu 20.04+
- **Privileges**: Administrator/root access required
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 100MB free space for application
- **Network**: Optional for certificate verification

## Installation

### Windows Installation

1. **Download** the SafeErase installer (SafeErase-Setup.msi) from the official website
2. **Right-click** the installer and select "Run as administrator"
3. **Follow** the installation wizard prompts
4. **Launch** SafeErase from the Start menu or desktop shortcut

### macOS Installation

1. **Download** the SafeErase disk image (SafeErase.dmg)
2. **Double-click** the DMG file to mount it
3. **Drag** SafeErase.app to the Applications folder
4. **Right-click** SafeErase in Applications and select "Open" (first launch only)
5. **Enter** your administrator password when prompted

### Linux Installation

#### Ubuntu/Debian
```bash
# Download and install the DEB package
wget https://releases.safeerase.com/safeerase_1.0.0_amd64.deb
sudo dpkg -i safeerase_1.0.0_amd64.deb
sudo apt-get install -f  # Install dependencies if needed
```

#### RHEL/CentOS/Fedora
```bash
# Download and install the RPM package
wget https://releases.safeerase.com/safeerase-1.0.0-1.x86_64.rpm
sudo rpm -i safeerase-1.0.0-1.x86_64.rpm
```

#### AppImage (Universal)
```bash
# Download and run the AppImage
wget https://releases.safeerase.com/SafeErase-1.0.0-x86_64.AppImage
chmod +x SafeErase-1.0.0-x86_64.AppImage
sudo ./SafeErase-1.0.0-x86_64.AppImage
```

## Getting Started

### First Launch

1. **Launch SafeErase** with administrator privileges
2. **Review** the welcome screen and safety warnings
3. **Accept** the license agreement
4. **Configure** initial settings (optional)

### Main Interface

The SafeErase main interface consists of:
- **Menu Bar**: Access to all major functions
- **Device List**: Shows all detected storage devices
- **Status Panel**: Displays system status and recent operations
- **Action Buttons**: Quick access to common operations

### Safety Warnings

⚠️ **IMPORTANT SAFETY INFORMATION**
- SafeErase permanently destroys data - this action cannot be undone
- Always verify you have selected the correct device before starting
- Ensure important data is backed up before wiping
- Do not interrupt the wiping process once started
- Verify certificates after completion

## Device Selection

### Automatic Detection

SafeErase automatically detects all connected storage devices when launched. The device list shows:
- **Device Name**: Manufacturer and model
- **Capacity**: Total storage capacity
- **Interface**: Connection type (SATA, NVMe, USB, etc.)
- **Status**: Current device status
- **System Disk**: Warning if device contains the operating system

### Device Information

Click on any device to view detailed information:
- **Serial Number**: Unique device identifier
- **Firmware Version**: Device firmware information
- **Health Status**: SMART health information
- **Supported Features**: Available wiping methods
- **Partition Information**: Current partition layout

### Device Filtering

Use the filter options to show/hide devices:
- **Show System Disks**: Include drives containing the OS
- **Show Removable Devices**: Include USB drives and external storage
- **Show Network Devices**: Include network-attached storage
- **Minimum Size Filter**: Hide devices below specified size

### Safety Checks

SafeErase includes several safety mechanisms:
- **System Disk Warning**: Clear warnings for system drives
- **Confirmation Dialogs**: Multiple confirmation steps
- **Device Verification**: Verify device identity before wiping
- **Read-Only Check**: Prevent wiping of read-only devices

## Wipe Configuration

### Selecting Wipe Algorithm

Choose the appropriate wiping algorithm based on your requirements:

#### NIST SP 800-88 (Recommended)
- **Security Level**: Standard
- **Passes**: 1
- **Speed**: Fast
- **Use Case**: Most modern SSDs and general use
- **Compliance**: NIST guidelines

#### DoD 5220.22-M
- **Security Level**: High
- **Passes**: 3
- **Speed**: Medium
- **Use Case**: High-security environments
- **Compliance**: US Department of Defense

#### Gutmann Algorithm
- **Security Level**: Maximum
- **Passes**: 35
- **Speed**: Slow
- **Use Case**: Maximum security for legacy drives
- **Compliance**: Academic research standard

#### Hardware Secure Erase
- **Security Level**: High
- **Passes**: 1 (hardware-level)
- **Speed**: Very Fast
- **Use Case**: Modern SSDs with hardware support
- **Compliance**: ATA/NVMe standards

### Advanced Options

#### Verification Settings
- **Enable Verification**: Verify wipe completion (recommended)
- **Verification Samples**: Number of random samples to check
- **Verification Method**: Random sampling or systematic

#### HPA/DCO Settings
- **Detect HPA**: Check for Host Protected Areas
- **Clear HPA**: Remove Host Protected Areas if found
- **Detect DCO**: Check for Device Configuration Overlay
- **Clear DCO**: Remove Device Configuration Overlay if found

#### Performance Settings
- **Block Size**: I/O block size for operations
- **Concurrent Operations**: Number of simultaneous operations
- **Progress Updates**: Frequency of progress reporting

### Certificate Options

#### Certificate Format
- **PDF Certificate**: Human-readable certificate with QR code
- **JSON Certificate**: Machine-readable certificate data
- **Both Formats**: Generate both PDF and JSON certificates

#### Certificate Content
- **Include Technical Details**: Detailed operation information
- **Include Compliance Info**: Standards compliance information
- **Include QR Code**: QR code for quick verification
- **Organization Info**: Your organization details

## Monitoring Progress

### Progress Display

During wiping operations, SafeErase displays:
- **Overall Progress**: Percentage completion
- **Current Pass**: Which pass is currently running
- **Speed**: Current and average transfer rates
- **Time Remaining**: Estimated time to completion
- **Bytes Processed**: Amount of data processed

### Real-Time Updates

The progress display updates in real-time showing:
- **Current Operation**: What the system is currently doing
- **Device Status**: Individual device progress
- **System Resources**: CPU and memory usage
- **Error Messages**: Any issues encountered

### Operation Control

During wiping operations, you can:
- **Pause Operation**: Temporarily pause the wipe (if supported)
- **Cancel Operation**: Stop the wipe process
- **View Logs**: See detailed operation logs
- **Minimize to Tray**: Continue operation in background

### Completion Notification

When wiping completes, SafeErase will:
- **Display Completion Dialog**: Show operation results
- **Generate Certificate**: Create tamper-proof certificate
- **Play Notification Sound**: Audio notification (if enabled)
- **Send Email Report**: Email results (if configured)

## Certificate Management

### Certificate Generation

SafeErase automatically generates certificates upon successful completion:
- **Unique Certificate ID**: UUID for each certificate
- **Digital Signature**: Cryptographically signed for authenticity
- **Timestamp**: Precise completion time
- **Device Information**: Complete device details
- **Wipe Details**: Algorithm and verification results

### Certificate Formats

#### PDF Certificate
- **Human-Readable**: Easy to read and print
- **QR Code**: Quick verification code
- **Logo Support**: Your organization logo
- **Archival Format**: PDF/A for long-term storage

#### JSON Certificate
- **Machine-Readable**: For automated processing
- **Digital Signature**: JWS (JSON Web Signature)
- **Complete Data**: All operation details
- **API Integration**: Easy integration with systems

### Certificate Verification

#### Online Verification
1. **Visit** the verification website
2. **Enter** the certificate ID or scan QR code
3. **View** verification results
4. **Download** original certificate if needed

#### Offline Verification
1. **Use** the built-in verification tool
2. **Load** the certificate file
3. **Verify** digital signature
4. **Check** certificate integrity

### Certificate Storage

#### Recommended Practices
- **Secure Storage**: Store certificates in secure location
- **Multiple Copies**: Keep backup copies
- **Access Control**: Limit access to authorized personnel
- **Retention Policy**: Follow your data retention requirements

#### Export Options
- **Individual Export**: Export single certificates
- **Batch Export**: Export multiple certificates
- **Archive Creation**: Create compressed archives
- **Database Export**: Export to database formats

## Settings

### General Settings

#### Application Preferences
- **Language**: Interface language selection
- **Theme**: Light or dark theme
- **Startup Behavior**: Launch preferences
- **Update Checking**: Automatic update settings

#### Security Settings
- **Certificate Signing**: Configure signing keys
- **Verification URLs**: Set verification endpoints
- **Audit Logging**: Enable detailed logging
- **Access Control**: User permission settings

### Wiping Preferences

#### Default Algorithms
- **Primary Algorithm**: Default wiping method
- **Fallback Algorithm**: Alternative if primary fails
- **Hardware Preference**: Prefer hardware methods
- **Verification Default**: Enable verification by default

#### Performance Tuning
- **I/O Block Size**: Optimize for your hardware
- **Memory Usage**: Limit memory consumption
- **CPU Priority**: Process priority setting
- **Concurrent Limit**: Maximum simultaneous operations

### Organization Settings

#### Company Information
- **Organization Name**: Your company name
- **Contact Information**: Email and phone
- **Address**: Physical address
- **Logo**: Company logo for certificates

#### Compliance Settings
- **Required Standards**: Mandatory compliance standards
- **Certificate Templates**: Custom certificate layouts
- **Approval Workflow**: Certificate approval process
- **Retention Policies**: Data retention requirements

## Troubleshooting

### Common Issues

#### "Access Denied" Errors
**Problem**: Cannot access storage devices
**Solution**: 
1. Ensure SafeErase is running as administrator/root
2. Check device permissions
3. Verify device is not in use by other applications
4. Try disconnecting and reconnecting USB devices

#### "Device Not Found" Errors
**Problem**: Storage device not detected
**Solution**:
1. Check physical connections
2. Verify device appears in system device manager
3. Try different USB port or cable
4. Update device drivers
5. Restart SafeErase

#### Slow Wiping Performance
**Problem**: Wiping operation is very slow
**Solution**:
1. Check for background applications using disk
2. Verify device health status
3. Try different I/O block size
4. Use hardware secure erase if available
5. Check for thermal throttling

#### Certificate Generation Fails
**Problem**: Cannot generate certificates
**Solution**:
1. Check disk space for certificate storage
2. Verify write permissions to output directory
3. Check system date and time
4. Restart SafeErase and try again
5. Contact support if issue persists

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| E001 | Device access denied | Run as administrator |
| E002 | Device not found | Check connections |
| E003 | Insufficient space | Free up disk space |
| E004 | Operation cancelled | User cancelled operation |
| E005 | Verification failed | Check device integrity |
| E006 | Certificate error | Check signing configuration |

### Log Files

SafeErase maintains detailed log files for troubleshooting:
- **Location**: `%APPDATA%\SafeErase\logs` (Windows), `~/.safeerase/logs` (Linux/macOS)
- **Rotation**: Logs are rotated daily
- **Levels**: ERROR, WARN, INFO, DEBUG
- **Retention**: 30 days by default

### Getting Support

If you need additional help:
1. **Check Documentation**: Review this manual and FAQ
2. **Search Knowledge Base**: Visit support website
3. **Contact Support**: Email support@safeerase.com
4. **Include Information**: Attach log files and system information

## FAQ

### General Questions

**Q: Is SafeErase free to use?**
A: SafeErase offers both free and commercial licenses. The free version includes basic wiping functionality, while the commercial version includes advanced features and support.

**Q: Can SafeErase wipe SSDs effectively?**
A: Yes, SafeErase includes specialized algorithms for SSDs including hardware secure erase and TRIM commands that are specifically designed for flash storage.

**Q: How long does wiping take?**
A: Wiping time depends on device size, algorithm, and hardware speed. Typical times range from minutes (hardware secure erase) to hours (multi-pass algorithms on large drives).

**Q: Can I wipe multiple devices simultaneously?**
A: Yes, SafeErase supports concurrent operations on multiple devices, limited by system resources and configuration settings.

### Security Questions

**Q: How secure is the wiping process?**
A: SafeErase uses industry-standard algorithms that meet or exceed government and military requirements for data destruction. The effectiveness depends on the algorithm chosen and device type.

**Q: Can wiped data be recovered?**
A: When properly wiped using appropriate algorithms, data recovery should not be possible with current technology. However, no method can guarantee 100% unrecoverability.

**Q: Are the certificates legally binding?**
A: The certificates provide cryptographic proof of the wiping process, but legal validity depends on local laws and regulations. Consult with legal counsel for specific requirements.

### Technical Questions

**Q: What file systems are supported?**
A: SafeErase operates at the hardware level and works regardless of file system. It can wipe drives with any file system or no file system.

**Q: Does SafeErase work with RAID arrays?**
A: SafeErase can wipe individual drives in a RAID array, but the array should be broken first. Consult your RAID documentation for proper procedures.

**Q: Can I create custom wiping algorithms?**
A: The commercial version allows custom algorithm configuration. Contact support for information about custom algorithm development.

**Q: Is network connectivity required?**
A: Network connectivity is optional. It's only needed for certificate verification and software updates. All core functionality works offline.
