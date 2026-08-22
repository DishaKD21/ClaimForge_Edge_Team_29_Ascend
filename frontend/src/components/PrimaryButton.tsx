import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS} from '../constants';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface PrimaryButtonProps {
  title: string;
  onPress: () => void;
  variant?: ButtonVariant;
  disabled?: boolean;
  loading?: boolean;
  icon?: string;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
}

export const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  disabled = false,
  loading = false,
  icon,
  style,
  textStyle,
  accessibilityLabel,
}) => {
  const isDisabled = disabled || loading;

  const buttonStyles = [
    styles.base,
    styles[variant],
    isDisabled && styles.disabled,
    style,
  ];

  const labelStyles = [
    styles.label,
    styles[`${variant}Label` as keyof typeof styles] as TextStyle,
    isDisabled && styles.disabledLabel,
    textStyle,
  ];

  return (
    <TouchableOpacity
      style={buttonStyles}
      onPress={onPress}
      disabled={isDisabled}
      activeOpacity={0.7}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || title}
      accessibilityState={{disabled: isDisabled, busy: loading}}>
      {loading ? (
        <ActivityIndicator
          size="small"
          color={variant === 'secondary' ? COLORS.primary : COLORS.white}
        />
      ) : (
        <>
          {icon && <Text style={styles.icon}>{icon}</Text>}
          <Text style={labelStyles}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
    borderRadius: BORDER_RADIUS.base,
  },
  primary: {
    backgroundColor: COLORS.primary,
  },
  secondary: {
    backgroundColor: COLORS.white,
    borderWidth: 1.5,
    borderColor: COLORS.primary,
  },
  danger: {
    backgroundColor: COLORS.error,
  },
  ghost: {
    backgroundColor: 'transparent',
  },
  disabled: {
    backgroundColor: COLORS.disabled,
    borderColor: COLORS.disabled,
  },
  label: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
  },
  primaryLabel: {
    color: COLORS.textOnPrimary,
  },
  secondaryLabel: {
    color: COLORS.primary,
  },
  dangerLabel: {
    color: COLORS.white,
  },
  ghostLabel: {
    color: COLORS.primary,
  },
  disabledLabel: {
    color: COLORS.disabledText,
  },
  icon: {
    marginRight: SPACING.sm,
    fontSize: TYPOGRAPHY.fontSize.md,
  },
});
