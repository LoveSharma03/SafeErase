//! SafeErase Certificate Generation System
//! 
//! This crate provides tamper-proof certificate generation for SafeErase wipe operations,
//! supporting both PDF and JSON formats with cryptographic verification using
//! OpenSSL and JSON Web Signatures.

pub mod certificate;
pub mod pdf;
pub mod json;
pub mod crypto;
pub mod templates;
pub mod verification;
pub mod error;

use std::path::Path;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

pub use certificate::{WipeCertificate, CertificateData, ComplianceInfo};
pub use pdf::PdfGenerator;
pub use json::JsonGenerator;
pub use crypto::{CertificateSigner, SignatureInfo};
pub use verification::CertificateVerifier;
pub use error::{CertificateError, Result};

/// Main certificate generation engine
#[derive(Debug)]
pub struct CertificateEngine {
    signer: CertificateSigner,
    pdf_generator: PdfGenerator,
    json_generator: JsonGenerator,
    verifier: CertificateVerifier,
}

/// Certificate generation options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CertificateOptions {
    /// Include QR code for verification
    pub include_qr_code: bool,
    /// Include detailed technical information
    pub include_technical_details: bool,
    /// Include compliance information
    pub include_compliance_info: bool,
    /// Custom certificate template
    pub template_name: Option<String>,
    /// Organization information
    pub organization: Option<OrganizationInfo>,
    /// Additional metadata
    pub metadata: std::collections::HashMap<String, String>,
}

/// Organization information for certificates
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OrganizationInfo {
    pub name: String,
    pub address: String,
    pub contact_email: String,
    pub contact_phone: Option<String>,
    pub website: Option<String>,
    pub logo_path: Option<String>,
    pub certification_authority: Option<String>,
}

/// Certificate output formats
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CertificateFormat {
    PDF,
    JSON,
    Both,
}

/// Certificate generation result
#[derive(Debug, Clone)]
pub struct CertificateResult {
    pub certificate_id: Uuid,
    pub pdf_path: Option<String>,
    pub json_path: Option<String>,
    pub signature_info: SignatureInfo,
    pub generated_at: DateTime<Utc>,
    pub verification_url: Option<String>,
    pub qr_code_data: Option<String>,
}

impl CertificateEngine {
    /// Create a new certificate engine
    pub fn new() -> Result<Self> {
        let signer = CertificateSigner::new()?;
        let pdf_generator = PdfGenerator::new()?;
        let json_generator = JsonGenerator::new()?;
        let verifier = CertificateVerifier::new()?;
        
        Ok(Self {
            signer,
            pdf_generator,
            json_generator,
            verifier,
        })
    }
    
    /// Create a new certificate engine with custom signing key
    pub fn with_signing_key<P: AsRef<Path>>(private_key_path: P, public_key_path: P) -> Result<Self> {
        let signer = CertificateSigner::from_files(private_key_path, public_key_path)?;
        let pdf_generator = PdfGenerator::new()?;
        let json_generator = JsonGenerator::new()?;
        let verifier = CertificateVerifier::new()?;
        
        Ok(Self {
            signer,
            pdf_generator,
            json_generator,
            verifier,
        })
    }
    
    /// Generate a wipe certificate
    pub async fn generate_certificate(
        &self,
        wipe_result: &safe_erase_core::WipeResult,
        verification_result: Option<&safe_erase_core::VerificationResult>,
        format: CertificateFormat,
        options: CertificateOptions,
        output_dir: &Path,
    ) -> Result<CertificateResult> {
        // Create certificate data
        let certificate_data = self.create_certificate_data(
            wipe_result,
            verification_result,
            &options,
        ).await?;
        
        // Create the certificate
        let certificate = WipeCertificate::new(certificate_data);
        
        // Sign the certificate
        let signed_certificate = self.signer.sign_certificate(&certificate).await?;
        
        // Generate outputs based on format
        let mut pdf_path = None;
        let mut json_path = None;
        
        match format {
            CertificateFormat::PDF => {
                pdf_path = Some(self.generate_pdf(&signed_certificate, &options, output_dir).await?);
            }
            CertificateFormat::JSON => {
                json_path = Some(self.generate_json(&signed_certificate, output_dir).await?);
            }
            CertificateFormat::Both => {
                pdf_path = Some(self.generate_pdf(&signed_certificate, &options, output_dir).await?);
                json_path = Some(self.generate_json(&signed_certificate, output_dir).await?);
            }
        }
        
        // Generate QR code data if requested
        let qr_code_data = if options.include_qr_code {
            Some(self.generate_qr_code_data(&signed_certificate)?)
        } else {
            None
        };
        
        // Generate verification URL
        let verification_url = self.generate_verification_url(&signed_certificate);
        
        Ok(CertificateResult {
            certificate_id: signed_certificate.certificate_id(),
            pdf_path,
            json_path,
            signature_info: signed_certificate.signature_info().clone(),
            generated_at: Utc::now(),
            verification_url,
            qr_code_data,
        })
    }
    
    /// Verify a certificate
    pub async fn verify_certificate<P: AsRef<Path>>(&self, certificate_path: P) -> Result<bool> {
        self.verifier.verify_certificate_file(certificate_path).await
    }
    
    /// Create certificate data from wipe and verification results
    async fn create_certificate_data(
        &self,
        wipe_result: &safe_erase_core::WipeResult,
        verification_result: Option<&safe_erase_core::VerificationResult>,
        options: &CertificateOptions,
    ) -> Result<CertificateData> {
        let certificate_id = Uuid::new_v4();
        let generated_at = Utc::now();
        
        // Create compliance information
        let compliance_info = if options.include_compliance_info {
            Some(ComplianceInfo::from_algorithm(&wipe_result.algorithm))
        } else {
            None
        };
        
        // Create technical details
        let technical_details = if options.include_technical_details {
            Some(self.create_technical_details(wipe_result, verification_result))
        } else {
            None
        };
        
        Ok(CertificateData {
            certificate_id,
            generated_at,
            device_info: certificate::DeviceInfo {
                path: wipe_result.device_path.clone(),
                serial: wipe_result.device_serial.clone(),
                model: wipe_result.device_model.clone(),
                size: wipe_result.bytes_wiped,
            },
            wipe_info: certificate::WipeInfo {
                algorithm: wipe_result.algorithm,
                started_at: wipe_result.started_at,
                completed_at: wipe_result.completed_at,
                duration: wipe_result.duration,
                passes_completed: wipe_result.passes_completed,
                verification_passed: wipe_result.verification_passed,
            },
            verification_info: verification_result.map(|vr| certificate::VerificationInfo {
                verification_id: vr.verification_id,
                verification_type: vr.verification_type,
                samples_tested: vr.samples_tested,
                samples_passed: vr.samples_passed,
                success_rate: vr.success_rate,
                overall_result: vr.overall_result,
            }),
            compliance_info,
            technical_details,
            organization: options.organization.clone(),
            metadata: options.metadata.clone(),
        })
    }
    
    /// Create technical details section
    fn create_technical_details(
        &self,
        wipe_result: &safe_erase_core::WipeResult,
        verification_result: Option<&safe_erase_core::VerificationResult>,
    ) -> std::collections::HashMap<String, serde_json::Value> {
        let mut details = std::collections::HashMap::new();
        
        // Add performance statistics
        details.insert("performance".to_string(), serde_json::to_value(&wipe_result.performance_stats).unwrap());
        
        // Add HPA/DCO information
        details.insert("hpa_detected".to_string(), serde_json::Value::Bool(wipe_result.hpa_detected));
        details.insert("hpa_cleared".to_string(), serde_json::Value::Bool(wipe_result.hpa_cleared));
        details.insert("dco_detected".to_string(), serde_json::Value::Bool(wipe_result.dco_detected));
        details.insert("dco_cleared".to_string(), serde_json::Value::Bool(wipe_result.dco_cleared));
        
        // Add verification details if available
        if let Some(verification) = verification_result {
            details.insert("entropy_analysis".to_string(), serde_json::to_value(&verification.entropy_analysis).unwrap());
            details.insert("pattern_analysis".to_string(), serde_json::to_value(&verification.pattern_analysis).unwrap());
        }
        
        details
    }
    
    /// Generate PDF certificate
    async fn generate_pdf(
        &self,
        certificate: &certificate::SignedCertificate,
        options: &CertificateOptions,
        output_dir: &Path,
    ) -> Result<String> {
        let filename = format!("wipe_certificate_{}.pdf", certificate.certificate_id());
        let output_path = output_dir.join(&filename);
        
        self.pdf_generator.generate_certificate(certificate, options, &output_path).await?;
        
        Ok(output_path.to_string_lossy().to_string())
    }
    
    /// Generate JSON certificate
    async fn generate_json(
        &self,
        certificate: &certificate::SignedCertificate,
        output_dir: &Path,
    ) -> Result<String> {
        let filename = format!("wipe_certificate_{}.json", certificate.certificate_id());
        let output_path = output_dir.join(&filename);
        
        self.json_generator.generate_certificate(certificate, &output_path).await?;
        
        Ok(output_path.to_string_lossy().to_string())
    }
    
    /// Generate QR code data for certificate verification
    fn generate_qr_code_data(&self, certificate: &certificate::SignedCertificate) -> Result<String> {
        // Create verification data
        let verification_data = serde_json::json!({
            "certificate_id": certificate.certificate_id(),
            "signature": certificate.signature_info().signature,
            "verification_url": self.generate_verification_url(certificate)
        });
        
        Ok(verification_data.to_string())
    }
    
    /// Generate verification URL for the certificate
    fn generate_verification_url(&self, certificate: &certificate::SignedCertificate) -> Option<String> {
        // This would typically point to a web service for certificate verification
        Some(format!("https://verify.safeerase.com/certificate/{}", certificate.certificate_id()))
    }
}

impl Default for CertificateOptions {
    fn default() -> Self {
        Self {
            include_qr_code: true,
            include_technical_details: true,
            include_compliance_info: true,
            template_name: None,
            organization: None,
            metadata: std::collections::HashMap::new(),
        }
    }
}

impl std::fmt::Display for CertificateFormat {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            CertificateFormat::PDF => write!(f, "PDF"),
            CertificateFormat::JSON => write!(f, "JSON"),
            CertificateFormat::Both => write!(f, "PDF and JSON"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_certificate_options_default() {
        let options = CertificateOptions::default();
        assert!(options.include_qr_code);
        assert!(options.include_technical_details);
        assert!(options.include_compliance_info);
        assert!(options.template_name.is_none());
    }
    
    #[test]
    fn test_certificate_format_display() {
        assert_eq!(CertificateFormat::PDF.to_string(), "PDF");
        assert_eq!(CertificateFormat::JSON.to_string(), "JSON");
        assert_eq!(CertificateFormat::Both.to_string(), "PDF and JSON");
    }
}
