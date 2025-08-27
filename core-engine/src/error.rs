//! Error types for SafeErase operations

use thiserror::Error;

/// Result type alias for SafeErase operations
pub type Result<T> = std::result::Result<T, SafeEraseError>;

/// Comprehensive error types for SafeErase operations
#[derive(Error, Debug)]
pub enum SafeEraseError {
    /// Device-related errors
    #[error("Device not found: {0}")]
    DeviceNotFound(String),
    
    #[error("Device access denied: {0}")]
    DeviceAccessDenied(String),
    
    #[error("Device is busy or locked: {0}")]
    DeviceBusy(String),
    
    #[error("Device I/O error: {0}")]
    DeviceIoError(String),
    
    #[error("Unsupported device type: {0}")]
    UnsupportedDevice(String),
    
    /// Wipe operation errors
    #[error("Wipe operation failed: {0}")]
    WipeFailed(String),
    
    #[error("Wipe operation was cancelled")]
    WipeCancelled,
    
    #[error("Wipe verification failed")]
    VerificationFailed,
    
    #[error("Unsupported wipe algorithm: {0}")]
    UnsupportedAlgorithm(String),
    
    /// System-level errors
    #[error("Insufficient privileges - administrator/root access required")]
    InsufficientPrivileges,
    
    #[error("System command failed: {0}")]
    SystemCommandFailed(String),
    
    #[error("Platform not supported: {0}")]
    UnsupportedPlatform(String),
    
    /// Certificate and security errors
    #[error("Certificate generation failed: {0}")]
    CertificateError(String),
    
    #[error("Cryptographic operation failed: {0}")]
    CryptographicError(String),
    
    #[error("Digital signature verification failed")]
    SignatureVerificationFailed,
    
    /// Configuration and validation errors
    #[error("Invalid configuration: {0}")]
    InvalidConfiguration(String),
    
    #[error("Invalid parameter: {0}")]
    InvalidParameter(String),
    
    #[error("Operation timeout: {0}")]
    Timeout(String),
    
    /// I/O and file system errors
    #[error("File system error: {0}")]
    FileSystemError(String),
    
    #[error("Permission denied: {0}")]
    PermissionDenied(String),
    
    /// Network and communication errors
    #[error("Network error: {0}")]
    NetworkError(String),
    
    #[error("Communication timeout")]
    CommunicationTimeout,
    
    /// Generic errors
    #[error("Internal error: {0}")]
    Internal(String),
    
    #[error("Unknown error: {0}")]
    Unknown(String),
}

impl SafeEraseError {
    /// Check if the error is recoverable
    pub fn is_recoverable(&self) -> bool {
        match self {
            SafeEraseError::DeviceBusy(_) => true,
            SafeEraseError::CommunicationTimeout => true,
            SafeEraseError::NetworkError(_) => true,
            SafeEraseError::Timeout(_) => true,
            _ => false,
        }
    }
    
    /// Get error severity level
    pub fn severity(&self) -> ErrorSeverity {
        match self {
            SafeEraseError::InsufficientPrivileges => ErrorSeverity::Critical,
            SafeEraseError::UnsupportedPlatform(_) => ErrorSeverity::Critical,
            SafeEraseError::VerificationFailed => ErrorSeverity::High,
            SafeEraseError::WipeFailed(_) => ErrorSeverity::High,
            SafeEraseError::CertificateError(_) => ErrorSeverity::High,
            SafeEraseError::DeviceNotFound(_) => ErrorSeverity::Medium,
            SafeEraseError::DeviceAccessDenied(_) => ErrorSeverity::Medium,
            SafeEraseError::InvalidConfiguration(_) => ErrorSeverity::Medium,
            SafeEraseError::DeviceBusy(_) => ErrorSeverity::Low,
            SafeEraseError::WipeCancelled => ErrorSeverity::Low,
            _ => ErrorSeverity::Medium,
        }
    }
    
    /// Get user-friendly error message
    pub fn user_message(&self) -> String {
        match self {
            SafeEraseError::InsufficientPrivileges => {
                "Administrator or root privileges are required to access storage devices.".to_string()
            }
            SafeEraseError::DeviceNotFound(device) => {
                format!("The device '{}' could not be found. Please check if it's connected.", device)
            }
            SafeEraseError::DeviceAccessDenied(device) => {
                format!("Access to device '{}' was denied. Please check permissions.", device)
            }
            SafeEraseError::DeviceBusy(device) => {
                format!("Device '{}' is currently busy. Please close any applications using it.", device)
            }
            SafeEraseError::VerificationFailed => {
                "Wipe verification failed. The data may not have been completely erased.".to_string()
            }
            SafeEraseError::WipeFailed(reason) => {
                format!("The wipe operation failed: {}", reason)
            }
            SafeEraseError::UnsupportedDevice(device) => {
                format!("Device type '{}' is not supported for secure wiping.", device)
            }
            _ => self.to_string(),
        }
    }
}

/// Error severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorSeverity {
    Low,
    Medium,
    High,
    Critical,
}

impl std::fmt::Display for ErrorSeverity {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ErrorSeverity::Low => write!(f, "Low"),
            ErrorSeverity::Medium => write!(f, "Medium"),
            ErrorSeverity::High => write!(f, "High"),
            ErrorSeverity::Critical => write!(f, "Critical"),
        }
    }
}

// Implement conversions from common error types
impl From<std::io::Error> for SafeEraseError {
    fn from(err: std::io::Error) -> Self {
        match err.kind() {
            std::io::ErrorKind::NotFound => SafeEraseError::DeviceNotFound(err.to_string()),
            std::io::ErrorKind::PermissionDenied => SafeEraseError::DeviceAccessDenied(err.to_string()),
            std::io::ErrorKind::TimedOut => SafeEraseError::Timeout(err.to_string()),
            _ => SafeEraseError::DeviceIoError(err.to_string()),
        }
    }
}

impl From<openssl::error::ErrorStack> for SafeEraseError {
    fn from(err: openssl::error::ErrorStack) -> Self {
        SafeEraseError::CryptographicError(err.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_error_severity() {
        assert_eq!(SafeEraseError::InsufficientPrivileges.severity(), ErrorSeverity::Critical);
        assert_eq!(SafeEraseError::VerificationFailed.severity(), ErrorSeverity::High);
        assert_eq!(SafeEraseError::DeviceBusy("test".to_string()).severity(), ErrorSeverity::Low);
    }
    
    #[test]
    fn test_error_recoverability() {
        assert!(SafeEraseError::DeviceBusy("test".to_string()).is_recoverable());
        assert!(!SafeEraseError::InsufficientPrivileges.is_recoverable());
    }
    
    #[test]
    fn test_user_messages() {
        let error = SafeEraseError::DeviceNotFound("sda".to_string());
        let message = error.user_message();
        assert!(message.contains("sda"));
        assert!(message.contains("could not be found"));
    }
}
