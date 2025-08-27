import 'dart:io';
import 'package:flutter/services.dart';

/// Platform-specific utilities
class PlatformUtils {
  static bool _isInitialized = false;
  
  /// Initialize platform-specific services
  static Future<void> initialize() async {
    if (_isInitialized) return;
    
    // Set up platform-specific configurations
    if (Platform.isWindows) {
      await _initializeWindows();
    } else if (Platform.isLinux) {
      await _initializeLinux();
    } else if (Platform.isMacOS) {
      await _initializeMacOS();
    }
    
    _isInitialized = true;
  }
  
  static Future<void> _initializeWindows() async {
    // Windows-specific initialization
    print('Initializing Windows platform services');
  }
  
  static Future<void> _initializeLinux() async {
    // Linux-specific initialization
    print('Initializing Linux platform services');
  }
  
  static Future<void> _initializeMacOS() async {
    // macOS-specific initialization
    print('Initializing macOS platform services');
  }
  
  /// Check if running on Windows
  static bool get isWindows => Platform.isWindows;
  
  /// Check if running on Linux
  static bool get isLinux => Platform.isLinux;
  
  /// Check if running on macOS
  static bool get isMacOS => Platform.isMacOS;
  
  /// Get platform name
  static String get platformName => Platform.operatingSystem;
  
  /// Check if running with elevated privileges
  static Future<bool> hasElevatedPrivileges() async {
    try {
      if (Platform.isWindows) {
        // Check if running as administrator on Windows
        final result = await Process.run('net', ['session'], runInShell: true);
        return result.exitCode == 0;
      } else {
        // Check if running as root on Unix-like systems
        final result = await Process.run('id', ['-u']);
        return result.stdout.toString().trim() == '0';
      }
    } catch (e) {
      print('Error checking privileges: $e');
      return false;
    }
  }
  
  /// Request elevated privileges
  static Future<bool> requestElevatedPrivileges() async {
    try {
      if (Platform.isWindows) {
        // On Windows, we would need to restart the app with elevated privileges
        // This is typically done by the installer or by the user
        return false;
      } else {
        // On Unix-like systems, we can use sudo
        // But this requires user interaction
        return false;
      }
    } catch (e) {
      print('Error requesting elevated privileges: $e');
      return false;
    }
  }
  
  /// Get system information
  static Future<Map<String, String>> getSystemInfo() async {
    final info = <String, String>{};
    
    info['platform'] = Platform.operatingSystem;
    info['version'] = Platform.operatingSystemVersion;
    info['locale'] = Platform.localeName;
    
    try {
      if (Platform.isWindows) {
        final result = await Process.run('systeminfo', []);
        // Parse systeminfo output for additional details
        info['details'] = result.stdout.toString();
      } else {
        final result = await Process.run('uname', ['-a']);
        info['details'] = result.stdout.toString().trim();
      }
    } catch (e) {
      print('Error getting system info: $e');
    }
    
    return info;
  }
}
