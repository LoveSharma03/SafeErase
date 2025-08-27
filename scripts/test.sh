#!/bin/bash

# SafeErase Test Script
# Comprehensive testing for all components

set -e

echo "🧪 SafeErase Test Suite"
echo "======================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test and track results
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running: $test_name"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command"; then
        print_success "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_error "$test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Core engine tests
test_core_engine() {
    print_status "Testing SafeErase core engine..."
    
    cd core-engine
    
    # Unit tests
    run_test "Core engine unit tests" "cargo test --lib"
    
    # Integration tests
    run_test "Core engine integration tests" "cargo test --test '*'"
    
    # Documentation tests
    run_test "Core engine doc tests" "cargo test --doc"
    
    # Benchmark tests (if available)
    if [ -d "benches" ]; then
        run_test "Core engine benchmarks" "cargo bench --no-run"
    fi
    
    # Clippy linting
    run_test "Core engine linting" "cargo clippy -- -D warnings"
    
    # Format check
    run_test "Core engine formatting" "cargo fmt -- --check"
    
    cd ..
}

# Certificate system tests
test_certificates() {
    print_status "Testing certificate generation system..."
    
    cd certificate-gen
    
    # Unit tests
    run_test "Certificate unit tests" "cargo test --lib"
    
    # Integration tests
    run_test "Certificate integration tests" "cargo test --test '*'"
    
    # Documentation tests
    run_test "Certificate doc tests" "cargo test --doc"
    
    # Clippy linting
    run_test "Certificate linting" "cargo clippy -- -D warnings"
    
    # Format check
    run_test "Certificate formatting" "cargo fmt -- --check"
    
    cd ..
}

# Flutter UI tests
test_flutter_ui() {
    if ! command -v flutter &> /dev/null; then
        print_warning "Flutter not found, skipping UI tests"
        return 0
    fi
    
    print_status "Testing Flutter UI..."
    
    cd ui-flutter
    
    # Get dependencies
    flutter pub get
    
    # Unit tests
    run_test "Flutter unit tests" "flutter test"
    
    # Widget tests
    run_test "Flutter widget tests" "flutter test test/widget_test.dart"
    
    # Integration tests (if available)
    if [ -d "integration_test" ]; then
        run_test "Flutter integration tests" "flutter test integration_test/"
    fi
    
    # Analyze code
    run_test "Flutter code analysis" "flutter analyze"
    
    cd ..
}

# Security tests
test_security() {
    print_status "Running security tests..."
    
    # Check for common security issues in Rust code
    if command -v cargo-audit &> /dev/null; then
        run_test "Rust security audit" "cargo audit"
    else
        print_warning "cargo-audit not installed, skipping security audit"
    fi
    
    # Check for hardcoded secrets
    if command -v git &> /dev/null; then
        run_test "Secret scanning" "! git log --all --full-history -- '*.rs' '*.dart' | grep -i -E '(password|secret|key|token).*=.*['\"].*['\"]'"
    fi
}

# Performance tests
test_performance() {
    print_status "Running performance tests..."
    
    cd core-engine
    
    # Run benchmarks if available
    if [ -d "benches" ]; then
        run_test "Performance benchmarks" "cargo bench"
    else
        print_warning "No benchmarks found, skipping performance tests"
    fi
    
    cd ..
}

# Compliance tests
test_compliance() {
    print_status "Running compliance validation tests..."
    
    # Test NIST 800-88 compliance
    run_test "NIST 800-88 algorithm validation" "cd core-engine && cargo test test_nist_compliance"
    
    # Test DoD 5220.22-M compliance
    run_test "DoD 5220.22-M algorithm validation" "cd core-engine && cargo test test_dod_compliance"
    
    # Test certificate format compliance
    run_test "Certificate format validation" "cd certificate-gen && cargo test test_certificate_format"
}

# Memory safety tests
test_memory_safety() {
    print_status "Running memory safety tests..."
    
    # Valgrind tests (Linux only)
    if command -v valgrind &> /dev/null && [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_test "Memory leak detection" "cd core-engine && cargo test --release && valgrind --leak-check=full --error-exitcode=1 ./target/release/deps/safe_erase_core-*"
    else
        print_warning "Valgrind not available, skipping memory leak tests"
    fi
    
    # Address sanitizer tests
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_test "Address sanitizer" "cd core-engine && RUSTFLAGS='-Z sanitizer=address' cargo test --target x86_64-unknown-linux-gnu"
    fi
}

# Cross-platform tests
test_cross_platform() {
    print_status "Running cross-platform compatibility tests..."
    
    # Test compilation for different targets
    if command -v rustup &> /dev/null; then
        # Add common targets if not already added
        rustup target add x86_64-pc-windows-gnu 2>/dev/null || true
        rustup target add x86_64-apple-darwin 2>/dev/null || true
        
        # Test Windows target (if not on Windows)
        if [[ "$OSTYPE" != "msys" ]] && [[ "$OSTYPE" != "win32" ]]; then
            run_test "Windows cross-compilation" "cd core-engine && cargo check --target x86_64-pc-windows-gnu"
        fi
        
        # Test macOS target (if not on macOS)
        if [[ "$OSTYPE" != "darwin"* ]]; then
            run_test "macOS cross-compilation" "cd core-engine && cargo check --target x86_64-apple-darwin"
        fi
    fi
}

# Generate test report
generate_report() {
    print_status "Generating test report..."
    
    echo ""
    echo "📊 Test Results Summary"
    echo "======================="
    echo "Tests Run:    $TESTS_RUN"
    echo "Tests Passed: $TESTS_PASSED"
    echo "Tests Failed: $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "All tests passed! ✅"
        return 0
    else
        print_error "$TESTS_FAILED test(s) failed! ❌"
        return 1
    fi
}

# Main test execution
run_all_tests() {
    print_status "Starting comprehensive test suite..."
    
    # Core functionality tests
    test_core_engine
    test_certificates
    test_flutter_ui
    
    # Security and compliance tests
    test_security
    test_compliance
    
    # Performance and memory tests
    test_performance
    test_memory_safety
    
    # Cross-platform tests
    test_cross_platform
    
    # Generate final report
    generate_report
}

# Parse command line arguments
case "${1:-all}" in
    "core")
        test_core_engine
        generate_report
        ;;
    "certificates")
        test_certificates
        generate_report
        ;;
    "ui")
        test_flutter_ui
        generate_report
        ;;
    "security")
        test_security
        generate_report
        ;;
    "performance")
        test_performance
        generate_report
        ;;
    "compliance")
        test_compliance
        generate_report
        ;;
    "memory")
        test_memory_safety
        generate_report
        ;;
    "cross-platform")
        test_cross_platform
        generate_report
        ;;
    "all")
        run_all_tests
        ;;
    "help")
        echo "SafeErase Test Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  all           Run all tests (default)"
        echo "  core          Test core engine only"
        echo "  certificates  Test certificate system only"
        echo "  ui            Test Flutter UI only"
        echo "  security      Run security tests"
        echo "  performance   Run performance tests"
        echo "  compliance    Run compliance validation tests"
        echo "  memory        Run memory safety tests"
        echo "  cross-platform Run cross-platform tests"
        echo "  help          Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        print_status "Use '$0 help' for usage information"
        exit 1
        ;;
esac

exit $?
