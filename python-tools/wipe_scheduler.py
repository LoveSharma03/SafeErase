#!/usr/bin/env python3
"""
SafeErase Wipe Scheduler
Command-line tool for scheduling and managing batch wipe operations
"""

import argparse
import json
import sys
import asyncio
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from python_api.safeerase_api import SafeEraseAPI, WipeAlgorithm, WipeOptions, WipeStatus

class WipeScheduler:
    """Manages scheduled wipe operations"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.api = SafeEraseAPI()
        self.config_file = config_file
        self.config = self._load_config()
        self.active_jobs = {}
        self.completed_jobs = []
        
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        default_config = {
            'default_algorithm': 'nist_800_88',
            'default_options': {
                'verify_wipe': True,
                'clear_hpa': True,
                'clear_dco': True,
                'verification_samples': 1000
            },
            'max_concurrent_operations': 2,
            'auto_generate_certificates': True,
            'certificate_output_dir': './certificates',
            'log_level': 'INFO'
        }
        
        if not self.config_file or not Path(self.config_file).exists():
            return default_config
            
        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
                    
            # Merge with defaults
            default_config.update(config)
            return default_config
            
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}")
            return default_config
            
    async def initialize(self):
        """Initialize the scheduler"""
        return await self.api.initialize()
        
    async def create_job(self, job_config: Dict) -> str:
        """Create a new wipe job
        
        Args:
            job_config: Job configuration
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Validate job configuration
        required_fields = ['devices', 'algorithm']
        for field in required_fields:
            if field not in job_config:
                raise ValueError(f"Missing required field: {field}")
                
        # Set defaults
        job = {
            'id': job_id,
            'name': job_config.get('name', f"Wipe Job {job_id[:8]}"),
            'description': job_config.get('description', ''),
            'devices': job_config['devices'],
            'algorithm': job_config['algorithm'],
            'options': job_config.get('options', self.config['default_options']),
            'schedule': job_config.get('schedule'),
            'created_at': datetime.now(),
            'status': 'pending',
            'operations': [],
            'progress': {
                'total_devices': len(job_config['devices']),
                'completed_devices': 0,
                'failed_devices': 0,
                'overall_progress': 0.0
            }
        }
        
        self.active_jobs[job_id] = job
        return job_id
        
    async def start_job(self, job_id: str) -> bool:
        """Start a wipe job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job started successfully
        """
        job = self.active_jobs.get(job_id)
        if not job:
            return False
            
        if job['status'] != 'pending':
            return False
            
        job['status'] = 'running'
        job['started_at'] = datetime.now()
        
        # Start wipe operations
        asyncio.create_task(self._execute_job(job_id))
        
        return True
        
    async def _execute_job(self, job_id: str):
        """Execute a wipe job"""
        job = self.active_jobs[job_id]
        
        try:
            # Get algorithm
            algorithm = WipeAlgorithm(job['algorithm'])
            
            # Create wipe options
            options_dict = job['options']
            options = WipeOptions(
                verify_wipe=options_dict.get('verify_wipe', True),
                clear_hpa=options_dict.get('clear_hpa', True),
                clear_dco=options_dict.get('clear_dco', True),
                verification_samples=options_dict.get('verification_samples', 1000),
                block_size=options_dict.get('block_size', 1048576)
            )
            
            # Start operations for each device
            max_concurrent = self.config['max_concurrent_operations']
            semaphore = asyncio.Semaphore(max_concurrent)
            
            tasks = []
            for device_id in job['devices']:
                task = asyncio.create_task(
                    self._wipe_device(job_id, device_id, algorithm, options, semaphore)
                )
                tasks.append(task)
                
            # Wait for all operations to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Update job status
            job['status'] = 'completed'
            job['completed_at'] = datetime.now()
            
            # Generate summary report
            await self._generate_job_report(job_id)
            
        except Exception as e:
            job['status'] = 'failed'
            job['error_message'] = str(e)
            job['completed_at'] = datetime.now()
            
    async def _wipe_device(
        self,
        job_id: str,
        device_id: str,
        algorithm: WipeAlgorithm,
        options: WipeOptions,
        semaphore: asyncio.Semaphore
    ):
        """Wipe a single device"""
        async with semaphore:
            job = self.active_jobs[job_id]
            
            try:
                # Start wipe operation
                operation_id = await self.api.start_wipe(device_id, algorithm, options)
                
                # Add to job operations
                operation_info = {
                    'operation_id': operation_id,
                    'device_id': device_id,
                    'started_at': datetime.now(),
                    'status': 'running'
                }
                job['operations'].append(operation_info)
                
                # Monitor progress
                while True:
                    progress = await self.api.get_wipe_progress(operation_id)
                    if not progress:
                        break
                        
                    if progress.status in [WipeStatus.COMPLETED, WipeStatus.FAILED, WipeStatus.CANCELLED]:
                        break
                        
                    await asyncio.sleep(5)  # Check every 5 seconds
                    
                # Get final result
                result = await self.api.get_wipe_result(operation_id)
                
                # Update operation info
                operation_info['status'] = result.status.value
                operation_info['completed_at'] = datetime.now()
                
                if result.status == WipeStatus.COMPLETED:
                    job['progress']['completed_devices'] += 1
                    
                    # Generate certificate if enabled
                    if self.config['auto_generate_certificates']:
                        try:
                            cert_dir = Path(self.config['certificate_output_dir'])
                            cert_dir.mkdir(parents=True, exist_ok=True)
                            
                            cert_path = cert_dir / f"cert_{operation_id[:8]}.json"
                            certificate = await self.api.generate_certificate(operation_id, str(cert_path))
                            operation_info['certificate_id'] = certificate.certificate_id
                            operation_info['certificate_path'] = str(cert_path)
                            
                        except Exception as e:
                            operation_info['certificate_error'] = str(e)
                            
                else:
                    job['progress']['failed_devices'] += 1
                    operation_info['error_message'] = result.error_message
                    
                # Update overall progress
                total = job['progress']['total_devices']
                completed = job['progress']['completed_devices']
                failed = job['progress']['failed_devices']
                job['progress']['overall_progress'] = ((completed + failed) / total) * 100
                
            except Exception as e:
                job['progress']['failed_devices'] += 1
                operation_info = {
                    'device_id': device_id,
                    'status': 'failed',
                    'error_message': str(e),
                    'started_at': datetime.now(),
                    'completed_at': datetime.now()
                }
                job['operations'].append(operation_info)
                
    async def _generate_job_report(self, job_id: str):
        """Generate a job completion report"""
        job = self.active_jobs[job_id]
        
        report = {
            'job_id': job_id,
            'job_name': job['name'],
            'description': job['description'],
            'algorithm': job['algorithm'],
            'created_at': job['created_at'].isoformat(),
            'started_at': job.get('started_at', '').isoformat() if job.get('started_at') else '',
            'completed_at': job.get('completed_at', '').isoformat() if job.get('completed_at') else '',
            'duration': str(job.get('completed_at', datetime.now()) - job.get('started_at', datetime.now())),
            'status': job['status'],
            'progress': job['progress'],
            'operations': []
        }
        
        for op in job['operations']:
            op_report = {
                'operation_id': op.get('operation_id', ''),
                'device_id': op['device_id'],
                'status': op['status'],
                'started_at': op['started_at'].isoformat(),
                'completed_at': op.get('completed_at', '').isoformat() if op.get('completed_at') else '',
                'certificate_id': op.get('certificate_id', ''),
                'certificate_path': op.get('certificate_path', ''),
                'error_message': op.get('error_message', '')
            }
            report['operations'].append(op_report)
            
        # Save report
        report_dir = Path('./reports')
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f"job_report_{job_id[:8]}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        job['report_path'] = str(report_path)
        
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job cancelled successfully
        """
        job = self.active_jobs.get(job_id)
        if not job or job['status'] != 'running':
            return False
            
        # Cancel all active operations
        for operation in job['operations']:
            if operation['status'] == 'running':
                try:
                    await self.api.cancel_wipe(operation['operation_id'])
                    operation['status'] = 'cancelled'
                    operation['completed_at'] = datetime.now()
                except Exception:
                    pass
                    
        job['status'] = 'cancelled'
        job['completed_at'] = datetime.now()
        
        return True
        
    def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get job status
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information
        """
        job = self.active_jobs.get(job_id)
        if not job:
            return None
            
        return {
            'id': job['id'],
            'name': job['name'],
            'status': job['status'],
            'progress': job['progress'],
            'created_at': job['created_at'].isoformat(),
            'started_at': job.get('started_at', '').isoformat() if job.get('started_at') else '',
            'completed_at': job.get('completed_at', '').isoformat() if job.get('completed_at') else '',
            'operations_count': len(job['operations']),
            'error_message': job.get('error_message', '')
        }
        
    def list_jobs(self) -> List[Dict]:
        """List all jobs
        
        Returns:
            List of job status information
        """
        jobs = []
        for job_id in self.active_jobs:
            status = self.get_job_status(job_id)
            if status:
                jobs.append(status)
        return jobs
        
    def cleanup(self):
        """Cleanup scheduler resources"""
        self.api.cleanup()

def load_job_config(config_path: str) -> Dict:
    """Load job configuration from file"""
    with open(config_path, 'r') as f:
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return yaml.safe_load(f)
        else:
            return json.load(f)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Schedule and manage batch wipe operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create job_config.yaml
  %(prog)s start job_12345678
  %(prog)s status job_12345678
  %(prog)s list
  %(prog)s cancel job_12345678
        """
    )
    
    parser.add_argument(
        'command',
        choices=['create', 'start', 'cancel', 'status', 'list'],
        help='Command to execute'
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='Job ID or configuration file'
    )
    
    parser.add_argument(
        '--config',
        help='Scheduler configuration file'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    # Create scheduler
    scheduler = WipeScheduler(args.config)
    
    try:
        # Initialize
        if not await scheduler.initialize():
            print("Error: Failed to initialize scheduler")
            return 1
            
        # Execute command
        if args.command == 'create':
            if not args.target:
                print("Error: Job configuration file required")
                return 1
                
            job_config = load_job_config(args.target)
            job_id = await scheduler.create_job(job_config)
            
            if args.json:
                print(json.dumps({'job_id': job_id}))
            else:
                print(f"Created job: {job_id}")
                
        elif args.command == 'start':
            if not args.target:
                print("Error: Job ID required")
                return 1
                
            success = await scheduler.start_job(args.target)
            
            if args.json:
                print(json.dumps({'success': success}))
            else:
                if success:
                    print(f"Started job: {args.target}")
                else:
                    print(f"Failed to start job: {args.target}")
                    
        elif args.command == 'cancel':
            if not args.target:
                print("Error: Job ID required")
                return 1
                
            success = await scheduler.cancel_job(args.target)
            
            if args.json:
                print(json.dumps({'success': success}))
            else:
                if success:
                    print(f"Cancelled job: {args.target}")
                else:
                    print(f"Failed to cancel job: {args.target}")
                    
        elif args.command == 'status':
            if not args.target:
                print("Error: Job ID required")
                return 1
                
            status = scheduler.get_job_status(args.target)
            
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                if status:
                    print(f"Job: {status['name']} ({status['id']})")
                    print(f"Status: {status['status']}")
                    print(f"Progress: {status['progress']['overall_progress']:.1f}%")
                    print(f"Devices: {status['progress']['completed_devices']}/{status['progress']['total_devices']} completed")
                    if status['progress']['failed_devices'] > 0:
                        print(f"Failed: {status['progress']['failed_devices']}")
                else:
                    print(f"Job not found: {args.target}")
                    
        elif args.command == 'list':
            jobs = scheduler.list_jobs()
            
            if args.json:
                print(json.dumps(jobs, indent=2))
            else:
                if jobs:
                    print(f"{'Job ID':<12} {'Name':<20} {'Status':<12} {'Progress':<10}")
                    print("-" * 60)
                    for job in jobs:
                        progress = f"{job['progress']['overall_progress']:.1f}%"
                        print(f"{job['id'][:8]:<12} {job['name'][:20]:<20} {job['status']:<12} {progress:<10}")
                else:
                    print("No jobs found")
                    
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        scheduler.cleanup()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
