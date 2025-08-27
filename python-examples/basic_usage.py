#!/usr/bin/env python3
"""
SafeErase Python API - Basic Usage Examples
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from python_api.safeerase_api import SafeEraseAPI, WipeAlgorithm, WipeOptions, WipeStatus

async def example_device_discovery():
    """Example: Discover storage devices"""
    print("=== Device Discovery Example ===")
    
    api = SafeEraseAPI()
    await api.initialize()
    
    try:
        # Discover devices
        devices = await api.discover_devices()
        
        print(f"Found {len(devices)} storage devices:")
        for device in devices:
            print(f"  {device.name}")
            print(f"    Path: {device.path}")
            print(f"    Size: {device.get_size_formatted()}")
            print(f"    Type: {device.device_type.value}")
            print(f"    Removable: {'Yes' if device.is_removable else 'No'}")
            print(f"    System Disk: {'Yes' if device.is_system_disk else 'No'}")
            print()
            
    finally:
        api.cleanup()

async def example_algorithm_info():
    """Example: Get available algorithms"""
    print("=== Available Algorithms ===")
    
    api = SafeEraseAPI()
    await api.initialize()
    
    try:
        algorithms = api.get_available_algorithms()
        
        for algo in algorithms:
            print(f"Algorithm: {algo['name']}")
            print(f"  Description: {algo['description']}")
            print(f"  Passes: {algo['passes']}")
            print(f"  Security Level: {algo['security_level']}")
            print(f"  Compliance: {', '.join(algo['compliance'])}")
            print(f"  Recommended for: {', '.join(algo['recommended_for'])}")
            print()
            
    finally:
        api.cleanup()

async def example_wipe_operation():
    """Example: Perform a wipe operation (simulation)"""
    print("=== Wipe Operation Example ===")
    
    api = SafeEraseAPI()
    await api.initialize()
    
    try:
        # Discover devices
        devices = await api.discover_devices()
        if not devices:
            print("No devices found")
            return
            
        # Find a non-system device for demonstration
        target_device = None
        for device in devices:
            if not device.is_system_disk:
                target_device = device
                break
                
        if not target_device:
            print("No non-system devices found for safe demonstration")
            return
            
        print(f"Target device: {target_device.name}")
        print(f"Size: {target_device.get_size_formatted()}")
        print()
        
        # Configure wipe options
        options = WipeOptions(
            verify_wipe=True,
            clear_hpa=True,
            clear_dco=True,
            verification_samples=500  # Reduced for demo
        )
        
        # Progress callback
        def progress_callback(progress):
            print(f"Progress: {progress.progress_percent:.1f}% - {progress.current_operation}")
            
        # Start wipe operation
        print("Starting wipe operation...")
        operation_id = await api.start_wipe(
            target_device.id,
            WipeAlgorithm.NIST_800_88,
            options
        )
        
        # Set progress callback
        api.set_progress_callback(operation_id, progress_callback)
        
        print(f"Operation ID: {operation_id}")
        
        # Monitor progress
        while True:
            progress = await api.get_wipe_progress(operation_id)
            if not progress:
                break
                
            if progress.status in [WipeStatus.COMPLETED, WipeStatus.FAILED, WipeStatus.CANCELLED]:
                break
                
            await asyncio.sleep(1)
            
        # Get final result
        result = await api.get_wipe_result(operation_id)
        
        print(f"\nWipe operation completed!")
        print(f"Status: {result.status.value}")
        print(f"Duration: {result.duration}")
        print(f"Bytes wiped: {result.bytes_wiped:,}")
        print(f"Verification passed: {result.verification_passed}")
        
        # Generate certificate
        if result.status == WipeStatus.COMPLETED:
            print("\nGenerating certificate...")
            certificate = await api.generate_certificate(operation_id)
            print(f"Certificate ID: {certificate.certificate_id}")
            print(f"Generated at: {certificate.generated_at}")
            
    finally:
        api.cleanup()

async def example_certificate_verification():
    """Example: Verify a certificate"""
    print("=== Certificate Verification Example ===")
    
    api = SafeEraseAPI()
    await api.initialize()
    
    try:
        # This would typically verify an existing certificate file
        # For demonstration, we'll show the process
        
        cert_path = "example_certificate.json"
        
        # In a real scenario, you would have an actual certificate file
        print(f"Verifying certificate: {cert_path}")
        
        # Note: This would fail since the file doesn't exist
        # but shows the API usage
        try:
            is_valid = await api.verify_certificate(cert_path)
            print(f"Certificate valid: {is_valid}")
        except FileNotFoundError:
            print("Certificate file not found (this is expected in the demo)")
            
    finally:
        api.cleanup()

async def example_batch_operations():
    """Example: Batch operations on multiple devices"""
    print("=== Batch Operations Example ===")
    
    api = SafeEraseAPI()
    await api.initialize()
    
    try:
        # Discover devices
        devices = await api.discover_devices()
        
        # Filter non-system devices
        target_devices = [d for d in devices if not d.is_system_disk]
        
        if not target_devices:
            print("No non-system devices found for batch operation")
            return
            
        print(f"Found {len(target_devices)} devices for batch operation:")
        for device in target_devices:
            print(f"  {device.name} ({device.get_size_formatted()})")
            
        # Start operations for all devices
        operations = []
        for device in target_devices[:2]:  # Limit to 2 devices for demo
            print(f"\nStarting wipe for {device.name}...")
            operation_id = await api.start_wipe(
                device.id,
                WipeAlgorithm.NIST_800_88
            )
            operations.append({
                'id': operation_id,
                'device': device,
                'status': 'running'
            })
            
        # Monitor all operations
        print("\nMonitoring batch operations...")
        while operations:
            completed_ops = []
            
            for op in operations:
                progress = await api.get_wipe_progress(op['id'])
                if progress and progress.status in [WipeStatus.COMPLETED, WipeStatus.FAILED, WipeStatus.CANCELLED]:
                    result = await api.get_wipe_result(op['id'])
                    print(f"Device {op['device'].name}: {result.status.value}")
                    completed_ops.append(op)
                    
            # Remove completed operations
            for op in completed_ops:
                operations.remove(op)
                
            if operations:
                await asyncio.sleep(2)
                
        print("Batch operations completed!")
        
    finally:
        api.cleanup()

async def main():
    """Run all examples"""
    examples = [
        ("Device Discovery", example_device_discovery),
        ("Algorithm Information", example_algorithm_info),
        ("Wipe Operation", example_wipe_operation),
        ("Certificate Verification", example_certificate_verification),
        ("Batch Operations", example_batch_operations),
    ]
    
    print("SafeErase Python API Examples")
    print("=" * 50)
    
    for name, example_func in examples:
        print(f"\n{name}")
        print("-" * len(name))
        
        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {e}")
            
        print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
