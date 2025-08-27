import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class WipeProgressPage extends StatelessWidget {
  final String? operationId;
  
  const WipeProgressPage({Key? key, this.operationId}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Wipe Progress',
      showBackButton: true,
      body: Center(
        child: Text('Wipe Progress Page - Operation: $operationId'),
      ),
    );
  }
}
