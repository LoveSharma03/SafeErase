import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class DeviceSelectionPage extends StatelessWidget {
  const DeviceSelectionPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const AppScaffold(
      title: 'Select Device',
      showBackButton: true,
      body: Center(
        child: Text('Device Selection Page - Coming Soon'),
      ),
    );
  }
}
