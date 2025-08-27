//! Linux-specific implementation for device access and operations

use std::fs::{File, OpenOptions};
use std::io::{Read, Write, Seek, SeekFrom};
use std::os::unix::fs::OpenOptionsExt;
use std::path::Path;
use tokio::fs;
use tokio::process::Command;
use tracing::{debug, warn, error};

use crate::device::{DeviceType, StorageInterface, HealthStatus};
use crate::error::{SafeEraseError, Result};
use super::{PlatformDeviceInfo, SmartInfo, PlatformDeviceCapabilities};

/// Linux-specific device handle
#[derive(Debug)]
pub struct LinuxDeviceHandle {
    file: File,
    device_path: String,
}

/// Check if the current process has root privileges
pub fn has_admin_privileges() -> bool {
    unsafe { libc::geteuid() == 0 }
}

/// Enumerate all storage devices on Linux
pub async fn enumerate_storage_devices() -> Result<Vec<String>> {
    let mut devices = Vec::new();
    
    // Check /proc/partitions for block devices
    let partitions_content = fs::read_to_string("/proc/partitions").await
        .map_err(|e| SafeEraseError::FileSystemError(e.to_string()))?;
    
    for line in partitions_content.lines().skip(2) { // Skip header lines
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 4 {
            let device_name = parts[3];
            // Only include whole disks, not partitions
            if !device_name.chars().last().unwrap_or('0').is_ascii_digit() {
                let device_path = format!("/dev/{}", device_name);
                if Path::new(&device_path).exists() {
                    devices.push(device_path);
                }
            }
        }
    }
    
    // Also check for NVMe devices
    if let Ok(mut nvme_dir) = fs::read_dir("/dev").await {
        while let Ok(Some(entry)) = nvme_dir.next_entry().await {
            let name = entry.file_name();
            let name_str = name.to_string_lossy();
            if name_str.starts_with("nvme") && name_str.ends_with("n1") {
                devices.push(format!("/dev/{}", name_str));
            }
        }
    }
    
    debug!("Found {} storage devices on Linux", devices.len());
    Ok(devices)
}

/// Open a device for low-level access on Linux
pub async fn open_device(device_path: &str) -> Result<LinuxDeviceHandle> {
    debug!("Opening Linux device: {}", device_path);
    
    let file = OpenOptions::new()
        .read(true)
        .write(true)
        .custom_flags(libc::O_DIRECT | libc::O_SYNC)
        .open(device_path)
        .map_err(|e| match e.kind() {
            std::io::ErrorKind::PermissionDenied => SafeEraseError::DeviceAccessDenied(device_path.to_string()),
            std::io::ErrorKind::NotFound => SafeEraseError::DeviceNotFound(device_path.to_string()),
            _ => SafeEraseError::DeviceIoError(e.to_string()),
        })?;
    
    Ok(LinuxDeviceHandle {
        file,
        device_path: device_path.to_string(),
    })
}

/// Get basic device information on Linux
pub async fn get_device_info(handle: &LinuxDeviceHandle) -> Result<PlatformDeviceInfo> {
    let device_name = Path::new(&handle.device_path)
        .file_name()
        .and_then(|n| n.to_str())
        .unwrap_or("unknown");
    
    // Get device size using blockdev
    let size = get_device_size(&handle.device_path).await?;
    
    // Try to get model and serial from sysfs
    let (model, serial) = get_device_identity(device_name).await;
    
    // Determine device type
    let device_type = determine_device_type(device_name, &model).await;
    let interface = determine_interface(device_name, &device_type).await;
    
    // Check if it's removable
    let is_removable = check_if_removable(device_name).await;
    
    // Check if it's a system disk (contains root filesystem)
    let is_system_disk = check_if_system_disk(&handle.device_path).await;
    
    Ok(PlatformDeviceInfo {
        name: device_name.to_string(),
        model: model.unwrap_or_else(|| "Unknown Model".to_string()),
        serial: serial.unwrap_or_else(|| "Unknown Serial".to_string()),
        size,
        device_type,
        interface,
        is_removable,
        is_system_disk,
        supports_secure_erase: device_type == DeviceType::SSD || device_type == DeviceType::NVMe,
        supports_hpa_dco: device_type == DeviceType::HDD || device_type == DeviceType::SSD,
        firmware_version: None, // TODO: Implement firmware version detection
    })
}

/// Get SMART information from device on Linux
pub async fn get_smart_info(handle: &LinuxDeviceHandle) -> Result<SmartInfo> {
    // Use smartctl to get SMART information
    let output = Command::new("smartctl")
        .args(["-A", &handle.device_path])
        .output()
        .await;
    
    match output {
        Ok(output) if output.status.success() => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            parse_smart_output(&stdout)
        }
        _ => {
            warn!("Failed to get SMART info for {}", handle.device_path);
            Ok(SmartInfo::default())
        }
    }
}

/// Query device capabilities for wiping operations on Linux
pub async fn query_device_capabilities(handle: &LinuxDeviceHandle) -> Result<PlatformDeviceCapabilities> {
    // Get basic geometry
    let logical_sector_size = get_logical_sector_size(&handle.device_path).await?;
    let physical_sector_size = get_physical_sector_size(&handle.device_path).await?;
    let max_lba = get_device_size(&handle.device_path).await? / logical_sector_size as u64;
    
    // Check for various capabilities
    let supports_trim = check_trim_support(&handle.device_path).await;
    let supports_ata_secure_erase = check_ata_secure_erase_support(&handle.device_path).await;
    let supports_nvme_format = handle.device_path.contains("nvme");
    
    Ok(PlatformDeviceCapabilities {
        supports_ata_secure_erase,
        supports_nvme_format,
        supports_trim,
        supports_write_same: true, // Most Linux systems support WRITE SAME
        supports_hpa_detection: true,
        supports_dco_detection: true,
        max_lba,
        logical_sector_size,
        physical_sector_size,
    })
}

/// Execute ATA Secure Erase command on Linux
pub async fn ata_secure_erase(handle: &LinuxDeviceHandle, enhanced: bool) -> Result<()> {
    let erase_type = if enhanced { "enhanced" } else { "normal" };
    
    // First, set a user password (required for secure erase)
    let set_password = Command::new("hdparm")
        .args(["--user-master", "u", "--security-set-pass", "p", &handle.device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if !set_password.status.success() {
        return Err(SafeEraseError::SystemCommandFailed(
            "Failed to set security password".to_string()
        ));
    }
    
    // Execute secure erase
    let erase_cmd = Command::new("hdparm")
        .args(["--user-master", "u", "--security-erase", erase_type, &handle.device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if !erase_cmd.status.success() {
        return Err(SafeEraseError::WipeFailed(
            "ATA Secure Erase command failed".to_string()
        ));
    }
    
    Ok(())
}

/// Execute NVMe Format command on Linux
pub async fn nvme_format(handle: &LinuxDeviceHandle, secure_erase: bool) -> Result<()> {
    let mut args = vec!["format", &handle.device_path];
    if secure_erase {
        args.extend_from_slice(&["--ses", "1"]);
    }
    
    let output = Command::new("nvme")
        .args(&args)
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if !output.status.success() {
        return Err(SafeEraseError::WipeFailed(
            "NVMe Format command failed".to_string()
        ));
    }
    
    Ok(())
}

/// Write data to device sectors on Linux
pub async fn write_sectors(
    handle: &LinuxDeviceHandle,
    start_lba: u64,
    data: &[u8],
) -> Result<usize> {
    // This is a simplified implementation
    // In a real implementation, you'd need to handle sector alignment and use proper I/O
    Err(SafeEraseError::Internal("Direct sector writing not yet implemented".to_string()))
}

/// Read data from device sectors on Linux
pub async fn read_sectors(
    handle: &LinuxDeviceHandle,
    start_lba: u64,
    buffer: &mut [u8],
) -> Result<usize> {
    // This is a simplified implementation
    // In a real implementation, you'd need to handle sector alignment and use proper I/O
    Err(SafeEraseError::Internal("Direct sector reading not yet implemented".to_string()))
}

/// Flush device write cache on Linux
pub async fn flush_cache(handle: &LinuxDeviceHandle) -> Result<()> {
    let output = Command::new("hdparm")
        .args(["-f", &handle.device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if !output.status.success() {
        warn!("Failed to flush cache for {}", handle.device_path);
    }
    
    Ok(())
}

/// Detect and clear HPA (Host Protected Area) on Linux
pub async fn detect_and_clear_hpa(handle: &LinuxDeviceHandle) -> Result<bool> {
    // Check for HPA using hdparm
    let output = Command::new("hdparm")
        .args(["-N", &handle.device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        if stdout.contains("HPA") {
            // Clear HPA
            let clear_output = Command::new("hdparm")
                .args(["-N", "p", &handle.device_path])
                .output()
                .await
                .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
            
            return Ok(clear_output.status.success());
        }
    }
    
    Ok(false)
}

/// Detect and clear DCO (Device Configuration Overlay) on Linux
pub async fn detect_and_clear_dco(handle: &LinuxDeviceHandle) -> Result<bool> {
    // DCO detection and clearing is more complex and typically requires specialized tools
    // This is a placeholder implementation
    warn!("DCO detection/clearing not fully implemented for Linux");
    Ok(false)
}

// Helper functions

async fn get_device_size(device_path: &str) -> Result<u64> {
    let output = Command::new("blockdev")
        .args(["--getsize64", device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if output.status.success() {
        let size_str = String::from_utf8_lossy(&output.stdout);
        size_str.trim().parse::<u64>()
            .map_err(|e| SafeEraseError::Internal(format!("Failed to parse device size: {}", e)))
    } else {
        Err(SafeEraseError::SystemCommandFailed("Failed to get device size".to_string()))
    }
}

async fn get_device_identity(device_name: &str) -> (Option<String>, Option<String>) {
    let model_path = format!("/sys/block/{}/device/model", device_name);
    let serial_path = format!("/sys/block/{}/device/serial", device_name);
    
    let model = fs::read_to_string(&model_path).await.ok()
        .map(|s| s.trim().to_string());
    let serial = fs::read_to_string(&serial_path).await.ok()
        .map(|s| s.trim().to_string());
    
    (model, serial)
}

async fn determine_device_type(device_name: &str, model: &Option<String>) -> DeviceType {
    if device_name.starts_with("nvme") {
        return DeviceType::NVMe;
    }
    
    // Check if it's an SSD by looking at the rotational attribute
    let rotational_path = format!("/sys/block/{}/queue/rotational", device_name);
    if let Ok(content) = fs::read_to_string(&rotational_path).await {
        if content.trim() == "0" {
            return DeviceType::SSD;
        } else {
            return DeviceType::HDD;
        }
    }
    
    // Fallback to model-based detection
    if let Some(model) = model {
        let model_lower = model.to_lowercase();
        if model_lower.contains("ssd") || model_lower.contains("solid") {
            return DeviceType::SSD;
        }
    }
    
    DeviceType::Unknown
}

async fn determine_interface(device_name: &str, device_type: &DeviceType) -> StorageInterface {
    match device_type {
        DeviceType::NVMe => StorageInterface::NVMe,
        _ => {
            if device_name.starts_with("sd") {
                StorageInterface::SATA
            } else if device_name.starts_with("hd") {
                StorageInterface::IDE
            } else {
                StorageInterface::Unknown
            }
        }
    }
}

async fn check_if_removable(device_name: &str) -> bool {
    let removable_path = format!("/sys/block/{}/removable", device_name);
    fs::read_to_string(&removable_path).await
        .map(|content| content.trim() == "1")
        .unwrap_or(false)
}

async fn check_if_system_disk(device_path: &str) -> bool {
    // Check if any partition of this device contains the root filesystem
    let output = Command::new("lsblk")
        .args(["-n", "-o", "MOUNTPOINT", device_path])
        .output()
        .await;
    
    if let Ok(output) = output {
        let stdout = String::from_utf8_lossy(&output.stdout);
        return stdout.lines().any(|line| line.trim() == "/");
    }
    
    false
}

async fn get_logical_sector_size(device_path: &str) -> Result<u32> {
    let output = Command::new("blockdev")
        .args(["--getss", device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if output.status.success() {
        let size_str = String::from_utf8_lossy(&output.stdout);
        size_str.trim().parse::<u32>()
            .map_err(|e| SafeEraseError::Internal(format!("Failed to parse sector size: {}", e)))
    } else {
        Ok(512) // Default sector size
    }
}

async fn get_physical_sector_size(device_path: &str) -> Result<u32> {
    let output = Command::new("blockdev")
        .args(["--getpbsz", device_path])
        .output()
        .await
        .map_err(|e| SafeEraseError::SystemCommandFailed(e.to_string()))?;
    
    if output.status.success() {
        let size_str = String::from_utf8_lossy(&output.stdout);
        size_str.trim().parse::<u32>()
            .map_err(|e| SafeEraseError::Internal(format!("Failed to parse physical sector size: {}", e)))
    } else {
        Ok(512) // Default sector size
    }
}

async fn check_trim_support(device_path: &str) -> bool {
    let output = Command::new("lsblk")
        .args(["-D", "-o", "DISC-GRAN", device_path])
        .output()
        .await;
    
    if let Ok(output) = output {
        let stdout = String::from_utf8_lossy(&output.stdout);
        return !stdout.trim().is_empty() && stdout.trim() != "0B";
    }
    
    false
}

async fn check_ata_secure_erase_support(device_path: &str) -> bool {
    let output = Command::new("hdparm")
        .args(["-I", device_path])
        .output()
        .await;
    
    if let Ok(output) = output {
        let stdout = String::from_utf8_lossy(&output.stdout);
        return stdout.contains("Security") && stdout.contains("erase");
    }
    
    false
}

fn parse_smart_output(output: &str) -> Result<SmartInfo> {
    let mut smart_info = SmartInfo::default();
    
    for line in output.lines() {
        if line.contains("Temperature_Celsius") {
            if let Some(temp_str) = line.split_whitespace().nth(9) {
                smart_info.temperature = temp_str.parse().ok();
            }
        }
        // Add more SMART attribute parsing as needed
    }
    
    smart_info.health_status = HealthStatus::Good; // Simplified
    Ok(smart_info)
}
