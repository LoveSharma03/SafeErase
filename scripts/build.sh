#!/bin/bash

# SafeErase Build Script
# This script builds all components of the SafeErase project

set -e

echo "🔧 Building SafeErase Project"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Rust is installed
check_rust() {
    if ! command -v cargo &> /dev/null; then
        print_error "Rust/Cargo not found. Please install Rust from https://rustup.rs/"
        exit 1
    fi
    print_success "Rust/Cargo found: $(cargo --version)"
}

# Check if Flutter is installed
check_flutter() {
    if ! command -v flutter &> /dev/null; then
        print_warning "Flutter not found. UI components will be skipped."
        return 1
    fi
    print_success "Flutter found: $(flutter --version | head -n 1)"
    return 0
}

# Build Rust core engine
build_core() {
    print_status "Building SafeErase core engine..."
    cd core-engine
    
    # Run tests first
    print_status "Running core engine tests..."
    cargo test --release
    
    # Build the library
    print_status "Building core engine library..."
    cargo build --release
    
    cd ..
    print_success "Core engine built successfully"
}

# Build certificate generation system
build_certificates() {
    print_status "Building certificate generation system..."
    cd certificate-gen
    
    # Run tests first
    print_status "Running certificate tests..."
    cargo test --release
    
    # Build the library
    print_status "Building certificate library..."
    cargo build --release
    
    cd ..
    print_success "Certificate system built successfully"
}

# Build Flutter UI
build_flutter_ui() {
    if ! check_flutter; then
        return 0
    fi
    
    print_status "Building Flutter UI..."
    cd ui-flutter
    
    # Get dependencies
    print_status "Getting Flutter dependencies..."
    flutter pub get
    
    # Run code generation
    print_status "Running code generation..."
    flutter packages pub run build_runner build --delete-conflicting-outputs
    
    # Build for current platform
    print_status "Building Flutter app for current platform..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        flutter build linux --release
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        flutter build macos --release
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        flutter build windows --release
    fi
    
    cd ..
    print_success "Flutter UI built successfully"
}

# Create distribution package
create_package() {
    print_status "Creating distribution package..."
    
    # Create dist directory
    mkdir -p dist
    
    # Copy core libraries
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        cp target/release/libsafe_erase_core.so dist/
        cp target/release/libsafe_erase_certificates.so dist/
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        cp target/release/libsafe_erase_core.dylib dist/
        cp target/release/libsafe_erase_certificates.dylib dist/
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        cp target/release/safe_erase_core.dll dist/
        cp target/release/safe_erase_certificates.dll dist/
    fi
    
    # Copy Flutter app if built
    if [ -d "ui-flutter/build" ]; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            cp -r ui-flutter/build/linux/x64/release/bundle/* dist/
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            cp -r ui-flutter/build/macos/Build/Products/Release/* dist/
        elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            cp -r ui-flutter/build/windows/runner/Release/* dist/
        fi
    fi
    
    # Copy documentation
    cp README.md dist/
    cp LICENSE dist/ 2>/dev/null || true
    
    print_success "Distribution package created in dist/"
}

# Run all builds
run_all_builds() {
    print_status "Starting full build process..."
    
    # Check prerequisites
    check_rust
    
    # Build components
    build_core
    build_certificates
    build_flutter_ui
    
    # Create package
    create_package
    
    print_success "Build completed successfully!"
    print_status "Distribution files are available in the 'dist' directory"
}

# Parse command line arguments
case "${1:-all}" in
    "core")
        check_rust
        build_core
        ;;
    "certificates")
        check_rust
        build_certificates
        ;;
    "ui")
        build_flutter_ui
        ;;
    "package")
        create_package
        ;;
    "all")
        run_all_builds
        ;;
    "clean")
        print_status "Cleaning build artifacts..."
        cargo clean
        rm -rf ui-flutter/build
        rm -rf dist
        print_success "Clean completed"
        ;;
    "help")
        echo "SafeErase Build Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  all          Build all components (default)"
        echo "  core         Build only the core engine"
        echo "  certificates Build only the certificate system"
        echo "  ui           Build only the Flutter UI"
        echo "  package      Create distribution package"
        echo "  clean        Clean all build artifacts"
        echo "  help         Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        print_status "Use '$0 help' for usage information"
        exit 1
        ;;
esac
