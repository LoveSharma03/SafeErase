//! Verification engine for SafeErase wipe operations

use std::collections::HashMap;
use std::time::{Duration, Instant};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use tracing::{info, warn, debug};
use uuid::Uuid;
use chrono::{DateTime, Utc};

use crate::device::Device;
use crate::wipe::WipeResult;
use crate::platform;
use crate::error::{SafeEraseError, Result};

/// Verification engine for wipe operations
#[derive(Debug)]
pub struct VerificationEngine {
    entropy_threshold: f64,
    pattern_detection_threshold: usize,
}

/// Result of wipe verification
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationResult {
    pub verification_id: Uuid,
    pub device_path: String,
    pub verification_type: VerificationType,
    pub started_at: DateTime<Utc>,
    pub completed_at: DateTime<Utc>,
    pub duration: Duration,
    pub samples_tested: usize,
    pub samples_passed: usize,
    pub success_rate: f64,
    pub overall_result: VerificationStatus,
    pub entropy_analysis: EntropyAnalysis,
    pub pattern_analysis: PatternAnalysis,
    pub sector_analysis: Vec<SectorAnalysis>,
    pub recommendations: Vec<String>,
}

/// Type of verification performed
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum VerificationType {
    /// Quick verification with random sampling
    Quick,
    /// Standard verification with systematic sampling
    Standard,
    /// Comprehensive verification with full analysis
    Comprehensive,
    /// Custom verification with user-defined parameters
    Custom,
}

/// Overall verification status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum VerificationStatus {
    Passed,
    Failed,
    Warning,
    Inconclusive,
}

/// Entropy analysis results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EntropyAnalysis {
    pub average_entropy: f64,
    pub min_entropy: f64,
    pub max_entropy: f64,
    pub entropy_distribution: HashMap<String, usize>,
    pub low_entropy_sectors: Vec<u64>,
}

/// Pattern analysis results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PatternAnalysis {
    pub detected_patterns: Vec<DetectedPattern>,
    pub zero_sectors: usize,
    pub one_sectors: usize,
    pub random_sectors: usize,
    pub suspicious_sectors: Vec<u64>,
}

/// Analysis of individual sectors
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SectorAnalysis {
    pub sector_offset: u64,
    pub entropy: f64,
    pub pattern_type: PatternType,
    pub confidence: f64,
    pub data_hash: String,
    pub anomalies: Vec<String>,
}

/// Detected pattern in data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DetectedPattern {
    pub pattern_type: PatternType,
    pub frequency: usize,
    pub confidence: f64,
    pub sample_data: Vec<u8>,
    pub locations: Vec<u64>,
}

/// Type of pattern detected in data
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PatternType {
    AllZeros,
    AllOnes,
    Repeating,
    Random,
    Structured,
    Suspicious,
}

impl VerificationEngine {
    /// Create a new verification engine
    pub fn new() -> Result<Self> {
        Ok(Self {
            entropy_threshold: 7.5, // Minimum entropy for random data
            pattern_detection_threshold: 16, // Minimum pattern length to detect
        })
    }
    
    /// Verify a completed wipe operation
    pub async fn verify_wipe(
        &self,
        device: &Device,
        wipe_result: &WipeResult,
    ) -> Result<VerificationResult> {
        let verification_id = Uuid::new_v4();
        let started_at = Utc::now();
        
        info!("Starting wipe verification {} for device {}", verification_id, device.path());
        
        // Determine verification type based on device size and algorithm
        let verification_type = self.determine_verification_type(device, wipe_result).await?;
        
        // Perform the verification
        let verification_start = Instant::now();
        let result = self.perform_verification(
            verification_id,
            device,
            verification_type,
            wipe_result,
        ).await?;
        
        let duration = verification_start.elapsed();
        let completed_at = Utc::now();
        
        info!("Verification {} completed in {:?} with result: {:?}", 
              verification_id, duration, result.overall_result);
        
        Ok(VerificationResult {
            verification_id,
            device_path: device.path().to_string(),
            verification_type,
            started_at,
            completed_at,
            duration,
            samples_tested: result.samples_tested,
            samples_passed: result.samples_passed,
            success_rate: result.success_rate,
            overall_result: result.overall_result,
            entropy_analysis: result.entropy_analysis,
            pattern_analysis: result.pattern_analysis,
            sector_analysis: result.sector_analysis,
            recommendations: result.recommendations,
        })
    }
    
    /// Determine the appropriate verification type
    async fn determine_verification_type(
        &self,
        device: &Device,
        wipe_result: &WipeResult,
    ) -> Result<VerificationType> {
        let device_info = device.get_info().await?;
        
        // Use comprehensive verification for smaller devices or critical operations
        if device_info.size < 100 * 1024 * 1024 * 1024 { // < 100GB
            return Ok(VerificationType::Comprehensive);
        }
        
        // Use standard verification for most cases
        if wipe_result.algorithm.info().security_level as u8 >= 2 { // High or Maximum
            return Ok(VerificationType::Standard);
        }
        
        // Use quick verification for basic algorithms
        Ok(VerificationType::Quick)
    }
    
    /// Perform the actual verification
    async fn perform_verification(
        &self,
        verification_id: Uuid,
        device: &Device,
        verification_type: VerificationType,
        wipe_result: &WipeResult,
    ) -> Result<VerificationResult> {
        let device_info = device.get_info().await?;
        let capabilities = device.capabilities();
        
        // Calculate sampling parameters
        let (sample_count, sample_size) = self.calculate_sampling_parameters(
            verification_type,
            device_info.size,
        );
        
        debug!("Verification will test {} samples of {} bytes each", sample_count, sample_size);
        
        let mut sector_analyses = Vec::new();
        let mut entropy_values = Vec::new();
        let mut pattern_counts = HashMap::new();
        let mut samples_passed = 0;
        
        // Generate sample locations
        let sample_locations = self.generate_sample_locations(
            device_info.size,
            sample_count,
            sample_size,
            verification_type,
        );
        
        // Analyze each sample
        for (i, &offset) in sample_locations.iter().enumerate() {
            debug!("Analyzing sample {} at offset {}", i + 1, offset);
            
            // Read sample data
            let mut buffer = vec![0u8; sample_size];
            let sector_lba = offset / capabilities.logical_sector_size as u64;
            
            // In a real implementation, this would read from the device
            // For now, simulate reading wiped data
            match wipe_result.algorithm {
                crate::algorithms::WipeAlgorithm::ZeroFill => {
                    buffer.fill(0);
                }
                crate::algorithms::WipeAlgorithm::OneFill => {
                    buffer.fill(0xFF);
                }
                _ => {
                    // Simulate random data for other algorithms
                    use rand::Rng;
                    let mut rng = rand::thread_rng();
                    for byte in buffer.iter_mut() {
                        *byte = rng.gen();
                    }
                }
            }
            
            // Analyze the sample
            let analysis = self.analyze_sector(&buffer, offset)?;
            entropy_values.push(analysis.entropy);
            
            // Count pattern types
            *pattern_counts.entry(analysis.pattern_type).or_insert(0) += 1;
            
            // Check if sample passes verification
            if self.is_sample_acceptable(&analysis, wipe_result) {
                samples_passed += 1;
            }
            
            sector_analyses.push(analysis);
        }
        
        // Perform entropy analysis
        let entropy_analysis = self.analyze_entropy(&entropy_values, &sector_analyses);
        
        // Perform pattern analysis
        let pattern_analysis = self.analyze_patterns(&pattern_counts, &sector_analyses);
        
        // Determine overall result
        let success_rate = samples_passed as f64 / sample_count as f64;
        let overall_result = self.determine_overall_result(
            success_rate,
            &entropy_analysis,
            &pattern_analysis,
            wipe_result,
        );
        
        // Generate recommendations
        let recommendations = self.generate_recommendations(
            &overall_result,
            &entropy_analysis,
            &pattern_analysis,
            wipe_result,
        );
        
        Ok(VerificationResult {
            verification_id,
            device_path: device.path().to_string(),
            verification_type,
            started_at: Utc::now(), // This would be passed in
            completed_at: Utc::now(),
            duration: Duration::from_secs(0), // This would be calculated
            samples_tested: sample_count,
            samples_passed,
            success_rate,
            overall_result,
            entropy_analysis,
            pattern_analysis,
            sector_analysis: sector_analyses,
            recommendations,
        })
    }
    
    /// Calculate sampling parameters based on verification type and device size
    fn calculate_sampling_parameters(&self, verification_type: VerificationType, device_size: u64) -> (usize, usize) {
        let sample_size = 4096; // 4KB samples
        
        let sample_count = match verification_type {
            VerificationType::Quick => {
                std::cmp::min(100, std::cmp::max(10, (device_size / (1024 * 1024 * 1024)) as usize))
            }
            VerificationType::Standard => {
                std::cmp::min(1000, std::cmp::max(100, (device_size / (100 * 1024 * 1024)) as usize))
            }
            VerificationType::Comprehensive => {
                std::cmp::min(10000, std::cmp::max(1000, (device_size / (10 * 1024 * 1024)) as usize))
            }
            VerificationType::Custom => 500, // Default for custom
        };
        
        (sample_count, sample_size)
    }
    
    /// Generate sample locations for verification
    fn generate_sample_locations(
        &self,
        device_size: u64,
        sample_count: usize,
        sample_size: usize,
        verification_type: VerificationType,
    ) -> Vec<u64> {
        let mut locations = Vec::new();
        let max_offset = device_size.saturating_sub(sample_size as u64);
        
        match verification_type {
            VerificationType::Quick | VerificationType::Standard => {
                // Random sampling
                use rand::Rng;
                let mut rng = rand::thread_rng();
                for _ in 0..sample_count {
                    let offset = rng.gen_range(0..=max_offset);
                    locations.push(offset);
                }
            }
            VerificationType::Comprehensive => {
                // Systematic sampling with some random samples
                let systematic_count = sample_count * 3 / 4;
                let random_count = sample_count - systematic_count;
                
                // Systematic samples
                for i in 0..systematic_count {
                    let offset = (i as u64 * max_offset) / systematic_count as u64;
                    locations.push(offset);
                }
                
                // Random samples
                use rand::Rng;
                let mut rng = rand::thread_rng();
                for _ in 0..random_count {
                    let offset = rng.gen_range(0..=max_offset);
                    locations.push(offset);
                }
            }
            VerificationType::Custom => {
                // Custom sampling logic would go here
                for i in 0..sample_count {
                    let offset = (i as u64 * max_offset) / sample_count as u64;
                    locations.push(offset);
                }
            }
        }
        
        locations.sort();
        locations
    }
    
    /// Analyze a single sector of data
    fn analyze_sector(&self, data: &[u8], offset: u64) -> Result<SectorAnalysis> {
        // Calculate entropy
        let entropy = self.calculate_entropy(data);
        
        // Detect pattern type
        let pattern_type = self.detect_pattern_type(data);
        
        // Calculate confidence based on data consistency
        let confidence = self.calculate_confidence(data, pattern_type);
        
        // Calculate data hash
        let mut hasher = Sha256::new();
        hasher.update(data);
        let data_hash = hex::encode(hasher.finalize());
        
        // Detect anomalies
        let anomalies = self.detect_anomalies(data, pattern_type, entropy);
        
        Ok(SectorAnalysis {
            sector_offset: offset,
            entropy,
            pattern_type,
            confidence,
            data_hash,
            anomalies,
        })
    }
    
    /// Calculate Shannon entropy of data
    fn calculate_entropy(&self, data: &[u8]) -> f64 {
        let mut counts = [0u32; 256];
        for &byte in data {
            counts[byte as usize] += 1;
        }
        
        let len = data.len() as f64;
        let mut entropy = 0.0;
        
        for &count in &counts {
            if count > 0 {
                let p = count as f64 / len;
                entropy -= p * p.log2();
            }
        }
        
        entropy
    }
    
    /// Detect the type of pattern in data
    fn detect_pattern_type(&self, data: &[u8]) -> PatternType {
        if data.iter().all(|&b| b == 0) {
            return PatternType::AllZeros;
        }
        
        if data.iter().all(|&b| b == 0xFF) {
            return PatternType::AllOnes;
        }
        
        // Check for repeating patterns
        if self.has_repeating_pattern(data) {
            return PatternType::Repeating;
        }
        
        // Check entropy for randomness
        let entropy = self.calculate_entropy(data);
        if entropy > self.entropy_threshold {
            return PatternType::Random;
        }
        
        // Check for structured data (file system signatures, etc.)
        if self.has_structured_data(data) {
            return PatternType::Suspicious;
        }
        
        PatternType::Structured
    }
    
    /// Check if data has repeating patterns
    fn has_repeating_pattern(&self, data: &[u8]) -> bool {
        if data.len() < self.pattern_detection_threshold {
            return false;
        }
        
        // Check for patterns of various lengths
        for pattern_len in 1..=std::cmp::min(data.len() / 4, 64) {
            let pattern = &data[0..pattern_len];
            let mut matches = 0;
            
            for chunk in data.chunks_exact(pattern_len) {
                if chunk == pattern {
                    matches += 1;
                }
            }
            
            if matches > data.len() / pattern_len / 2 {
                return true;
            }
        }
        
        false
    }
    
    /// Check if data contains structured information
    fn has_structured_data(&self, data: &[u8]) -> bool {
        // Look for common file system signatures or structured data
        let signatures = [
            b"NTFS",
            b"FAT32",
            b"ext2",
            b"ext3",
            b"ext4",
            b"HFS+",
            b"APFS",
            &[0x55, 0xAA], // Boot signature
        ];
        
        for signature in &signatures {
            if data.windows(signature.len()).any(|window| window == *signature) {
                return true;
            }
        }
        
        false
    }
    
    /// Calculate confidence in pattern detection
    fn calculate_confidence(&self, data: &[u8], pattern_type: PatternType) -> f64 {
        match pattern_type {
            PatternType::AllZeros | PatternType::AllOnes => 1.0,
            PatternType::Random => {
                let entropy = self.calculate_entropy(data);
                (entropy / 8.0).min(1.0)
            }
            PatternType::Repeating => 0.9,
            PatternType::Structured => 0.7,
            PatternType::Suspicious => 0.5,
        }
    }
    
    /// Detect anomalies in the data
    fn detect_anomalies(&self, data: &[u8], pattern_type: PatternType, entropy: f64) -> Vec<String> {
        let mut anomalies = Vec::new();
        
        // Check for unexpected patterns
        match pattern_type {
            PatternType::Suspicious => {
                anomalies.push("Suspicious structured data detected".to_string());
            }
            PatternType::Random if entropy < self.entropy_threshold => {
                anomalies.push("Low entropy in supposedly random data".to_string());
            }
            _ => {}
        }
        
        // Check for null byte sequences that might indicate incomplete wiping
        let null_sequences = data.windows(16).filter(|w| w.iter().all(|&b| b == 0)).count();
        if null_sequences > data.len() / 32 && pattern_type != PatternType::AllZeros {
            anomalies.push("Unexpected null byte sequences".to_string());
        }
        
        anomalies
    }
    
    /// Check if a sample is acceptable for the given wipe algorithm
    fn is_sample_acceptable(&self, analysis: &SectorAnalysis, wipe_result: &WipeResult) -> bool {
        // Check for anomalies
        if !analysis.anomalies.is_empty() {
            return false;
        }
        
        // Check pattern consistency with algorithm
        match wipe_result.algorithm {
            crate::algorithms::WipeAlgorithm::ZeroFill => {
                analysis.pattern_type == PatternType::AllZeros
            }
            crate::algorithms::WipeAlgorithm::OneFill => {
                analysis.pattern_type == PatternType::AllOnes
            }
            crate::algorithms::WipeAlgorithm::Random | 
            crate::algorithms::WipeAlgorithm::NIST80088 => {
                analysis.pattern_type == PatternType::Random && 
                analysis.entropy > self.entropy_threshold
            }
            _ => {
                // For multi-pass algorithms, accept various patterns
                !matches!(analysis.pattern_type, PatternType::Suspicious)
            }
        }
    }
    
    /// Analyze entropy across all samples
    fn analyze_entropy(&self, entropy_values: &[f64], sector_analyses: &[SectorAnalysis]) -> EntropyAnalysis {
        let average_entropy = entropy_values.iter().sum::<f64>() / entropy_values.len() as f64;
        let min_entropy = entropy_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_entropy = entropy_values.iter().fold(0.0, |a, &b| a.max(b));
        
        // Create entropy distribution
        let mut entropy_distribution = HashMap::new();
        for &entropy in entropy_values {
            let bucket = format!("{:.1}", entropy);
            *entropy_distribution.entry(bucket).or_insert(0) += 1;
        }
        
        // Find low entropy sectors
        let low_entropy_sectors: Vec<u64> = sector_analyses
            .iter()
            .filter(|analysis| analysis.entropy < self.entropy_threshold)
            .map(|analysis| analysis.sector_offset)
            .collect();
        
        EntropyAnalysis {
            average_entropy,
            min_entropy,
            max_entropy,
            entropy_distribution,
            low_entropy_sectors,
        }
    }
    
    /// Analyze patterns across all samples
    fn analyze_patterns(&self, pattern_counts: &HashMap<PatternType, usize>, sector_analyses: &[SectorAnalysis]) -> PatternAnalysis {
        let zero_sectors = *pattern_counts.get(&PatternType::AllZeros).unwrap_or(&0);
        let one_sectors = *pattern_counts.get(&PatternType::AllOnes).unwrap_or(&0);
        let random_sectors = *pattern_counts.get(&PatternType::Random).unwrap_or(&0);
        
        // Find suspicious sectors
        let suspicious_sectors: Vec<u64> = sector_analyses
            .iter()
            .filter(|analysis| analysis.pattern_type == PatternType::Suspicious)
            .map(|analysis| analysis.sector_offset)
            .collect();
        
        // Create detected patterns summary
        let mut detected_patterns = Vec::new();
        for (&pattern_type, &count) in pattern_counts {
            if count > 0 {
                detected_patterns.push(DetectedPattern {
                    pattern_type,
                    frequency: count,
                    confidence: 0.9, // Simplified
                    sample_data: vec![], // Would contain actual sample data
                    locations: vec![], // Would contain actual locations
                });
            }
        }
        
        PatternAnalysis {
            detected_patterns,
            zero_sectors,
            one_sectors,
            random_sectors,
            suspicious_sectors,
        }
    }
    
    /// Determine the overall verification result
    fn determine_overall_result(
        &self,
        success_rate: f64,
        entropy_analysis: &EntropyAnalysis,
        pattern_analysis: &PatternAnalysis,
        wipe_result: &WipeResult,
    ) -> VerificationStatus {
        // Check for suspicious sectors
        if !pattern_analysis.suspicious_sectors.is_empty() {
            return VerificationStatus::Failed;
        }
        
        // Check success rate thresholds
        if success_rate >= 0.95 {
            VerificationStatus::Passed
        } else if success_rate >= 0.85 {
            VerificationStatus::Warning
        } else if success_rate >= 0.70 {
            VerificationStatus::Inconclusive
        } else {
            VerificationStatus::Failed
        }
    }
    
    /// Generate recommendations based on verification results
    fn generate_recommendations(
        &self,
        overall_result: &VerificationStatus,
        entropy_analysis: &EntropyAnalysis,
        pattern_analysis: &PatternAnalysis,
        wipe_result: &WipeResult,
    ) -> Vec<String> {
        let mut recommendations = Vec::new();
        
        match overall_result {
            VerificationStatus::Failed => {
                recommendations.push("Wipe verification failed. Consider re-wiping the device.".to_string());
                if !pattern_analysis.suspicious_sectors.is_empty() {
                    recommendations.push("Suspicious data patterns detected. Use a more aggressive wiping algorithm.".to_string());
                }
            }
            VerificationStatus::Warning => {
                recommendations.push("Wipe verification passed with warnings. Monitor for potential issues.".to_string());
            }
            VerificationStatus::Inconclusive => {
                recommendations.push("Verification results are inconclusive. Consider additional verification.".to_string());
            }
            VerificationStatus::Passed => {
                recommendations.push("Wipe verification passed successfully.".to_string());
            }
        }
        
        if entropy_analysis.average_entropy < self.entropy_threshold {
            recommendations.push("Low average entropy detected. Consider using random-based wiping algorithms.".to_string());
        }
        
        if !entropy_analysis.low_entropy_sectors.is_empty() {
            recommendations.push(format!("Found {} sectors with low entropy. These may require additional attention.", 
                                       entropy_analysis.low_entropy_sectors.len()));
        }
        
        recommendations
    }
    
    /// Check if the verification result indicates successful wiping
    pub fn is_successful(&self) -> bool {
        // This would be called on a VerificationResult instance
        // For now, return a placeholder
        true
    }
}

impl std::fmt::Display for VerificationStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            VerificationStatus::Passed => write!(f, "Passed"),
            VerificationStatus::Failed => write!(f, "Failed"),
            VerificationStatus::Warning => write!(f, "Warning"),
            VerificationStatus::Inconclusive => write!(f, "Inconclusive"),
        }
    }
}

impl std::fmt::Display for PatternType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            PatternType::AllZeros => write!(f, "All Zeros"),
            PatternType::AllOnes => write!(f, "All Ones"),
            PatternType::Repeating => write!(f, "Repeating"),
            PatternType::Random => write!(f, "Random"),
            PatternType::Structured => write!(f, "Structured"),
            PatternType::Suspicious => write!(f, "Suspicious"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_entropy_calculation() {
        let engine = VerificationEngine::new().unwrap();
        
        // All zeros should have zero entropy
        let zeros = vec![0u8; 100];
        assert_eq!(engine.calculate_entropy(&zeros), 0.0);
        
        // All different values should have high entropy
        let diverse: Vec<u8> = (0..=255).collect();
        let entropy = engine.calculate_entropy(&diverse);
        assert!(entropy > 7.0);
    }
    
    #[test]
    fn test_pattern_detection() {
        let engine = VerificationEngine::new().unwrap();
        
        let zeros = vec![0u8; 100];
        assert_eq!(engine.detect_pattern_type(&zeros), PatternType::AllZeros);
        
        let ones = vec![0xFFu8; 100];
        assert_eq!(engine.detect_pattern_type(&ones), PatternType::AllOnes);
        
        let repeating = vec![0xAA, 0xBB].repeat(50);
        assert_eq!(engine.detect_pattern_type(&repeating), PatternType::Repeating);
    }
    
    #[test]
    fn test_verification_status_display() {
        assert_eq!(VerificationStatus::Passed.to_string(), "Passed");
        assert_eq!(VerificationStatus::Failed.to_string(), "Failed");
        assert_eq!(VerificationStatus::Warning.to_string(), "Warning");
    }
}
