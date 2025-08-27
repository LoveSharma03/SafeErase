import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class WipeConfigurationPage extends StatelessWidget {
  final String? deviceId;
  
  const WipeConfigurationPage({Key? key, this.deviceId}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Configure Wipe',
      showBackButton: true,
      body: Center(
        child: Text('Wipe Configuration Page - Device: $deviceId'),
      ),
    );
  }
}
