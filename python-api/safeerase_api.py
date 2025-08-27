"""
SafeErase Python API - High-level Python interface to SafeErase core functionality
"""

import asyncio
import ctypes
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import platform
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class WipeAlgorithm(Enum):
    """Available wiping algorithms"""
    NIST_800_88 = "nist_800_88"
    DOD_5220_22_M = "dod_5220_22_m"
    GUTMANN = "gutmann"
    ATA_SECURE_ERASE = "ata_secure_erase"
    NVME_FORMAT = "nvme_format"
    RANDOM_OVERWRITE = "random_overwrite"

class WipeStatus(Enum):
    """Wipe operation status"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    IN_PROGRESS = "in_progress"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeviceType(Enum):
    """Storage device types"""
    HDD = "hdd"
    SSD = "ssd"
    NVME = "nvme"
    USB = "usb"
    SD_CARD = "sd_card"
    EMMC = "emmc"
    UNKNOWN = "unknown"

@dataclass
class DeviceInfo:
    """Storage device information"""
    id: str
    name: str
    path: str
    size: int
    device_type: DeviceType
    interface: str
    is_removable: bool
    is_system_disk: bool
    supports_secure_erase: bool
    supports_hpa_dco: bool
    serial_number: str
    model: str
    firmware_version: str
    health_status: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['device_type'] = self.device_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceInfo':
        """Create from dictionary"""
        data['device_type'] = DeviceType(data['device_type'])
        return cls(**data)

@dataclass
class WipeOptions:
    """Wipe operation options"""
    verify_wipe: bool = True
    clear_hpa: bool = True
    clear_dco: bool = True
    verification_samples: int = 1000
    block_size: int = 1048576  # 1MB
    passes: Optional[int] = None  # Override algorithm default
    pattern: Optional[bytes] = None  # Custom pattern
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        if data['pattern']:
            data['pattern'] = data['pattern'].hex()
        return data

@dataclass
class WipeProgress:
    """Wipe operation progress"""
    operation_id: str
    status: WipeStatus
    progress_percent: float
    current_pass: int
    total_passes: int
    bytes_processed: int
    total_bytes: int
    speed_mbps: float
    estimated_remaining: Optional[timedelta]
    current_operation: str
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if data['estimated_remaining']:
            data['estimated_remaining'] = data['estimated_remaining'].total_seconds()
        return data

@dataclass
class WipeResult:
    """Wipe operation result"""
    operation_id: str
    device_id: str
    algorithm: WipeAlgorithm
    status: WipeStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[timedelta]
    bytes_wiped: int
    passes_completed: int
    verification_passed: Optional[bool]
    hpa_detected: bool
    hpa_cleared: bool
    dco_detected: bool
    dco_cleared: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['algorithm'] = self.algorithm.value
        data['status'] = self.status.value
        data['started_at'] = self.started_at.isoformat()
        if data['completed_at']:
            data['completed_at'] = data['completed_at'].isoformat()
        if data['duration']:
            data['duration'] = data['duration'].total_seconds()
        return data

@dataclass
class CertificateInfo:
    """Certificate information"""
    certificate_id: str
    operation_id: str
    device_info: DeviceInfo
    wipe_result: WipeResult
    generated_at: datetime
    signature: str
    verification_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'certificate_id': self.certificate_id,
            'operation_id': self.operation_id,
            'device_info': self.device_info.to_dict(),
            'wipe_result': self.wipe_result.to_dict(),
            'generated_at': self.generated_at.isoformat(),
            'signature': self.signature,
            'verification_url': self.verification_url
        }

class SafeEraseAPI:
    """High-level Python API for SafeErase functionality"""
    
    def __init__(self, library_path: Optional[str] = None):
        """Initialize the SafeErase API
        
        Args:
            library_path: Path to the SafeErase core library
        """
        self.library_path = library_path or self._get_default_library_path()
        self.library = None
        self.initialized = False
        self.active_operations = {}
        self.progress_callbacks = {}
        
        self._load_library()
        
    def _get_default_library_path(self) -> str:
        """Get default library path based on platform"""
        if platform.system() == "Windows":
            return "safe_erase_core.dll"
        elif platform.system() == "Darwin":
            return "libsafe_erase_core.dylib"
        else:
            return "libsafe_erase_core.so"
            
    def _load_library(self):
        """Load the SafeErase core library"""
        try:
            self.library = ctypes.CDLL(self.library_path)
            self._setup_function_signatures()
            self.initialized = True
        except OSError as e:
            # Library not found, use mock implementation for development
            print(f"Warning: SafeErase core library not found ({e}). Using mock implementation.")
            self.library = None
            self.initialized = True
            
    def _setup_function_signatures(self):
        """Set up function signatures for the C library"""
        if not self.library:
            return
            
        # Define function signatures
        # This would be implemented based on the actual C API
        pass
        
    async def initialize(self) -> bool:
        """Initialize the SafeErase system
        
        Returns:
            True if initialization successful
        """
        if not self.initialized:
            return False
            
        # Perform any necessary initialization
        return True
        
    async def discover_devices(self) -> List[DeviceInfo]:
        """Discover available storage devices
        
        Returns:
            List of discovered devices
        """
        if self.library:
            # Call actual library function
            # This would be implemented with proper C API calls
            pass
            
        # Mock implementation for development
        return await self._mock_discover_devices()
        
    async def _mock_discover_devices(self) -> List[DeviceInfo]:
        """Mock device discovery for development"""
        await asyncio.sleep(1)  # Simulate discovery time
        
        devices = [
            DeviceInfo(
                id="dev_001",
                name="Samsung SSD 980 PRO 1TB",
                path="/dev/nvme0n1" if platform.system() != "Windows" else "\\\\.\\PhysicalDrive0",
                size=1000204886016,
                device_type=DeviceType.NVME,
                interface="NVMe PCIe 4.0",
                is_removable=False,
                is_system_disk=True,
                supports_secure_erase=True,
                supports_hpa_dco=False,
                serial_number="S6B2NS0R123456",
                model="Samsung SSD 980 PRO 1TB",
                firmware_version="5B2QGXA7",
                health_status="Good"
            ),
            DeviceInfo(
                id="dev_002",
                name="SanDisk Ultra USB 3.0 32GB",
                path="/dev/sdb" if platform.system() != "Windows" else "\\\\.\\PhysicalDrive1",
                size=32212254720,
                device_type=DeviceType.USB,
                interface="USB 3.0",
                is_removable=True,
                is_system_disk=False,
                supports_secure_erase=False,
                supports_hpa_dco=False,
                serial_number="4C530001234567890123",
                model="SanDisk Ultra USB 3.0",
                firmware_version="1.00",
                health_status="Good"
            ),
            DeviceInfo(
                id="dev_003",
                name="Western Digital Blue 2TB",
                path="/dev/sdc" if platform.system() != "Windows" else "\\\\.\\PhysicalDrive2",
                size=2000398934016,
                device_type=DeviceType.HDD,
                interface="SATA 6.0 Gb/s",
                is_removable=False,
                is_system_disk=False,
                supports_secure_erase=True,
                supports_hpa_dco=True,
                serial_number="WD-WCC4N7123456",
                model="WDC WD20EZRZ-00Z5HB0",
                firmware_version="80.00A80",
                health_status="Good"
            )
        ]
        
        return devices
        
    async def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get detailed information about a specific device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Device information or None if not found
        """
        devices = await self.discover_devices()
        for device in devices:
            if device.id == device_id:
                return device
        return None
        
    def get_available_algorithms(self) -> List[Dict[str, Union[str, int]]]:
        """Get list of available wiping algorithms
        
        Returns:
            List of algorithm information
        """
        return [
            {
                "id": WipeAlgorithm.NIST_800_88.value,
                "name": "NIST SP 800-88 Rev. 1",
                "description": "Single pass with verification (Recommended for SSDs)",
                "passes": 1,
                "security_level": "Standard",
                "compliance": ["NIST SP 800-88"],
                "recommended_for": ["SSD", "NVMe"]
            },
            {
                "id": WipeAlgorithm.DOD_5220_22_M.value,
                "name": "DoD 5220.22-M",
                "description": "Three-pass overwrite (High security)",
                "passes": 3,
                "security_level": "High",
                "compliance": ["DoD 5220.22-M"],
                "recommended_for": ["HDD", "SSD"]
            },
            {
                "id": WipeAlgorithm.GUTMANN.value,
                "name": "Gutmann Algorithm",
                "description": "35-pass maximum security (Legacy drives)",
                "passes": 35,
                "security_level": "Maximum",
                "compliance": ["Academic Research"],
                "recommended_for": ["HDD"]
            },
            {
                "id": WipeAlgorithm.ATA_SECURE_ERASE.value,
                "name": "ATA Secure Erase",
                "description": "Hardware-level secure erase (Fast)",
                "passes": 1,
                "security_level": "High",
                "compliance": ["ATA Standard"],
                "recommended_for": ["SSD", "HDD"]
            },
            {
                "id": WipeAlgorithm.NVME_FORMAT.value,
                "name": "NVMe Format",
                "description": "NVMe Format with secure erase (Very fast)",
                "passes": 1,
                "security_level": "High",
                "compliance": ["NVMe Standard"],
                "recommended_for": ["NVMe"]
            }
        ]
        
    async def start_wipe(
        self,
        device_id: str,
        algorithm: WipeAlgorithm,
        options: Optional[WipeOptions] = None
    ) -> str:
        """Start a wipe operation
        
        Args:
            device_id: Device to wipe
            algorithm: Wiping algorithm to use
            options: Wipe options
            
        Returns:
            Operation ID
        """
        if options is None:
            options = WipeOptions()
            
        operation_id = str(uuid.uuid4())
        
        # Get device info
        device = await self.get_device_info(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")
            
        # Create operation
        self.active_operations[operation_id] = {
            'device_id': device_id,
            'algorithm': algorithm,
            'options': options,
            'started_at': datetime.now(),
            'status': WipeStatus.INITIALIZING
        }
        
        # Start wipe in background
        asyncio.create_task(self._perform_wipe(operation_id, device, algorithm, options))
        
        return operation_id
        
    async def _perform_wipe(
        self,
        operation_id: str,
        device: DeviceInfo,
        algorithm: WipeAlgorithm,
        options: WipeOptions
    ):
        """Perform the actual wipe operation"""
        try:
            operation = self.active_operations[operation_id]
            operation['status'] = WipeStatus.IN_PROGRESS
            
            # Get algorithm info
            algo_info = next(
                (a for a in self.get_available_algorithms() if a['id'] == algorithm.value),
                None
            )
            
            if not algo_info:
                raise ValueError(f"Unknown algorithm: {algorithm}")
                
            total_passes = options.passes or algo_info['passes']
            
            # Simulate wipe progress
            for pass_num in range(1, total_passes + 1):
                operation['current_pass'] = pass_num
                operation['total_passes'] = total_passes
                
                # Simulate pass progress
                for progress in range(0, 101, 5):
                    if operation_id not in self.active_operations:
                        return  # Operation was cancelled
                        
                    overall_progress = ((pass_num - 1) * 100 + progress) / total_passes
                    
                    # Update progress
                    progress_info = WipeProgress(
                        operation_id=operation_id,
                        status=WipeStatus.IN_PROGRESS,
                        progress_percent=overall_progress,
                        current_pass=pass_num,
                        total_passes=total_passes,
                        bytes_processed=int(device.size * overall_progress / 100),
                        total_bytes=device.size,
                        speed_mbps=50.0 + (progress % 50),  # Mock speed
                        estimated_remaining=timedelta(
                            seconds=int((100 - overall_progress) * 2)
                        ),
                        current_operation=f"Pass {pass_num}: Overwriting data"
                    )
                    
                    # Call progress callback if set
                    if operation_id in self.progress_callbacks:
                        try:
                            await self.progress_callbacks[operation_id](progress_info)
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                            
                    await asyncio.sleep(0.1)  # Simulate work
                    
            # Verification phase
            if options.verify_wipe:
                operation['status'] = WipeStatus.VERIFYING
                
                for progress in range(0, 101, 10):
                    if operation_id not in self.active_operations:
                        return
                        
                    progress_info = WipeProgress(
                        operation_id=operation_id,
                        status=WipeStatus.VERIFYING,
                        progress_percent=100.0,
                        current_pass=total_passes,
                        total_passes=total_passes,
                        bytes_processed=device.size,
                        total_bytes=device.size,
                        speed_mbps=100.0,
                        estimated_remaining=timedelta(seconds=int((100 - progress) * 0.5)),
                        current_operation=f"Verifying wipe: {progress}%"
                    )
                    
                    if operation_id in self.progress_callbacks:
                        try:
                            await self.progress_callbacks[operation_id](progress_info)
                        except Exception:
                            pass
                            
                    await asyncio.sleep(0.2)
                    
            # Complete operation
            operation['status'] = WipeStatus.COMPLETED
            operation['completed_at'] = datetime.now()
            
            # Final progress update
            final_progress = WipeProgress(
                operation_id=operation_id,
                status=WipeStatus.COMPLETED,
                progress_percent=100.0,
                current_pass=total_passes,
                total_passes=total_passes,
                bytes_processed=device.size,
                total_bytes=device.size,
                speed_mbps=0.0,
                estimated_remaining=timedelta(0),
                current_operation="Wipe completed successfully"
            )
            
            if operation_id in self.progress_callbacks:
                try:
                    await self.progress_callbacks[operation_id](final_progress)
                except Exception:
                    pass
                    
        except Exception as e:
            # Handle operation failure
            operation = self.active_operations.get(operation_id)
            if operation:
                operation['status'] = WipeStatus.FAILED
                operation['error_message'] = str(e)
                operation['completed_at'] = datetime.now()
                
    async def get_wipe_progress(self, operation_id: str) -> Optional[WipeProgress]:
        """Get progress of a wipe operation
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            Progress information or None if operation not found
        """
        operation = self.active_operations.get(operation_id)
        if not operation:
            return None
            
        # This would typically query the actual operation status
        # For now, return a mock progress based on operation state
        return WipeProgress(
            operation_id=operation_id,
            status=operation['status'],
            progress_percent=50.0,  # Mock progress
            current_pass=1,
            total_passes=1,
            bytes_processed=0,
            total_bytes=0,
            speed_mbps=0.0,
            estimated_remaining=None,
            current_operation="Mock operation"
        )
        
    async def cancel_wipe(self, operation_id: str) -> bool:
        """Cancel a wipe operation
        
        Args:
            operation_id: Operation to cancel
            
        Returns:
            True if cancellation successful
        """
        if operation_id in self.active_operations:
            operation = self.active_operations[operation_id]
            operation['status'] = WipeStatus.CANCELLED
            operation['completed_at'] = datetime.now()
            return True
        return False
        
    def set_progress_callback(
        self,
        operation_id: str,
        callback: Callable[[WipeProgress], None]
    ):
        """Set progress callback for an operation
        
        Args:
            operation_id: Operation identifier
            callback: Progress callback function
        """
        self.progress_callbacks[operation_id] = callback
        
    async def get_wipe_result(self, operation_id: str) -> Optional[WipeResult]:
        """Get result of a completed wipe operation
        
        Args:
            operation_id: Operation identifier
            
        Returns:
            Wipe result or None if operation not found
        """
        operation = self.active_operations.get(operation_id)
        if not operation:
            return None
            
        return WipeResult(
            operation_id=operation_id,
            device_id=operation['device_id'],
            algorithm=operation['algorithm'],
            status=operation['status'],
            started_at=operation['started_at'],
            completed_at=operation.get('completed_at'),
            duration=operation.get('completed_at', datetime.now()) - operation['started_at'],
            bytes_wiped=0,  # Would be filled from actual operation
            passes_completed=operation.get('total_passes', 1),
            verification_passed=True,  # Mock result
            hpa_detected=False,
            hpa_cleared=False,
            dco_detected=False,
            dco_cleared=False,
            error_message=operation.get('error_message')
        )
        
    async def generate_certificate(
        self,
        operation_id: str,
        output_path: Optional[str] = None
    ) -> CertificateInfo:
        """Generate a tamper-proof certificate for a wipe operation
        
        Args:
            operation_id: Operation identifier
            output_path: Output file path (optional)
            
        Returns:
            Certificate information
        """
        # Get operation result
        wipe_result = await self.get_wipe_result(operation_id)
        if not wipe_result:
            raise ValueError(f"Operation not found: {operation_id}")
            
        # Get device info
        device_info = await self.get_device_info(wipe_result.device_id)
        if not device_info:
            raise ValueError(f"Device not found: {wipe_result.device_id}")
            
        # Generate certificate
        certificate_id = str(uuid.uuid4())
        
        certificate = CertificateInfo(
            certificate_id=certificate_id,
            operation_id=operation_id,
            device_info=device_info,
            wipe_result=wipe_result,
            generated_at=datetime.now(),
            signature="mock_signature_" + certificate_id[:8],  # Mock signature
            verification_url=f"https://verify.safeerase.com/cert/{certificate_id}"
        )
        
        # Save certificate if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(certificate.to_dict(), f, indent=2)
                
        return certificate
        
    async def verify_certificate(self, certificate_path: str) -> bool:
        """Verify a certificate file
        
        Args:
            certificate_path: Path to certificate file
            
        Returns:
            True if certificate is valid
        """
        try:
            with open(certificate_path, 'r') as f:
                cert_data = json.load(f)
                
            # Basic validation (would include cryptographic verification)
            required_fields = [
                'certificate_id', 'operation_id', 'device_info',
                'wipe_result', 'generated_at', 'signature'
            ]
            
            for field in required_fields:
                if field not in cert_data:
                    return False
                    
            return True
            
        except Exception:
            return False
            
    def cleanup(self):
        """Cleanup API resources"""
        self.active_operations.clear()
        self.progress_callbacks.clear()
        
        if self.library:
            # Cleanup library resources
            pass

# Convenience functions for common operations

async def quick_wipe(
    device_path: str,
    algorithm: WipeAlgorithm = WipeAlgorithm.NIST_800_88,
    progress_callback: Optional[Callable[[WipeProgress], None]] = None
) -> WipeResult:
    """Perform a quick wipe operation
    
    Args:
        device_path: Path to device to wipe
        algorithm: Wiping algorithm to use
        progress_callback: Optional progress callback
        
    Returns:
        Wipe result
    """
    api = SafeEraseAPI()
    await api.initialize()
    
    # Find device by path
    devices = await api.discover_devices()
    device = next((d for d in devices if d.path == device_path), None)
    
    if not device:
        raise ValueError(f"Device not found: {device_path}")
        
    # Start wipe
    operation_id = await api.start_wipe(device.id, algorithm)
    
    if progress_callback:
        api.set_progress_callback(operation_id, progress_callback)
        
    # Wait for completion
    while True:
        progress = await api.get_wipe_progress(operation_id)
        if not progress or progress.status in [WipeStatus.COMPLETED, WipeStatus.FAILED, WipeStatus.CANCELLED]:
            break
        await asyncio.sleep(1)
        
    result = await api.get_wipe_result(operation_id)
    api.cleanup()
    
    return result

# Example usage
if __name__ == "__main__":
    async def main():
        api = SafeEraseAPI()
        await api.initialize()
        
        # Discover devices
        devices = await api.discover_devices()
        print(f"Found {len(devices)} devices:")
        for device in devices:
            print(f"  {device.name} ({device.get_size_formatted()})")
            
        # Get algorithms
        algorithms = api.get_available_algorithms()
        print(f"\nAvailable algorithms:")
        for algo in algorithms:
            print(f"  {algo['name']} - {algo['description']}")
            
        api.cleanup()
        
    asyncio.run(main())
