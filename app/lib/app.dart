import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/app_provider.dart';
import 'screens/splash_screen.dart';
import 'theme/app_theme.dart';

class JanArogyaApp extends StatelessWidget {
  const JanArogyaApp({super.key});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppProvider>();

    // Sync the static JaColors palette to whatever theme is about to render,
    // so that any widget reading JaColors.foo inside build() picks up the
    // right colour.
    final platformBrightness = MediaQuery.platformBrightnessOf(context);
    AppTheme.applyMode(app.themeMode, platformBrightness);

    return MaterialApp(
      title: 'JanArogya',
      debugShowCheckedModeBanner: false,
      theme:     AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: app.themeMode,
      home: const SplashScreen(),
    );
  }
}
