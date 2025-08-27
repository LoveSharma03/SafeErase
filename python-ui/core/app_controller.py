"""
SafeErase Application Controller
Manages the core application logic and coordinates between UI and backend
"""

import asyncio
import threading
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass

from python_ui.core.device_manager import DeviceManager
from python_ui.core.wipe_engine import WipeEngine
from python_ui.core.certificate_manager import CertificateManager
from python_ui.utils.logger import get_logger

@dataclass
class WipeOperation:
    """Represents a wipe operation"""
    id: str
    device_id: str
    algorithm: str
    status: str
    progress: float
    started_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None

class SafeEraseController:
    """Main application controller"""
    
    def __init__(self, config):
        self.config = config
        self.logger = get_logger("SafeEraseController")
        
        # Core managers
        self.device_manager = DeviceManager()
        self.wipe_engine = WipeEngine()
        self.certificate_manager = CertificateManager()
        
        # Application state
        self.devices = {}
        self.active_operations = {}
        self.completed_operations = []
        
        # Event callbacks
        self.device_discovered_callback = None
        self.operation_progress_callback = None
        self.operation_completed_callback = None
        
        # Background thread for async operations
        self.background_thread = None
        self.event_loop = None
        self.shutdown_event = threading.Event()
        
        self.logger.info("SafeErase controller initialized")
        
    def start_background_thread(self):
        """Start the background thread for async operations"""
        if self.background_thread is None or not self.background_thread.is_alive():
            self.background_thread = threading.Thread(
                target=self._run_background_loop,
                daemon=True
            )
            self.background_thread.start()
            self.logger.info("Background thread started")
            
    def _run_background_loop(self):
        """Run the background event loop"""
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        
        try:
            self.event_loop.run_until_complete(self._background_tasks())
        except Exception as e:
            self.logger.error(f"Background loop error: {e}")
        finally:
            self.event_loop.close()
            
    async def _background_tasks(self):
        """Background tasks runner"""
        while not self.shutdown_event.is_set():
            try:
                # Update operation progress
                await self._update_operation_progress()
                
                # Check for device changes
                await self._check_device_changes()
                
                # Sleep before next iteration
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Background task error: {e}")
                await asyncio.sleep(5.0)
                
    async def _update_operation_progress(self):
        """Update progress for active operations"""
        for operation_id, operation in list(self.active_operations.items()):
            try:
                # Get progress from wipe engine
                progress_info = await self.wipe_engine.get_progress(operation_id)
                
                if progress_info:
                    operation.progress = progress_info.get('progress', 0)
                    operation.status = progress_info.get('status', 'unknown')
                    
                    # Check if operation completed
                    if operation.status in ['completed', 'failed', 'cancelled']:
                        self._handle_operation_completion(operation)
                        
                    # Notify UI of progress update
                    if self.operation_progress_callback:
                        self.operation_progress_callback(operation)
                        
            except Exception as e:
                self.logger.error(f"Error updating operation {operation_id}: {e}")
                
    async def _check_device_changes(self):
        """Check for device connection/disconnection"""
        try:
            current_devices = await self.device_manager.discover_devices()
            
            # Check for new devices
            for device in current_devices:
                if device.id not in self.devices:
                    self.devices[device.id] = device
                    if self.device_discovered_callback:
                        self.device_discovered_callback(device)
                        
            # Check for removed devices
            current_device_ids = {device.id for device in current_devices}
            removed_devices = set(self.devices.keys()) - current_device_ids
            
            for device_id in removed_devices:
                del self.devices[device_id]
                self.logger.info(f"Device removed: {device_id}")
                
        except Exception as e:
            self.logger.error(f"Error checking device changes: {e}")
            
    def _handle_operation_completion(self, operation: WipeOperation):
        """Handle completion of a wipe operation"""
        # Move from active to completed
        if operation.id in self.active_operations:
            del self.active_operations[operation.id]
            
        self.completed_operations.append(operation)
        
        # Generate certificate if successful
        if operation.status == 'completed':
            try:
                certificate = self.certificate_manager.generate_certificate(
                    operation, self.devices.get(operation.device_id)
                )
                operation.certificate_id = certificate.id
                self.logger.info(f"Certificate generated for operation {operation.id}")
            except Exception as e:
                self.logger.error(f"Failed to generate certificate: {e}")
                
        # Notify UI
        if self.operation_completed_callback:
            self.operation_completed_callback(operation)
            
        self.logger.info(f"Operation {operation.id} completed with status: {operation.status}")
        
    # Public API methods
    
    def set_device_discovered_callback(self, callback: Callable):
        """Set callback for device discovery events"""
        self.device_discovered_callback = callback
        
    def set_operation_progress_callback(self, callback: Callable):
        """Set callback for operation progress updates"""
        self.operation_progress_callback = callback
        
    def set_operation_completed_callback(self, callback: Callable):
        """Set callback for operation completion"""
        self.operation_completed_callback = callback
        
    async def discover_devices(self) -> List:
        """Discover available storage devices"""
        self.logger.info("Starting device discovery...")
        
        try:
            devices = await self.device_manager.discover_devices()
            
            # Update internal device list
            self.devices = {device.id: device for device in devices}
            
            self.logger.info(f"Discovered {len(devices)} devices")
            return devices
            
        except Exception as e:
            self.logger.error(f"Device discovery failed: {e}")
            raise
            
    def get_devices(self) -> List:
        """Get currently known devices"""
        return list(self.devices.values())
        
    def get_device(self, device_id: str):
        """Get a specific device by ID"""
        return self.devices.get(device_id)
        
    async def start_wipe_operation(self, device_id: str, algorithm: str, options: Dict) -> str:
        """Start a wipe operation"""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")
            
        # Create operation
        operation_id = str(uuid.uuid4())
        operation = WipeOperation(
            id=operation_id,
            device_id=device_id,
            algorithm=algorithm,
            status='starting',
            progress=0.0,
            started_at=datetime.now()
        )
        
        self.active_operations[operation_id] = operation
        
        try:
            # Start wipe in background
            await self.wipe_engine.start_wipe(operation_id, device, algorithm, options)
            
            operation.status = 'in_progress'
            self.logger.info(f"Wipe operation {operation_id} started for device {device_id}")
            
            return operation_id
            
        except Exception as e:
            operation.status = 'failed'
            operation.error_message = str(e)
            self.logger.error(f"Failed to start wipe operation: {e}")
            raise
            
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel an active wipe operation"""
        operation = self.active_operations.get(operation_id)
        if not operation:
            return False
            
        try:
            success = await self.wipe_engine.cancel_wipe(operation_id)
            
            if success:
                operation.status = 'cancelled'
                self.logger.info(f"Operation {operation_id} cancelled")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to cancel operation {operation_id}: {e}")
            return False
            
    def get_active_operations(self) -> List[WipeOperation]:
        """Get all active operations"""
        return list(self.active_operations.values())
        
    def get_completed_operations(self) -> List[WipeOperation]:
        """Get all completed operations"""
        return self.completed_operations.copy()
        
    def get_operation(self, operation_id: str) -> Optional[WipeOperation]:
        """Get a specific operation by ID"""
        # Check active operations first
        if operation_id in self.active_operations:
            return self.active_operations[operation_id]
            
        # Check completed operations
        for operation in self.completed_operations:
            if operation.id == operation_id:
                return operation
                
        return None
        
    def get_available_algorithms(self) -> List[Dict]:
        """Get available wiping algorithms"""
        return self.wipe_engine.get_available_algorithms()
        
    def validate_wipe_options(self, device_id: str, algorithm: str, options: Dict) -> Dict:
        """Validate wipe options for a device"""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device not found: {device_id}")
            
        return self.wipe_engine.validate_options(device, algorithm, options)
        
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'devices_count': len(self.devices),
            'active_operations': len(self.active_operations),
            'completed_operations': len(self.completed_operations),
            'admin_privileges': self.device_manager.has_admin_privileges(),
            'platform': self.device_manager.get_platform_info(),
        }
        
    def cleanup(self):
        """Cleanup controller resources"""
        self.logger.info("Cleaning up controller...")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Cancel active operations
        for operation_id in list(self.active_operations.keys()):
            try:
                asyncio.run_coroutine_threadsafe(
                    self.cancel_operation(operation_id),
                    self.event_loop
                ).result(timeout=5.0)
            except Exception as e:
                self.logger.error(f"Error cancelling operation {operation_id}: {e}")
                
        # Wait for background thread
        if self.background_thread and self.background_thread.is_alive():
            self.background_thread.join(timeout=10.0)
            
        # Cleanup managers
        self.device_manager.cleanup()
        self.wipe_engine.cleanup()
        self.certificate_manager.cleanup()
        
        self.logger.info("Controller cleanup completed")
