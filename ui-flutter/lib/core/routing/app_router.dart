import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:safe_erase_ui/features/home/presentation/pages/home_page.dart';
import 'package:safe_erase_ui/features/device_selection/presentation/pages/device_selection_page.dart';
import 'package:safe_erase_ui/features/wipe_configuration/presentation/pages/wipe_configuration_page.dart';
import 'package:safe_erase_ui/features/wipe_progress/presentation/pages/wipe_progress_page.dart';
import 'package:safe_erase_ui/features/certificate/presentation/pages/certificate_page.dart';
import 'package:safe_erase_ui/features/settings/presentation/pages/settings_page.dart';
import 'package:safe_erase_ui/features/about/presentation/pages/about_page.dart';
import 'package:safe_erase_ui/core/widgets/error_page.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    errorBuilder: (context, state) => ErrorPage(error: state.error),
    routes: [
      // Home route
      GoRoute(
        path: '/',
        name: 'home',
        builder: (context, state) => const HomePage(),
      ),
      
      // Device selection
      GoRoute(
        path: '/devices',
        name: 'device_selection',
        builder: (context, state) => const DeviceSelectionPage(),
      ),
      
      // Wipe configuration
      GoRoute(
        path: '/configure',
        name: 'wipe_configuration',
        builder: (context, state) {
          final deviceId = state.uri.queryParameters['device'];
          return WipeConfigurationPage(deviceId: deviceId);
        },
      ),
      
      // Wipe progress
      GoRoute(
        path: '/wipe',
        name: 'wipe_progress',
        builder: (context, state) {
          final operationId = state.uri.queryParameters['operation'];
          return WipeProgressPage(operationId: operationId);
        },
      ),
      
      // Certificate viewing
      GoRoute(
        path: '/certificate',
        name: 'certificate',
        builder: (context, state) {
          final certificateId = state.uri.queryParameters['id'];
          return CertificatePage(certificateId: certificateId);
        },
      ),
      
      // Settings
      GoRoute(
        path: '/settings',
        name: 'settings',
        builder: (context, state) => const SettingsPage(),
      ),
      
      // About
      GoRoute(
        path: '/about',
        name: 'about',
        builder: (context, state) => const AboutPage(),
      ),
    ],
  );
});

// Navigation helper extension
extension AppRouterExtension on GoRouter {
  void goToDeviceSelection() => go('/devices');
  
  void goToWipeConfiguration(String deviceId) => 
      go('/configure?device=$deviceId');
  
  void goToWipeProgress(String operationId) => 
      go('/wipe?operation=$operationId');
  
  void goToCertificate(String certificateId) => 
      go('/certificate?id=$certificateId');
  
  void goToSettings() => go('/settings');
  
  void goToAbout() => go('/about');
  
  void goHome() => go('/');
}
