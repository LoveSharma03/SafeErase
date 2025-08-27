import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class CertificatePage extends StatelessWidget {
  final String? certificateId;
  
  const CertificatePage({Key? key, this.certificateId}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Certificate',
      showBackButton: true,
      body: Center(
        child: Text('Certificate Page - ID: $certificateId'),
      ),
    );
  }
}
