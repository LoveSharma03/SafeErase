import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:safe_erase_ui/core/theme/app_theme.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';
import 'package:safe_erase_ui/core/widgets/status_card.dart';
import 'package:safe_erase_ui/features/home/presentation/providers/home_providers.dart';

class HomePage extends ConsumerWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final systemStatus = ref.watch(systemStatusProvider);
    final recentOperations = ref.watch(recentOperationsProvider);
    
    return AppScaffold(
      title: 'SafeErase',
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(AppTheme.spacingM),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Welcome section
            _buildWelcomeSection(context),
            const SizedBox(height: AppTheme.spacingL),
            
            // Quick actions
            _buildQuickActions(context),
            const SizedBox(height: AppTheme.spacingL),
            
            // System status
            systemStatus.when(
              data: (status) => _buildSystemStatus(context, status),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => StatusCard(
                title: 'System Status',
                status: 'Error',
                message: 'Failed to load system status',
                type: StatusType.error,
              ),
            ),
            const SizedBox(height: AppTheme.spacingL),
            
            // Recent operations
            recentOperations.when(
              data: (operations) => _buildRecentOperations(context, operations),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => StatusCard(
                title: 'Recent Operations',
                status: 'Error',
                message: 'Failed to load recent operations',
                type: StatusType.error,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildWelcomeSection(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AppTheme.spacingL),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  MdiIcons.shieldCheck,
                  size: 48,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: AppTheme.spacingM),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome to SafeErase',
                        style: AppTheme.headingMedium.copyWith(
                          color: Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                      const SizedBox(height: AppTheme.spacingS),
                      Text(
                        'Secure and reliable data wiping for IT asset recyclers',
                        style: AppTheme.bodyMedium.copyWith(
                          color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: AppTheme.spacingM),
            const Divider(),
            const SizedBox(height: AppTheme.spacingM),
            Row(
              children: [
                _buildFeatureChip(
                  context,
                  icon: MdiIcons.certificate,
                  label: 'Tamper-proof certificates',
                ),
                const SizedBox(width: AppTheme.spacingS),
                _buildFeatureChip(
                  context,
                  icon: MdiIcons.security,
                  label: 'Military-grade security',
                ),
                const SizedBox(width: AppTheme.spacingS),
                _buildFeatureChip(
                  context,
                  icon: MdiIcons.speedometer,
                  label: 'One-click operation',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildFeatureChip(BuildContext context, {required IconData icon, required String label}) {
    return Chip(
      avatar: Icon(icon, size: 16),
      label: Text(
        label,
        style: AppTheme.bodySmall,
      ),
      backgroundColor: Theme.of(context).colorScheme.primaryContainer,
    );
  }
  
  Widget _buildQuickActions(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: AppTheme.headingSmall.copyWith(
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        const SizedBox(height: AppTheme.spacingM),
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                context,
                icon: MdiIcons.harddisk,
                title: 'Start Wipe',
                subtitle: 'Select devices and begin secure wiping',
                onTap: () => context.go('/devices'),
              ),
            ),
            const SizedBox(width: AppTheme.spacingM),
            Expanded(
              child: _buildActionCard(
                context,
                icon: MdiIcons.fileDocument,
                title: 'View Certificates',
                subtitle: 'Browse and verify wipe certificates',
                onTap: () => context.go('/certificate'),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingM),
        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                context,
                icon: MdiIcons.cog,
                title: 'Settings',
                subtitle: 'Configure wiping preferences',
                onTap: () => context.go('/settings'),
              ),
            ),
            const SizedBox(width: AppTheme.spacingM),
            Expanded(
              child: _buildActionCard(
                context,
                icon: MdiIcons.information,
                title: 'About',
                subtitle: 'Learn more about SafeErase',
                onTap: () => context.go('/about'),
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildActionCard(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radiusL),
        child: Padding(
          padding: const EdgeInsets.all(AppTheme.spacingM),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                icon,
                size: 32,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(height: AppTheme.spacingM),
              Text(
                title,
                style: AppTheme.bodyLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).colorScheme.onSurface,
                ),
              ),
              const SizedBox(height: AppTheme.spacingS),
              Text(
                subtitle,
                style: AppTheme.bodySmall.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildSystemStatus(BuildContext context, SystemStatus status) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'System Status',
          style: AppTheme.headingSmall.copyWith(
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
        const SizedBox(height: AppTheme.spacingM),
        Row(
          children: [
            Expanded(
              child: StatusCard(
                title: 'Privileges',
                status: status.hasAdminPrivileges ? 'Administrator' : 'Limited',
                message: status.hasAdminPrivileges 
                    ? 'Full access to storage devices'
                    : 'Run as administrator for full access',
                type: status.hasAdminPrivileges ? StatusType.success : StatusType.warning,
              ),
            ),
            const SizedBox(width: AppTheme.spacingM),
            Expanded(
              child: StatusCard(
                title: 'Devices',
                status: '${status.availableDevices} Available',
                message: status.availableDevices > 0 
                    ? 'Ready for secure wiping'
                    : 'No storage devices detected',
                type: status.availableDevices > 0 ? StatusType.success : StatusType.info,
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildRecentOperations(BuildContext context, List<RecentOperation> operations) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Operations',
              style: AppTheme.headingSmall.copyWith(
                color: Theme.of(context).colorScheme.onSurface,
              ),
            ),
            if (operations.isNotEmpty)
              TextButton(
                onPressed: () => context.go('/certificate'),
                child: const Text('View All'),
              ),
          ],
        ),
        const SizedBox(height: AppTheme.spacingM),
        if (operations.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(AppTheme.spacingL),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      MdiIcons.history,
                      size: 48,
                      color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                    ),
                    const SizedBox(height: AppTheme.spacingM),
                    Text(
                      'No recent operations',
                      style: AppTheme.bodyMedium.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                      ),
                    ),
                    const SizedBox(height: AppTheme.spacingS),
                    Text(
                      'Start your first wipe operation to see it here',
                      style: AppTheme.bodySmall.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ...operations.take(3).map((operation) => _buildOperationCard(context, operation)),
      ],
    );
  }
  
  Widget _buildOperationCard(BuildContext context, RecentOperation operation) {
    return Card(
      margin: const EdgeInsets.only(bottom: AppTheme.spacingS),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getStatusColor(operation.status),
          child: Icon(
            _getStatusIcon(operation.status),
            color: Colors.white,
            size: 20,
          ),
        ),
        title: Text(
          operation.deviceModel,
          style: AppTheme.bodyMedium.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        subtitle: Text(
          '${operation.algorithm} • ${_formatDate(operation.completedAt)}',
          style: AppTheme.bodySmall,
        ),
        trailing: operation.certificateId != null
            ? IconButton(
                icon: const Icon(MdiIcons.certificate),
                onPressed: () => context.go('/certificate?id=${operation.certificateId}'),
                tooltip: 'View Certificate',
              )
            : null,
      ),
    );
  }
  
  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return AppTheme.customColors['success']!;
      case 'failed':
        return AppTheme.customColors['danger']!;
      case 'in_progress':
        return AppTheme.customColors['info']!;
      default:
        return AppTheme.customColors['warning']!;
    }
  }
  
  IconData _getStatusIcon(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return MdiIcons.checkCircle;
      case 'failed':
        return MdiIcons.alertCircle;
      case 'in_progress':
        return MdiIcons.progressClock;
      default:
        return MdiIcons.help;
    }
  }
  
  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);
    
    if (difference.inDays > 0) {
      return '${difference.inDays} day${difference.inDays == 1 ? '' : 's'} ago';
    } else if (difference.inHours > 0) {
      return '${difference.inHours} hour${difference.inHours == 1 ? '' : 's'} ago';
    } else if (difference.inMinutes > 0) {
      return '${difference.inMinutes} minute${difference.inMinutes == 1 ? '' : 's'} ago';
    } else {
      return 'Just now';
    }
  }
}

// Data models for the home page
class SystemStatus {
  final bool hasAdminPrivileges;
  final int availableDevices;
  final String version;
  
  SystemStatus({
    required this.hasAdminPrivileges,
    required this.availableDevices,
    required this.version,
  });
}

class RecentOperation {
  final String id;
  final String deviceModel;
  final String algorithm;
  final String status;
  final DateTime completedAt;
  final String? certificateId;
  
  RecentOperation({
    required this.id,
    required this.deviceModel,
    required this.algorithm,
    required this.status,
    required this.completedAt,
    this.certificateId,
  });
}
