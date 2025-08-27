import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:safe_erase_ui/core/services/safe_erase_service.dart';
import 'package:safe_erase_ui/features/home/presentation/pages/home_page.dart';

/// Provider for system status
final systemStatusProvider = FutureProvider<SystemStatus>((ref) async {
  final service = SafeEraseService.instance;
  final systemInfo = await service.getSystemInfo();
  final devices = await service.discoverDevices();
  
  return SystemStatus(
    hasAdminPrivileges: systemInfo.hasAdminPrivileges,
    availableDevices: devices.length,
    version: systemInfo.version,
  );
});

/// Provider for recent operations
final recentOperationsProvider = FutureProvider<List<RecentOperation>>((ref) async {
  // TODO: Implement actual recent operations loading
  // For now, return mock data
  return [
    RecentOperation(
      id: 'op1',
      deviceModel: 'Samsung SSD 980 PRO',
      algorithm: 'NIST 800-88',
      status: 'completed',
      completedAt: DateTime.now().subtract(const Duration(hours: 2)),
      certificateId: 'cert_123',
    ),
    RecentOperation(
      id: 'op2',
      deviceModel: 'USB Flash Drive',
      algorithm: 'DoD 5220.22-M',
      status: 'completed',
      completedAt: DateTime.now().subtract(const Duration(days: 1)),
      certificateId: 'cert_124',
    ),
  ];
});
