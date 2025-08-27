#!/usr/bin/env python3
"""
SafeErase Python Demo Runner
Interactive demonstration of Python components
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from python_api.safeerase_api import SafeEraseAPI, WipeAlgorithm, WipeOptions

class PythonDemo:
    """Interactive Python demo"""
    
    def __init__(self):
        self.api = SafeEraseAPI()
        
    async def run_demo(self):
        """Run the interactive demo"""
        print("🐍 SafeErase Python Components Demo")
        print("=" * 50)
        
        await self.api.initialize()
        
        try:
            while True:
                self.show_menu()
                choice = input("\nSelect option (1-7): ").strip()
                
                if choice == "1":
                    await self.demo_device_discovery()
                elif choice == "2":
                    await self.demo_algorithms()
                elif choice == "3":
                    await self.demo_wipe_simulation()
                elif choice == "4":
                    await self.demo_certificate_generation()
                elif choice == "5":
                    await self.demo_python_ui()
                elif choice == "6":
                    await self.demo_command_line_tools()
                elif choice == "7":
                    print("\n👋 Thank you for trying SafeErase Python components!")
                    break
                else:
                    print("❌ Invalid option. Please select 1-7.")
                    
                input("\nPress Enter to continue...")
                
        finally:
            self.api.cleanup()
            
    def show_menu(self):
        """Show the demo menu"""
        print("\n🎯 Python Demo Menu:")
        print("1. Device Discovery API")
        print("2. Algorithm Information")
        print("3. Wipe Operation Simulation")
        print("4. Certificate Generation")
        print("5. Python UI Components")
        print("6. Command-Line Tools")
        print("7. Exit Demo")
        
    async def demo_device_discovery(self):
        """Demo device discovery"""
        print("\n🔍 Device Discovery API Demo")
        print("-" * 40)
        
        print("Discovering storage devices...")
        devices = await self.api.discover_devices()
        
        print(f"\n✅ Found {len(devices)} storage devices:")
        
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
            print(f"   Size: {device.get_size_formatted()}")
            print(f"   Type: {device.device_type.value.upper()}")
            print(f"   Interface: {device.interface}")
            print(f"   Model: {device.model}")
            print(f"   Serial: {device.serial_number}")
            print(f"   Status: {status}")
            
        print(f"\n📊 API Usage:")
        print(f"   api = SafeEraseAPI()")
        print(f"   devices = await api.discover_devices()")
        print(f"   print(f'Found {{len(devices)}} devices')")
        
    async def demo_algorithms(self):
        """Demo algorithm information"""
        print("\n🔐 Algorithm Information Demo")
        print("-" * 40)
        
        algorithms = self.api.get_available_algorithms()
        
        print("Available wiping algorithms:")
        
        for i, algo in enumerate(algorithms, 1):
            print(f"\n{i}. {algo['name']}")
            print(f"   Description: {algo['description']}")
            print(f"   Passes: {algo['passes']}")
            print(f"   Security Level: {algo['security_level']}")
            print(f"   Compliance: {', '.join(algo['compliance'])}")
            print(f"   Recommended for: {', '.join(algo['recommended_for'])}")
            
        print(f"\n📊 API Usage:")
        print(f"   algorithms = api.get_available_algorithms()")
        print(f"   for algo in algorithms:")
        print(f"       print(algo['name'], algo['description'])")
        
    async def demo_wipe_simulation(self):
        """Demo wipe operation simulation"""
        print("\n🚀 Wipe Operation Simulation Demo")
        print("-" * 40)
        
        # Get devices
        devices = await self.api.discover_devices()
        non_system_devices = [d for d in devices if not d.is_system_disk]
        
        if not non_system_devices:
            print("❌ No non-system devices available for simulation")
            return
            
        device = non_system_devices[0]
        print(f"Target device: {device.name}")
        print(f"Size: {device.get_size_formatted()}")
        
        # Configure options
        options = WipeOptions(
            verify_wipe=True,
            clear_hpa=True,
            clear_dco=True,
            verification_samples=100  # Reduced for demo
        )
        
        print(f"\nStarting wipe simulation...")
        print(f"Algorithm: NIST SP 800-88")
        print(f"Options: Verify={options.verify_wipe}, HPA/DCO={options.clear_hpa}")
        
        # Start operation
        operation_id = await self.api.start_wipe(
            device.id,
            WipeAlgorithm.NIST_800_88,
            options
        )
        
        print(f"Operation ID: {operation_id[:8]}...")
        
        # Monitor progress (simplified for demo)
        last_progress = 0
        while True:
            progress = await self.api.get_wipe_progress(operation_id)
            if not progress:
                break
                
            if progress.progress_percent > last_progress + 10:
                print(f"Progress: {progress.progress_percent:.1f}% - {progress.current_operation}")
                last_progress = progress.progress_percent
                
            if progress.status.value in ['completed', 'failed', 'cancelled']:
                break
                
            await asyncio.sleep(0.5)
            
        # Get result
        result = await self.api.get_wipe_result(operation_id)
        print(f"\n✅ Wipe simulation completed!")
        print(f"Status: {result.status.value}")
        print(f"Passes completed: {result.passes_completed}")
        print(f"Verification: {'Passed' if result.verification_passed else 'Failed'}")
        
        print(f"\n📊 API Usage:")
        print(f"   operation_id = await api.start_wipe(device_id, algorithm, options)")
        print(f"   progress = await api.get_wipe_progress(operation_id)")
        print(f"   result = await api.get_wipe_result(operation_id)")
        
    async def demo_certificate_generation(self):
        """Demo certificate generation"""
        print("\n📜 Certificate Generation Demo")
        print("-" * 40)
        
        # Simulate a completed operation
        devices = await self.api.discover_devices()
        if not devices:
            print("❌ No devices available for certificate demo")
            return
            
        device = devices[0]
        
        # Start a quick operation for certificate demo
        operation_id = await self.api.start_wipe(
            device.id,
            WipeAlgorithm.NIST_800_88,
            WipeOptions(verify_wipe=False)  # Skip verification for speed
        )
        
        # Wait for completion
        while True:
            progress = await self.api.get_wipe_progress(operation_id)
            if not progress or progress.status.value in ['completed', 'failed']:
                break
            await asyncio.sleep(0.1)
            
        print("Generating tamper-proof certificate...")
        
        # Generate certificate
        certificate = await self.api.generate_certificate(operation_id)
        
        print(f"\n✅ Certificate generated successfully!")
        print(f"Certificate ID: {certificate.certificate_id}")
        print(f"Generated at: {certificate.generated_at}")
        print(f"Device: {certificate.device_info.name}")
        print(f"Algorithm: {certificate.wipe_result.algorithm.value}")
        print(f"Signature: {certificate.signature[:32]}...")
        print(f"Verification URL: {certificate.verification_url}")
        
        # Show certificate structure
        cert_dict = certificate.to_dict()
        print(f"\n📋 Certificate Structure:")
        print(f"   - Certificate ID")
        print(f"   - Device Information")
        print(f"   - Wipe Results")
        print(f"   - Digital Signature")
        print(f"   - Verification URL")
        
        print(f"\n📊 API Usage:")
        print(f"   certificate = await api.generate_certificate(operation_id)")
        print(f"   is_valid = await api.verify_certificate('cert.json')")
        
    async def demo_python_ui(self):
        """Demo Python UI components"""
        print("\n🖥️ Python UI Components Demo")
        print("-" * 40)
        
        print("SafeErase includes a complete Python UI built with CustomTkinter:")
        print()
        print("🎨 UI Features:")
        print("   • Modern, professional interface")
        print("   • Device discovery and selection")
        print("   • Real-time progress monitoring")
        print("   • Certificate management")
        print("   • Settings and configuration")
        print("   • Cross-platform compatibility")
        print()
        print("📁 UI Components:")
        print("   • MainWindow - Primary application window")
        print("   • DevicePanel - Device discovery and selection")
        print("   • OperationPanel - Wipe operation monitoring")
        print("   • CertificatePanel - Certificate management")
        print("   • SettingsPanel - Application settings")
        print()
        print("🚀 To launch the Python UI:")
        print("   python python-ui/main.py")
        print("   # or after installation:")
        print("   safeerase-ui")
        print()
        print("📦 UI Dependencies:")
        print("   • customtkinter - Modern UI framework")
        print("   • pillow - Image processing")
        print("   • tkinter-tooltip - Enhanced tooltips")
        
    async def demo_command_line_tools(self):
        """Demo command-line tools"""
        print("\n⚡ Command-Line Tools Demo")
        print("-" * 40)
        
        print("SafeErase includes powerful command-line tools:")
        print()
        
        print("🔍 Device Scanner:")
        print("   python python-tools/device_scanner.py")
        print("   • Discover and analyze storage devices")
        print("   • Get device recommendations")
        print("   • Export device information")
        print()
        
        print("📜 Certificate Validator:")
        print("   python python-tools/certificate_validator.py cert.json")
        print("   • Validate certificate integrity")
        print("   • Verify digital signatures")
        print("   • Check compliance standards")
        print()
        
        print("📅 Wipe Scheduler:")
        print("   python python-tools/wipe_scheduler.py create job.yaml")
        print("   • Schedule batch wipe operations")
        print("   • Monitor multiple devices")
        print("   • Generate batch reports")
        print()
        
        print("🛠️ Example Commands:")
        print("   # Scan devices with analysis")
        print("   safeerase-scan --verbose --json")
        print()
        print("   # Validate certificate")
        print("   safeerase-validate certificate.json")
        print()
        print("   # Create scheduled job")
        print("   safeerase-schedule create batch_job.yaml")
        print()
        
        print("📊 Tool Features:")
        print("   • JSON output for automation")
        print("   • Detailed analysis and recommendations")
        print("   • Batch processing capabilities")
        print("   • Integration with CI/CD pipelines")

async def main():
    """Main entry point"""
    demo = PythonDemo()
    
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
