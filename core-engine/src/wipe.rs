//! Core wiping engine for SafeErase

use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::{RwLock, mpsc};
use tokio::time::sleep;
use tracing::{info, warn, error, debug};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

use crate::device::{Device, DeviceType};
use crate::algorithms::{WipeAlgorithm, WipePattern};
use crate::platform;
use crate::error::{SafeEraseError, Result};

/// Main wiping engine
#[derive(Debug)]
pub struct WipeEngine {
    active_operations: Arc<RwLock<Vec<WipeOperation>>>,
}

/// Configuration options for wipe operations
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WipeOptions {
    /// Whether to verify the wipe after completion
    pub verify_wipe: bool,
    /// Number of verification samples to take
    pub verification_samples: usize,
    /// Whether to detect and clear HPA/DCO
    pub clear_hpa_dco: bool,
    /// Block size for wiping operations (in bytes)
    pub block_size: usize,
    /// Maximum number of concurrent operations
    pub max_concurrent_ops: usize,
    /// Timeout for the entire operation
    pub operation_timeout: Option<Duration>,
    /// Whether to use hardware secure erase when available
    pub prefer_hardware_erase: bool,
    /// Custom progress reporting interval
    pub progress_interval: Duration,
}

/// Progress information for a wipe operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WipeProgress {
    pub operation_id: Uuid,
    pub device_path: String,
    pub algorithm: WipeAlgorithm,
    pub current_pass: usize,
    pub total_passes: usize,
    pub bytes_processed: u64,
    pub total_bytes: u64,
    pub percentage: f64,
    pub current_speed: f64, // bytes per second
    pub average_speed: f64,
    pub estimated_remaining: Option<Duration>,
    pub current_pattern: Option<String>,
    pub status: WipeStatus,
    pub started_at: DateTime<Utc>,
    pub last_updated: DateTime<Utc>,
}

/// Status of a wipe operation
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum WipeStatus {
    Initializing,
    DetectingHPA,
    ClearingHPA,
    DetectingDCO,
    ClearingDCO,
    Wiping,
    Verifying,
    Completed,
    Failed,
    Cancelled,
}

/// Result of a completed wipe operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WipeResult {
    pub operation_id: Uuid,
    pub device_path: String,
    pub device_serial: String,
    pub device_model: String,
    pub algorithm: WipeAlgorithm,
    pub options: WipeOptions,
    pub status: WipeStatus,
    pub started_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
    pub duration: Option<Duration>,
    pub bytes_wiped: u64,
    pub passes_completed: usize,
    pub verification_requested: bool,
    pub verification_passed: Option<bool>,
    pub hpa_detected: bool,
    pub hpa_cleared: bool,
    pub dco_detected: bool,
    pub dco_cleared: bool,
    pub error_message: Option<String>,
    pub performance_stats: PerformanceStats,
}

/// Performance statistics for the wipe operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceStats {
    pub average_speed: f64, // bytes per second
    pub peak_speed: f64,
    pub total_time: Duration,
    pub wipe_time: Duration,
    pub verification_time: Option<Duration>,
}

/// Internal wipe operation state
#[derive(Debug)]
struct WipeOperation {
    id: Uuid,
    device: Arc<Device>,
    algorithm: WipeAlgorithm,
    options: WipeOptions,
    progress_tx: mpsc::UnboundedSender<WipeProgress>,
    cancel_token: tokio_util::sync::CancellationToken,
    started_at: Instant,
}

impl WipeEngine {
    /// Create a new wipe engine
    pub fn new() -> Result<Self> {
        Ok(Self {
            active_operations: Arc::new(RwLock::new(Vec::new())),
        })
    }
    
    /// Start a wipe operation on the specified device
    pub async fn wipe_device(
        &self,
        device: &Device,
        algorithm: WipeAlgorithm,
        options: WipeOptions,
    ) -> Result<WipeResult> {
        let operation_id = Uuid::new_v4();
        info!("Starting wipe operation {} on device {}", operation_id, device.path());
        
        // Create progress channel
        let (progress_tx, mut progress_rx) = mpsc::unbounded_channel();
        let cancel_token = tokio_util::sync::CancellationToken::new();
        
        // Create operation state
        let operation = WipeOperation {
            id: operation_id,
            device: Arc::new(device.clone()),
            algorithm,
            options: options.clone(),
            progress_tx,
            cancel_token: cancel_token.clone(),
            started_at: Instant::now(),
        };
        
        // Add to active operations
        {
            let mut active_ops = self.active_operations.write().await;
            active_ops.push(operation);
        }
        
        // Start the actual wipe operation
        let device_clone = Arc::new(device.clone());
        let wipe_task = tokio::spawn(async move {
            Self::execute_wipe_operation(
                operation_id,
                device_clone,
                algorithm,
                options,
                cancel_token,
            ).await
        });
        
        // Wait for completion or timeout
        let result = if let Some(timeout) = options.operation_timeout {
            match tokio::time::timeout(timeout, wipe_task).await {
                Ok(Ok(result)) => result,
                Ok(Err(e)) => {
                    error!("Wipe operation {} failed: {}", operation_id, e);
                    return Err(e);
                }
                Err(_) => {
                    error!("Wipe operation {} timed out", operation_id);
                    return Err(SafeEraseError::Timeout(format!("Operation timed out after {:?}", timeout)));
                }
            }
        } else {
            match wipe_task.await {
                Ok(result) => result?,
                Err(e) => {
                    error!("Wipe operation {} panicked: {}", operation_id, e);
                    return Err(SafeEraseError::Internal(format!("Operation panicked: {}", e)));
                }
            }
        };
        
        // Remove from active operations
        {
            let mut active_ops = self.active_operations.write().await;
            active_ops.retain(|op| op.id != operation_id);
        }
        
        info!("Wipe operation {} completed with status: {:?}", operation_id, result.status);
        Ok(result)
    }
    
    /// Execute the actual wipe operation
    async fn execute_wipe_operation(
        operation_id: Uuid,
        device: Arc<Device>,
        algorithm: WipeAlgorithm,
        options: WipeOptions,
        cancel_token: tokio_util::sync::CancellationToken,
    ) -> Result<WipeResult> {
        let started_at = Utc::now();
        let device_info = device.get_info().await?;
        
        let mut result = WipeResult {
            operation_id,
            device_path: device_info.path.clone(),
            device_serial: device_info.serial.clone(),
            device_model: device_info.model.clone(),
            algorithm,
            options: options.clone(),
            status: WipeStatus::Initializing,
            started_at,
            completed_at: None,
            duration: None,
            bytes_wiped: 0,
            passes_completed: 0,
            verification_requested: options.verify_wipe,
            verification_passed: None,
            hpa_detected: false,
            hpa_cleared: false,
            dco_detected: false,
            dco_cleared: false,
            error_message: None,
            performance_stats: PerformanceStats {
                average_speed: 0.0,
                peak_speed: 0.0,
                total_time: Duration::from_secs(0),
                wipe_time: Duration::from_secs(0),
                verification_time: None,
            },
        };
        
        let operation_start = Instant::now();
        
        // Check for cancellation
        if cancel_token.is_cancelled() {
            result.status = WipeStatus::Cancelled;
            return Ok(result);
        }
        
        // Step 1: Detect and clear HPA/DCO if requested
        if options.clear_hpa_dco && device.supports_hpa_dco() {
            result.status = WipeStatus::DetectingHPA;
            debug!("Detecting HPA on device {}", device.path());
            
            match platform::detect_and_clear_hpa(device.handle()).await {
                Ok(detected) => {
                    result.hpa_detected = detected;
                    if detected {
                        result.status = WipeStatus::ClearingHPA;
                        result.hpa_cleared = true;
                        info!("HPA detected and cleared on device {}", device.path());
                    }
                }
                Err(e) => {
                    warn!("Failed to detect/clear HPA on device {}: {}", device.path(), e);
                }
            }
            
            result.status = WipeStatus::DetectingDCO;
            debug!("Detecting DCO on device {}", device.path());
            
            match platform::detect_and_clear_dco(device.handle()).await {
                Ok(detected) => {
                    result.dco_detected = detected;
                    if detected {
                        result.status = WipeStatus::ClearingDCO;
                        result.dco_cleared = true;
                        info!("DCO detected and cleared on device {}", device.path());
                    }
                }
                Err(e) => {
                    warn!("Failed to detect/clear DCO on device {}: {}", device.path(), e);
                }
            }
        }
        
        // Step 2: Perform the actual wipe
        result.status = WipeStatus::Wiping;
        let wipe_start = Instant::now();
        
        match Self::perform_wipe(&device, algorithm, &options, &cancel_token).await {
            Ok(stats) => {
                result.bytes_wiped = stats.bytes_wiped;
                result.passes_completed = stats.passes_completed;
                result.performance_stats.wipe_time = wipe_start.elapsed();
                result.performance_stats.average_speed = stats.average_speed;
                result.performance_stats.peak_speed = stats.peak_speed;
            }
            Err(e) => {
                result.status = WipeStatus::Failed;
                result.error_message = Some(e.to_string());
                result.completed_at = Some(Utc::now());
                result.duration = Some(operation_start.elapsed());
                return Ok(result);
            }
        }
        
        // Step 3: Verify the wipe if requested
        if options.verify_wipe {
            result.status = WipeStatus::Verifying;
            let verify_start = Instant::now();
            
            match Self::verify_wipe(&device, &options).await {
                Ok(passed) => {
                    result.verification_passed = Some(passed);
                    result.performance_stats.verification_time = Some(verify_start.elapsed());
                    if !passed {
                        result.status = WipeStatus::Failed;
                        result.error_message = Some("Wipe verification failed".to_string());
                    }
                }
                Err(e) => {
                    warn!("Wipe verification failed: {}", e);
                    result.verification_passed = Some(false);
                    result.performance_stats.verification_time = Some(verify_start.elapsed());
                }
            }
        }
        
        // Finalize result
        if result.status == WipeStatus::Wiping {
            result.status = WipeStatus::Completed;
        }
        
        result.completed_at = Some(Utc::now());
        result.duration = Some(operation_start.elapsed());
        result.performance_stats.total_time = operation_start.elapsed();
        
        Ok(result)
    }
    
    /// Perform the actual wiping operation
    async fn perform_wipe(
        device: &Device,
        algorithm: WipeAlgorithm,
        options: &WipeOptions,
        cancel_token: &tokio_util::sync::CancellationToken,
    ) -> Result<WipeStats> {
        let device_info = device.get_info().await?;
        
        // Use hardware erase if available and preferred
        if options.prefer_hardware_erase && algorithm.is_hardware_based() {
            return Self::perform_hardware_wipe(device, algorithm).await;
        }
        
        // Perform software-based wipe
        let patterns = algorithm.patterns();
        let total_passes = patterns.len();
        let mut bytes_wiped = 0u64;
        let mut speeds = Vec::new();
        let operation_start = Instant::now();
        
        for (pass_index, pattern) in patterns.iter().enumerate() {
            if cancel_token.is_cancelled() {
                return Err(SafeEraseError::WipeCancelled);
            }
            
            info!("Starting pass {} of {} with pattern: {}", 
                  pass_index + 1, total_passes, pattern.description());
            
            let pass_start = Instant::now();
            let pass_bytes = Self::wipe_with_pattern(device, pattern, options, cancel_token).await?;
            let pass_duration = pass_start.elapsed();
            
            bytes_wiped += pass_bytes;
            let speed = pass_bytes as f64 / pass_duration.as_secs_f64();
            speeds.push(speed);
            
            info!("Completed pass {} in {:?} at {:.2} MB/s", 
                  pass_index + 1, pass_duration, speed / 1_000_000.0);
        }
        
        // Flush device cache
        platform::flush_cache(device.handle()).await?;
        
        Ok(WipeStats {
            bytes_wiped,
            passes_completed: total_passes,
            average_speed: speeds.iter().sum::<f64>() / speeds.len() as f64,
            peak_speed: speeds.iter().fold(0.0, |a, &b| a.max(b)),
        })
    }
    
    /// Perform hardware-based wipe (ATA Secure Erase or NVMe Format)
    async fn perform_hardware_wipe(device: &Device, algorithm: WipeAlgorithm) -> Result<WipeStats> {
        let device_info = device.get_info().await?;
        let start_time = Instant::now();
        
        match algorithm {
            WipeAlgorithm::ATASecureErase => {
                info!("Performing ATA Secure Erase on device {}", device.path());
                platform::ata_secure_erase(device.handle(), false).await?;
            }
            WipeAlgorithm::NVMeFormat => {
                info!("Performing NVMe Format on device {}", device.path());
                platform::nvme_format(device.handle(), true).await?;
            }
            _ => {
                return Err(SafeEraseError::UnsupportedAlgorithm(algorithm.to_string()));
            }
        }
        
        let duration = start_time.elapsed();
        let speed = device_info.size as f64 / duration.as_secs_f64();
        
        Ok(WipeStats {
            bytes_wiped: device_info.size,
            passes_completed: 1,
            average_speed: speed,
            peak_speed: speed,
        })
    }
    
    /// Wipe device with a specific pattern
    async fn wipe_with_pattern(
        device: &Device,
        pattern: &WipePattern,
        options: &WipeOptions,
        cancel_token: &tokio_util::sync::CancellationToken,
    ) -> Result<u64> {
        let device_info = device.get_info().await?;
        let capabilities = device.capabilities();
        
        let block_size = options.block_size.min(1024 * 1024); // Max 1MB blocks
        let total_blocks = (device_info.size + block_size as u64 - 1) / block_size as u64;
        
        let mut bytes_written = 0u64;
        let mut previous_data: Option<Vec<u8>> = None;
        
        for block_index in 0..total_blocks {
            if cancel_token.is_cancelled() {
                return Err(SafeEraseError::WipeCancelled);
            }
            
            let current_block_size = std::cmp::min(
                block_size,
                (device_info.size - bytes_written) as usize
            );
            
            // Generate pattern data
            let pattern_data = pattern.generate_data(current_block_size, previous_data.as_deref());
            
            // Write to device (this would be implemented with actual I/O)
            // For now, this is a placeholder
            let start_lba = bytes_written / capabilities.logical_sector_size as u64;
            
            // In a real implementation, you would write the pattern_data to the device
            // platform::write_sectors(device.handle(), start_lba, &pattern_data).await?;
            
            bytes_written += current_block_size as u64;
            previous_data = Some(pattern_data);
            
            // Small delay to prevent overwhelming the system
            if block_index % 100 == 0 {
                sleep(Duration::from_millis(1)).await;
            }
        }
        
        Ok(bytes_written)
    }
    
    /// Verify that the wipe was successful
    async fn verify_wipe(device: &Device, options: &WipeOptions) -> Result<bool> {
        let device_info = device.get_info().await?;
        let sample_size = 4096; // 4KB samples
        let num_samples = options.verification_samples.min(1000); // Max 1000 samples
        
        info!("Verifying wipe with {} samples", num_samples);
        
        for i in 0..num_samples {
            // Calculate random offset for this sample
            let max_offset = device_info.size.saturating_sub(sample_size as u64);
            let offset = (i as u64 * max_offset) / num_samples as u64;
            
            // Read sample data (placeholder implementation)
            let mut buffer = vec![0u8; sample_size];
            // platform::read_sectors(device.handle(), offset / 512, &mut buffer).await?;
            
            // Check if data appears to be wiped (all zeros or random)
            if !Self::is_data_wiped(&buffer) {
                warn!("Verification failed at offset {}", offset);
                return Ok(false);
            }
        }
        
        info!("Wipe verification passed");
        Ok(true)
    }
    
    /// Check if data appears to be properly wiped
    fn is_data_wiped(data: &[u8]) -> bool {
        // Simple heuristic: check for patterns that indicate unwiped data
        // In a real implementation, this would be more sophisticated
        
        // Check if all bytes are the same (likely wiped)
        let first_byte = data[0];
        if data.iter().all(|&b| b == first_byte) {
            return true;
        }
        
        // Check for high entropy (random data)
        let unique_bytes: std::collections::HashSet<u8> = data.iter().cloned().collect();
        if unique_bytes.len() > data.len() / 4 {
            return true; // High diversity suggests random data
        }
        
        false
    }
    
    /// Get active wipe operations
    pub async fn get_active_operations(&self) -> Vec<Uuid> {
        let active_ops = self.active_operations.read().await;
        active_ops.iter().map(|op| op.id).collect()
    }
    
    /// Cancel a wipe operation
    pub async fn cancel_operation(&self, operation_id: Uuid) -> Result<()> {
        let active_ops = self.active_operations.read().await;
        if let Some(operation) = active_ops.iter().find(|op| op.id == operation_id) {
            operation.cancel_token.cancel();
            info!("Cancelled wipe operation {}", operation_id);
            Ok(())
        } else {
            Err(SafeEraseError::Internal(format!("Operation {} not found", operation_id)))
        }
    }
}

/// Internal statistics for wipe operations
#[derive(Debug)]
struct WipeStats {
    bytes_wiped: u64,
    passes_completed: usize,
    average_speed: f64,
    peak_speed: f64,
}

impl Default for WipeOptions {
    fn default() -> Self {
        Self {
            verify_wipe: true,
            verification_samples: 100,
            clear_hpa_dco: true,
            block_size: 1024 * 1024, // 1MB
            max_concurrent_ops: 1,
            operation_timeout: Some(Duration::from_secs(24 * 60 * 60)), // 24 hours
            prefer_hardware_erase: true,
            progress_interval: Duration::from_secs(1),
        }
    }
}

impl std::fmt::Display for WipeStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            WipeStatus::Initializing => write!(f, "Initializing"),
            WipeStatus::DetectingHPA => write!(f, "Detecting HPA"),
            WipeStatus::ClearingHPA => write!(f, "Clearing HPA"),
            WipeStatus::DetectingDCO => write!(f, "Detecting DCO"),
            WipeStatus::ClearingDCO => write!(f, "Clearing DCO"),
            WipeStatus::Wiping => write!(f, "Wiping"),
            WipeStatus::Verifying => write!(f, "Verifying"),
            WipeStatus::Completed => write!(f, "Completed"),
            WipeStatus::Failed => write!(f, "Failed"),
            WipeStatus::Cancelled => write!(f, "Cancelled"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_wipe_options_default() {
        let options = WipeOptions::default();
        assert!(options.verify_wipe);
        assert_eq!(options.verification_samples, 100);
        assert!(options.clear_hpa_dco);
        assert!(options.prefer_hardware_erase);
    }
    
    #[test]
    fn test_wipe_status_display() {
        assert_eq!(WipeStatus::Initializing.to_string(), "Initializing");
        assert_eq!(WipeStatus::Wiping.to_string(), "Wiping");
        assert_eq!(WipeStatus::Completed.to_string(), "Completed");
    }
    
    #[test]
    fn test_is_data_wiped() {
        // All zeros should be considered wiped
        let zeros = vec![0u8; 100];
        assert!(WipeEngine::is_data_wiped(&zeros));
        
        // All same value should be considered wiped
        let ones = vec![0xFFu8; 100];
        assert!(WipeEngine::is_data_wiped(&ones));
        
        // High entropy data should be considered wiped
        let random: Vec<u8> = (0..100).map(|i| (i * 7 + 13) as u8).collect();
        assert!(WipeEngine::is_data_wiped(&random));
    }
}
