//! Platform-specific implementations for device access and operations

use serde::{Deserialize, Serialize};
use crate::device::{DeviceType, StorageInterface, HealthStatus};
use crate::error::Result;

#[cfg(target_os = "windows")]
mod windows;
#[cfg(target_os = "windows")]
pub use windows::*;

#[cfg(target_os = "linux")]
mod linux;
#[cfg(target_os = "linux")]
pub use linux::*;

#[cfg(target_os = "macos")]
mod macos;
#[cfg(target_os = "macos")]
pub use macos::*;

/// Platform-agnostic device handle
#[derive(Debug)]
pub struct DeviceHandle {
    #[cfg(target_os = "windows")]
    pub(crate) handle: windows::WindowsDeviceHandle,
    
    #[cfg(target_os = "linux")]
    pub(crate) handle: linux::LinuxDeviceHandle,
    
    #[cfg(target_os = "macos")]
    pub(crate) handle: macos::MacOSDeviceHandle,
}

/// Basic device information from platform APIs
#[derive(Debug, Clone)]
pub struct PlatformDeviceInfo {
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
}

/// SMART information from device
#[derive(Debug, Clone, Default)]
pub struct SmartInfo {
    pub temperature: Option<i32>,
    pub health_status: HealthStatus,
    pub power_on_hours: Option<u64>,
    pub power_cycle_count: Option<u64>,
    pub reallocated_sectors: Option<u64>,
    pub pending_sectors: Option<u64>,
}

/// Device capabilities for wiping operations
#[derive(Debug, Clone)]
pub struct PlatformDeviceCapabilities {
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

/// Check if the current process has administrative privileges
pub fn has_admin_privileges() -> bool {
    #[cfg(target_os = "windows")]
    return windows::has_admin_privileges();
    
    #[cfg(target_os = "linux")]
    return linux::has_admin_privileges();
    
    #[cfg(target_os = "macos")]
    return macos::has_admin_privileges();
}

/// Enumerate all storage devices on the system
pub async fn enumerate_storage_devices() -> Result<Vec<String>> {
    #[cfg(target_os = "windows")]
    return windows::enumerate_storage_devices().await;
    
    #[cfg(target_os = "linux")]
    return linux::enumerate_storage_devices().await;
    
    #[cfg(target_os = "macos")]
    return macos::enumerate_storage_devices().await;
}

/// Open a device for low-level access
pub async fn open_device(device_path: &str) -> Result<DeviceHandle> {
    #[cfg(target_os = "windows")]
    {
        let handle = windows::open_device(device_path).await?;
        Ok(DeviceHandle { handle })
    }
    
    #[cfg(target_os = "linux")]
    {
        let handle = linux::open_device(device_path).await?;
        Ok(DeviceHandle { handle })
    }
    
    #[cfg(target_os = "macos")]
    {
        let handle = macos::open_device(device_path).await?;
        Ok(DeviceHandle { handle })
    }
}

/// Get basic device information
pub async fn get_device_info(handle: &DeviceHandle) -> Result<PlatformDeviceInfo> {
    #[cfg(target_os = "windows")]
    return windows::get_device_info(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::get_device_info(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::get_device_info(&handle.handle).await;
}

/// Get SMART information from device
pub async fn get_smart_info(handle: &DeviceHandle) -> Result<SmartInfo> {
    #[cfg(target_os = "windows")]
    return windows::get_smart_info(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::get_smart_info(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::get_smart_info(&handle.handle).await;
}

/// Query device capabilities for wiping operations
pub async fn query_device_capabilities(handle: &DeviceHandle) -> Result<PlatformDeviceCapabilities> {
    #[cfg(target_os = "windows")]
    return windows::query_device_capabilities(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::query_device_capabilities(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::query_device_capabilities(&handle.handle).await;
}

/// Execute ATA Secure Erase command
pub async fn ata_secure_erase(handle: &DeviceHandle, enhanced: bool) -> Result<()> {
    #[cfg(target_os = "windows")]
    return windows::ata_secure_erase(&handle.handle, enhanced).await;
    
    #[cfg(target_os = "linux")]
    return linux::ata_secure_erase(&handle.handle, enhanced).await;
    
    #[cfg(target_os = "macos")]
    return macos::ata_secure_erase(&handle.handle, enhanced).await;
}

/// Execute NVMe Format command
pub async fn nvme_format(handle: &DeviceHandle, secure_erase: bool) -> Result<()> {
    #[cfg(target_os = "windows")]
    return windows::nvme_format(&handle.handle, secure_erase).await;
    
    #[cfg(target_os = "linux")]
    return linux::nvme_format(&handle.handle, secure_erase).await;
    
    #[cfg(target_os = "macos")]
    return macos::nvme_format(&handle.handle, secure_erase).await;
}

/// Write data to device sectors
pub async fn write_sectors(
    handle: &DeviceHandle,
    start_lba: u64,
    data: &[u8],
) -> Result<usize> {
    #[cfg(target_os = "windows")]
    return windows::write_sectors(&handle.handle, start_lba, data).await;
    
    #[cfg(target_os = "linux")]
    return linux::write_sectors(&handle.handle, start_lba, data).await;
    
    #[cfg(target_os = "macos")]
    return macos::write_sectors(&handle.handle, start_lba, data).await;
}

/// Read data from device sectors
pub async fn read_sectors(
    handle: &DeviceHandle,
    start_lba: u64,
    buffer: &mut [u8],
) -> Result<usize> {
    #[cfg(target_os = "windows")]
    return windows::read_sectors(&handle.handle, start_lba, buffer).await;
    
    #[cfg(target_os = "linux")]
    return linux::read_sectors(&handle.handle, start_lba, buffer).await;
    
    #[cfg(target_os = "macos")]
    return macos::read_sectors(&handle.handle, start_lba, buffer).await;
}

/// Flush device write cache
pub async fn flush_cache(handle: &DeviceHandle) -> Result<()> {
    #[cfg(target_os = "windows")]
    return windows::flush_cache(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::flush_cache(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::flush_cache(&handle.handle).await;
}

/// Detect and clear HPA (Host Protected Area)
pub async fn detect_and_clear_hpa(handle: &DeviceHandle) -> Result<bool> {
    #[cfg(target_os = "windows")]
    return windows::detect_and_clear_hpa(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::detect_and_clear_hpa(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::detect_and_clear_hpa(&handle.handle).await;
}

/// Detect and clear DCO (Device Configuration Overlay)
pub async fn detect_and_clear_dco(handle: &DeviceHandle) -> Result<bool> {
    #[cfg(target_os = "windows")]
    return windows::detect_and_clear_dco(&handle.handle).await;
    
    #[cfg(target_os = "linux")]
    return linux::detect_and_clear_dco(&handle.handle).await;
    
    #[cfg(target_os = "macos")]
    return macos::detect_and_clear_dco(&handle.handle).await;
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_privilege_check() {
        // This test will vary based on how the test is run
        let has_privs = has_admin_privileges();
        // Just ensure it doesn't panic
        println!("Has admin privileges: {}", has_privs);
    }
}
