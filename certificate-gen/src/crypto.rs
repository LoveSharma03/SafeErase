//! Cryptographic operations for certificate signing and verification

use std::path::Path;
use serde::{Deserialize, Serialize};
use openssl::{
    pkey::{PKey, Private, Public},
    rsa::Rsa,
    sign::{Signer, Verifier},
    hash::MessageDigest,
    base64,
};
use sha2::{Sha256, Digest};
use chrono::{DateTime, Utc};
use uuid::Uuid;

use crate::certificate::{WipeCertificate, SignedCertificate};
use crate::error::{CertificateError, Result};

/// Certificate signer for creating cryptographic signatures
#[derive(Debug)]
pub struct CertificateSigner {
    private_key: PKey<Private>,
    public_key: PKey<Public>,
    key_id: String,
}

/// Signature information attached to certificates
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SignatureInfo {
    pub signature: String,
    pub algorithm: SignatureAlgorithm,
    pub key_id: String,
    pub timestamp: DateTime<Utc>,
    pub certificate_hash: String,
    pub signature_version: u32,
}

/// Supported signature algorithms
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SignatureAlgorithm {
    RSA2048SHA256,
    RSA4096SHA256,
    ECDSAP256SHA256,
    ECDSAP384SHA384,
}

/// Key pair information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct KeyPairInfo {
    pub key_id: String,
    pub algorithm: SignatureAlgorithm,
    pub created_at: DateTime<Utc>,
    pub public_key_pem: String,
    pub fingerprint: String,
}

impl CertificateSigner {
    /// Create a new certificate signer with generated keys
    pub fn new() -> Result<Self> {
        let (private_key, public_key) = Self::generate_key_pair(SignatureAlgorithm::RSA2048SHA256)?;
        let key_id = Self::generate_key_id(&public_key)?;
        
        Ok(Self {
            private_key,
            public_key,
            key_id,
        })
    }
    
    /// Create a certificate signer from existing key files
    pub fn from_files<P: AsRef<Path>>(private_key_path: P, public_key_path: P) -> Result<Self> {
        let private_key_pem = std::fs::read_to_string(private_key_path)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        let public_key_pem = std::fs::read_to_string(public_key_path)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        let private_key = PKey::private_key_from_pem(private_key_pem.as_bytes())
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let public_key = PKey::public_key_from_pem(public_key_pem.as_bytes())
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let key_id = Self::generate_key_id(&public_key)?;
        
        Ok(Self {
            private_key,
            public_key,
            key_id,
        })
    }
    
    /// Generate a new key pair
    pub fn generate_key_pair(algorithm: SignatureAlgorithm) -> Result<(PKey<Private>, PKey<Public>)> {
        match algorithm {
            SignatureAlgorithm::RSA2048SHA256 => {
                let rsa = Rsa::generate(2048)
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                let private_key = PKey::from_rsa(rsa.clone())
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                let public_key = PKey::from_rsa(rsa)
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                Ok((private_key, public_key))
            }
            SignatureAlgorithm::RSA4096SHA256 => {
                let rsa = Rsa::generate(4096)
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                let private_key = PKey::from_rsa(rsa.clone())
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                let public_key = PKey::from_rsa(rsa)
                    .map_err(|e| CertificateError::KeyGenerationFailed(e.to_string()))?;
                
                Ok((private_key, public_key))
            }
            _ => Err(CertificateError::NotSupported(format!("Algorithm {:?} not yet implemented", algorithm))),
        }
    }
    
    /// Generate a unique key ID from the public key
    fn generate_key_id(public_key: &PKey<Public>) -> Result<String> {
        let public_key_der = public_key.public_key_to_der()
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let mut hasher = Sha256::new();
        hasher.update(&public_key_der);
        let hash = hasher.finalize();
        
        Ok(hex::encode(&hash[..8])) // Use first 8 bytes as key ID
    }
    
    /// Sign a certificate
    pub async fn sign_certificate(&self, certificate: &WipeCertificate) -> Result<SignedCertificate> {
        // Validate certificate before signing
        certificate.validate()?;
        
        // Serialize certificate for signing
        let certificate_json = serde_json::to_string(certificate)
            .map_err(|e| CertificateError::JsonSerializationFailed(e.to_string()))?;
        
        // Calculate certificate hash
        let mut hasher = Sha256::new();
        hasher.update(certificate_json.as_bytes());
        let certificate_hash = hex::encode(hasher.finalize());
        
        // Create signature
        let signature = self.create_signature(&certificate_json)?;
        
        let signature_info = SignatureInfo {
            signature,
            algorithm: SignatureAlgorithm::RSA2048SHA256, // Default for now
            key_id: self.key_id.clone(),
            timestamp: Utc::now(),
            certificate_hash,
            signature_version: 1,
        };
        
        Ok(SignedCertificate::new(certificate.clone(), signature_info))
    }
    
    /// Create a cryptographic signature
    fn create_signature(&self, data: &str) -> Result<String> {
        let mut signer = Signer::new(MessageDigest::sha256(), &self.private_key)
            .map_err(|e| CertificateError::SigningFailed(e.to_string()))?;
        
        signer.update(data.as_bytes())
            .map_err(|e| CertificateError::SigningFailed(e.to_string()))?;
        
        let signature = signer.sign_to_vec()
            .map_err(|e| CertificateError::SigningFailed(e.to_string()))?;
        
        Ok(base64::encode_block(&signature))
    }
    
    /// Get public key information
    pub fn get_key_info(&self) -> Result<KeyPairInfo> {
        let public_key_pem = self.public_key.public_key_to_pem()
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let fingerprint = self.calculate_fingerprint()?;
        
        Ok(KeyPairInfo {
            key_id: self.key_id.clone(),
            algorithm: SignatureAlgorithm::RSA2048SHA256,
            created_at: Utc::now(),
            public_key_pem: String::from_utf8(public_key_pem)
                .map_err(|e| CertificateError::CryptographicError(e.to_string()))?,
            fingerprint,
        })
    }
    
    /// Calculate public key fingerprint
    fn calculate_fingerprint(&self) -> Result<String> {
        let public_key_der = self.public_key.public_key_to_der()
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let mut hasher = Sha256::new();
        hasher.update(&public_key_der);
        let hash = hasher.finalize();
        
        // Format as colon-separated hex
        let hex_string = hex::encode(hash);
        let fingerprint = hex_string
            .chars()
            .collect::<Vec<char>>()
            .chunks(2)
            .map(|chunk| chunk.iter().collect::<String>())
            .collect::<Vec<String>>()
            .join(":");
        
        Ok(fingerprint.to_uppercase())
    }
    
    /// Export keys to files
    pub fn export_keys<P: AsRef<Path>>(&self, private_key_path: P, public_key_path: P) -> Result<()> {
        let private_key_pem = self.private_key.private_key_to_pem_pkcs8()
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let public_key_pem = self.public_key.public_key_to_pem()
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        std::fs::write(private_key_path, private_key_pem)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        std::fs::write(public_key_path, public_key_pem)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        Ok(())
    }
}

/// Certificate verifier for validating signatures
#[derive(Debug)]
pub struct CertificateVerifier {
    trusted_keys: std::collections::HashMap<String, PKey<Public>>,
}

impl CertificateVerifier {
    /// Create a new certificate verifier
    pub fn new() -> Result<Self> {
        Ok(Self {
            trusted_keys: std::collections::HashMap::new(),
        })
    }
    
    /// Add a trusted public key
    pub fn add_trusted_key(&mut self, key_id: String, public_key: PKey<Public>) {
        self.trusted_keys.insert(key_id, public_key);
    }
    
    /// Load trusted keys from a directory
    pub fn load_trusted_keys<P: AsRef<Path>>(&mut self, keys_dir: P) -> Result<usize> {
        let mut loaded_count = 0;
        
        let entries = std::fs::read_dir(keys_dir)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
            let path = entry.path();
            
            if path.extension().and_then(|s| s.to_str()) == Some("pem") {
                match self.load_public_key_file(&path) {
                    Ok((key_id, public_key)) => {
                        self.trusted_keys.insert(key_id, public_key);
                        loaded_count += 1;
                    }
                    Err(e) => {
                        eprintln!("Warning: Failed to load key from {:?}: {}", path, e);
                    }
                }
            }
        }
        
        Ok(loaded_count)
    }
    
    /// Load a public key from file
    fn load_public_key_file<P: AsRef<Path>>(&self, path: P) -> Result<(String, PKey<Public>)> {
        let pem_data = std::fs::read_to_string(path)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        let public_key = PKey::public_key_from_pem(pem_data.as_bytes())
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let key_id = CertificateSigner::generate_key_id(&public_key)?;
        
        Ok((key_id, public_key))
    }
    
    /// Verify a signed certificate
    pub async fn verify_certificate(&self, signed_certificate: &SignedCertificate) -> Result<bool> {
        // Validate the certificate structure
        signed_certificate.validate()?;
        
        // Get the public key for verification
        let public_key = self.trusted_keys.get(&signed_certificate.signature_info.key_id)
            .ok_or_else(|| CertificateError::SignatureVerificationFailed)?;
        
        // Serialize the certificate for verification
        let certificate_json = serde_json::to_string(&signed_certificate.certificate)
            .map_err(|e| CertificateError::JsonSerializationFailed(e.to_string()))?;
        
        // Verify the certificate hash
        let mut hasher = Sha256::new();
        hasher.update(certificate_json.as_bytes());
        let calculated_hash = hex::encode(hasher.finalize());
        
        if calculated_hash != signed_certificate.signature_info.certificate_hash {
            return Ok(false);
        }
        
        // Verify the signature
        self.verify_signature(&certificate_json, &signed_certificate.signature_info.signature, public_key)
    }
    
    /// Verify a cryptographic signature
    fn verify_signature(&self, data: &str, signature: &str, public_key: &PKey<Public>) -> Result<bool> {
        let signature_bytes = base64::decode_block(signature)
            .map_err(|e| CertificateError::CryptographicError(e.to_string()))?;
        
        let mut verifier = Verifier::new(MessageDigest::sha256(), public_key)
            .map_err(|e| CertificateError::SignatureVerificationFailed)?;
        
        verifier.update(data.as_bytes())
            .map_err(|e| CertificateError::SignatureVerificationFailed)?;
        
        let is_valid = verifier.verify(&signature_bytes)
            .map_err(|e| CertificateError::SignatureVerificationFailed)?;
        
        Ok(is_valid)
    }
    
    /// Verify a certificate from file
    pub async fn verify_certificate_file<P: AsRef<Path>>(&self, certificate_path: P) -> Result<bool> {
        let certificate_json = std::fs::read_to_string(certificate_path)
            .map_err(|e| CertificateError::FileOperationFailed(e.to_string()))?;
        
        let signed_certificate: SignedCertificate = serde_json::from_str(&certificate_json)
            .map_err(|e| CertificateError::JsonDeserializationFailed(e.to_string()))?;
        
        self.verify_certificate(&signed_certificate).await
    }
}

impl std::fmt::Display for SignatureAlgorithm {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SignatureAlgorithm::RSA2048SHA256 => write!(f, "RSA-2048 with SHA-256"),
            SignatureAlgorithm::RSA4096SHA256 => write!(f, "RSA-4096 with SHA-256"),
            SignatureAlgorithm::ECDSAP256SHA256 => write!(f, "ECDSA P-256 with SHA-256"),
            SignatureAlgorithm::ECDSAP384SHA384 => write!(f, "ECDSA P-384 with SHA-384"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::certificate::{CertificateData, DeviceInfo, WipeInfo};
    use std::collections::HashMap;
    
    fn create_test_certificate() -> WipeCertificate {
        let data = CertificateData {
            certificate_id: uuid::Uuid::new_v4(),
            generated_at: Utc::now(),
            device_info: DeviceInfo {
                path: "/dev/sda".to_string(),
                serial: "TEST123".to_string(),
                model: "Test Drive".to_string(),
                size: 1000000000,
            },
            wipe_info: WipeInfo {
                algorithm: safe_erase_core::WipeAlgorithm::NIST80088,
                started_at: Utc::now(),
                completed_at: Some(Utc::now()),
                duration: Some(std::time::Duration::from_secs(3600)),
                passes_completed: 1,
                verification_passed: Some(true),
            },
            verification_info: None,
            compliance_info: None,
            technical_details: None,
            organization: None,
            metadata: HashMap::new(),
        };
        
        WipeCertificate::new(data)
    }
    
    #[tokio::test]
    async fn test_certificate_signing_and_verification() {
        let signer = CertificateSigner::new().unwrap();
        let certificate = create_test_certificate();
        
        // Sign the certificate
        let signed_certificate = signer.sign_certificate(&certificate).await.unwrap();
        
        // Create verifier and add the public key
        let mut verifier = CertificateVerifier::new().unwrap();
        verifier.add_trusted_key(signer.key_id.clone(), signer.public_key.clone());
        
        // Verify the certificate
        let is_valid = verifier.verify_certificate(&signed_certificate).await.unwrap();
        assert!(is_valid);
    }
    
    #[test]
    fn test_key_generation() {
        let result = CertificateSigner::generate_key_pair(SignatureAlgorithm::RSA2048SHA256);
        assert!(result.is_ok());
        
        let (private_key, public_key) = result.unwrap();
        assert_eq!(private_key.bits(), 2048);
        assert_eq!(public_key.bits(), 2048);
    }
    
    #[test]
    fn test_key_id_generation() {
        let signer = CertificateSigner::new().unwrap();
        assert!(!signer.key_id.is_empty());
        assert_eq!(signer.key_id.len(), 16); // 8 bytes as hex = 16 characters
    }
    
    #[test]
    fn test_signature_algorithm_display() {
        assert_eq!(SignatureAlgorithm::RSA2048SHA256.to_string(), "RSA-2048 with SHA-256");
        assert_eq!(SignatureAlgorithm::RSA4096SHA256.to_string(), "RSA-4096 with SHA-256");
    }
}
