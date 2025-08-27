//! Device detection and management for SafeErase

use std::path::PathBuf;
use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use tokio::fs;
use tracing::{debug, info, warn};

use crate::error::{SafeEraseError, Result};
use crate::platform;

/// Information about a storage device
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeviceInfo {
    pub path: String,
    pub name: String,
    pub model: String,
    pub serial: String,
    pub size: u64,
    pub device_type: DeviceType,
    pub interface: StorageInterface,
    pub is_removable: bool,
    pub is_system_disk: bool,
    pub supports_secure_erase: bool,
    pub supports_hpa_dco: bool,
    pub firmware_version: Option<String>,
    pub temperature: Option<i32>,
    pub health_status: HealthStatus,
}

/// Types of storage devices
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum DeviceType {
    HDD,
    SSD,
    NVMe,
    eMMC,
    SD,
    USB,
    Unknown,
}

/// Storage interface types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum StorageInterface {
    SATA,
    NVMe,
    USB,
    SCSI,
    IDE,
    MMC,
    Unknown,
}

/// Device health status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum HealthStatus {
    Good,
    Warning,
    Critical,
    Unknown,
}

/// Represents an opened storage device
#[derive(Debug)]
pub struct Device {
    info: DeviceInfo,
    handle: platform::DeviceHandle,
    capabilities: DeviceCapabilities,
}

/// Device capabilities for wiping operations
#[derive(Debug, Clone)]
pub struct DeviceCapabilities {
    pub supports_ata_secure_erase: bool,
    pub supports_nvme_format: bool,
    pub supports_trim: bool,
    pub supports_write_same: bool,
    pub supports_hpa_detection: bool,
    pub supports_dco_detection: bool,
    pub max_lba: u64,
    pub logical_sector_size: u32,
    pub physical_sector_size: u32,
}

impl Device {
    /// Open a device for wiping operations
    pub async fn open(device_path: &str) -> Result<Self> {
        debug!("Opening device: {}", device_path);
        
        // Check if we have sufficient privileges
        if !platform::has_admin_privileges() {
            return Err(SafeEraseError::InsufficientPrivileges);
        }
        
        // Open the device handle
        let handle = platform::open_device(device_path).await?;
        
        // Get device information
        let info = Self::query_device_info(&handle, device_path).await?;
        
        // Query device capabilities
        let capabilities = Self::query_capabilities(&handle, &info).await?;
        
        info!("Successfully opened device: {} ({})", info.name, info.model);
        
        Ok(Self {
            info,
            handle,
            capabilities,
        })
    }
    
    /// Get device information
    pub async fn get_info(&self) -> Result<DeviceInfo> {
        Ok(self.info.clone())
    }
    
    /// Get device capabilities
    pub fn capabilities(&self) -> &DeviceCapabilities {
        &self.capabilities
    }
    
    /// Get device path
    pub fn path(&self) -> &str {
        &self.info.path
    }
    
    /// Check if device supports secure erase
    pub fn supports_secure_erase(&self) -> bool {
        self.capabilities.supports_ata_secure_erase || self.capabilities.supports_nvme_format
    }
    
    /// Check if device supports HPA/DCO detection
    pub fn supports_hpa_dco(&self) -> bool {
        self.capabilities.supports_hpa_detection || self.capabilities.supports_dco_detection
    }
    
    /// Get the device handle for low-level operations
    pub(crate) fn handle(&self) -> &platform::DeviceHandle {
        &self.handle
    }
    
    async fn query_device_info(
        handle: &platform::DeviceHandle,
        device_path: &str,
    ) -> Result<DeviceInfo> {
        let basic_info = platform::get_device_info(handle).await?;
        let smart_info = platform::get_smart_info(handle).await.unwrap_or_default();
        
        Ok(DeviceInfo {
            path: device_path.to_string(),
            name: basic_info.name,
            model: basic_info.model,
            serial: basic_info.serial,
            size: basic_info.size,
            device_type: basic_info.device_type,
            interface: basic_info.interface,
            is_removable: basic_info.is_removable,
            is_system_disk: basic_info.is_system_disk,
            supports_secure_erase: basic_info.supports_secure_erase,
            supports_hpa_dco: basic_info.supports_hpa_dco,
            firmware_version: basic_info.firmware_version,
            temperature: smart_info.temperature,
            health_status: smart_info.health_status,
        })
    }
    
    async fn query_capabilities(
        handle: &platform::DeviceHandle,
        info: &DeviceInfo,
    ) -> Result<DeviceCapabilities> {
        let caps = platform::query_device_capabilities(handle).await?;
        
        Ok(DeviceCapabilities {
            supports_ata_secure_erase: caps.supports_ata_secure_erase,
            supports_nvme_format: caps.supports_nvme_format,
            supports_trim: caps.supports_trim,
            supports_write_same: caps.supports_write_same,
            supports_hpa_detection: caps.supports_hpa_detection,
            supports_dco_detection: caps.supports_dco_detection,
            max_lba: caps.max_lba,
            logical_sector_size: caps.logical_sector_size,
            physical_sector_size: caps.physical_sector_size,
        })
    }
}

/// Discover all available storage devices
pub async fn discover_devices() -> Result<Vec<DeviceInfo>> {
    info!("Starting device discovery");
    
    let device_paths = platform::enumerate_storage_devices().await?;
    let mut devices = Vec::new();
    
    for path in device_paths {
        match Device::open(&path).await {
            Ok(device) => {
                let info = device.get_info().await?;
                devices.push(info);
            }
            Err(e) => {
                warn!("Failed to open device {}: {}", path, e);
                // Continue with other devices
            }
        }
    }
    
    info!("Discovered {} storage devices", devices.len());
    Ok(devices)
}

/// Filter devices based on criteria
pub fn filter_devices(
    devices: &[DeviceInfo],
    include_system: bool,
    include_removable: bool,
    min_size: Option<u64>,
) -> Vec<DeviceInfo> {
    devices
        .iter()
        .filter(|device| {
            if !include_system && device.is_system_disk {
                return false;
            }
            if !include_removable && device.is_removable {
                return false;
            }
            if let Some(min) = min_size {
                if device.size < min {
                    return false;
                }
            }
            true
        })
        .cloned()
        .collect()
}

impl std::fmt::Display for DeviceType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            DeviceType::HDD => write!(f, "Hard Disk Drive"),
            DeviceType::SSD => write!(f, "Solid State Drive"),
            DeviceType::NVMe => write!(f, "NVMe SSD"),
            DeviceType::eMMC => write!(f, "eMMC Storage"),
            DeviceType::SD => write!(f, "SD Card"),
            DeviceType::USB => write!(f, "USB Storage"),
            DeviceType::Unknown => write!(f, "Unknown"),
        }
    }
}

impl std::fmt::Display for StorageInterface {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            StorageInterface::SATA => write!(f, "SATA"),
            StorageInterface::NVMe => write!(f, "NVMe"),
            StorageInterface::USB => write!(f, "USB"),
            StorageInterface::SCSI => write!(f, "SCSI"),
            StorageInterface::IDE => write!(f, "IDE"),
            StorageInterface::MMC => write!(f, "MMC"),
            StorageInterface::Unknown => write!(f, "Unknown"),
        }
    }
}

impl std::fmt::Display for HealthStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            HealthStatus::Good => write!(f, "Good"),
            HealthStatus::Warning => write!(f, "Warning"),
            HealthStatus::Critical => write!(f, "Critical"),
            HealthStatus::Unknown => write!(f, "Unknown"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_device_type_display() {
        assert_eq!(DeviceType::SSD.to_string(), "Solid State Drive");
        assert_eq!(DeviceType::HDD.to_string(), "Hard Disk Drive");
    }
    
    #[test]
    fn test_filter_devices() {
        let devices = vec![
            DeviceInfo {
                path: "/dev/sda".to_string(),
                name: "System Disk".to_string(),
                model: "Test SSD".to_string(),
                serial: "123456".to_string(),
                size: 1000000000,
                device_type: DeviceType::SSD,
                interface: StorageInterface::SATA,
                is_removable: false,
                is_system_disk: true,
                supports_secure_erase: true,
                supports_hpa_dco: false,
                firmware_version: None,
                temperature: None,
                health_status: HealthStatus::Good,
            },
        ];
        
        let filtered = filter_devices(&devices, false, true, None);
        assert_eq!(filtered.len(), 0); // System disk filtered out
        
        let filtered = filter_devices(&devices, true, true, None);
        assert_eq!(filtered.len(), 1); // System disk included
    }
}
