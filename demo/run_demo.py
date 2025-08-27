#!/usr/bin/env python3
"""
SafeErase Demo Script
Demonstrates the SafeErase functionality without requiring Rust/Flutter installation
"""

import os
import sys
import time
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path

class SafeEraseDemo:
    def __init__(self):
        self.devices = []
        self.operations = {}
        self.certificates = []
        
    def print_banner(self):
        print("=" * 60)
        print("🔒 SafeErase - Secure Data Wiping Solution")
        print("=" * 60)
        print("Demo Version - Simulating Core Functionality")
        print()
        
    def discover_devices(self):
        """Simulate device discovery"""
        print("🔍 Discovering storage devices...")
        time.sleep(1)
        
        # Mock devices for demonstration
        self.devices = [
            {
                "id": "dev1",
                "name": "Samsung SSD 980 PRO 1TB",
                "path": "/dev/nvme0n1" if os.name != 'nt' else "\\\\?\\PhysicalDrive0",
                "size": 1000204886016,
                "type": "NVMe SSD",
                "interface": "NVMe",
                "removable": False,
                "system_disk": True,
                "supports_secure_erase": True,
                "supports_hpa_dco": False,
                "health": "Good"
            },
            {
                "id": "dev2", 
                "name": "SanDisk Ultra USB 3.0 32GB",
                "path": "/dev/sdb" if os.name != 'nt' else "\\\\?\\PhysicalDrive1",
                "size": 32212254720,
                "type": "USB Storage",
                "interface": "USB 3.0",
                "removable": True,
                "system_disk": False,
                "supports_secure_erase": False,
                "supports_hpa_dco": False,
                "health": "Good"
            },
            {
                "id": "dev3",
                "name": "Western Digital Blue 2TB",
                "path": "/dev/sdc" if os.name != 'nt' else "\\\\?\\PhysicalDrive2", 
                "size": 2000398934016,
                "type": "HDD",
                "interface": "SATA",
                "removable": False,
                "system_disk": False,
                "supports_secure_erase": True,
                "supports_hpa_dco": True,
                "health": "Good"
            }
        ]
        
        print(f"✅ Found {len(self.devices)} storage devices")
        return self.devices
        
    def display_devices(self):
        """Display discovered devices"""
        print("\n📱 Available Storage Devices:")
        print("-" * 80)
        
        for i, device in enumerate(self.devices, 1):
            size_gb = device['size'] / (1024**3)
            system_warning = " ⚠️  SYSTEM DISK" if device['system_disk'] else ""
            
            print(f"{i}. {device['name']}")
            print(f"   Path: {device['path']}")
            print(f"   Size: {size_gb:.1f} GB ({device['type']}, {device['interface']})")
            print(f"   Features: Secure Erase: {device['supports_secure_erase']}, HPA/DCO: {device['supports_hpa_dco']}")
            print(f"   Status: {device['health']}{system_warning}")
            print()
            
    def get_algorithms(self):
        """Get available wiping algorithms"""
        return {
            "1": {
                "name": "NIST SP 800-88",
                "description": "Single pass with verification (Recommended for SSDs)",
                "passes": 1,
                "security_level": "Standard",
                "compliance": ["NIST 800-88"],
                "speed": "Fast"
            },
            "2": {
                "name": "DoD 5220.22-M", 
                "description": "Three-pass overwrite (High security)",
                "passes": 3,
                "security_level": "High",
                "compliance": ["DoD 5220.22-M"],
                "speed": "Medium"
            },
            "3": {
                "name": "Gutmann Algorithm",
                "description": "35-pass maximum security (Legacy drives)",
                "passes": 35,
                "security_level": "Maximum", 
                "compliance": ["Academic Research"],
                "speed": "Slow"
            },
            "4": {
                "name": "ATA Secure Erase",
                "description": "Hardware-level secure erase (Fast)",
                "passes": 1,
                "security_level": "High",
                "compliance": ["ATA Standard"],
                "speed": "Very Fast"
            }
        }
        
    def display_algorithms(self):
        """Display available algorithms"""
        algorithms = self.get_algorithms()
        print("\n🔐 Available Wiping Algorithms:")
        print("-" * 60)
        
        for key, algo in algorithms.items():
            print(f"{key}. {algo['name']}")
            print(f"   {algo['description']}")
            print(f"   Passes: {algo['passes']} | Security: {algo['security_level']} | Speed: {algo['speed']}")
            print(f"   Compliance: {', '.join(algo['compliance'])}")
            print()
            
    def simulate_wipe(self, device, algorithm):
        """Simulate the wiping process"""
        operation_id = str(uuid.uuid4())
        
        print(f"\n🚀 Starting wipe operation: {operation_id}")
        print(f"Device: {device['name']}")
        print(f"Algorithm: {algorithm['name']}")
        print(f"Estimated time: {self.estimate_time(device, algorithm)}")
        print()
        
        # Store operation details
        self.operations[operation_id] = {
            "id": operation_id,
            "device": device,
            "algorithm": algorithm,
            "started_at": datetime.now(),
            "status": "in_progress",
            "progress": 0,
            "current_pass": 1,
            "total_passes": algorithm['passes']
        }
        
        # Simulate wiping progress
        total_steps = algorithm['passes'] * 20  # 20 steps per pass
        
        for step in range(total_steps + 1):
            progress = (step / total_steps) * 100
            current_pass = (step // 20) + 1
            
            if current_pass > algorithm['passes']:
                current_pass = algorithm['passes']
                
            self.operations[operation_id]['progress'] = progress
            self.operations[operation_id]['current_pass'] = current_pass
            
            # Display progress
            bar_length = 40
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            print(f"\r⏳ Pass {current_pass}/{algorithm['passes']} |{bar}| {progress:.1f}%", end='', flush=True)
            
            time.sleep(0.1)  # Simulate work
            
        print("\n")
        
        # Complete the operation
        self.operations[operation_id]['status'] = 'completed'
        self.operations[operation_id]['completed_at'] = datetime.now()
        self.operations[operation_id]['progress'] = 100
        
        print("✅ Wipe operation completed successfully!")
        
        # Simulate verification
        print("🔍 Performing verification...")
        time.sleep(2)
        print("✅ Verification passed - Data successfully destroyed")
        
        return operation_id
        
    def estimate_time(self, device, algorithm):
        """Estimate wipe time"""
        # Simple estimation based on device size and algorithm
        size_gb = device['size'] / (1024**3)
        
        if algorithm['name'] == "ATA Secure Erase":
            minutes = max(1, size_gb / 100)  # Very fast
        elif algorithm['passes'] == 1:
            minutes = size_gb / 10  # ~100 MB/s
        else:
            minutes = (size_gb / 10) * algorithm['passes']
            
        if minutes < 60:
            return f"{minutes:.0f} minutes"
        else:
            hours = minutes / 60
            return f"{hours:.1f} hours"
            
    def generate_certificate(self, operation_id):
        """Generate a tamper-proof certificate"""
        operation = self.operations[operation_id]
        
        print("\n📜 Generating tamper-proof certificate...")
        time.sleep(1)
        
        # Create certificate data
        certificate_data = {
            "certificate_id": str(uuid.uuid4()),
            "generated_at": datetime.now().isoformat(),
            "operation_id": operation_id,
            "device_info": {
                "name": operation['device']['name'],
                "path": operation['device']['path'],
                "size": operation['device']['size'],
                "type": operation['device']['type'],
                "serial": f"SN{hash(operation['device']['name']) % 1000000:06d}"
            },
            "wipe_info": {
                "algorithm": operation['algorithm']['name'],
                "started_at": operation['started_at'].isoformat(),
                "completed_at": operation['completed_at'].isoformat(),
                "duration": str(operation['completed_at'] - operation['started_at']),
                "passes_completed": operation['algorithm']['passes'],
                "verification_passed": True
            },
            "compliance_info": {
                "standards_met": operation['algorithm']['compliance'],
                "security_level": operation['algorithm']['security_level']
            },
            "organization": {
                "name": "Demo Organization",
                "contact": "demo@safeerase.com"
            }
        }
        
        # Generate digital signature (simulated)
        cert_json = json.dumps(certificate_data, sort_keys=True)
        signature = hashlib.sha256(cert_json.encode()).hexdigest()
        
        signed_certificate = {
            "certificate": certificate_data,
            "signature_info": {
                "signature": signature,
                "algorithm": "SHA256-RSA2048",
                "timestamp": datetime.now().isoformat(),
                "key_id": "demo_key_001"
            }
        }
        
        # Save certificate
        cert_filename = f"certificate_{certificate_data['certificate_id'][:8]}.json"
        cert_path = Path("demo") / "certificates" / cert_filename
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(cert_path, 'w') as f:
            json.dump(signed_certificate, f, indent=2)
            
        self.certificates.append(signed_certificate)
        
        print(f"✅ Certificate generated: {cert_filename}")
        print(f"📁 Saved to: {cert_path}")
        print(f"🔐 Digital signature: {signature[:16]}...")
        
        return signed_certificate
        
    def verify_certificate(self, cert_path):
        """Verify a certificate"""
        print(f"\n🔍 Verifying certificate: {cert_path}")
        
        try:
            with open(cert_path, 'r') as f:
                signed_cert = json.load(f)
                
            # Verify signature (simulated)
            cert_json = json.dumps(signed_cert['certificate'], sort_keys=True)
            expected_signature = hashlib.sha256(cert_json.encode()).hexdigest()
            actual_signature = signed_cert['signature_info']['signature']
            
            if expected_signature == actual_signature:
                print("✅ Certificate signature is valid")
                print("✅ Certificate has not been tampered with")
                return True
            else:
                print("❌ Certificate signature is invalid")
                return False
                
        except Exception as e:
            print(f"❌ Certificate verification failed: {e}")
            return False
            
    def display_system_status(self):
        """Display system status"""
        print("\n💻 System Status:")
        print("-" * 40)
        print(f"Platform: {sys.platform}")
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Admin Privileges: {'Yes' if os.name == 'nt' else 'Simulated'}")
        print(f"Available Devices: {len(self.devices)}")
        print(f"Completed Operations: {len([op for op in self.operations.values() if op['status'] == 'completed'])}")
        print(f"Generated Certificates: {len(self.certificates)}")
        
    def interactive_demo(self):
        """Run interactive demonstration"""
        self.print_banner()
        
        while True:
            print("\n🎯 SafeErase Demo Menu:")
            print("1. Discover Devices")
            print("2. View Available Algorithms") 
            print("3. Start Wipe Operation")
            print("4. View System Status")
            print("5. Verify Certificate")
            print("6. Exit Demo")
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == "1":
                self.discover_devices()
                self.display_devices()
                
            elif choice == "2":
                self.display_algorithms()
                
            elif choice == "3":
                if not self.devices:
                    print("❌ No devices discovered. Please run device discovery first.")
                    continue
                    
                self.display_devices()
                
                try:
                    device_choice = int(input("Select device (number): ")) - 1
                    if device_choice < 0 or device_choice >= len(self.devices):
                        print("❌ Invalid device selection")
                        continue
                        
                    selected_device = self.devices[device_choice]
                    
                    if selected_device['system_disk']:
                        confirm = input("⚠️  WARNING: This is a system disk! Continue? (yes/no): ")
                        if confirm.lower() != 'yes':
                            print("Operation cancelled")
                            continue
                            
                    self.display_algorithms()
                    algo_choice = input("Select algorithm (1-4): ").strip()
                    algorithms = self.get_algorithms()
                    
                    if algo_choice not in algorithms:
                        print("❌ Invalid algorithm selection")
                        continue
                        
                    selected_algorithm = algorithms[algo_choice]
                    
                    # Final confirmation
                    print(f"\n⚠️  FINAL CONFIRMATION:")
                    print(f"Device: {selected_device['name']}")
                    print(f"Algorithm: {selected_algorithm['name']}")
                    print(f"This will PERMANENTLY DESTROY all data on the device!")
                    
                    final_confirm = input("Type 'WIPE' to confirm: ")
                    if final_confirm != 'WIPE':
                        print("Operation cancelled")
                        continue
                        
                    # Perform wipe
                    operation_id = self.simulate_wipe(selected_device, selected_algorithm)
                    
                    # Generate certificate
                    certificate = self.generate_certificate(operation_id)
                    
                except (ValueError, KeyboardInterrupt):
                    print("❌ Invalid input or operation cancelled")
                    
            elif choice == "4":
                self.display_system_status()
                
            elif choice == "5":
                cert_dir = Path("demo") / "certificates"
                if not cert_dir.exists():
                    print("❌ No certificates found")
                    continue
                    
                cert_files = list(cert_dir.glob("*.json"))
                if not cert_files:
                    print("❌ No certificate files found")
                    continue
                    
                print("\n📜 Available Certificates:")
                for i, cert_file in enumerate(cert_files, 1):
                    print(f"{i}. {cert_file.name}")
                    
                try:
                    cert_choice = int(input("Select certificate to verify: ")) - 1
                    if 0 <= cert_choice < len(cert_files):
                        self.verify_certificate(cert_files[cert_choice])
                    else:
                        print("❌ Invalid selection")
                except ValueError:
                    print("❌ Invalid input")
                    
            elif choice == "6":
                print("\n👋 Thank you for trying SafeErase!")
                print("For the full version with real device wiping capabilities,")
                print("install Rust and Flutter, then run: ./scripts/build.sh")
                break
                
            else:
                print("❌ Invalid option. Please select 1-6.")

def main():
    """Main entry point"""
    demo = SafeEraseDemo()
    
    try:
        demo.interactive_demo()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        
if __name__ == "__main__":
    main()
