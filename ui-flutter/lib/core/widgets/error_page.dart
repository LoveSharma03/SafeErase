import 'package:flutter/material.dart';
import 'package:material_design_icons_flutter/material_design_icons_flutter.dart';
import 'package:safe_erase_ui/core/theme/app_theme.dart';

class ErrorPage extends StatelessWidget {
  final Object? error;
  final String? message;
  final VoidCallback? onRetry;

  const ErrorPage({
    Key? key,
    this.error,
    this.message,
    this.onRetry,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Error'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(AppTheme.spacingL),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                MdiIcons.alertCircleOutline,
                size: 64,
                color: AppTheme.customColors['danger'],
              ),
              const SizedBox(height: AppTheme.spacingL),
              Text(
                'Something went wrong',
                style: AppTheme.headingMedium.copyWith(
                  color: Theme.of(context).colorScheme.onSurface,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppTheme.spacingM),
              Text(
                message ?? error?.toString() ?? 'An unexpected error occurred',
                style: AppTheme.bodyMedium.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppTheme.spacingL),
              if (onRetry != null)
                ElevatedButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(MdiIcons.refresh),
                  label: const Text('Retry'),
                ),
              const SizedBox(height: AppTheme.spacingM),
              TextButton(
                onPressed: () => Navigator.of(context).pushReplacementNamed('/'),
                child: const Text('Go Home'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
