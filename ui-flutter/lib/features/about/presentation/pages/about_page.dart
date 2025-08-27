import 'package:flutter/material.dart';
import 'package:safe_erase_ui/core/widgets/app_scaffold.dart';

class AboutPage extends StatelessWidget {
  const AboutPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const AppScaffold(
      title: 'About',
      showBackButton: true,
      body: Center(
        child: Text('About Page - Coming Soon'),
      ),
    );
  }
}
