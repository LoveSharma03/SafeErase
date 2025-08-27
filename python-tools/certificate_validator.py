#!/usr/bin/env python3
"""
SafeErase Certificate Validator
Command-line tool for validating SafeErase certificates
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: cryptography library not available. Signature verification disabled.")

class CertificateValidator:
    """Validates SafeErase certificates"""
    
    def __init__(self, trusted_keys_dir: Optional[str] = None):
        self.trusted_keys_dir = Path(trusted_keys_dir) if trusted_keys_dir else None
        self.trusted_keys = {}
        self.load_trusted_keys()
        
    def load_trusted_keys(self):
        """Load trusted public keys"""
        if not self.trusted_keys_dir or not self.trusted_keys_dir.exists():
            return
            
        for key_file in self.trusted_keys_dir.glob("*.pem"):
            try:
                with open(key_file, 'rb') as f:
                    public_key = serialization.load_pem_public_key(f.read())
                    key_id = key_file.stem
                    self.trusted_keys[key_id] = public_key
                    print(f"Loaded trusted key: {key_id}")
            except Exception as e:
                print(f"Warning: Failed to load key {key_file}: {e}")
                
    def validate_certificate(self, cert_path: str) -> Dict[str, any]:
        """Validate a certificate file
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            Validation result dictionary
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'certificate_info': {},
            'signature_valid': False,
            'structure_valid': False,
            'data_integrity': False
        }
        
        try:
            # Load certificate
            with open(cert_path, 'r') as f:
                cert_data = json.load(f)
                
            result['certificate_info'] = self._extract_certificate_info(cert_data)
            
            # Validate structure
            structure_result = self._validate_structure(cert_data)
            result['structure_valid'] = structure_result['valid']
            result['errors'].extend(structure_result['errors'])
            result['warnings'].extend(structure_result['warnings'])
            
            # Validate data integrity
            integrity_result = self._validate_data_integrity(cert_data)
            result['data_integrity'] = integrity_result['valid']
            result['errors'].extend(integrity_result['errors'])
            
            # Validate signature
            if CRYPTO_AVAILABLE:
                signature_result = self._validate_signature(cert_data)
                result['signature_valid'] = signature_result['valid']
                result['errors'].extend(signature_result['errors'])
                result['warnings'].extend(signature_result['warnings'])
            else:
                result['warnings'].append("Cryptographic signature validation not available")
                
            # Overall validity
            result['valid'] = (
                result['structure_valid'] and 
                result['data_integrity'] and
                (result['signature_valid'] or not CRYPTO_AVAILABLE)
            )
            
        except Exception as e:
            result['errors'].append(f"Failed to load certificate: {e}")
            
        return result
        
    def _extract_certificate_info(self, cert_data: Dict) -> Dict:
        """Extract basic certificate information"""
        info = {}
        
        try:
            cert = cert_data.get('certificate', {})
            data = cert.get('data', {})
            
            info['certificate_id'] = data.get('certificate_id', 'Unknown')
            info['generated_at'] = data.get('generated_at', 'Unknown')
            info['device_name'] = data.get('device_info', {}).get('name', 'Unknown')
            info['device_serial'] = data.get('device_info', {}).get('serial', 'Unknown')
            info['algorithm'] = data.get('wipe_info', {}).get('algorithm', 'Unknown')
            info['version'] = cert.get('version', 'Unknown')
            info['format_version'] = cert.get('format_version', 'Unknown')
            
            # Signature info
            sig_info = cert_data.get('signature_info', {})
            info['signature_algorithm'] = sig_info.get('algorithm', 'Unknown')
            info['key_id'] = sig_info.get('key_id', 'Unknown')
            info['signed_at'] = sig_info.get('timestamp', 'Unknown')
            
        except Exception as e:
            info['error'] = f"Failed to extract info: {e}"
            
        return info
        
    def _validate_structure(self, cert_data: Dict) -> Dict:
        """Validate certificate structure"""
        result = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check top-level structure
        required_top_level = ['certificate', 'signature_info']
        for field in required_top_level:
            if field not in cert_data:
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False
                
        if not result['valid']:
            return result
            
        # Check certificate structure
        cert = cert_data['certificate']
        required_cert_fields = ['data', 'version', 'format_version']
        for field in required_cert_fields:
            if field not in cert:
                result['errors'].append(f"Missing certificate field: {field}")
                result['valid'] = False
                
        # Check certificate data structure
        if 'data' in cert:
            data = cert['data']
            required_data_fields = [
                'certificate_id', 'generated_at', 'device_info', 'wipe_info'
            ]
            for field in required_data_fields:
                if field not in data:
                    result['errors'].append(f"Missing certificate data field: {field}")
                    result['valid'] = False
                    
            # Check device info
            if 'device_info' in data:
                device_info = data['device_info']
                required_device_fields = ['path', 'serial', 'model', 'size']
                for field in required_device_fields:
                    if field not in device_info:
                        result['warnings'].append(f"Missing device info field: {field}")
                        
            # Check wipe info
            if 'wipe_info' in data:
                wipe_info = data['wipe_info']
                required_wipe_fields = ['algorithm', 'started_at']
                for field in required_wipe_fields:
                    if field not in wipe_info:
                        result['errors'].append(f"Missing wipe info field: {field}")
                        result['valid'] = False
                        
        # Check signature info structure
        sig_info = cert_data['signature_info']
        required_sig_fields = ['signature', 'algorithm', 'key_id', 'timestamp']
        for field in required_sig_fields:
            if field not in sig_info:
                result['errors'].append(f"Missing signature info field: {field}")
                result['valid'] = False
                
        return result
        
    def _validate_data_integrity(self, cert_data: Dict) -> Dict:
        """Validate data integrity"""
        result = {'valid': True, 'errors': []}
        
        try:
            # Check timestamp consistency
            cert_data_obj = cert_data['certificate']['data']
            sig_info = cert_data['signature_info']
            
            generated_at = cert_data_obj.get('generated_at')
            signed_at = sig_info.get('timestamp')
            
            if generated_at and signed_at:
                try:
                    gen_time = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
                    sign_time = datetime.fromisoformat(signed_at.replace('Z', '+00:00'))
                    
                    if sign_time < gen_time:
                        result['errors'].append("Signature timestamp is before certificate generation time")
                        result['valid'] = False
                        
                except ValueError as e:
                    result['errors'].append(f"Invalid timestamp format: {e}")
                    result['valid'] = False
                    
            # Check wipe info consistency
            wipe_info = cert_data_obj.get('wipe_info', {})
            started_at = wipe_info.get('started_at')
            completed_at = wipe_info.get('completed_at')
            
            if started_at and completed_at:
                try:
                    start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    
                    if end_time < start_time:
                        result['errors'].append("Wipe completion time is before start time")
                        result['valid'] = False
                        
                except ValueError as e:
                    result['errors'].append(f"Invalid wipe timestamp format: {e}")
                    result['valid'] = False
                    
            # Check verification consistency
            verification_info = cert_data_obj.get('verification_info')
            if verification_info:
                samples_tested = verification_info.get('samples_tested', 0)
                samples_passed = verification_info.get('samples_passed', 0)
                success_rate = verification_info.get('success_rate', 0)
                
                if samples_passed > samples_tested:
                    result['errors'].append("Samples passed cannot exceed samples tested")
                    result['valid'] = False
                    
                if samples_tested > 0:
                    calculated_rate = samples_passed / samples_tested
                    if abs(calculated_rate - success_rate) > 0.01:
                        result['errors'].append("Success rate does not match sample counts")
                        result['valid'] = False
                        
        except Exception as e:
            result['errors'].append(f"Data integrity check failed: {e}")
            result['valid'] = False
            
        return result
        
    def _validate_signature(self, cert_data: Dict) -> Dict:
        """Validate cryptographic signature"""
        result = {'valid': False, 'errors': [], 'warnings': []}
        
        if not CRYPTO_AVAILABLE:
            result['warnings'].append("Cryptographic validation not available")
            return result
            
        try:
            sig_info = cert_data['signature_info']
            signature_b64 = sig_info['signature']
            key_id = sig_info['key_id']
            algorithm = sig_info['algorithm']
            
            # Get public key
            public_key = self.trusted_keys.get(key_id)
            if not public_key:
                result['warnings'].append(f"Trusted key not found for key_id: {key_id}")
                # Try to validate with any available key
                if self.trusted_keys:
                    public_key = next(iter(self.trusted_keys.values()))
                    result['warnings'].append("Using first available trusted key")
                else:
                    result['errors'].append("No trusted keys available for verification")
                    return result
                    
            # Prepare certificate data for verification
            cert_json = json.dumps(cert_data['certificate'], sort_keys=True, separators=(',', ':'))
            cert_bytes = cert_json.encode('utf-8')
            
            # Decode signature
            try:
                signature_bytes = base64.b64decode(signature_b64)
            except Exception as e:
                result['errors'].append(f"Invalid signature encoding: {e}")
                return result
                
            # Verify signature based on algorithm
            try:
                if 'RSA' in algorithm.upper():
                    public_key.verify(
                        signature_bytes,
                        cert_bytes,
                        padding.PKCS1v15(),
                        hashes.SHA256()
                    )
                    result['valid'] = True
                else:
                    result['errors'].append(f"Unsupported signature algorithm: {algorithm}")
                    
            except InvalidSignature:
                result['errors'].append("Signature verification failed - certificate may be tampered")
            except Exception as e:
                result['errors'].append(f"Signature verification error: {e}")
                
        except Exception as e:
            result['errors'].append(f"Signature validation failed: {e}")
            
        return result
        
    def validate_multiple_certificates(self, cert_paths: List[str]) -> Dict[str, Dict]:
        """Validate multiple certificates
        
        Args:
            cert_paths: List of certificate file paths
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        
        for cert_path in cert_paths:
            print(f"Validating: {cert_path}")
            results[cert_path] = self.validate_certificate(cert_path)
            
        return results

def print_validation_result(cert_path: str, result: Dict):
    """Print validation result in a readable format"""
    print(f"\n{'='*60}")
    print(f"Certificate Validation Report: {Path(cert_path).name}")
    print(f"{'='*60}")
    
    # Overall status
    status = "✅ VALID" if result['valid'] else "❌ INVALID"
    print(f"Overall Status: {status}")
    
    # Certificate information
    info = result['certificate_info']
    print(f"\nCertificate Information:")
    print(f"  ID: {info.get('certificate_id', 'Unknown')}")
    print(f"  Generated: {info.get('generated_at', 'Unknown')}")
    print(f"  Device: {info.get('device_name', 'Unknown')}")
    print(f"  Serial: {info.get('device_serial', 'Unknown')}")
    print(f"  Algorithm: {info.get('algorithm', 'Unknown')}")
    print(f"  Version: {info.get('version', 'Unknown')}")
    
    # Validation details
    print(f"\nValidation Details:")
    print(f"  Structure: {'✅' if result['structure_valid'] else '❌'}")
    print(f"  Data Integrity: {'✅' if result['data_integrity'] else '❌'}")
    print(f"  Signature: {'✅' if result['signature_valid'] else '❌' if CRYPTO_AVAILABLE else '⚠️ N/A'}")
    
    # Errors
    if result['errors']:
        print(f"\nErrors:")
        for error in result['errors']:
            print(f"  ❌ {error}")
            
    # Warnings
    if result['warnings']:
        print(f"\nWarnings:")
        for warning in result['warnings']:
            print(f"  ⚠️ {warning}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate SafeErase certificates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s certificate.json
  %(prog)s cert1.json cert2.json cert3.json
  %(prog)s --trusted-keys ./keys certificate.json
  %(prog)s --json certificate.json
        """
    )
    
    parser.add_argument(
        'certificates',
        nargs='+',
        help='Certificate files to validate'
    )
    
    parser.add_argument(
        '--trusted-keys',
        help='Directory containing trusted public keys (.pem files)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only show errors and warnings'
    )
    
    args = parser.parse_args()
    
    # Create validator
    validator = CertificateValidator(args.trusted_keys)
    
    # Validate certificates
    all_valid = True
    results = {}
    
    for cert_path in args.certificates:
        if not Path(cert_path).exists():
            print(f"Error: Certificate file not found: {cert_path}")
            all_valid = False
            continue
            
        result = validator.validate_certificate(cert_path)
        results[cert_path] = result
        
        if not result['valid']:
            all_valid = False
            
        if args.json:
            continue
        elif args.quiet:
            if result['errors'] or result['warnings']:
                print_validation_result(cert_path, result)
        else:
            print_validation_result(cert_path, result)
            
    # Output JSON results if requested
    if args.json:
        print(json.dumps(results, indent=2))
        
    # Summary
    if not args.json and len(args.certificates) > 1:
        valid_count = sum(1 for r in results.values() if r['valid'])
        total_count = len(results)
        
        print(f"\n{'='*60}")
        print(f"Validation Summary: {valid_count}/{total_count} certificates valid")
        print(f"{'='*60}")
        
    # Exit with appropriate code
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()
