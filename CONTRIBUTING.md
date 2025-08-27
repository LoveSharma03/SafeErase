# Contributing to SafeErase

Thank you for your interest in contributing to SafeErase! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Security Considerations](#security-considerations)

## Code of Conduct

SafeErase is committed to providing a welcoming and inclusive environment for all contributors. We expect all participants to adhere to our Code of Conduct:

- **Be respectful**: Treat all community members with respect and kindness
- **Be inclusive**: Welcome newcomers and help them get started
- **Be collaborative**: Work together constructively and share knowledge
- **Be professional**: Maintain professional standards in all interactions
- **Report issues**: Report any violations to the maintainers

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- **Rust**: Latest stable version (install from [rustup.rs](https://rustup.rs/))
- **Flutter**: Latest stable version (for UI contributions)
- **Git**: For version control
- **Platform tools**: Platform-specific development tools

### Repository Structure

```
SafeErase/
├── core-engine/          # Rust core wiping engine
├── certificate-gen/      # Certificate generation system
├── ui-flutter/           # Flutter cross-platform UI
├── ui-dotnet/           # .NET alternative UI (future)
├── bootable-iso/        # Linux ISO creation tools
├── tests/               # Integration and system tests
├── docs/                # Documentation
├── scripts/             # Build and utility scripts
└── examples/            # Usage examples
```

### Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/safeerase/SafeErase.git
   cd SafeErase
   ```

2. **Install dependencies**:
   ```bash
   # Rust dependencies
   cargo build
   
   # Flutter dependencies (if contributing to UI)
   cd ui-flutter
   flutter pub get
   cd ..
   ```

3. **Run tests**:
   ```bash
   ./scripts/test.sh
   ```

4. **Build the project**:
   ```bash
   ./scripts/build.sh
   ```

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

#### Code Contributions
- **Bug fixes**: Fix existing issues
- **New features**: Add new functionality
- **Performance improvements**: Optimize existing code
- **Platform support**: Add support for new platforms
- **Algorithm implementations**: Add new wiping algorithms

#### Documentation Contributions
- **User documentation**: Improve user manuals and guides
- **Technical documentation**: Enhance API and technical docs
- **Code comments**: Add or improve code documentation
- **Examples**: Create usage examples and tutorials

#### Testing Contributions
- **Unit tests**: Add or improve unit test coverage
- **Integration tests**: Create integration test scenarios
- **Performance tests**: Add benchmark and performance tests
- **Security tests**: Contribute security validation tests

#### Other Contributions
- **Bug reports**: Report issues with detailed information
- **Feature requests**: Suggest new features or improvements
- **Translations**: Help translate the interface
- **Design**: Contribute UI/UX improvements

### Contribution Process

1. **Check existing issues**: Look for existing issues or discussions
2. **Create an issue**: For new features or significant changes
3. **Fork the repository**: Create your own fork
4. **Create a branch**: Use descriptive branch names
5. **Make changes**: Implement your contribution
6. **Test thoroughly**: Ensure all tests pass
7. **Submit pull request**: Follow the PR template

## Development Setup

### Rust Development

#### Required Tools
```bash
# Install Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install additional components
rustup component add clippy rustfmt

# Install cargo tools
cargo install cargo-audit cargo-outdated
```

#### IDE Setup
Recommended IDEs for Rust development:
- **VS Code**: With rust-analyzer extension
- **IntelliJ IDEA**: With Rust plugin
- **Vim/Neovim**: With rust.vim and coc-rust-analyzer

### Flutter Development

#### Required Tools
```bash
# Install Flutter
git clone https://github.com/flutter/flutter.git
export PATH="$PATH:`pwd`/flutter/bin"

# Verify installation
flutter doctor
```

#### IDE Setup
Recommended IDEs for Flutter development:
- **VS Code**: With Flutter and Dart extensions
- **Android Studio**: With Flutter plugin
- **IntelliJ IDEA**: With Flutter plugin

### Platform-Specific Setup

#### Windows Development
- **Visual Studio**: With C++ build tools
- **Windows SDK**: Latest version
- **Administrator privileges**: Required for testing

#### Linux Development
- **Build essentials**: `sudo apt install build-essential`
- **System libraries**: Platform-specific libraries
- **Root access**: Required for device testing

#### macOS Development
- **Xcode**: Latest version from App Store
- **Command line tools**: `xcode-select --install`
- **Administrator privileges**: Required for testing

## Pull Request Process

### Before Submitting

1. **Update documentation**: Update relevant documentation
2. **Add tests**: Include tests for new functionality
3. **Run full test suite**: Ensure all tests pass
4. **Check formatting**: Run `cargo fmt` and `flutter format`
5. **Run linting**: Run `cargo clippy` and `flutter analyze`
6. **Update changelog**: Add entry to CHANGELOG.md

### PR Requirements

#### Title and Description
- **Clear title**: Descriptive and concise
- **Detailed description**: Explain what and why
- **Issue reference**: Link to related issues
- **Breaking changes**: Clearly mark breaking changes

#### Code Quality
- **Follows coding standards**: Adheres to project style
- **Well documented**: Includes appropriate comments
- **Tested**: Includes relevant tests
- **No warnings**: Passes all linting checks

#### Review Process
1. **Automated checks**: CI/CD pipeline must pass
2. **Code review**: At least one maintainer review
3. **Testing**: Manual testing if required
4. **Documentation review**: Documentation changes reviewed
5. **Final approval**: Maintainer approval required

### Merge Criteria

Pull requests will be merged when:
- All automated checks pass
- Code review is approved
- Documentation is updated
- Tests are included and passing
- No merge conflicts exist

## Coding Standards

### Rust Code Style

#### Formatting
- Use `cargo fmt` with default settings
- Maximum line length: 100 characters
- Use 4 spaces for indentation
- Follow Rust naming conventions

#### Code Organization
```rust
// File structure
use std::...;           // Standard library imports
use external_crate::...; // External crate imports
use crate::...;         // Internal imports

// Constants
const MAX_RETRIES: usize = 3;

// Types
pub struct MyStruct {
    field: Type,
}

// Implementation
impl MyStruct {
    pub fn new() -> Self {
        // Implementation
    }
}
```

#### Error Handling
- Use `Result<T, E>` for fallible operations
- Create custom error types when appropriate
- Provide meaningful error messages
- Use `?` operator for error propagation

#### Documentation
```rust
/// Brief description of the function
/// 
/// # Arguments
/// 
/// * `param` - Description of parameter
/// 
/// # Returns
/// 
/// Description of return value
/// 
/// # Errors
/// 
/// Description of possible errors
/// 
/// # Examples
/// 
/// ```
/// let result = my_function(42);
/// assert_eq!(result, expected);
/// ```
pub fn my_function(param: i32) -> Result<String, MyError> {
    // Implementation
}
```

### Flutter Code Style

#### Formatting
- Use `flutter format` with default settings
- Maximum line length: 80 characters
- Use 2 spaces for indentation
- Follow Dart naming conventions

#### Widget Organization
```dart
class MyWidget extends StatelessWidget {
  const MyWidget({
    Key? key,
    required this.title,
    this.subtitle,
  }) : super(key: key);

  final String title;
  final String? subtitle;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: _buildAppBar(),
      body: _buildBody(),
    );
  }

  Widget _buildAppBar() {
    // Implementation
  }

  Widget _buildBody() {
    // Implementation
  }
}
```

## Testing Requirements

### Test Coverage

#### Minimum Coverage
- **Unit tests**: >90% coverage for core components
- **Integration tests**: All major workflows
- **Platform tests**: All supported platforms
- **Security tests**: All security-critical components

#### Test Types
```rust
// Unit tests
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_function_name() {
        // Test implementation
    }

    #[tokio::test]
    async fn test_async_function() {
        // Async test implementation
    }
}

// Integration tests (in tests/ directory)
#[tokio::test]
async fn test_full_workflow() {
    // Integration test implementation
}

// Benchmark tests
#[cfg(test)]
mod benches {
    use criterion::{black_box, criterion_group, criterion_main, Criterion};

    fn benchmark_function(c: &mut Criterion) {
        c.bench_function("function_name", |b| {
            b.iter(|| function_name(black_box(input)))
        });
    }

    criterion_group!(benches, benchmark_function);
    criterion_main!(benches);
}
```

### Test Data

#### Mock Data
- Use realistic test data
- Include edge cases
- Test error conditions
- Avoid real device access in unit tests

#### Test Isolation
- Tests should be independent
- Clean up resources after tests
- Use temporary files/directories
- Mock external dependencies

## Security Considerations

### Security Review

All contributions involving security-critical components require:
- **Security review**: By security-focused maintainer
- **Threat modeling**: Consider security implications
- **Penetration testing**: For significant changes
- **Documentation**: Security considerations documented

### Sensitive Information

#### Secrets Management
- Never commit secrets or keys
- Use environment variables for configuration
- Implement secure key generation
- Follow cryptographic best practices

#### Data Handling
- Minimize data exposure
- Implement secure deletion
- Use constant-time comparisons
- Validate all inputs

### Vulnerability Reporting

If you discover a security vulnerability:
1. **Do not** create a public issue
2. **Email** security@safeerase.com
3. **Include** detailed information
4. **Wait** for response before disclosure

## Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: contribute@safeerase.com for contribution questions
- **Documentation**: Check existing documentation first

### Mentorship

New contributors can request mentorship:
- **Getting started**: Help with initial setup
- **Code review**: Guidance on code quality
- **Best practices**: Learn project conventions
- **Career development**: Open source contribution advice

## Recognition

We value all contributions and provide recognition through:
- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in release announcements
- **Social media**: Highlighted on project social media
- **Swag**: Occasional contributor swag for significant contributions

Thank you for contributing to SafeErase! Your efforts help make secure data destruction accessible to everyone.
