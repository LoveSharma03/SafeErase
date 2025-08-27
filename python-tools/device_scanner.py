#!/usr/bin/env python3
"""
SafeErase Device Scanner
Command-line tool for discovering and analyzing storage devices
"""

import argparse
import json
import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
import platform

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from python_api.safeerase_api import SafeEraseAPI, DeviceInfo, DeviceType

class DeviceScanner:
    """Scans and analyzes storage devices"""
    
    def __init__(self):
        self.api = SafeEraseAPI()
        
    async def initialize(self):
        """Initialize the scanner"""
        return await self.api.initialize()
        
    async def scan_devices(self, include_system: bool = False, include_removable: bool = True) -> List[DeviceInfo]:
        """Scan for storage devices
        
        Args:
            include_system: Include system disks
            include_removable: Include removable devices
            
        Returns:
            List of discovered devices
        """
        devices = await self.api.discover_devices()
        
        # Filter devices based on options
        filtered_devices = []
        for device in devices:
            if not include_system and device.is_system_disk:
                continue
            if not include_removable and device.is_removable:
                continue
            filtered_devices.append(device)
            
        return filtered_devices
        
    def analyze_device(self, device: DeviceInfo) -> Dict:
        """Analyze a device and provide recommendations
        
        Args:
            device: Device to analyze
            
        Returns:
            Analysis results
        """
        analysis = {
            'device_id': device.id,
            'basic_info': {
                'name': device.name,
                'path': device.path,
                'size_bytes': device.size,
                'size_formatted': self._format_size(device.size),
                'type': device.device_type.value,
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
            },
            'recommendations': self._get_recommendations(device),
            'warnings': self._get_warnings(device),
            'wipe_options': self._get_wipe_options(device)
        }
        
        return analysis
        
    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        size = float(size_bytes)
        unit_index = 0
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
            
        return f"{size:.1f} {units[unit_index]}"
        
    def _get_recommendations(self, device: DeviceInfo) -> List[str]:
        """Get recommendations for the device"""
        recommendations = []
        
        # Algorithm recommendations
        if device.device_type == DeviceType.NVME:
            recommendations.append("Use NVMe Format for fastest wiping")
            recommendations.append("NIST SP 800-88 is also suitable for this device")
        elif device.device_type == DeviceType.SSD:
            if device.supports_secure_erase:
                recommendations.append("Use ATA Secure Erase for hardware-level wiping")
            recommendations.append("NIST SP 800-88 is recommended for SSDs")
        elif device.device_type == DeviceType.HDD:
            if device.supports_secure_erase:
                recommendations.append("ATA Secure Erase available for this device")
            recommendations.append("DoD 5220.22-M provides good security for HDDs")
            if device.size > 2 * 1024**4:  # > 2TB
                recommendations.append("Consider NIST SP 800-88 for faster wiping of large drives")
        elif device.device_type == DeviceType.USB:
            recommendations.append("Use DoD 5220.22-M for removable devices")
            recommendations.append("Verify wipe completion due to wear leveling")
            
        # HPA/DCO recommendations
        if device.supports_hpa_dco:
            recommendations.append("Enable HPA/DCO detection and clearing")
            
        # Verification recommendations
        if device.device_type in [DeviceType.SSD, DeviceType.NVME]:
            recommendations.append("Enable verification due to wear leveling")
        elif device.size > 1024**4:  # > 1TB
            recommendations.append("Consider sampling verification for large drives")
            
        return recommendations
        
    def _get_warnings(self, device: DeviceInfo) -> List[str]:
        """Get warnings for the device"""
        warnings = []
        
        if device.is_system_disk:
            warnings.append("⚠️ SYSTEM DISK: Contains operating system - wiping will make system unbootable")
            
        if device.health_status.lower() not in ['good', 'healthy']:
            warnings.append(f"⚠️ HEALTH: Device health is '{device.health_status}' - may affect wipe reliability")
            
        if device.device_type == DeviceType.USB and device.size > 128 * 1024**3:  # > 128GB
            warnings.append("⚠️ LARGE USB: Large USB devices may have complex wear leveling")
            
        if not device.supports_secure_erase and device.device_type in [DeviceType.SSD, DeviceType.NVME]:
            warnings.append("⚠️ NO SECURE ERASE: Hardware secure erase not available")
            
        if device.serial_number in ['Unknown', '', None]:
            warnings.append("⚠️ NO SERIAL: Device serial number not available")
            
        return warnings
        
    def _get_wipe_options(self, device: DeviceInfo) -> Dict:
        """Get recommended wipe options for the device"""
        options = {
            'verify_wipe': True,
            'clear_hpa': device.supports_hpa_dco,
            'clear_dco': device.supports_hpa_dco,
            'verification_samples': 1000,
        }
        
        # Adjust verification samples based on device size
        if device.size > 2 * 1024**4:  # > 2TB
            options['verification_samples'] = 500  # Fewer samples for large drives
        elif device.size < 32 * 1024**3:  # < 32GB
            options['verification_samples'] = 2000  # More samples for small drives
            
        # Block size recommendations
        if device.device_type == DeviceType.NVME:
            options['block_size'] = 4 * 1024 * 1024  # 4MB for NVMe
        elif device.device_type == DeviceType.SSD:
            options['block_size'] = 2 * 1024 * 1024  # 2MB for SSD
        else:
            options['block_size'] = 1024 * 1024  # 1MB for HDD
            
        return options

def print_device_summary(devices: List[DeviceInfo]):
    """Print a summary of discovered devices"""
    print(f"\n{'='*80}")
    print(f"Device Discovery Summary")
    print(f"{'='*80}")
    print(f"Found {len(devices)} storage devices:")
    
    for i, device in enumerate(devices, 1):
        status_indicators = []
        if device.is_system_disk:
            status_indicators.append("⚠️ SYSTEM")
        if device.is_removable:
            status_indicators.append("🔌 REMOVABLE")
        if device.supports_secure_erase:
            status_indicators.append("🔒 SECURE ERASE")
            
        status = " | ".join(status_indicators) if status_indicators else "Ready"
        
        print(f"\n{i}. {device.name}")
        print(f"   Path: {device.path}")
        print(f"   Size: {DeviceScanner()._format_size(device.size)} ({device.device_type.value.upper()}, {device.interface})")
        print(f"   Model: {device.model}")
        print(f"   Serial: {device.serial_number}")
        print(f"   Status: {status}")

def print_device_analysis(analysis: Dict):
    """Print detailed device analysis"""
    device_name = analysis['basic_info']['name']
    
    print(f"\n{'='*80}")
    print(f"Device Analysis: {device_name}")
    print(f"{'='*80}")
    
    # Basic information
    basic = analysis['basic_info']
    print(f"\nBasic Information:")
    print(f"  Name: {basic['name']}")
    print(f"  Path: {basic['path']}")
    print(f"  Size: {basic['size_formatted']} ({basic['size_bytes']:,} bytes)")
    print(f"  Type: {basic['type'].upper()}")
    print(f"  Interface: {basic['interface']}")
    
    # Hardware information
    hardware = analysis['hardware_info']
    print(f"\nHardware Information:")
    print(f"  Model: {hardware['model']}")
    print(f"  Serial: {hardware['serial_number']}")
    print(f"  Firmware: {hardware['firmware_version']}")
    print(f"  Health: {hardware['health_status']}")
    
    # Capabilities
    caps = analysis['capabilities']
    print(f"\nCapabilities:")
    print(f"  Removable: {'Yes' if caps['is_removable'] else 'No'}")
    print(f"  System Disk: {'Yes' if caps['is_system_disk'] else 'No'}")
    print(f"  Secure Erase: {'Yes' if caps['supports_secure_erase'] else 'No'}")
    print(f"  HPA/DCO Support: {'Yes' if caps['supports_hpa_dco'] else 'No'}")
    
    # Warnings
    if analysis['warnings']:
        print(f"\nWarnings:")
        for warning in analysis['warnings']:
            print(f"  {warning}")
            
    # Recommendations
    if analysis['recommendations']:
        print(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
            
    # Wipe options
    options = analysis['wipe_options']
    print(f"\nRecommended Wipe Options:")
    print(f"  Verify Wipe: {'Yes' if options['verify_wipe'] else 'No'}")
    print(f"  Clear HPA: {'Yes' if options['clear_hpa'] else 'No'}")
    print(f"  Clear DCO: {'Yes' if options['clear_dco'] else 'No'}")
    print(f"  Verification Samples: {options['verification_samples']:,}")
    print(f"  Block Size: {DeviceScanner()._format_size(options['block_size'])}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Scan and analyze storage devices for secure wiping",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Scan all non-system devices
  %(prog)s --include-system         # Include system disks
  %(prog)s --exclude-removable      # Exclude removable devices
  %(prog)s --analyze dev_001         # Analyze specific device
  %(prog)s --json                   # Output in JSON format
        """
    )
    
    parser.add_argument(
        '--include-system',
        action='store_true',
        help='Include system disks in scan'
    )
    
    parser.add_argument(
        '--exclude-removable',
        action='store_true',
        help='Exclude removable devices from scan'
    )
    
    parser.add_argument(
        '--analyze',
        metavar='DEVICE_ID',
        help='Analyze specific device by ID'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed analysis for all devices'
    )
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = DeviceScanner()
    
    try:
        # Initialize
        if not await scanner.initialize():
            print("Error: Failed to initialize device scanner")
            return 1
            
        # Scan devices
        devices = await scanner.scan_devices(
            include_system=args.include_system,
            include_removable=not args.exclude_removable
        )
        
        if not devices:
            print("No devices found matching the specified criteria")
            return 0
            
        # Analyze specific device
        if args.analyze:
            device = next((d for d in devices if d.id == args.analyze), None)
            if not device:
                print(f"Error: Device '{args.analyze}' not found")
                return 1
                
            analysis = scanner.analyze_device(device)
            
            if args.json:
                print(json.dumps(analysis, indent=2))
            else:
                print_device_analysis(analysis)
                
            return 0
            
        # Output results
        if args.json:
            # JSON output
            results = {
                'platform': platform.system(),
                'device_count': len(devices),
                'devices': []
            }
            
            for device in devices:
                device_data = device.to_dict()
                if args.verbose:
                    device_data['analysis'] = scanner.analyze_device(device)
                results['devices'].append(device_data)
                
            print(json.dumps(results, indent=2))
            
        else:
            # Human-readable output
            print_device_summary(devices)
            
            if args.verbose:
                for device in devices:
                    analysis = scanner.analyze_device(device)
                    print_device_analysis(analysis)
                    
        return 0
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        scanner.api.cleanup()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
