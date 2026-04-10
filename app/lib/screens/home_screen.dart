import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../l10n/app_strings.dart';
import '../providers/app_provider.dart';
import '../services/tts_service.dart';
import '../theme/app_theme.dart';
import 'chat_screen.dart';
import 'history_screen.dart';
import 'scan_entry_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _speaking = false;

  @override
  void initState() {
    super.initState();
    TtsService().onStop = () {
      if (mounted) setState(() => _speaking = false);
    };
  }

  @override
  void dispose() {
    TtsService().stop();
    super.dispose();
  }

  Future<void> _toggleGreeting() async {
    final lang = context.read<AppProvider>().langCode;
    final s    = AppStrings(lang);
    if (_speaking) {
      await TtsService().stop();
      setState(() => _speaking = false);
    } else {
      setState(() => _speaking = true);
      await TtsService().speak(s.homeGreeting, langCode: lang);
    }
  }

  Future<void> _callHelpline() async {
    final uri = Uri(scheme: 'tel', path: '18001112345');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  @override
  Widget build(BuildContext context) {
    final lang = context.watch<AppProvider>().langCode;
    final s    = AppStrings(lang);

    return Scaffold(
      backgroundColor: context.primaryBg,
      appBar: AppBar(
        title: Row(children: [
          Icon(Icons.health_and_safety, color: context.accent, size: 22),
          const SizedBox(width: 8),
          Text(s.appName, style: TextStyle(
            color: context.textPrimary, fontSize: 20, fontWeight: FontWeight.bold,
          )),
        ]),
        actions: [
          // Theme toggle
          IconButton(
            icon: Icon(
              context.isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
              color: context.textSec,
            ),
            onPressed: () {
              final p = context.read<AppProvider>();
              p.setTheme(context.isDark ? ThemeMode.light : ThemeMode.dark);
            },
          ),
          // Language selector
          _LangSelector(lang: lang),
          const SizedBox(width: 4),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Greeting card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: context.accent,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(s.homeGreeting,
                            style: const TextStyle(
                                color: Colors.white, fontSize: 20,
                                fontWeight: FontWeight.bold)),
                      ),
                      // TTS speaker button
                      GestureDetector(
                        onTap: _toggleGreeting,
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.2),
                            shape: BoxShape.circle,
                          ),
                          child: Icon(
                            _speaking
                                ? Icons.stop_rounded
                                : Icons.volume_up_rounded,
                            color: Colors.white, size: 20,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  Text(s.appTagline,
                      style: const TextStyle(color: Colors.white70, fontSize: 13)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Scan Now card
            _ActionCard(
              icon: Icons.camera_alt,
              title: s.homeScanNow,
              subtitle: s.homeCameraHint,
              onTap: () {
                // Navigate to Scan tab via MainShell
                final scaffold = Scaffold.maybeOf(context);
                if (scaffold != null) {
                  // Using IndexedStack — navigate via parent
                  _navigateToTab(context, 1);
                }
              },
              primary: true,
            ),
            const SizedBox(height: 12),

            // View History card
            _ActionCard(
              icon: Icons.history,
              title: s.homeViewHistory,
              subtitle: s.homeHistoryHint,
              onTap: () => _navigateToTab(context, 2),
              primary: false,
            ),
            const SizedBox(height: 12),

            // Health Chat card
            _ChatCard(s: s),
            const SizedBox(height: 24),

            // Cancer Helpline
            InkWell(
              onTap: _callHelpline,
              borderRadius: BorderRadius.circular(12),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: context.cardBg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: context.border),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 40, height: 40,
                      decoration: BoxDecoration(
                        color: context.danger.withValues(alpha: 0.12),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(Icons.phone, color: context.danger, size: 20),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(s.helplineLabel,
                            style: TextStyle(
                                color: context.textSec, fontSize: 12)),
                        Text(s.helplineNumber,
                            style: TextStyle(
                                color: context.textPrimary,
                                fontSize: 16, fontWeight: FontWeight.bold)),
                        Text('Toll-Free 24/7',
                            style: TextStyle(color: context.textSec, fontSize: 11)),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 16),

            // Disclaimer
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: context.warning.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: context.warning.withValues(alpha: 0.4)),
              ),
              child: Text(s.disclaimer,
                  style: TextStyle(
                      color: context.textSec, fontSize: 12, height: 1.5,
                      fontStyle: FontStyle.italic)),
            ),
          ],
        ),
      ),
    );
  }

  void _navigateToTab(BuildContext context, int idx) {
    if (idx == 1) {
      Navigator.push(context,
          MaterialPageRoute(builder: (_) => const ScanEntryScreen()));
    } else if (idx == 2) {
      Navigator.push(context,
          MaterialPageRoute(builder: (_) => const HistoryScreen()));
    }
  }
}

class _ChatCard extends StatelessWidget {
  final AppStrings s;
  const _ChatCard({required this.s});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const ChatScreen()),
      ),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: context.cardBg,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: context.accentSec.withValues(alpha: 0.5)),
          boxShadow: context.isDark
              ? null
              : [BoxShadow(color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 6, offset: const Offset(0, 2))],
        ),
        child: Row(
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: context.accentSec.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.chat_bubble_outline,
                  color: context.accentSec, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(s.navChat,
                      style: TextStyle(
                          color: context.textPrimary,
                          fontSize: 16, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text('${s.chatWelcome.split('.').first}.',
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                          color: context.textSec, fontSize: 13)),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios, color: context.textSec, size: 14),
          ],
        ),
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final bool primary;

  const _ActionCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    required this.primary,
  });

  @override
  Widget build(BuildContext context) {
    final color = primary ? context.accent : context.accentSec;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: context.cardBg,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: primary ? color.withValues(alpha: 0.5) : context.border,
          ),
          boxShadow: context.isDark
              ? null
              : [BoxShadow(color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 6, offset: const Offset(0, 2))],
        ),
        child: Row(
          children: [
            Container(
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: TextStyle(
                          color: context.textPrimary,
                          fontSize: 16, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: TextStyle(
                          color: context.textSec, fontSize: 13, height: 1.4)),
                ],
              ),
            ),
            Icon(Icons.arrow_forward_ios, color: context.textSec, size: 14),
          ],
        ),
      ),
    );
  }
}

class _LangSelector extends StatelessWidget {
  final String lang;
  const _LangSelector({required this.lang});

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<String>(
      initialValue: lang,
      onSelected: (code) => context.read<AppProvider>().setLanguage(code),
      offset: const Offset(0, 44),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: context.accent.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: context.accent.withValues(alpha: 0.3)),
        ),
        child: Text(AppStrings.langNames[lang] ?? lang,
            style: TextStyle(
                color: context.accent, fontSize: 12, fontWeight: FontWeight.w600)),
      ),
      itemBuilder: (_) => AppStrings.supportedLangs.map((code) =>
        PopupMenuItem<String>(
          value: code,
          child: Row(children: [
            if (code == lang)
              Icon(Icons.check, color: context.accent, size: 16)
            else
              const SizedBox(width: 16),
            const SizedBox(width: 8),
            Text(AppStrings.langNames[code] ?? code),
          ]),
        ),
      ).toList(),
    );
  }
}
