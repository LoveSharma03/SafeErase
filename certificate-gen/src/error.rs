//! Error types for certificate generation

use thiserror::Error;

/// Result type alias for certificate operations
pub type Result<T> = std::result::Result<T, CertificateError>;

/// Comprehensive error types for certificate operations
#[derive(Error, Debug)]
pub enum CertificateError {
    /// Cryptographic errors
    #[error("Cryptographic operation failed: {0}")]
    CryptographicError(String),
    
    #[error("Key generation failed: {0}")]
    KeyGenerationFailed(String),
    
    #[error("Signing failed: {0}")]
    SigningFailed(String),
    
    #[error("Signature verification failed")]
    SignatureVerificationFailed,
    
    #[error("Invalid certificate format: {0}")]
    InvalidCertificateFormat(String),
    
    /// PDF generation errors
    #[error("PDF generation failed: {0}")]
    PdfGenerationFailed(String),
    
    #[error("PDF template error: {0}")]
    PdfTemplateError(String),
    
    #[error("Font loading failed: {0}")]
    FontLoadingFailed(String),
    
    /// JSON errors
    #[error("JSON serialization failed: {0}")]
    JsonSerializationFailed(String),
    
    #[error("JSON deserialization failed: {0}")]
    JsonDeserializationFailed(String),
    
    /// File I/O errors
    #[error("File operation failed: {0}")]
    FileOperationFailed(String),
    
    #[error("File not found: {0}")]
    FileNotFound(String),
    
    #[error("Permission denied: {0}")]
    PermissionDenied(String),
    
    #[error("Invalid file format: {0}")]
    InvalidFileFormat(String),
    
    /// Template errors
    #[error("Template not found: {0}")]
    TemplateNotFound(String),
    
    #[error("Template parsing failed: {0}")]
    TemplateParsingFailed(String),
    
    #[error("Template rendering failed: {0}")]
    TemplateRenderingFailed(String),
    
    /// QR code errors
    #[error("QR code generation failed: {0}")]
    QrCodeGenerationFailed(String),
    
    #[error("QR code data too large: {0}")]
    QrCodeDataTooLarge(String),
    
    /// Validation errors
    #[error("Certificate validation failed: {0}")]
    CertificateValidationFailed(String),
    
    #[error("Invalid certificate data: {0}")]
    InvalidCertificateData(String),
    
    #[error("Missing required field: {0}")]
    MissingRequiredField(String),
    
    #[error("Invalid timestamp: {0}")]
    InvalidTimestamp(String),
    
    /// Network errors (for verification services)
    #[error("Network error: {0}")]
    NetworkError(String),
    
    #[error("Verification service unavailable")]
    VerificationServiceUnavailable,
    
    #[error("Certificate not found in verification database")]
    CertificateNotFoundInDatabase,
    
    /// Configuration errors
    #[error("Invalid configuration: {0}")]
    InvalidConfiguration(String),
    
    #[error("Missing configuration: {0}")]
    MissingConfiguration(String),
    
    /// Generic errors
    #[error("Internal error: {0}")]
    Internal(String),
    
    #[error("Operation not supported: {0}")]
    NotSupported(String),
}

impl CertificateError {
    /// Check if the error is recoverable
    pub fn is_recoverable(&self) -> bool {
        match self {
            CertificateError::NetworkError(_) => true,
            CertificateError::VerificationServiceUnavailable => true,
            CertificateError::FileOperationFailed(_) => true,
            CertificateError::PermissionDenied(_) => false,
            CertificateError::SignatureVerificationFailed => false,
            CertificateError::InvalidCertificateFormat(_) => false,
            _ => false,
        }
    }
    
    /// Get error severity level
    pub fn severity(&self) -> ErrorSeverity {
        match self {
            CertificateError::SignatureVerificationFailed => ErrorSeverity::Critical,
            CertificateError::CryptographicError(_) => ErrorSeverity::Critical,
            CertificateError::KeyGenerationFailed(_) => ErrorSeverity::Critical,
            CertificateError::InvalidCertificateFormat(_) => ErrorSeverity::High,
            CertificateError::CertificateValidationFailed(_) => ErrorSeverity::High,
            CertificateError::PdfGenerationFailed(_) => ErrorSeverity::Medium,
            CertificateError::JsonSerializationFailed(_) => ErrorSeverity::Medium,
            CertificateError::TemplateNotFound(_) => ErrorSeverity::Medium,
            CertificateError::QrCodeGenerationFailed(_) => ErrorSeverity::Low,
            CertificateError::NetworkError(_) => ErrorSeverity::Low,
            _ => ErrorSeverity::Medium,
        }
    }
    
    /// Get user-friendly error message
    pub fn user_message(&self) -> String {
        match self {
            CertificateError::SignatureVerificationFailed => {
                "Certificate signature verification failed. The certificate may have been tampered with.".to_string()
            }
            CertificateError::CryptographicError(_) => {
                "A cryptographic error occurred. Please check your security configuration.".to_string()
            }
            CertificateError::PdfGenerationFailed(_) => {
                "Failed to generate PDF certificate. Please try again or use JSON format.".to_string()
            }
            CertificateError::FileNotFound(file) => {
                format!("Required file '{}' was not found. Please check the file path.", file)
            }
            CertificateError::PermissionDenied(path) => {
                format!("Permission denied accessing '{}'. Please check file permissions.", path)
            }
            CertificateError::TemplateNotFound(template) => {
                format!("Certificate template '{}' was not found. Please check template configuration.", template)
            }
            CertificateError::VerificationServiceUnavailable => {
                "Certificate verification service is currently unavailable. Please try again later.".to_string()
            }
            CertificateError::InvalidCertificateData(reason) => {
                format!("Invalid certificate data: {}. Please check the input data.", reason)
            }
            _ => self.to_string(),
        }
    }
    
    /// Get error category for logging and metrics
    pub fn category(&self) -> ErrorCategory {
        match self {
            CertificateError::CryptographicError(_) |
            CertificateError::KeyGenerationFailed(_) |
            CertificateError::SigningFailed(_) |
            CertificateError::SignatureVerificationFailed => ErrorCategory::Cryptographic,
            
            CertificateError::PdfGenerationFailed(_) |
            CertificateError::PdfTemplateError(_) |
            CertificateError::FontLoadingFailed(_) => ErrorCategory::PdfGeneration,
            
            CertificateError::JsonSerializationFailed(_) |
            CertificateError::JsonDeserializationFailed(_) => ErrorCategory::JsonProcessing,
            
            CertificateError::FileOperationFailed(_) |
            CertificateError::FileNotFound(_) |
            CertificateError::PermissionDenied(_) |
            CertificateError::InvalidFileFormat(_) => ErrorCategory::FileSystem,
            
            CertificateError::TemplateNotFound(_) |
            CertificateError::TemplateParsingFailed(_) |
            CertificateError::TemplateRenderingFailed(_) => ErrorCategory::Template,
            
            CertificateError::QrCodeGenerationFailed(_) |
            CertificateError::QrCodeDataTooLarge(_) => ErrorCategory::QrCode,
            
            CertificateError::NetworkError(_) |
            CertificateError::VerificationServiceUnavailable |
            CertificateError::CertificateNotFoundInDatabase => ErrorCategory::Network,
            
            CertificateError::CertificateValidationFailed(_) |
            CertificateError::InvalidCertificateData(_) |
            CertificateError::MissingRequiredField(_) |
            CertificateError::InvalidTimestamp(_) => ErrorCategory::Validation,
            
            CertificateError::InvalidConfiguration(_) |
            CertificateError::MissingConfiguration(_) => ErrorCategory::Configuration,
            
            CertificateError::Internal(_) |
            CertificateError::NotSupported(_) => ErrorCategory::Internal,
            
            _ => ErrorCategory::Unknown,
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

/// Error categories for classification
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ErrorCategory {
    Cryptographic,
    PdfGeneration,
    JsonProcessing,
    FileSystem,
    Template,
    QrCode,
    Network,
    Validation,
    Configuration,
    Internal,
    Unknown,
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

impl std::fmt::Display for ErrorCategory {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ErrorCategory::Cryptographic => write!(f, "Cryptographic"),
            ErrorCategory::PdfGeneration => write!(f, "PDF Generation"),
            ErrorCategory::JsonProcessing => write!(f, "JSON Processing"),
            ErrorCategory::FileSystem => write!(f, "File System"),
            ErrorCategory::Template => write!(f, "Template"),
            ErrorCategory::QrCode => write!(f, "QR Code"),
            ErrorCategory::Network => write!(f, "Network"),
            ErrorCategory::Validation => write!(f, "Validation"),
            ErrorCategory::Configuration => write!(f, "Configuration"),
            ErrorCategory::Internal => write!(f, "Internal"),
            ErrorCategory::Unknown => write!(f, "Unknown"),
        }
    }
}

// Implement conversions from common error types
impl From<std::io::Error> for CertificateError {
    fn from(err: std::io::Error) -> Self {
        match err.kind() {
            std::io::ErrorKind::NotFound => CertificateError::FileNotFound(err.to_string()),
            std::io::ErrorKind::PermissionDenied => CertificateError::PermissionDenied(err.to_string()),
            _ => CertificateError::FileOperationFailed(err.to_string()),
        }
    }
}

impl From<serde_json::Error> for CertificateError {
    fn from(err: serde_json::Error) -> Self {
        if err.is_syntax() || err.is_data() {
            CertificateError::JsonDeserializationFailed(err.to_string())
        } else {
            CertificateError::JsonSerializationFailed(err.to_string())
        }
    }
}

impl From<openssl::error::ErrorStack> for CertificateError {
    fn from(err: openssl::error::ErrorStack) -> Self {
        CertificateError::CryptographicError(err.to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_error_severity() {
        assert_eq!(CertificateError::SignatureVerificationFailed.severity(), ErrorSeverity::Critical);
        assert_eq!(CertificateError::PdfGenerationFailed("test".to_string()).severity(), ErrorSeverity::Medium);
        assert_eq!(CertificateError::QrCodeGenerationFailed("test".to_string()).severity(), ErrorSeverity::Low);
    }
    
    #[test]
    fn test_error_category() {
        assert_eq!(CertificateError::CryptographicError("test".to_string()).category(), ErrorCategory::Cryptographic);
        assert_eq!(CertificateError::PdfGenerationFailed("test".to_string()).category(), ErrorCategory::PdfGeneration);
        assert_eq!(CertificateError::NetworkError("test".to_string()).category(), ErrorCategory::Network);
    }
    
    #[test]
    fn test_error_recoverability() {
        assert!(CertificateError::NetworkError("test".to_string()).is_recoverable());
        assert!(!CertificateError::SignatureVerificationFailed.is_recoverable());
        assert!(!CertificateError::PermissionDenied("test".to_string()).is_recoverable());
    }
    
    #[test]
    fn test_user_messages() {
        let error = CertificateError::FileNotFound("test.pdf".to_string());
        let message = error.user_message();
        assert!(message.contains("test.pdf"));
        assert!(message.contains("not found"));
    }
    
    #[test]
    fn test_error_conversion() {
        let io_error = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let cert_error: CertificateError = io_error.into();
        assert!(matches!(cert_error, CertificateError::FileNotFound(_)));
    }
}
