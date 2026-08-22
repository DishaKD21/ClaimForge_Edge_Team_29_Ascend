/**
 * ClaimForge Edge Design System
 * Professional insurance/fintech visual style.
 * Clean, minimal, trustworthy, modern.
 */

export const COLORS = {
  // Primary palette
  primary: '#1B5E8C',
  primaryDark: '#134264',
  primaryLight: '#2E7EB5',
  primaryFaded: '#E8F2F8',

  // Secondary / Accent
  accent: '#2A9D6F',
  accentDark: '#1E7A55',
  accentLight: '#34C088',
  accentFaded: '#E6F7F0',

  // Neutrals
  white: '#FFFFFF',
  background: '#F7F9FB',
  surface: '#FFFFFF',
  border: '#E2E8F0',
  borderLight: '#F1F5F9',
  divider: '#EDF2F7',

  // Text
  textPrimary: '#1A202C',
  textSecondary: '#4A5568',
  textMuted: '#A0AEC0',
  textOnPrimary: '#FFFFFF',
  textOnAccent: '#FFFFFF',

  // Status
  success: '#2A9D6F',
  successLight: '#E6F7F0',
  warning: '#D97706',
  warningLight: '#FEF3C7',
  error: '#DC2626',
  errorLight: '#FEE2E2',
  info: '#1B5E8C',
  infoLight: '#E8F2F8',

  // Misc
  overlay: 'rgba(0, 0, 0, 0.5)',
  shadow: 'rgba(0, 0, 0, 0.08)',
  disabled: '#CBD5E1',
  disabledText: '#94A3B8',
  placeholder: '#A0AEC0',
} as const;

export const TYPOGRAPHY = {
  // Font families - system fonts for cross-platform
  fontFamily: {
    regular: undefined, // Uses system default
    medium: undefined,
    bold: undefined,
  },

  // Font sizes
  fontSize: {
    xs: 11,
    sm: 13,
    base: 15,
    md: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
    '4xl': 36,
  },

  // Font weights
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  },

  // Line heights
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.75,
  },
} as const;

export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 20,
  xl: 24,
  '2xl': 32,
  '3xl': 40,
  '4xl': 48,
  '5xl': 64,
} as const;

export const BORDER_RADIUS = {
  sm: 6,
  base: 8,
  md: 10,
  lg: 12,
  xl: 16,
  full: 9999,
} as const;

export const SHADOWS = {
  sm: {
    shadowColor: COLORS.shadow,
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 1,
    shadowRadius: 2,
    elevation: 1,
  },
  base: {
    shadowColor: COLORS.shadow,
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 1,
    shadowRadius: 4,
    elevation: 2,
  },
  md: {
    shadowColor: COLORS.shadow,
    shadowOffset: {width: 0, height: 4},
    shadowOpacity: 1,
    shadowRadius: 8,
    elevation: 4,
  },
  lg: {
    shadowColor: COLORS.shadow,
    shadowOffset: {width: 0, height: 8},
    shadowOpacity: 1,
    shadowRadius: 16,
    elevation: 8,
  },
} as const;

export const BUTTON_STYLES = {
  primary: {
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.base,
    minHeight: 48,
  },
  secondary: {
    backgroundColor: COLORS.white,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.base,
    minHeight: 48,
  },
  danger: {
    backgroundColor: COLORS.error,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.base,
    minHeight: 48,
  },
  ghost: {
    backgroundColor: 'transparent',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.base,
    minHeight: 48,
  },
} as const;

export const INPUT_STYLES = {
  container: {
    marginBottom: SPACING.base,
  },
  label: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xs,
  },
  input: {
    backgroundColor: COLORS.white,
    borderWidth: 1,
    borderColor: COLORS.border,
    borderRadius: BORDER_RADIUS.base,
    paddingHorizontal: SPACING.base,
    paddingVertical: SPACING.md,
    fontSize: TYPOGRAPHY.fontSize.base,
    color: COLORS.textPrimary,
    minHeight: 48,
  },
  inputFocused: {
    borderColor: COLORS.primary,
    borderWidth: 1.5,
  },
  inputError: {
    borderColor: COLORS.error,
    borderWidth: 1.5,
  },
  errorText: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.error,
    marginTop: SPACING.xs,
  },
} as const;

export const CARD_STYLES = {
  base: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.base,
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOWS.base,
  },
  elevated: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.base,
    ...SHADOWS.md,
  },
} as const;

export const LAYOUT = {
  screenPadding: SPACING.base,
  contentMaxWidth: 600,
  headerHeight: 56,
} as const;
