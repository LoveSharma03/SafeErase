import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

/// Service for interfacing with the SafeErase core engine
class SafeEraseService {
  static final SafeEraseService _instance = SafeEraseService._internal();
  static SafeEraseService get instance => _instance;
  
  SafeEraseService._internal();
  
  DynamicLibrary? _library;
  bool _isInitialized = false;
  
  /// Initialize the SafeErase service
  Future<void> initialize() async {
    if (_isInitialized) return;
    
    try {
      // Load the native library
      _library = _loadLibrary();
      _isInitialized = true;
      print('SafeErase service initialized successfully');
    } catch (e) {
      print('Failed to initialize SafeErase service: $e');
      // Continue without native functionality for development
    }
  }
  
  /// Load the appropriate native library for the platform
  DynamicLibrary _loadLibrary() {
    if (Platform.isWindows) {
      return DynamicLibrary.open('safe_erase_core.dll');
    } else if (Platform.isLinux) {
      return DynamicLibrary.open('libsafe_erase_core.so');
    } else if (Platform.isMacOS) {
      return DynamicLibrary.open('libsafe_erase_core.dylib');
    } else {
      throw UnsupportedError('Platform not supported');
    }
  }
  
  /// Check if the service is initialized
  bool get isInitialized => _isInitialized;
  
  /// Discover available storage devices
  Future<List<DeviceInfo>> discoverDevices() async {
    // TODO: Implement native call to discover devices
    // For now, return mock data for development
    return [
      DeviceInfo(
        id: 'dev1',
        name: 'Samsung SSD 980 PRO',
        path: '/dev/nvme0n1',
        size: 1000204886016,
        deviceType: 'NVMe SSD',
        isRemovable: false,
        isSystemDisk: true,
      ),
      DeviceInfo(
        id: 'dev2',
        name: 'USB Flash Drive',
        path: '/dev/sdb',
        size: 32212254720,
        deviceType: 'USB Storage',
        isRemovable: true,
        isSystemDisk: false,
      ),
    ];
  }
  
  /// Start a wipe operation
  Future<String> startWipe({
    required String deviceId,
    required String algorithm,
    required Map<String, dynamic> options,
  }) async {
    // TODO: Implement native call to start wipe
    // For now, return a mock operation ID
    return 'op_${DateTime.now().millisecondsSinceEpoch}';
  }
  
  /// Get wipe progress
  Future<WipeProgress> getWipeProgress(String operationId) async {
    // TODO: Implement native call to get progress
    // For now, return mock progress
    return WipeProgress(
      operationId: operationId,
      status: 'in_progress',
      percentage: 45.0,
      currentPass: 1,
      totalPasses: 3,
      bytesProcessed: 450000000,
      totalBytes: 1000000000,
      estimatedRemaining: const Duration(minutes: 15),
    );
  }
  
  /// Cancel a wipe operation
  Future<void> cancelWipe(String operationId) async {
    // TODO: Implement native call to cancel wipe
    print('Cancelling wipe operation: $operationId');
  }
  
  /// Check if running with administrator privileges
  Future<bool> hasAdminPrivileges() async {
    // TODO: Implement native call to check privileges
    // For now, return true for development
    return true;
  }
  
  /// Get system information
  Future<SystemInfo> getSystemInfo() async {
    // TODO: Implement native call to get system info
    return SystemInfo(
      version: '1.0.0',
      platform: Platform.operatingSystem,
      hasAdminPrivileges: await hasAdminPrivileges(),
    );
  }
}

/// Device information model
class DeviceInfo {
  final String id;
  final String name;
  final String path;
  final int size;
  final String deviceType;
  final bool isRemovable;
  final bool isSystemDisk;
  
  DeviceInfo({
    required this.id,
    required this.name,
    required this.path,
    required this.size,
    required this.deviceType,
    required this.isRemovable,
    required this.isSystemDisk,
  });
  
  String get formattedSize {
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    double bytes = size.toDouble();
    int unitIndex = 0;
    
    while (bytes >= 1024 && unitIndex < units.length - 1) {
      bytes /= 1024;
      unitIndex++;
    }
    
    return '${bytes.toStringAsFixed(1)} ${units[unitIndex]}';
  }
}

/// Wipe progress model
class WipeProgress {
  final String operationId;
  final String status;
  final double percentage;
  final int currentPass;
  final int totalPasses;
  final int bytesProcessed;
  final int totalBytes;
  final Duration estimatedRemaining;
  
  WipeProgress({
    required this.operationId,
    required this.status,
    required this.percentage,
    required this.currentPass,
    required this.totalPasses,
    required this.bytesProcessed,
    required this.totalBytes,
    required this.estimatedRemaining,
  });
}

/// System information model
class SystemInfo {
  final String version;
  final String platform;
  final bool hasAdminPrivileges;
  
  SystemInfo({
    required this.version,
    required this.platform,
    required this.hasAdminPrivileges,
  });
}
