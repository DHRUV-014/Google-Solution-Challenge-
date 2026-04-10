import 'package:flutter/material.dart';

/// All app colors — never use hex values directly in widgets.
class AppColors {
  // ── Dark Mode ──────────────────────────────────────────────────────────────
  static const darkPrimaryBg    = Color(0xFF0A0E1A);
  static const darkSecondaryBg  = Color(0xFF111827);
  static const darkCardBg       = Color(0xFF1A2234);
  static const darkAccent        = Color(0xFF3B82F6);
  static const darkAccentSec    = Color(0xFF60A5FA);
  static const darkSuccess      = Color(0xFF10B981);
  static const darkWarning      = Color(0xFFF59E0B);
  static const darkDanger       = Color(0xFFEF4444);
  static const darkTextPrimary  = Color(0xFFF9FAFB);
  static const darkTextSec      = Color(0xFF9CA3AF);
  static const darkBorder       = Color(0xFF1F2937);

  // ── Light Mode ─────────────────────────────────────────────────────────────
  static const lightPrimaryBg   = Color(0xFFF8FAFC);
  static const lightSecondaryBg = Color(0xFFFFFFFF);
  static const lightCardBg      = Color(0xFFFFFFFF);
  static const lightAccent      = Color(0xFF2563EB);
  static const lightAccentSec   = Color(0xFF3B82F6);
  static const lightSuccess     = Color(0xFF059669);
  static const lightWarning     = Color(0xFFD97706);
  static const lightDanger      = Color(0xFFDC2626);
  static const lightTextPrimary = Color(0xFF111827);
  static const lightTextSec     = Color(0xFF6B7280);
  static const lightBorder      = Color(0xFFE5E7EB);
}

/// Extension to access semantic colors from BuildContext.
extension AppColorsX on BuildContext {
  bool get isDark => Theme.of(this).brightness == Brightness.dark;

  Color get primaryBg   => isDark ? AppColors.darkPrimaryBg   : AppColors.lightPrimaryBg;
  Color get secondaryBg => isDark ? AppColors.darkSecondaryBg : AppColors.lightSecondaryBg;
  Color get cardBg      => isDark ? AppColors.darkCardBg      : AppColors.lightCardBg;
  Color get accent      => isDark ? AppColors.darkAccent      : AppColors.lightAccent;
  Color get accentSec   => isDark ? AppColors.darkAccentSec   : AppColors.lightAccentSec;
  Color get success     => isDark ? AppColors.darkSuccess     : AppColors.lightSuccess;
  Color get warning     => isDark ? AppColors.darkWarning     : AppColors.lightWarning;
  Color get danger      => isDark ? AppColors.darkDanger      : AppColors.lightDanger;
  Color get textPrimary => isDark ? AppColors.darkTextPrimary : AppColors.lightTextPrimary;
  Color get textSec     => isDark ? AppColors.darkTextSec     : AppColors.lightTextSec;
  Color get border      => isDark ? AppColors.darkBorder      : AppColors.lightBorder;
}

class AppTheme {
  static ThemeData light() {
    const accent = AppColors.lightAccent;
    return ThemeData(
      brightness: Brightness.light,
      useMaterial3: true,
      scaffoldBackgroundColor: AppColors.lightPrimaryBg,
      colorScheme: const ColorScheme.light(
        primary: accent,
        secondary: AppColors.lightAccentSec,
        surface: AppColors.lightCardBg,
        onPrimary: Colors.white,
        onSurface: AppColors.lightTextPrimary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.lightSecondaryBg,
        foregroundColor: AppColors.lightTextPrimary,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: TextStyle(
          color: AppColors.lightTextPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.lightCardBg,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: AppColors.lightBorder),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accent,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accent,
          side: const BorderSide(color: accent),
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      dividerTheme: const DividerThemeData(color: AppColors.lightBorder),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.lightSecondaryBg,
        selectedItemColor: AppColors.lightAccent,
        unselectedItemColor: AppColors.lightTextSec,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
    );
  }

  static ThemeData dark() {
    const accent = AppColors.darkAccent;
    return ThemeData(
      brightness: Brightness.dark,
      useMaterial3: true,
      scaffoldBackgroundColor: AppColors.darkPrimaryBg,
      colorScheme: const ColorScheme.dark(
        primary: accent,
        secondary: AppColors.darkAccentSec,
        surface: AppColors.darkCardBg,
        onPrimary: Colors.white,
        onSurface: AppColors.darkTextPrimary,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.darkSecondaryBg,
        foregroundColor: AppColors.darkTextPrimary,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: TextStyle(
          color: AppColors.darkTextPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.darkCardBg,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: AppColors.darkBorder),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accent,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: accent,
          side: const BorderSide(color: accent),
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
        ),
      ),
      dividerTheme: const DividerThemeData(color: AppColors.darkBorder),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.darkSecondaryBg,
        selectedItemColor: AppColors.darkAccent,
        unselectedItemColor: AppColors.darkTextSec,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
      ),
    );
  }
}
