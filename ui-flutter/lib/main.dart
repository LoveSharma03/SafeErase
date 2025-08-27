import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:safe_erase_ui/core/theme/app_theme.dart';
import 'package:safe_erase_ui/core/routing/app_router.dart';
import 'package:safe_erase_ui/core/services/safe_erase_service.dart';
import 'package:safe_erase_ui/core/utils/platform_utils.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize platform-specific services
  await PlatformUtils.initialize();
  
  // Initialize SafeErase core service
  await SafeEraseService.instance.initialize();
  
  runApp(
    ProviderScope(
      child: SafeEraseApp(),
    ),
  );
}

class SafeEraseApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(appRouterProvider);
    
    return MaterialApp.router(
      title: 'SafeErase - Secure Data Wiping',
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
