"""
Platform-specific utilities for SafeErase Python UI
"""

import os
import sys
import platform
import subprocess
from typing import Dict, Optional, List
import ctypes

def get_platform_info() -> Dict[str, str]:
    """Get comprehensive platform information"""
    return {
        'platform': platform.system(),
        'version': platform.version(),
        'release': platform.release(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }

def check_admin_privileges() -> bool:
    """Check if running with administrator/root privileges"""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def request_admin_privileges() -> bool:
    """Request administrator privileges (Windows only)"""
    if platform.system() != 'Windows':
        return False
        
    try:
        import ctypes
        
        # Check if already admin
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
            
        # Request elevation
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        return True
        
    except Exception:
        return False

def get_system_drives() -> List[str]:
    """Get list of system drives"""
    drives = []
    
    if platform.system() == 'Windows':
        try:
            import string
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
        except Exception:
            pass
    else:
        # Unix-like systems
        drives = ['/']
        
        # Check for common mount points
        common_mounts = ['/mnt', '/media', '/Volumes']
        for mount_base in common_mounts:
            if os.path.exists(mount_base):
                try:
                    for item in os.listdir(mount_base):
                        mount_point = os.path.join(mount_base, item)
                        if os.path.ismount(mount_point):
                            drives.append(mount_point)
                except Exception:
                    pass
                    
    return drives

def get_disk_usage(path: str) -> Optional[Dict[str, int]]:
    """Get disk usage information for a path"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        return {
            'total': total,
            'used': used,
            'free': free,
            'percent_used': (used / total) * 100 if total > 0 else 0
        }
    except Exception:
        return None

def is_path_writable(path: str) -> bool:
    """Check if a path is writable"""
    try:
        return os.access(path, os.W_OK)
    except Exception:
        return False

def get_temp_directory() -> str:
    """Get system temporary directory"""
    import tempfile
    return tempfile.gettempdir()

def get_user_documents_dir() -> str:
    """Get user documents directory"""
    if platform.system() == 'Windows':
        try:
            import ctypes.wintypes
            CSIDL_PERSONAL = 5
            SHGFP_TYPE_CURRENT = 0
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
            return buf.value
        except Exception:
            return os.path.expanduser("~/Documents")
    else:
        return os.path.expanduser("~/Documents")

def get_application_data_dir() -> str:
    """Get application data directory"""
    if platform.system() == 'Windows':
        return os.path.expandvars(r'%APPDATA%\SafeErase')
    elif platform.system() == 'Darwin':
        return os.path.expanduser('~/Library/Application Support/SafeErase')
    else:
        return os.path.expanduser('~/.safeerase')

def ensure_directory_exists(path: str) -> bool:
    """Ensure a directory exists, create if necessary"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False

def run_command(command: List[str], timeout: int = 30) -> Optional[Dict[str, str]]:
    """Run a system command and return result"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'success': result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': 'Command timed out',
            'returncode': -1,
            'success': False
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': str(e),
            'returncode': -1,
            'success': False
        }

def get_system_info() -> Dict[str, str]:
    """Get detailed system information"""
    info = get_platform_info()
    
    # Add additional system information
    try:
        import psutil
        
        # Memory information
        memory = psutil.virtual_memory()
        info['total_memory'] = f"{memory.total // (1024**3)} GB"
        info['available_memory'] = f"{memory.available // (1024**3)} GB"
        
        # CPU information
        info['cpu_count'] = str(psutil.cpu_count())
        info['cpu_percent'] = f"{psutil.cpu_percent(interval=1):.1f}%"
        
        # Disk information
        disk = psutil.disk_usage('/')
        info['disk_total'] = f"{disk.total // (1024**3)} GB"
        info['disk_free'] = f"{disk.free // (1024**3)} GB"
        
    except ImportError:
        pass
    except Exception:
        pass
        
    return info

def open_file_explorer(path: str) -> bool:
    """Open file explorer at the specified path"""
    try:
        if platform.system() == 'Windows':
            os.startfile(path)
        elif platform.system() == 'Darwin':
            subprocess.run(['open', path])
        else:
            subprocess.run(['xdg-open', path])
        return True
    except Exception:
        return False

def open_url(url: str) -> bool:
    """Open URL in default browser"""
    try:
        import webbrowser
        webbrowser.open(url)
        return True
    except Exception:
        return False

def get_network_interfaces() -> List[Dict[str, str]]:
    """Get network interface information"""
    interfaces = []
    
    try:
        import psutil
        
        for interface_name, addresses in psutil.net_if_addrs().items():
            interface_info = {
                'name': interface_name,
                'addresses': []
            }
            
            for addr in addresses:
                if addr.family.name in ['AF_INET', 'AF_INET6']:
                    interface_info['addresses'].append({
                        'family': addr.family.name,
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                    
            if interface_info['addresses']:
                interfaces.append(interface_info)
                
    except ImportError:
        pass
    except Exception:
        pass
        
    return interfaces

def check_internet_connectivity() -> bool:
    """Check if internet connectivity is available"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        return False

def get_environment_variables() -> Dict[str, str]:
    """Get relevant environment variables"""
    relevant_vars = [
        'PATH', 'HOME', 'USER', 'USERNAME', 'USERPROFILE',
        'TEMP', 'TMP', 'APPDATA', 'LOCALAPPDATA',
        'PROGRAMFILES', 'PROGRAMFILES(X86)', 'SYSTEMROOT'
    ]
    
    env_vars = {}
    for var in relevant_vars:
        value = os.environ.get(var)
        if value:
            env_vars[var] = value
            
    return env_vars

def is_process_running(process_name: str) -> bool:
    """Check if a process is running"""
    try:
        import psutil
        
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                return True
        return False
        
    except ImportError:
        # Fallback for systems without psutil
        if platform.system() == 'Windows':
            result = run_command(['tasklist', '/FI', f'IMAGENAME eq {process_name}'])
            return result and process_name in result['stdout']
        else:
            result = run_command(['pgrep', '-f', process_name])
            return result and result['returncode'] == 0
            
    except Exception:
        return False

def kill_process(process_name: str) -> bool:
    """Kill a process by name"""
    try:
        import psutil
        
        killed = False
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                try:
                    proc.terminate()
                    killed = True
                except Exception:
                    pass
                    
        return killed
        
    except ImportError:
        # Fallback for systems without psutil
        if platform.system() == 'Windows':
            result = run_command(['taskkill', '/F', '/IM', process_name])
            return result and result['returncode'] == 0
        else:
            result = run_command(['pkill', '-f', process_name])
            return result and result['returncode'] == 0
            
    except Exception:
        return False

def get_hardware_info() -> Dict[str, str]:
    """Get hardware information"""
    info = {}
    
    try:
        if platform.system() == 'Windows':
            # Windows-specific hardware info
            result = run_command(['wmic', 'computersystem', 'get', 'model,manufacturer', '/format:csv'])
            if result and result['success']:
                lines = result['stdout'].strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split(',')
                    if len(parts) >= 3:
                        info['manufacturer'] = parts[1].strip()
                        info['model'] = parts[2].strip()
                        
        elif platform.system() == 'Linux':
            # Linux-specific hardware info
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if line.startswith('model name'):
                            info['cpu'] = line.split(':')[1].strip()
                            break
            except Exception:
                pass
                
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            memory_kb = int(line.split()[1])
                            info['memory'] = f"{memory_kb // 1024} MB"
                            break
            except Exception:
                pass
                
    except Exception:
        pass
        
    return info
