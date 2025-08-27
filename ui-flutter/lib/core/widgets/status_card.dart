import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:safe_erase_ui/core/theme/app_theme.dart';

enum StatusType {
  success,
  warning,
  error,
  info,
}

class StatusCard extends StatelessWidget {
  final String title;
  final String status;
  final String message;
  final StatusType type;
  final VoidCallback? onTap;

  const StatusCard({
    Key? key,
    required this.title,
    required this.status,
    required this.message,
    required this.type,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor();
    final icon = _getStatusIcon();

    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppTheme.radiusL),
        child: Padding(
          padding: const EdgeInsets.all(AppTheme.spacingM),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    icon,
                    color: color,
                    size: 24,
                  ),
                  const SizedBox(width: AppTheme.spacingS),
                  Expanded(
                    child: Text(
                      title,
                      style: AppTheme.bodyMedium.copyWith(
                        fontWeight: FontWeight.w600,
                        color: Theme.of(context).colorScheme.onSurface,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AppTheme.spacingS),
              Text(
                status,
                style: AppTheme.bodyLarge.copyWith(
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
              const SizedBox(height: AppTheme.spacingXS),
              Text(
                message,
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

  Color _getStatusColor() {
    switch (type) {
      case StatusType.success:
        return AppTheme.customColors['success']!;
      case StatusType.warning:
        return AppTheme.customColors['warning']!;
      case StatusType.error:
        return AppTheme.customColors['danger']!;
      case StatusType.info:
        return AppTheme.customColors['info']!;
    }
  }

  IconData _getStatusIcon() {
    switch (type) {
      case StatusType.success:
        return MdiIcons.checkCircle;
      case StatusType.warning:
        return MdiIcons.alertCircle;
      case StatusType.error:
        return MdiIcons.closeCircle;
      case StatusType.info:
        return MdiIcons.informationOutline;
    }
  }
}
