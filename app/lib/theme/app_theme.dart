import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// ── Palette ───────────────────────────────────────────────────────────────────
//
// JaColors.foo is a runtime getter that returns the light or dark variant
// depending on JaColors._dark. The flag is flipped by AppTheme.applyMode()
// before each MaterialApp build, so widgets that read JaColors.foo inside
// build() pick up the right colour after a Provider notifyListeners().
//
// Defining the palettes as `static const` keeps them as compile-time constants;
// the public surface is only the getters, which are NOT const. That means
// callers who wrote `BorderSide(color: JaColors.line)` will fail to
// compile and the `const` keyword needs to be removed from those sites.
class JaColors {
  static bool _dark = false;
  static bool get isDark => _dark;
  static set dark(bool v) => _dark = v;

  // Light palette
  static const _lBg          = Color(0xFFFFF9F1);
  static const _lSurface     = Color(0xFFFFFFFF);
  static const _lInk         = Color(0xFF2A241D);
  static const _lInkSoft     = Color(0xFF6B5F52);
  static const _lLine        = Color(0xFFE8D9C4);
  static const _lBrand       = Color(0xFF1F7A5A);
  static const _lBrandDark   = Color(0xFF155C43);
  static const _lBrandSoft   = Color(0xFFE1F1E8);
  static const _lAccent      = Color(0xFFE0803A);
  static const _lAccentSoft  = Color(0xFFFDE7D5);
  static const _lDanger      = Color(0xFFC13A2B);
  static const _lDangerSoft  = Color(0xFFFBE0DB);
  static const _lWarn        = Color(0xFFE6A817);
  static const _lWarnSoft    = Color(0xFFFFF2D0);

  // Dark palette
  static const _dBg          = Color(0xFF14110E);
  static const _dSurface     = Color(0xFF1F1B16);
  static const _dInk         = Color(0xFFF4ECDF);
  static const _dInkSoft     = Color(0xFFB8AC9B);
  static const _dLine        = Color(0xFF3A322A);
  static const _dBrand       = Color(0xFF4DBF92);
  static const _dBrandDark   = Color(0xFF8FE6BA);
  static const _dBrandSoft   = Color(0xFF1B3A2E);
  static const _dAccent      = Color(0xFFF09F62);
  static const _dAccentSoft  = Color(0xFF3A2A1C);
  static const _dDanger      = Color(0xFFEF6F62);
  static const _dDangerSoft  = Color(0xFF3D1F1B);
  static const _dWarn        = Color(0xFFF2C24D);
  static const _dWarnSoft    = Color(0xFF3A2E14);

  static Color get bg         => _dark ? _dBg         : _lBg;
  static Color get surface    => _dark ? _dSurface    : _lSurface;
  static Color get ink        => _dark ? _dInk        : _lInk;
  static Color get inkSoft    => _dark ? _dInkSoft    : _lInkSoft;
  static Color get line       => _dark ? _dLine       : _lLine;
  static Color get brand      => _dark ? _dBrand      : _lBrand;
  static Color get brandDark  => _dark ? _dBrandDark  : _lBrandDark;
  static Color get brandSoft  => _dark ? _dBrandSoft  : _lBrandSoft;
  static Color get accent     => _dark ? _dAccent     : _lAccent;
  static Color get accentSoft => _dark ? _dAccentSoft : _lAccentSoft;
  static Color get danger     => _dark ? _dDanger     : _lDanger;
  static Color get dangerSoft => _dark ? _dDangerSoft : _lDangerSoft;
  static Color get warn       => _dark ? _dWarn       : _lWarn;
  static Color get warnSoft   => _dark ? _dWarnSoft   : _lWarnSoft;

  // Card shadow stays subtle in light, almost-invisible black in dark.
  static List<BoxShadow> get cardShadow => _dark
      ? const [BoxShadow(color: Color(0x40000000), blurRadius: 24, offset: Offset(0, 8))]
      : const [BoxShadow(color: Color(0x18000000), blurRadius: 24, offset: Offset(0, 8))];
}

// ── Semantic extensions ───────────────────────────────────────────────────────
extension JaColorsX on BuildContext {
  Color get bg         => JaColors.bg;
  Color get surface    => JaColors.surface;
  Color get ink        => JaColors.ink;
  Color get inkSoft    => JaColors.inkSoft;
  Color get line       => JaColors.line;
  Color get brand      => JaColors.brand;
  Color get brandDark  => JaColors.brandDark;
  Color get brandSoft  => JaColors.brandSoft;
  Color get accent     => JaColors.accent;
  Color get accentSoft => JaColors.accentSoft;
  Color get danger     => JaColors.danger;
  Color get dangerSoft => JaColors.dangerSoft;
  Color get warn       => JaColors.warn;
  Color get warnSoft   => JaColors.warnSoft;

  // Legacy compat
  Color get primaryBg   => JaColors.bg;
  Color get secondaryBg => JaColors.surface;
  Color get cardBg      => JaColors.surface;
  Color get success     => JaColors.brand;
  Color get warning     => JaColors.warn;
  Color get textPrimary => JaColors.ink;
  Color get textSec     => JaColors.inkSoft;
  Color get border      => JaColors.line;
  bool  get isDark      => JaColors.isDark;
}

// ── Typography ────────────────────────────────────────────────────────────────
class JaText {
  // Defaults are nullable so that they resolve against the *current* JaColors
  // at call time (not at class-load time, which would freeze the light values).
  static TextStyle heading(double size, {Color? color, FontWeight weight = FontWeight.w800}) =>
      GoogleFonts.nunito(fontSize: size, fontWeight: weight, color: color ?? JaColors.ink, height: 1.2);

  static TextStyle body(double size, {Color? color, FontWeight weight = FontWeight.w400}) =>
      GoogleFonts.notoSans(fontSize: size, fontWeight: weight, color: color ?? JaColors.ink, height: 1.55);

  static TextStyle label(double size, {Color? color}) =>
      GoogleFonts.notoSans(fontSize: size, fontWeight: FontWeight.w700, color: color ?? JaColors.inkSoft);
}

// ── Theme ─────────────────────────────────────────────────────────────────────
class AppTheme {
  /// Flips the JaColors dark flag based on the requested ThemeMode and the
  /// platform brightness. Call before each MaterialApp build so the static
  /// palette matches the theme that is about to render.
  static void applyMode(ThemeMode mode, Brightness platform) {
    JaColors.dark = switch (mode) {
      ThemeMode.dark   => true,
      ThemeMode.light  => false,
      ThemeMode.system => platform == Brightness.dark,
    };
  }

  static ThemeData light() => _build(Brightness.light);
  static ThemeData dark()  => _build(Brightness.dark);

  // Single ThemeData factory — JaColors is already pointing at the right
  // palette by the time this runs (see applyMode).
  static ThemeData _build(Brightness brightness) {
    final isDark = brightness == Brightness.dark;
    final scheme = isDark
        ? ColorScheme.dark(
            primary:  JaColors._dBrand,
            secondary: JaColors._dAccent,
            surface:  JaColors._dSurface,
            error:    JaColors._dDanger,
            onPrimary: Colors.white,
            onSurface: JaColors._dInk,
            onError:  Colors.white,
          )
        : ColorScheme.light(
            primary:  JaColors._lBrand,
            secondary: JaColors._lAccent,
            surface:  JaColors._lSurface,
            error:    JaColors._lDanger,
            onPrimary: Colors.white,
            onSurface: JaColors._lInk,
            onError:  Colors.white,
          );

    final ink     = isDark ? JaColors._dInk     : JaColors._lInk;
    final inkSoft = isDark ? JaColors._dInkSoft : JaColors._lInkSoft;
    final bg      = isDark ? JaColors._dBg      : JaColors._lBg;
    final surface = isDark ? JaColors._dSurface : JaColors._lSurface;
    final line    = isDark ? JaColors._dLine    : JaColors._lLine;
    final brand   = isDark ? JaColors._dBrand   : JaColors._lBrand;
    final brandSoft = isDark ? JaColors._dBrandSoft : JaColors._lBrandSoft;
    final brandDark = isDark ? JaColors._dBrandDark : JaColors._lBrandDark;

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      scaffoldBackgroundColor: bg,
      colorScheme: scheme,
      textTheme: GoogleFonts.notoSansTextTheme().copyWith(
        displayLarge:   GoogleFonts.nunito(fontSize: 40, fontWeight: FontWeight.w800, color: ink),
        displayMedium:  GoogleFonts.nunito(fontSize: 32, fontWeight: FontWeight.w800, color: ink),
        headlineLarge:  GoogleFonts.nunito(fontSize: 28, fontWeight: FontWeight.w800, color: ink),
        headlineMedium: GoogleFonts.nunito(fontSize: 24, fontWeight: FontWeight.w700, color: ink),
        titleLarge:     GoogleFonts.nunito(fontSize: 20, fontWeight: FontWeight.w700, color: ink),
        titleMedium:    GoogleFonts.nunito(fontSize: 18, fontWeight: FontWeight.w700, color: ink),
        bodyLarge:      GoogleFonts.notoSans(fontSize: 17, color: ink),
        bodyMedium:     GoogleFonts.notoSans(fontSize: 15, color: ink),
        bodySmall:      GoogleFonts.notoSans(fontSize: 13, color: inkSoft),
        labelLarge:     GoogleFonts.notoSans(fontSize: 14, fontWeight: FontWeight.w700, color: ink),
        labelSmall:     GoogleFonts.notoSans(fontSize: 12, fontWeight: FontWeight.w700, color: inkSoft, letterSpacing: 0.5),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: surface,
        foregroundColor: ink,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        titleTextStyle: GoogleFonts.nunito(fontSize: 20, fontWeight: FontWeight.w800, color: ink),
        iconTheme: IconThemeData(color: ink),
      ),
      cardTheme: CardThemeData(
        color: surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(color: line),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: brand,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.nunito(fontSize: 18, fontWeight: FontWeight.w700),
          elevation: 0,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: brand,
          side: BorderSide(color: brand, width: 2),
          minimumSize: const Size(double.infinity, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: GoogleFonts.nunito(fontSize: 18, fontWeight: FontWeight.w700),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: line, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: line, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: brand, width: 2),
        ),
        hintStyle: GoogleFonts.notoSans(fontSize: 15, color: inkSoft),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      ),
      dividerTheme: DividerThemeData(color: line, thickness: 1),
      chipTheme: ChipThemeData(
        backgroundColor: brandSoft,
        labelStyle: GoogleFonts.notoSans(fontSize: 13, fontWeight: FontWeight.w600, color: brandDark),
        side: BorderSide.none,
        shape: const StadiumBorder(),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: surface,
        selectedItemColor: brand,
        unselectedItemColor: inkSoft,
        type: BottomNavigationBarType.fixed,
        elevation: 0,
        selectedLabelStyle: GoogleFonts.notoSans(fontSize: 12, fontWeight: FontWeight.w700),
        unselectedLabelStyle: GoogleFonts.notoSans(fontSize: 12),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: brand,
        linearTrackColor: line,
        circularTrackColor: line,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: surface,
        surfaceTintColor: Colors.transparent,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: isDark ? JaColors._dSurface : JaColors._lInk,
        contentTextStyle: GoogleFonts.notoSans(
          fontSize: 14, color: isDark ? JaColors._dInk : Colors.white,
        ),
      ),
    );
  }

  // Legacy single-arg helper kept so any older `AppTheme.get()` calls compile.
  static ThemeData get() => light();
}

// Legacy AppColors compat (do not extend; kept for any old references)
class AppColors {
  static const lightPrimaryBg   = JaColors._lBg;
  static const lightSecondaryBg = JaColors._lSurface;
  static const lightCardBg      = JaColors._lSurface;
  static const lightAccent      = JaColors._lBrand;
  static const lightAccentSec   = JaColors._lBrandSoft;
  static const lightSuccess     = JaColors._lBrand;
  static const lightWarning     = JaColors._lWarn;
  static const lightDanger      = JaColors._lDanger;
  static const lightTextPrimary = JaColors._lInk;
  static const lightTextSec     = JaColors._lInkSoft;
  static const lightBorder      = JaColors._lLine;
  static const darkPrimaryBg    = JaColors._dBg;
  static const darkSecondaryBg  = JaColors._dSurface;
  static const darkCardBg       = JaColors._dSurface;
  static const darkAccent       = JaColors._dBrand;
  static const darkAccentSec    = JaColors._dBrandSoft;
  static const darkSuccess      = JaColors._dBrand;
  static const darkWarning      = JaColors._dWarn;
  static const darkDanger       = JaColors._dDanger;
  static const darkTextPrimary  = JaColors._dInk;
  static const darkTextSec      = JaColors._dInkSoft;
  static const darkBorder       = JaColors._dLine;
}
