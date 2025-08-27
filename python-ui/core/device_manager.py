"""
Device Manager - Handles storage device discovery and management
"""

import asyncio
import platform
import psutil
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path

from python_ui.utils.logger import get_logger
from python_ui.utils.platform_utils import get_platform_info, check_admin_privileges

@dataclass
class DeviceInfo:
    """Storage device information"""
    id: str
    name: str
    path: str
    size: int
    device_type: str
    interface: str
    is_removable: bool
    is_system_disk: bool
    supports_secure_erase: bool
    supports_hpa_dco: bool
    health_status: str
    serial_number: str
    model: str
    firmware_version: str
    
    def get_size_formatted(self) -> str:
        """Get formatted size string"""
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{size:.1f} {units[unit_index]}"

class DeviceManager:
    """Manages storage device discovery and operations"""
    
    def __init__(self):
        self.logger = get_logger("DeviceManager")
        self.platform_info = get_platform_info()
        self.cached_devices = {}
        self.last_discovery = None
        
        self.logger.info(f"Device manager initialized for {self.platform_info['platform']}")
        
    async def discover_devices(self) -> List[DeviceInfo]:
        """Discover all available storage devices"""
        self.logger.info("Starting device discovery...")
        
        try:
            if self.platform_info['platform'] == 'Windows':
                devices = await self._discover_windows_devices()
            elif self.platform_info['platform'] == 'Linux':
                devices = await self._discover_linux_devices()
            elif self.platform_info['platform'] == 'Darwin':
                devices = await self._discover_macos_devices()
            else:
                raise RuntimeError(f"Unsupported platform: {self.platform_info['platform']}")
                
            # Update cache
            self.cached_devices = {device.id: device for device in devices}
            self.last_discovery = asyncio.get_event_loop().time()
            
            self.logger.info(f"Discovered {len(devices)} storage devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Device discovery failed: {e}")
            raise
            
    async def _discover_windows_devices(self) -> List[DeviceInfo]:
        """Discover devices on Windows"""
        devices = []
        
        try:
            import wmi
            c = wmi.WMI()
            
            # Get physical drives
            for disk in c.Win32_DiskDrive():
                try:
                    device = await self._create_windows_device_info(disk)
                    if device:
                        devices.append(device)
                except Exception as e:
                    self.logger.warning(f"Error processing Windows device {disk.DeviceID}: {e}")
                    
        except ImportError:
            self.logger.warning("WMI not available, using psutil fallback")
            devices = await self._discover_psutil_devices()
            
        return devices
        
    async def _create_windows_device_info(self, disk) -> Optional[DeviceInfo]:
        """Create device info from Windows WMI disk object"""
        try:
            # Basic information
            device_id = f"win_{disk.Index}"
            name = disk.Model or f"Drive {disk.Index}"
            path = f"\\\\.\\PhysicalDrive{disk.Index}"
            size = int(disk.Size) if disk.Size else 0
            
            # Device type detection
            device_type = "Unknown"
            interface = "Unknown"
            
            if disk.InterfaceType:
                interface = disk.InterfaceType
                if "USB" in interface.upper():
                    device_type = "USB Storage"
                elif "SATA" in interface.upper():
                    device_type = "SATA Drive"
                elif "SCSI" in interface.upper():
                    device_type = "SCSI Drive"
                elif "IDE" in interface.upper():
                    device_type = "IDE Drive"
                    
            # Check if removable
            is_removable = disk.MediaType and "Removable" in disk.MediaType
            
            # Check if system disk (simplified check)
            is_system_disk = disk.Index == 0  # Usually the first drive
            
            # Hardware capabilities (would need more detailed detection)
            supports_secure_erase = interface in ["SATA", "NVMe"]
            supports_hpa_dco = device_type in ["SATA Drive", "IDE Drive"]
            
            return DeviceInfo(
                id=device_id,
                name=name,
                path=path,
                size=size,
                device_type=device_type,
                interface=interface,
                is_removable=is_removable,
                is_system_disk=is_system_disk,
                supports_secure_erase=supports_secure_erase,
                supports_hpa_dco=supports_hpa_dco,
                health_status="Good",  # Would need SMART data
                serial_number=disk.SerialNumber or "Unknown",
                model=disk.Model or "Unknown",
                firmware_version=disk.FirmwareRevision or "Unknown"
            )
            
        except Exception as e:
            self.logger.error(f"Error creating Windows device info: {e}")
            return None
            
    async def _discover_linux_devices(self) -> List[DeviceInfo]:
        """Discover devices on Linux"""
        devices = []
        
        try:
            # Read from /proc/partitions and /sys/block
            block_devices = []
            
            # Get block devices from /sys/block
            sys_block = Path("/sys/block")
            if sys_block.exists():
                for device_path in sys_block.iterdir():
                    if device_path.name.startswith(('sd', 'hd', 'nvme', 'mmcblk')):
                        block_devices.append(device_path.name)
                        
            # Create device info for each block device
            for device_name in block_devices:
                try:
                    device = await self._create_linux_device_info(device_name)
                    if device:
                        devices.append(device)
                except Exception as e:
                    self.logger.warning(f"Error processing Linux device {device_name}: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Linux device discovery error: {e}")
            devices = await self._discover_psutil_devices()
            
        return devices
        
    async def _create_linux_device_info(self, device_name: str) -> Optional[DeviceInfo]:
        """Create device info from Linux block device"""
        try:
            device_path = f"/dev/{device_name}"
            sys_path = Path(f"/sys/block/{device_name}")
            
            # Basic information
            device_id = f"linux_{device_name}"
            name = device_name
            
            # Get size
            size = 0
            size_file = sys_path / "size"
            if size_file.exists():
                with open(size_file, 'r') as f:
                    sectors = int(f.read().strip())
                    size = sectors * 512  # Assume 512-byte sectors
                    
            # Detect device type and interface
            device_type = "Unknown"
            interface = "Unknown"
            
            if device_name.startswith('sd'):
                device_type = "SATA/SCSI Drive"
                interface = "SATA"
            elif device_name.startswith('hd'):
                device_type = "IDE Drive"
                interface = "IDE"
            elif device_name.startswith('nvme'):
                device_type = "NVMe SSD"
                interface = "NVMe"
            elif device_name.startswith('mmcblk'):
                device_type = "MMC/SD Card"
                interface = "MMC"
                
            # Check if removable
            removable_file = sys_path / "removable"
            is_removable = False
            if removable_file.exists():
                with open(removable_file, 'r') as f:
                    is_removable = f.read().strip() == "1"
                    
            # Check if system disk (simplified)
            is_system_disk = device_name in ['sda', 'hda', 'nvme0n1']
            
            # Hardware capabilities
            supports_secure_erase = interface in ["SATA", "NVMe"]
            supports_hpa_dco = interface in ["SATA", "IDE"]
            
            # Get model information
            model_file = sys_path / "device" / "model"
            model = "Unknown"
            if model_file.exists():
                with open(model_file, 'r') as f:
                    model = f.read().strip()
                    
            return DeviceInfo(
                id=device_id,
                name=name,
                path=device_path,
                size=size,
                device_type=device_type,
                interface=interface,
                is_removable=is_removable,
                is_system_disk=is_system_disk,
                supports_secure_erase=supports_secure_erase,
                supports_hpa_dco=supports_hpa_dco,
                health_status="Good",
                serial_number="Unknown",
                model=model,
                firmware_version="Unknown"
            )
            
        except Exception as e:
            self.logger.error(f"Error creating Linux device info for {device_name}: {e}")
            return None
            
    async def _discover_macos_devices(self) -> List[DeviceInfo]:
        """Discover devices on macOS"""
        devices = []
        
        try:
            # Use diskutil on macOS
            import subprocess
            
            result = subprocess.run(
                ['diskutil', 'list', '-plist'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse plist output (simplified)
            # In a real implementation, you'd use plistlib
            lines = result.stdout.split('\n')
            
            for line in lines:
                if '/dev/disk' in line and 'physical' in line:
                    disk_name = line.strip().split()[0]
                    try:
                        device = await self._create_macos_device_info(disk_name)
                        if device:
                            devices.append(device)
                    except Exception as e:
                        self.logger.warning(f"Error processing macOS device {disk_name}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"macOS device discovery error: {e}")
            devices = await self._discover_psutil_devices()
            
        return devices
        
    async def _create_macos_device_info(self, disk_name: str) -> Optional[DeviceInfo]:
        """Create device info from macOS disk"""
        try:
            import subprocess
            
            # Get disk info
            result = subprocess.run(
                ['diskutil', 'info', '-plist', disk_name],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse basic info (simplified)
            device_id = f"macos_{disk_name.replace('/dev/', '')}"
            name = disk_name
            path = disk_name
            
            # Extract size and other info from diskutil output
            # This is a simplified implementation
            size = 0
            device_type = "Unknown"
            interface = "Unknown"
            is_removable = False
            
            return DeviceInfo(
                id=device_id,
                name=name,
                path=path,
                size=size,
                device_type=device_type,
                interface=interface,
                is_removable=is_removable,
                is_system_disk=False,
                supports_secure_erase=True,
                supports_hpa_dco=False,
                health_status="Good",
                serial_number="Unknown",
                model="Unknown",
                firmware_version="Unknown"
            )
            
        except Exception as e:
            self.logger.error(f"Error creating macOS device info for {disk_name}: {e}")
            return None
            
    async def _discover_psutil_devices(self) -> List[DeviceInfo]:
        """Fallback device discovery using psutil"""
        devices = []
        
        try:
            disk_partitions = psutil.disk_partitions(all=True)
            processed_devices = set()
            
            for partition in disk_partitions:
                # Extract device name (remove partition number)
                device_path = partition.device
                
                # Skip if already processed
                if device_path in processed_devices:
                    continue
                processed_devices.add(device_path)
                
                try:
                    # Get disk usage
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    device_id = f"psutil_{hash(device_path) % 10000}"
                    name = device_path
                    
                    device = DeviceInfo(
                        id=device_id,
                        name=name,
                        path=device_path,
                        size=usage.total,
                        device_type="Unknown",
                        interface="Unknown",
                        is_removable=False,
                        is_system_disk=partition.mountpoint == "/",
                        supports_secure_erase=False,
                        supports_hpa_dco=False,
                        health_status="Unknown",
                        serial_number="Unknown",
                        model="Unknown",
                        firmware_version="Unknown"
                    )
                    
                    devices.append(device)
                    
                except Exception as e:
                    self.logger.warning(f"Error processing psutil device {device_path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"psutil device discovery error: {e}")
            
        return devices
        
    def get_device_details(self, device_id: str) -> Optional[Dict]:
        """Get detailed information about a specific device"""
        device = self.cached_devices.get(device_id)
        if not device:
            return None
            
        return {
            'basic_info': {
                'id': device.id,
                'name': device.name,
                'path': device.path,
                'size': device.size,
                'size_formatted': device.get_size_formatted(),
                'type': device.device_type,
                'interface': device.interface,
            },
            'capabilities': {
                'is_removable': device.is_removable,
                'is_system_disk': device.is_system_disk,
                'supports_secure_erase': device.supports_secure_erase,
                'supports_hpa_dco': device.supports_hpa_dco,
            },
            'hardware_info': {
                'serial_number': device.serial_number,
                'model': device.model,
                'firmware_version': device.firmware_version,
                'health_status': device.health_status,
            }
        }
        
    def has_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        return check_admin_privileges()
        
    def get_platform_info(self) -> Dict:
        """Get platform information"""
        return self.platform_info
        
    def cleanup(self):
        """Cleanup device manager resources"""
        self.logger.info("Cleaning up device manager...")
        self.cached_devices.clear()
