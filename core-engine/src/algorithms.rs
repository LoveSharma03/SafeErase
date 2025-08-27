//! Secure wiping algorithms for SafeErase

use serde::{Deserialize, Serialize};
use rand::{Rng, SeedableRng};
use rand::rngs::ChaCha20Rng;
use sha2::{Sha256, Digest};

/// Supported wiping algorithms
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum WipeAlgorithm {
    /// NIST 800-88 - Single pass with cryptographic erase for SSDs
    NIST80088,
    /// DoD 5220.22-M - Three-pass overwrite pattern
    DoD522022M,
    /// Gutmann - 35-pass algorithm for maximum security
    Gutmann,
    /// Random - Cryptographically secure random data
    Random,
    /// Zero Fill - Single pass with zeros
    ZeroFill,
    /// One Fill - Single pass with ones
    OneFill,
    /// ATA Secure Erase - Hardware-level secure erase
    ATASecureErase,
    /// NVMe Format - NVMe secure format
    NVMeFormat,
    /// Custom pattern
    Custom(Vec<WipePattern>),
}

/// Individual wipe pattern for a single pass
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum WipePattern {
    /// Fill with zeros
    Zeros,
    /// Fill with ones (0xFF)
    Ones,
    /// Fill with specific byte value
    Fixed(u8),
    /// Fill with cryptographically secure random data
    Random,
    /// Fill with pseudorandom data using a seed
    PseudoRandom(u64),
    /// Complement of previous pass
    Complement,
    /// Specific pattern (repeating)
    Pattern(Vec<u8>),
}

/// Wipe algorithm metadata
#[derive(Debug, Clone)]
pub struct AlgorithmInfo {
    pub name: String,
    pub description: String,
    pub passes: usize,
    pub security_level: SecurityLevel,
    pub compliance_standards: Vec<String>,
    pub estimated_time_factor: f64, // Relative to single pass
}

/// Security level classification
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum SecurityLevel {
    Basic,
    Standard,
    High,
    Maximum,
}

impl WipeAlgorithm {
    /// Get algorithm information
    pub fn info(&self) -> AlgorithmInfo {
        match self {
            WipeAlgorithm::NIST80088 => AlgorithmInfo {
                name: "NIST 800-88".to_string(),
                description: "NIST Special Publication 800-88 - Single pass with verification".to_string(),
                passes: 1,
                security_level: SecurityLevel::Standard,
                compliance_standards: vec!["NIST 800-88".to_string()],
                estimated_time_factor: 1.0,
            },
            WipeAlgorithm::DoD522022M => AlgorithmInfo {
                name: "DoD 5220.22-M".to_string(),
                description: "US Department of Defense - Three-pass overwrite".to_string(),
                passes: 3,
                security_level: SecurityLevel::High,
                compliance_standards: vec!["DoD 5220.22-M".to_string()],
                estimated_time_factor: 3.0,
            },
            WipeAlgorithm::Gutmann => AlgorithmInfo {
                name: "Gutmann".to_string(),
                description: "Peter Gutmann's 35-pass algorithm for maximum security".to_string(),
                passes: 35,
                security_level: SecurityLevel::Maximum,
                compliance_standards: vec!["Academic Research".to_string()],
                estimated_time_factor: 35.0,
            },
            WipeAlgorithm::Random => AlgorithmInfo {
                name: "Random".to_string(),
                description: "Single pass with cryptographically secure random data".to_string(),
                passes: 1,
                security_level: SecurityLevel::Standard,
                compliance_standards: vec!["General Purpose".to_string()],
                estimated_time_factor: 1.0,
            },
            WipeAlgorithm::ZeroFill => AlgorithmInfo {
                name: "Zero Fill".to_string(),
                description: "Single pass overwrite with zeros".to_string(),
                passes: 1,
                security_level: SecurityLevel::Basic,
                compliance_standards: vec!["Basic Sanitization".to_string()],
                estimated_time_factor: 0.8,
            },
            WipeAlgorithm::OneFill => AlgorithmInfo {
                name: "One Fill".to_string(),
                description: "Single pass overwrite with ones (0xFF)".to_string(),
                passes: 1,
                security_level: SecurityLevel::Basic,
                compliance_standards: vec!["Basic Sanitization".to_string()],
                estimated_time_factor: 0.8,
            },
            WipeAlgorithm::ATASecureErase => AlgorithmInfo {
                name: "ATA Secure Erase".to_string(),
                description: "Hardware-level secure erase using ATA commands".to_string(),
                passes: 1,
                security_level: SecurityLevel::High,
                compliance_standards: vec!["ATA Standard".to_string()],
                estimated_time_factor: 0.5,
            },
            WipeAlgorithm::NVMeFormat => AlgorithmInfo {
                name: "NVMe Format".to_string(),
                description: "NVMe secure format with cryptographic erase".to_string(),
                passes: 1,
                security_level: SecurityLevel::High,
                compliance_standards: vec!["NVMe Standard".to_string()],
                estimated_time_factor: 0.3,
            },
            WipeAlgorithm::Custom(patterns) => AlgorithmInfo {
                name: "Custom".to_string(),
                description: "User-defined wipe pattern".to_string(),
                passes: patterns.len(),
                security_level: SecurityLevel::Standard,
                compliance_standards: vec!["Custom".to_string()],
                estimated_time_factor: patterns.len() as f64,
            },
        }
    }
    
    /// Get the wipe patterns for this algorithm
    pub fn patterns(&self) -> Vec<WipePattern> {
        match self {
            WipeAlgorithm::NIST80088 => vec![WipePattern::Random],
            WipeAlgorithm::DoD522022M => vec![
                WipePattern::Zeros,
                WipePattern::Ones,
                WipePattern::Random,
            ],
            WipeAlgorithm::Gutmann => Self::gutmann_patterns(),
            WipeAlgorithm::Random => vec![WipePattern::Random],
            WipeAlgorithm::ZeroFill => vec![WipePattern::Zeros],
            WipeAlgorithm::OneFill => vec![WipePattern::Ones],
            WipeAlgorithm::ATASecureErase => vec![], // Hardware command, no patterns
            WipeAlgorithm::NVMeFormat => vec![], // Hardware command, no patterns
            WipeAlgorithm::Custom(patterns) => patterns.clone(),
        }
    }
    
    /// Check if this algorithm uses hardware commands
    pub fn is_hardware_based(&self) -> bool {
        matches!(self, WipeAlgorithm::ATASecureErase | WipeAlgorithm::NVMeFormat)
    }
    
    /// Get recommended algorithms for different device types
    pub fn recommended_for_ssd() -> Vec<WipeAlgorithm> {
        vec![
            WipeAlgorithm::ATASecureErase,
            WipeAlgorithm::NIST80088,
            WipeAlgorithm::Random,
        ]
    }
    
    pub fn recommended_for_hdd() -> Vec<WipeAlgorithm> {
        vec![
            WipeAlgorithm::DoD522022M,
            WipeAlgorithm::NIST80088,
            WipeAlgorithm::Gutmann,
        ]
    }
    
    pub fn recommended_for_nvme() -> Vec<WipeAlgorithm> {
        vec![
            WipeAlgorithm::NVMeFormat,
            WipeAlgorithm::NIST80088,
            WipeAlgorithm::Random,
        ]
    }
    
    /// Generate the Gutmann 35-pass pattern
    fn gutmann_patterns() -> Vec<WipePattern> {
        vec![
            // Random passes
            WipePattern::Random,
            WipePattern::Random,
            WipePattern::Random,
            WipePattern::Random,
            // Specific patterns for different encoding schemes
            WipePattern::Pattern(vec![0x55, 0x55, 0x55]),
            WipePattern::Pattern(vec![0xAA, 0xAA, 0xAA]),
            WipePattern::Pattern(vec![0x92, 0x49, 0x24]),
            WipePattern::Pattern(vec![0x49, 0x24, 0x92]),
            WipePattern::Pattern(vec![0x24, 0x92, 0x49]),
            WipePattern::Zeros,
            WipePattern::Pattern(vec![0x11, 0x11, 0x11]),
            WipePattern::Pattern(vec![0x22, 0x22, 0x22]),
            WipePattern::Pattern(vec![0x33, 0x33, 0x33]),
            WipePattern::Pattern(vec![0x44, 0x44, 0x44]),
            WipePattern::Pattern(vec![0x55, 0x55, 0x55]),
            WipePattern::Pattern(vec![0x66, 0x66, 0x66]),
            WipePattern::Pattern(vec![0x77, 0x77, 0x77]),
            WipePattern::Pattern(vec![0x88, 0x88, 0x88]),
            WipePattern::Pattern(vec![0x99, 0x99, 0x99]),
            WipePattern::Pattern(vec![0xAA, 0xAA, 0xAA]),
            WipePattern::Pattern(vec![0xBB, 0xBB, 0xBB]),
            WipePattern::Pattern(vec![0xCC, 0xCC, 0xCC]),
            WipePattern::Pattern(vec![0xDD, 0xDD, 0xDD]),
            WipePattern::Pattern(vec![0xEE, 0xEE, 0xEE]),
            WipePattern::Ones,
            WipePattern::Pattern(vec![0x92, 0x49, 0x24]),
            WipePattern::Pattern(vec![0x49, 0x24, 0x92]),
            WipePattern::Pattern(vec![0x24, 0x92, 0x49]),
            WipePattern::Pattern(vec![0x6D, 0xB6, 0xDB]),
            WipePattern::Pattern(vec![0xB6, 0xDB, 0x6D]),
            WipePattern::Pattern(vec![0xDB, 0x6D, 0xB6]),
            // Final random passes
            WipePattern::Random,
            WipePattern::Random,
            WipePattern::Random,
            WipePattern::Random,
        ]
    }
}

impl WipePattern {
    /// Generate data for this pattern
    pub fn generate_data(&self, size: usize, previous_data: Option<&[u8]>) -> Vec<u8> {
        match self {
            WipePattern::Zeros => vec![0u8; size],
            WipePattern::Ones => vec![0xFFu8; size],
            WipePattern::Fixed(byte) => vec![*byte; size],
            WipePattern::Random => {
                let mut rng = ChaCha20Rng::from_entropy();
                (0..size).map(|_| rng.gen()).collect()
            }
            WipePattern::PseudoRandom(seed) => {
                let mut rng = ChaCha20Rng::seed_from_u64(*seed);
                (0..size).map(|_| rng.gen()).collect()
            }
            WipePattern::Complement => {
                if let Some(prev) = previous_data {
                    prev.iter().map(|&b| !b).collect()
                } else {
                    vec![0xFFu8; size] // Default to ones if no previous data
                }
            }
            WipePattern::Pattern(pattern) => {
                let mut data = Vec::with_capacity(size);
                for i in 0..size {
                    data.push(pattern[i % pattern.len()]);
                }
                data
            }
        }
    }
    
    /// Get a human-readable description of this pattern
    pub fn description(&self) -> String {
        match self {
            WipePattern::Zeros => "Fill with zeros (0x00)".to_string(),
            WipePattern::Ones => "Fill with ones (0xFF)".to_string(),
            WipePattern::Fixed(byte) => format!("Fill with fixed byte (0x{:02X})", byte),
            WipePattern::Random => "Fill with cryptographically secure random data".to_string(),
            WipePattern::PseudoRandom(seed) => format!("Fill with pseudorandom data (seed: {})", seed),
            WipePattern::Complement => "Fill with complement of previous pass".to_string(),
            WipePattern::Pattern(pattern) => {
                let hex_pattern: Vec<String> = pattern.iter().map(|b| format!("{:02X}", b)).collect();
                format!("Fill with repeating pattern: {}", hex_pattern.join(" "))
            }
        }
    }
    
    /// Calculate a hash of the pattern for verification
    pub fn pattern_hash(&self) -> String {
        let mut hasher = Sha256::new();
        match self {
            WipePattern::Zeros => hasher.update(b"zeros"),
            WipePattern::Ones => hasher.update(b"ones"),
            WipePattern::Fixed(byte) => {
                hasher.update(b"fixed");
                hasher.update(&[*byte]);
            }
            WipePattern::Random => hasher.update(b"random"),
            WipePattern::PseudoRandom(seed) => {
                hasher.update(b"pseudorandom");
                hasher.update(&seed.to_le_bytes());
            }
            WipePattern::Complement => hasher.update(b"complement"),
            WipePattern::Pattern(pattern) => {
                hasher.update(b"pattern");
                hasher.update(pattern);
            }
        }
        hex::encode(hasher.finalize())
    }
}

impl std::fmt::Display for WipeAlgorithm {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.info().name)
    }
}

impl std::fmt::Display for SecurityLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SecurityLevel::Basic => write!(f, "Basic"),
            SecurityLevel::Standard => write!(f, "Standard"),
            SecurityLevel::High => write!(f, "High"),
            SecurityLevel::Maximum => write!(f, "Maximum"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_algorithm_info() {
        let nist = WipeAlgorithm::NIST80088;
        let info = nist.info();
        assert_eq!(info.name, "NIST 800-88");
        assert_eq!(info.passes, 1);
        assert_eq!(info.security_level, SecurityLevel::Standard);
    }
    
    #[test]
    fn test_dod_patterns() {
        let dod = WipeAlgorithm::DoD522022M;
        let patterns = dod.patterns();
        assert_eq!(patterns.len(), 3);
        assert_eq!(patterns[0], WipePattern::Zeros);
        assert_eq!(patterns[1], WipePattern::Ones);
        assert_eq!(patterns[2], WipePattern::Random);
    }
    
    #[test]
    fn test_gutmann_patterns() {
        let gutmann = WipeAlgorithm::Gutmann;
        let patterns = gutmann.patterns();
        assert_eq!(patterns.len(), 35);
    }
    
    #[test]
    fn test_pattern_generation() {
        let zeros = WipePattern::Zeros;
        let data = zeros.generate_data(10, None);
        assert_eq!(data, vec![0u8; 10]);
        
        let ones = WipePattern::Ones;
        let data = ones.generate_data(5, None);
        assert_eq!(data, vec![0xFFu8; 5]);
        
        let fixed = WipePattern::Fixed(0xAA);
        let data = fixed.generate_data(3, None);
        assert_eq!(data, vec![0xAAu8; 3]);
    }
    
    #[test]
    fn test_complement_pattern() {
        let original = vec![0x00, 0xFF, 0xAA, 0x55];
        let complement = WipePattern::Complement;
        let data = complement.generate_data(4, Some(&original));
        assert_eq!(data, vec![0xFF, 0x00, 0x55, 0xAA]);
    }
    
    #[test]
    fn test_repeating_pattern() {
        let pattern = WipePattern::Pattern(vec![0x12, 0x34]);
        let data = pattern.generate_data(6, None);
        assert_eq!(data, vec![0x12, 0x34, 0x12, 0x34, 0x12, 0x34]);
    }
    
    #[test]
    fn test_hardware_based_detection() {
        assert!(WipeAlgorithm::ATASecureErase.is_hardware_based());
        assert!(WipeAlgorithm::NVMeFormat.is_hardware_based());
        assert!(!WipeAlgorithm::NIST80088.is_hardware_based());
        assert!(!WipeAlgorithm::DoD522022M.is_hardware_based());
    }
}
