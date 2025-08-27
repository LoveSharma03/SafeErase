import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const AppScaffold(
      title: 'Settings',
      showBackButton: true,
      body: Center(
        child: Text('Settings Page - Coming Soon'),
      ),
    );
  }
}
