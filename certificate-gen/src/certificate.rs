//! Core certificate data structures and functionality

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

use crate::crypto::SignatureInfo;
use crate::error::Result;

/// Main wipe certificate structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WipeCertificate {
    pub data: CertificateData,
    pub version: String,
    pub format_version: u32,
}

/// Signed certificate with cryptographic signature
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SignedCertificate {
    pub certificate: WipeCertificate,
    pub signature_info: SignatureInfo,
    pub signed_at: DateTime<Utc>,
}

/// Core certificate data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CertificateData {
    pub certificate_id: Uuid,
    pub generated_at: DateTime<Utc>,
    pub device_info: DeviceInfo,
    pub wipe_info: WipeInfo,
    pub verification_info: Option<VerificationInfo>,
    pub compliance_info: Option<ComplianceInfo>,
    pub technical_details: Option<HashMap<String, serde_json::Value>>,
    pub organization: Option<crate::OrganizationInfo>,
    pub metadata: HashMap<String, String>,
}

/// Device information in certificate
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceInfo {
    pub path: String,
    pub serial: String,
    pub model: String,
    pub size: u64,
}

/// Wipe operation information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WipeInfo {
    pub algorithm: safe_erase_core::WipeAlgorithm,
    pub started_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub duration: Option<std::time::Duration>,
    pub passes_completed: usize,
    pub verification_passed: Option<bool>,
}

/// Verification information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationInfo {
    pub verification_id: Uuid,
    pub verification_type: safe_erase_core::VerificationType,
    pub samples_tested: usize,
    pub samples_passed: usize,
    pub success_rate: f64,
    pub overall_result: safe_erase_core::VerificationStatus,
}

/// Compliance and standards information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComplianceInfo {
    pub standards_met: Vec<ComplianceStandard>,
    pub security_level: SecurityLevel,
    pub certification_body: Option<String>,
    pub compliance_notes: Vec<String>,
}

/// Individual compliance standard
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComplianceStandard {
    pub name: String,
    pub version: Option<String>,
    pub description: String,
    pub requirements_met: Vec<String>,
    pub compliance_level: ComplianceLevel,
}

/// Security level classification
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SecurityLevel {
    Basic,
    Standard,
    High,
    Maximum,
    Custom,
}

/// Compliance level for standards
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ComplianceLevel {
    FullyCompliant,
    PartiallyCompliant,
    NotCompliant,
    NotApplicable,
}

impl WipeCertificate {
    /// Create a new wipe certificate
    pub fn new(data: CertificateData) -> Self {
        Self {
            data,
            version: env!("CARGO_PKG_VERSION").to_string(),
            format_version: 1,
        }
    }
    
    /// Get certificate ID
    pub fn certificate_id(&self) -> Uuid {
        self.data.certificate_id
    }
    
    /// Get device serial number
    pub fn device_serial(&self) -> &str {
        &self.data.device_info.serial
    }
    
    /// Get wipe algorithm used
    pub fn wipe_algorithm(&self) -> &safe_erase_core::WipeAlgorithm {
        &self.data.wipe_info.algorithm
    }
    
    /// Check if verification was performed and passed
    pub fn is_verification_passed(&self) -> bool {
        self.data.wipe_info.verification_passed.unwrap_or(false)
    }
    
    /// Get compliance standards met
    pub fn compliance_standards(&self) -> Vec<&str> {
        self.data.compliance_info
            .as_ref()
            .map(|ci| ci.standards_met.iter().map(|s| s.name.as_str()).collect())
            .unwrap_or_default()
    }
    
    /// Validate certificate data integrity
    pub fn validate(&self) -> Result<()> {
        // Check required fields
        if self.data.certificate_id.is_nil() {
            return Err(crate::error::CertificateError::InvalidCertificateData(
                "Certificate ID cannot be nil".to_string()
            ));
        }
        
        if self.data.device_info.serial.is_empty() {
            return Err(crate::error::CertificateError::MissingRequiredField(
                "Device serial number".to_string()
            ));
        }
        
        if self.data.device_info.model.is_empty() {
            return Err(crate::error::CertificateError::MissingRequiredField(
                "Device model".to_string()
            ));
        }
        
        // Check timestamps
        if let Some(completed_at) = self.data.wipe_info.completed_at {
            if completed_at < self.data.wipe_info.started_at {
                return Err(crate::error::CertificateError::InvalidTimestamp(
                    "Completion time cannot be before start time".to_string()
                ));
            }
        }
        
        // Check verification consistency
        if let Some(verification_info) = &self.data.verification_info {
            if verification_info.samples_passed > verification_info.samples_tested {
                return Err(crate::error::CertificateError::InvalidCertificateData(
                    "Samples passed cannot exceed samples tested".to_string()
                ));
            }
            
            let calculated_rate = verification_info.samples_passed as f64 / verification_info.samples_tested as f64;
            if (calculated_rate - verification_info.success_rate).abs() > 0.01 {
                return Err(crate::error::CertificateError::InvalidCertificateData(
                    "Success rate does not match sample counts".to_string()
                ));
            }
        }
        
        Ok(())
    }
    
    /// Get a summary of the certificate
    pub fn summary(&self) -> CertificateSummary {
        CertificateSummary {
            certificate_id: self.data.certificate_id,
            device_model: self.data.device_info.model.clone(),
            device_serial: self.data.device_info.serial.clone(),
            algorithm: self.data.wipe_info.algorithm,
            completed_at: self.data.wipe_info.completed_at,
            verification_passed: self.data.wipe_info.verification_passed,
            security_level: self.data.compliance_info
                .as_ref()
                .map(|ci| ci.security_level)
                .unwrap_or(SecurityLevel::Basic),
        }
    }
}

impl SignedCertificate {
    /// Create a new signed certificate
    pub fn new(certificate: WipeCertificate, signature_info: SignatureInfo) -> Self {
        Self {
            certificate,
            signature_info,
            signed_at: Utc::now(),
        }
    }
    
    /// Get certificate ID
    pub fn certificate_id(&self) -> Uuid {
        self.certificate.certificate_id()
    }
    
    /// Get signature information
    pub fn signature_info(&self) -> &SignatureInfo {
        &self.signature_info
    }
    
    /// Get the underlying certificate
    pub fn certificate(&self) -> &WipeCertificate {
        &self.certificate
    }
    
    /// Validate the signed certificate
    pub fn validate(&self) -> Result<()> {
        // Validate the underlying certificate
        self.certificate.validate()?;
        
        // Check signature timestamp
        if self.signed_at < self.certificate.data.generated_at {
            return Err(crate::error::CertificateError::InvalidTimestamp(
                "Signature time cannot be before certificate generation time".to_string()
            ));
        }
        
        Ok(())
    }
}

impl ComplianceInfo {
    /// Create compliance information from wipe algorithm
    pub fn from_algorithm(algorithm: &safe_erase_core::WipeAlgorithm) -> Self {
        let algorithm_info = algorithm.info();
        let mut standards_met = Vec::new();
        let mut compliance_notes = Vec::new();
        
        // Map algorithm to compliance standards
        for standard_name in &algorithm_info.compliance_standards {
            let standard = match standard_name.as_str() {
                "NIST 800-88" => ComplianceStandard {
                    name: "NIST SP 800-88 Rev. 1".to_string(),
                    version: Some("Revision 1".to_string()),
                    description: "Guidelines for Media Sanitization".to_string(),
                    requirements_met: vec![
                        "Clear sanitization method".to_string(),
                        "Cryptographic erase for SSDs".to_string(),
                    ],
                    compliance_level: ComplianceLevel::FullyCompliant,
                },
                "DoD 5220.22-M" => ComplianceStandard {
                    name: "DoD 5220.22-M".to_string(),
                    version: Some("Change 2".to_string()),
                    description: "National Industrial Security Program Operating Manual".to_string(),
                    requirements_met: vec![
                        "Three-pass overwrite".to_string(),
                        "Pattern verification".to_string(),
                    ],
                    compliance_level: ComplianceLevel::FullyCompliant,
                },
                "ATA Standard" => ComplianceStandard {
                    name: "ATA/ATAPI Command Set".to_string(),
                    version: Some("ACS-4".to_string()),
                    description: "Hardware-based secure erase".to_string(),
                    requirements_met: vec![
                        "ATA Secure Erase command".to_string(),
                        "Hardware-level sanitization".to_string(),
                    ],
                    compliance_level: ComplianceLevel::FullyCompliant,
                },
                "NVMe Standard" => ComplianceStandard {
                    name: "NVMe Specification".to_string(),
                    version: Some("1.4".to_string()),
                    description: "NVMe Format with Secure Erase".to_string(),
                    requirements_met: vec![
                        "NVMe Format command".to_string(),
                        "Cryptographic erase".to_string(),
                    ],
                    compliance_level: ComplianceLevel::FullyCompliant,
                },
                _ => ComplianceStandard {
                    name: standard_name.clone(),
                    version: None,
                    description: "Custom or proprietary standard".to_string(),
                    requirements_met: vec!["Algorithm-specific requirements".to_string()],
                    compliance_level: ComplianceLevel::PartiallyCompliant,
                },
            };
            standards_met.push(standard);
        }
        
        // Determine overall security level
        let security_level = match algorithm_info.security_level {
            safe_erase_core::SecurityLevel::Basic => SecurityLevel::Basic,
            safe_erase_core::SecurityLevel::Standard => SecurityLevel::Standard,
            safe_erase_core::SecurityLevel::High => SecurityLevel::High,
            safe_erase_core::SecurityLevel::Maximum => SecurityLevel::Maximum,
        };
        
        // Add algorithm-specific notes
        compliance_notes.push(format!("Algorithm: {}", algorithm_info.name));
        compliance_notes.push(format!("Passes: {}", algorithm_info.passes));
        compliance_notes.push(format!("Security Level: {}", security_level));
        
        Self {
            standards_met,
            security_level,
            certification_body: Some("SafeErase Certification Authority".to_string()),
            compliance_notes,
        }
    }
    
    /// Check if fully compliant with all standards
    pub fn is_fully_compliant(&self) -> bool {
        self.standards_met.iter().all(|s| s.compliance_level == ComplianceLevel::FullyCompliant)
    }
    
    /// Get list of non-compliant standards
    pub fn non_compliant_standards(&self) -> Vec<&ComplianceStandard> {
        self.standards_met
            .iter()
            .filter(|s| s.compliance_level == ComplianceLevel::NotCompliant)
            .collect()
    }
}

/// Certificate summary for quick display
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CertificateSummary {
    pub certificate_id: Uuid,
    pub device_model: String,
    pub device_serial: String,
    pub algorithm: safe_erase_core::WipeAlgorithm,
    pub completed_at: Option<DateTime<Utc>>,
    pub verification_passed: Option<bool>,
    pub security_level: SecurityLevel,
}

impl std::fmt::Display for SecurityLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SecurityLevel::Basic => write!(f, "Basic"),
            SecurityLevel::Standard => write!(f, "Standard"),
            SecurityLevel::High => write!(f, "High"),
            SecurityLevel::Maximum => write!(f, "Maximum"),
            SecurityLevel::Custom => write!(f, "Custom"),
        }
    }
}

impl std::fmt::Display for ComplianceLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ComplianceLevel::FullyCompliant => write!(f, "Fully Compliant"),
            ComplianceLevel::PartiallyCompliant => write!(f, "Partially Compliant"),
            ComplianceLevel::NotCompliant => write!(f, "Not Compliant"),
            ComplianceLevel::NotApplicable => write!(f, "Not Applicable"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;
    
    fn create_test_certificate_data() -> CertificateData {
        CertificateData {
            certificate_id: Uuid::new_v4(),
            generated_at: Utc::now(),
            device_info: DeviceInfo {
                path: "/dev/sda".to_string(),
                serial: "TEST123456".to_string(),
                model: "Test SSD".to_string(),
                size: 1000000000,
            },
            wipe_info: WipeInfo {
                algorithm: safe_erase_core::WipeAlgorithm::NIST80088,
                started_at: Utc::now(),
                completed_at: Some(Utc::now()),
                duration: Some(Duration::from_secs(3600)),
                passes_completed: 1,
                verification_passed: Some(true),
            },
            verification_info: None,
            compliance_info: None,
            technical_details: None,
            organization: None,
            metadata: HashMap::new(),
        }
    }
    
    #[test]
    fn test_certificate_creation() {
        let data = create_test_certificate_data();
        let certificate = WipeCertificate::new(data);
        
        assert_eq!(certificate.format_version, 1);
        assert!(!certificate.certificate_id().is_nil());
    }
    
    #[test]
    fn test_certificate_validation() {
        let data = create_test_certificate_data();
        let certificate = WipeCertificate::new(data);
        
        assert!(certificate.validate().is_ok());
    }
    
    #[test]
    fn test_compliance_info_from_algorithm() {
        let algorithm = safe_erase_core::WipeAlgorithm::NIST80088;
        let compliance = ComplianceInfo::from_algorithm(&algorithm);
        
        assert!(!compliance.standards_met.is_empty());
        assert_eq!(compliance.security_level, SecurityLevel::Standard);
        assert!(compliance.is_fully_compliant());
    }
    
    #[test]
    fn test_certificate_summary() {
        let data = create_test_certificate_data();
        let certificate = WipeCertificate::new(data);
        let summary = certificate.summary();
        
        assert_eq!(summary.device_serial, "TEST123456");
        assert_eq!(summary.device_model, "Test SSD");
        assert_eq!(summary.verification_passed, Some(true));
    }
}
