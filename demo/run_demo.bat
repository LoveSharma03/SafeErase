@echo off
setlocal enabledelayedexpansion

:: SafeErase Demo Script for Windows
:: Demonstrates project structure and functionality

title SafeErase - Secure Data Wiping Solution Demo

:banner
cls
echo ================================================================
echo                🔒 SafeErase Demo - Windows Version
echo ================================================================
echo.
echo A comprehensive secure data wiping solution for IT asset recyclers
echo.
echo Key Features:
echo ✓ Military-grade data destruction
echo ✓ Tamper-proof certificates  
echo ✓ Cross-platform support
echo ✓ One-click operation
echo ✓ Industry compliance (NIST 800-88, DoD 5220.22-M)
echo.
echo ================================================================
echo.

:main_menu
echo 🎯 SafeErase Demo Menu:
echo.
echo 1. Show Project Structure
echo 2. Display System Requirements
echo 3. Simulate Device Discovery
echo 4. Show Wiping Algorithms
echo 5. Simulate Wipe Operation
echo 6. Show Certificate Features
echo 7. Display Build Instructions
echo 8. Exit Demo
echo.
set /p choice="Select option (1-8): "

if "%choice%"=="1" goto show_structure
if "%choice%"=="2" goto show_requirements
if "%choice%"=="3" goto simulate_discovery
if "%choice%"=="4" goto show_algorithms
if "%choice%"=="5" goto simulate_wipe
if "%choice%"=="6" goto show_certificates
if "%choice%"=="7" goto show_build
if "%choice%"=="8" goto exit_demo
goto invalid_choice

:show_structure
cls
echo 📁 SafeErase Project Structure:
echo ================================================================
echo.
echo SafeErase/
echo ├── core-engine/          # Rust-based wiping engine
echo │   ├── src/
echo │   │   ├── lib.rs         # Main library interface
echo │   │   ├── device.rs      # Device detection and management
echo │   │   ├── wipe.rs        # Wiping operations
echo │   │   ├── algorithms.rs  # Wiping algorithms
echo │   │   ├── verification.rs# Wipe verification
echo │   │   └── platform/      # Platform-specific code
echo │   └── Cargo.toml         # Rust dependencies
echo.
echo ├── certificate-gen/       # Certificate generation system
echo │   ├── src/
echo │   │   ├── lib.rs         # Certificate library
echo │   │   ├── certificate.rs # Certificate data structures
echo │   │   ├── crypto.rs      # Cryptographic operations
echo │   │   ├── pdf.rs         # PDF generation
echo │   │   └── json.rs        # JSON export
echo │   └── Cargo.toml
echo.
echo ├── ui-flutter/            # Cross-platform UI
echo │   ├── lib/
echo │   │   ├── main.dart      # Application entry point
echo │   │   ├── core/          # Core UI components
echo │   │   └── features/      # Feature-specific UI
echo │   └── pubspec.yaml       # Flutter dependencies
echo.
echo ├── scripts/               # Build and utility scripts
echo │   ├── build.sh           # Cross-platform build script
echo │   └── test.sh            # Comprehensive test suite
echo.
echo ├── docs/                  # Documentation
echo │   ├── user-manual.md     # User documentation
echo │   └── technical-specs.md # Technical specifications
echo.
echo └── demo/                  # Demonstration files
echo     ├── run_demo.py        # Python demo script
echo     └── run_demo.bat       # Windows demo script
echo.
pause
goto main_menu

:show_requirements
cls
echo 💻 System Requirements:
echo ================================================================
echo.
echo Minimum Requirements:
echo ├── Operating System: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
echo ├── Memory: 4GB RAM (8GB recommended)
echo ├── Storage: 100MB free space
echo ├── Privileges: Administrator/root access required
echo └── Network: Optional (for certificate verification)
echo.
echo Development Requirements:
echo ├── Rust: Latest stable version (rustup.rs)
echo ├── Flutter: Latest stable version (flutter.dev)
echo ├── Platform Tools: Visual Studio Build Tools (Windows)
echo └── Git: For version control
echo.
echo Supported Storage Interfaces:
echo ├── SATA: Traditional hard drives and SSDs
echo ├── NVMe: Modern NVMe SSDs
echo ├── USB: External storage devices
echo ├── SCSI: Enterprise storage systems
echo └── IDE: Legacy storage devices
echo.
echo Supported Device Types:
echo ├── HDD: Traditional spinning hard drives
echo ├── SSD: SATA-based solid state drives
echo ├── NVMe: NVMe-based solid state drives
echo ├── eMMC: Embedded multimedia cards
echo ├── SD: SD cards and variants
echo └── USB: USB flash drives and external drives
echo.
pause
goto main_menu

:simulate_discovery
cls
echo 🔍 Simulating Device Discovery...
echo ================================================================
echo.
timeout /t 2 /nobreak >nul
echo ✅ Found 3 storage devices:
echo.
echo 1. Samsung SSD 980 PRO 1TB
echo    ├── Path: \\?\PhysicalDrive0
echo    ├── Size: 1000.2 GB (NVMe SSD)
echo    ├── Interface: NVMe PCIe 4.0
echo    ├── Features: Secure Erase: Yes, HPA/DCO: No
echo    ├── Health: Good
echo    └── ⚠️  SYSTEM DISK - Contains Windows OS
echo.
echo 2. SanDisk Ultra USB 3.0 32GB
echo    ├── Path: \\?\PhysicalDrive1
echo    ├── Size: 32.2 GB (USB Storage)
echo    ├── Interface: USB 3.0
echo    ├── Features: Secure Erase: No, HPA/DCO: No
echo    ├── Health: Good
echo    └── 🔌 REMOVABLE - External device
echo.
echo 3. Western Digital Blue 2TB
echo    ├── Path: \\?\PhysicalDrive2
echo    ├── Size: 2000.4 GB (HDD)
echo    ├── Interface: SATA 6.0 Gb/s
echo    ├── Features: Secure Erase: Yes, HPA/DCO: Yes
echo    ├── Health: Good
echo    └── 💾 DATA DISK - Safe to wipe
echo.
echo Device discovery completed successfully!
echo.
pause
goto main_menu

:show_algorithms
cls
echo 🔐 Available Wiping Algorithms:
echo ================================================================
echo.
echo 1. NIST SP 800-88 Rev. 1 (Recommended)
echo    ├── Passes: 1
echo    ├── Method: Cryptographic erase for SSDs, single overwrite for HDDs
echo    ├── Security Level: Standard
echo    ├── Speed: Fast
echo    ├── Compliance: NIST Special Publication 800-88
echo    └── Use Case: Government and enterprise environments
echo.
echo 2. DoD 5220.22-M (High Security)
echo    ├── Passes: 3
echo    ├── Pattern: Zeros → Ones → Random data
echo    ├── Security Level: High
echo    ├── Speed: Medium
echo    ├── Compliance: US Department of Defense standard
echo    └── Use Case: Military and high-security environments
echo.
echo 3. Gutmann Algorithm (Maximum Security)
echo    ├── Passes: 35
echo    ├── Method: Complex pattern sequence for older drives
echo    ├── Security Level: Maximum
echo    ├── Speed: Slow
echo    ├── Compliance: Academic research standard
echo    └── Use Case: Maximum security for legacy systems
echo.
echo 4. ATA Secure Erase (Hardware-Based)
echo    ├── Passes: 1 (hardware-level)
echo    ├── Method: Hardware command to drive controller
echo    ├── Security Level: High
echo    ├── Speed: Very Fast
echo    ├── Compliance: ATA/ATAPI Command Set standard
echo    └── Use Case: Modern SSDs and HDDs with hardware support
echo.
echo 5. NVMe Format (SSD-Optimized)
echo    ├── Passes: 1 (cryptographic erase)
echo    ├── Method: NVMe Format command with secure erase
echo    ├── Security Level: High
echo    ├── Speed: Very Fast
echo    ├── Compliance: NVMe specification
echo    └── Use Case: NVMe SSDs with format support
echo.
pause
goto main_menu

:simulate_wipe
cls
echo 🚀 Simulating Wipe Operation:
echo ================================================================
echo.
echo Selected Device: SanDisk Ultra USB 3.0 32GB
echo Selected Algorithm: NIST SP 800-88 Rev. 1
echo Estimated Time: 3 minutes
echo.
echo ⚠️  FINAL CONFIRMATION:
echo This will PERMANENTLY DESTROY all data on the device!
echo.
set /p confirm="Type 'WIPE' to confirm: "
if not "%confirm%"=="WIPE" (
    echo Operation cancelled.
    pause
    goto main_menu
)

echo.
echo 🔄 Starting wipe operation...
echo Operation ID: op_demo_12345678
echo.

:: Simulate progress
for /l %%i in (0,5,100) do (
    set /a bar_filled=%%i/5
    set bar=
    for /l %%j in (1,1,!bar_filled!) do set bar=!bar!█
    for /l %%j in (!bar_filled!,1,19) do set bar=!bar!-
    echo ⏳ Pass 1/1 ^|!bar!^| %%i%%
    timeout /t 1 /nobreak >nul
    cls
    echo 🚀 Simulating Wipe Operation:
    echo ================================================================
    echo.
    echo Selected Device: SanDisk Ultra USB 3.0 32GB
    echo Selected Algorithm: NIST SP 800-88 Rev. 1
    echo Operation ID: op_demo_12345678
    echo.
)

echo ✅ Wipe operation completed successfully!
echo.
echo 🔍 Performing verification...
timeout /t 2 /nobreak >nul
echo ✅ Verification passed - Data successfully destroyed
echo.
echo 📜 Generating tamper-proof certificate...
timeout /t 2 /nobreak >nul
echo ✅ Certificate generated: certificate_demo123.json
echo 🔐 Digital signature: a1b2c3d4e5f6789a...
echo 📁 Saved to: demo\certificates\
echo.
echo Wipe operation completed with certificate generation!
echo.
pause
goto main_menu

:show_certificates
cls
echo 📜 Certificate Features:
echo ================================================================
echo.
echo Tamper-Proof Certificates Include:
echo.
echo 🆔 Certificate Information:
echo ├── Unique Certificate ID (UUID)
echo ├── Generation timestamp
echo ├── Digital signature (RSA-2048/4096)
echo └── Cryptographic hash verification
echo.
echo 💾 Device Information:
echo ├── Device name and model
echo ├── Serial number
echo ├── Storage capacity
echo ├── Device type and interface
echo └── Health status
echo.
echo 🔐 Wipe Information:
echo ├── Algorithm used
echo ├── Start and completion times
echo ├── Operation duration
echo ├── Number of passes completed
echo └── Verification results
echo.
echo 📋 Compliance Information:
echo ├── Standards met (NIST, DoD, etc.)
echo ├── Security level achieved
echo ├── Certification authority
echo └── Compliance notes
echo.
echo 🏢 Organization Information:
echo ├── Company name and contact
echo ├── Address and website
echo ├── Logo (for PDF certificates)
echo └── Certification authority
echo.
echo 🔍 Verification Features:
echo ├── QR code for quick verification
echo ├── Online verification portal
echo ├── Offline verification tool
echo └── Certificate integrity checking
echo.
echo 📄 Output Formats:
echo ├── PDF: Human-readable with QR code
echo ├── JSON: Machine-readable with JWS
echo ├── Both formats available
echo └── Long-term archival support
echo.
pause
goto main_menu

:show_build
cls
echo 🔧 Build Instructions:
echo ================================================================
echo.
echo To build the full SafeErase application:
echo.
echo 1. Install Prerequisites:
echo    ├── Rust: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs ^| sh
echo    ├── Flutter: Download from https://flutter.dev/docs/get-started/install
echo    └── Git: Download from https://git-scm.com/
echo.
echo 2. Clone Repository:
echo    git clone https://github.com/safeerase/SafeErase.git
echo    cd SafeErase
echo.
echo 3. Build Core Components:
echo    ├── Core Engine: cd core-engine ^&^& cargo build --release
echo    ├── Certificates: cd certificate-gen ^&^& cargo build --release
echo    └── UI: cd ui-flutter ^&^& flutter build windows
echo.
echo 4. Run Automated Build:
echo    ./scripts/build.sh    (Linux/macOS)
echo    scripts\build.bat     (Windows)
echo.
echo 5. Run Tests:
echo    ./scripts/test.sh     (Linux/macOS)
echo    scripts\test.bat      (Windows)
echo.
echo 6. Create Distribution:
echo    The build script creates a 'dist' folder with:
echo    ├── Core libraries (.dll/.so/.dylib)
echo    ├── UI application
echo    ├── Documentation
echo    └── Example certificates
echo.
echo Platform-Specific Notes:
echo.
echo Windows:
echo ├── Requires Visual Studio Build Tools
echo ├── Administrator privileges needed for testing
echo └── Windows SDK recommended
echo.
echo Linux:
echo ├── Requires build-essential package
echo ├── Root access needed for device testing
echo └── Platform-specific libraries may be needed
echo.
echo macOS:
echo ├── Requires Xcode command line tools
echo ├── Administrator privileges needed for testing
echo └── May require additional permissions for device access
echo.
pause
goto main_menu

:invalid_choice
echo.
echo ❌ Invalid option. Please select 1-8.
echo.
pause
goto main_menu

:exit_demo
cls
echo.
echo 👋 Thank you for trying SafeErase!
echo.
echo This demo showcased the key features of SafeErase:
echo ✓ Comprehensive device detection
echo ✓ Multiple wiping algorithms
echo ✓ Real-time progress monitoring
echo ✓ Tamper-proof certificate generation
echo ✓ Industry compliance standards
echo.
echo For the full version with real device wiping capabilities:
echo 1. Install Rust from https://rustup.rs/
echo 2. Install Flutter from https://flutter.dev/
echo 3. Run: ./scripts/build.sh
echo 4. Launch the SafeErase application
echo.
echo ⚠️  Remember: Always run with administrator privileges
echo ⚠️  Warning: Real wiping permanently destroys data
echo.
echo Visit: https://github.com/safeerase/SafeErase
echo Email: support@safeerase.com
echo.
pause
exit /b 0
