//! SafeErase Core Engine
//! 
//! This crate provides the core functionality for secure data wiping operations,
//! including support for various storage devices, wiping algorithms, and 
//! hardware-specific features like HPA/DCO and SSD secure erase.

pub mod device;
pub mod wipe;
pub mod algorithms;
pub mod verification;
pub mod platform;
pub mod error;

use std::sync::Arc;
use tokio::sync::RwLock;
use tracing::{info, warn, error};

// Add missing dependency
use tokio_util;

pub use device::{Device, DeviceInfo, DeviceType, StorageInterface};
pub use wipe::{WipeEngine, WipeProgress, WipeResult, WipeOptions};
pub use algorithms::{WipeAlgorithm, WipePattern};
pub use verification::{VerificationEngine, VerificationResult};
pub use error::{SafeEraseError, Result};

/// Main SafeErase engine that coordinates all wiping operations
#[derive(Debug)]
pub struct SafeEraseEngine {
    devices: Arc<RwLock<Vec<Device>>>,
    wipe_engine: WipeEngine,
    verification_engine: VerificationEngine,
}

impl SafeEraseEngine {
    /// Create a new SafeErase engine instance
    pub fn new() -> Result<Self> {
        info!("Initializing SafeErase engine");
        
        let wipe_engine = WipeEngine::new()?;
        let verification_engine = VerificationEngine::new()?;
        
        Ok(Self {
            devices: Arc::new(RwLock::new(Vec::new())),
            wipe_engine,
            verification_engine,
        })
    }
    
    /// Discover all available storage devices
    pub async fn discover_devices(&self) -> Result<Vec<DeviceInfo>> {
        info!("Discovering storage devices");
        
        let discovered = device::discover_devices().await?;
        let mut devices = self.devices.write().await;
        devices.clear();
        
        for device_info in &discovered {
            match Device::open(&device_info.path).await {
                Ok(device) => {
                    info!("Successfully opened device: {}", device_info.name);
                    devices.push(device);
                }
                Err(e) => {
                    warn!("Failed to open device {}: {}", device_info.name, e);
                }
            }
        }
        
        Ok(discovered)
    }
    
    /// Start a secure wipe operation on the specified device
    pub async fn start_wipe(
        &self,
        device_path: &str,
        algorithm: WipeAlgorithm,
        options: WipeOptions,
    ) -> Result<WipeResult> {
        info!("Starting wipe operation on device: {}", device_path);
        
        let devices = self.devices.read().await;
        let device = devices
            .iter()
            .find(|d| d.path() == device_path)
            .ok_or_else(|| SafeEraseError::DeviceNotFound(device_path.to_string()))?;
        
        // Perform the wipe operation
        let wipe_result = self.wipe_engine.wipe_device(device, algorithm, options).await?;
        
        // Verify the wipe if requested
        if wipe_result.verification_requested {
            info!("Starting verification for device: {}", device_path);
            let verification_result = self.verification_engine
                .verify_wipe(device, &wipe_result)
                .await?;
            
            if !verification_result.is_successful() {
                error!("Wipe verification failed for device: {}", device_path);
                return Err(SafeEraseError::VerificationFailed);
            }
        }
        
        info!("Wipe operation completed successfully for device: {}", device_path);
        Ok(wipe_result)
    }
    
    /// Get the current status of all devices
    pub async fn get_device_status(&self) -> Result<Vec<DeviceInfo>> {
        let devices = self.devices.read().await;
        let mut device_infos = Vec::new();
        
        for device in devices.iter() {
            device_infos.push(device.get_info().await?);
        }
        
        Ok(device_infos)
    }
}

impl Default for SafeEraseEngine {
    fn default() -> Self {
        Self::new().expect("Failed to create SafeErase engine")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_engine_creation() {
        let engine = SafeEraseEngine::new();
        assert!(engine.is_ok());
    }
    
    #[tokio::test]
    async fn test_device_discovery() {
        let engine = SafeEraseEngine::new().unwrap();
        let result = engine.discover_devices().await;
        // Should not fail even if no devices are found
        assert!(result.is_ok());
    }
}
