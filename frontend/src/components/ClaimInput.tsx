import React, {useState} from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TextInputProps,
  ViewStyle,
} from 'react-native';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS} from '../constants';

interface ClaimInputProps extends Omit<TextInputProps, 'style'> {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  required?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  containerStyle?: ViewStyle;
  accessibilityLabel?: string;
}

export const ClaimInput: React.FC<ClaimInputProps> = ({
  label,
  value,
  onChangeText,
  error,
  required = false,
  multiline = false,
  numberOfLines = 1,
  containerStyle,
  accessibilityLabel,
  ...textInputProps
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const inputStyles = [
    styles.input,
    multiline && styles.multiline,
    multiline && {minHeight: numberOfLines * 24 + 24},
    isFocused && styles.inputFocused,
    !!error && styles.inputError,
  ];

  return (
    <View style={[styles.container, containerStyle]}>
      <Text style={styles.label}>
        {label}
        {required && <Text style={styles.required}> *</Text>}
      </Text>
      <TextInput
        style={inputStyles}
        value={value}
        onChangeText={onChangeText}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        multiline={multiline}
        numberOfLines={numberOfLines}
        textAlignVertical={multiline ? 'top' : 'center'}
        placeholderTextColor={COLORS.placeholder}
        accessibilityLabel={accessibilityLabel || label}
        accessibilityState={{disabled: textInputProps.editable === false}}
        {...textInputProps}
      />
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: SPACING.base,
  },
  label: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xs,
  },
  required: {
    color: COLORS.error,
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
  multiline: {
    paddingTop: SPACING.md,
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
});
