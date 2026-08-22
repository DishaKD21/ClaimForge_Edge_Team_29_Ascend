import React from 'react';
import {View, Text, StyleSheet} from 'react-native';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS} from '../constants';
import {CLAIM_STEPS} from '../constants';

interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps?: number;
}

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  currentStep,
  totalSteps = CLAIM_STEPS.length,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.stepsRow}>
        {CLAIM_STEPS.slice(0, totalSteps).map((step, index) => {
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;

          return (
            <View key={step.key} style={styles.stepItem}>
              <View
                style={[
                  styles.stepCircle,
                  isActive && styles.stepCircleActive,
                  isCompleted && styles.stepCircleCompleted,
                ]}>
                <Text
                  style={[
                    styles.stepIcon,
                    (isActive || isCompleted) && styles.stepIconActive,
                  ]}>
                  {isCompleted ? '✓' : step.icon}
                </Text>
              </View>
              <Text
                style={[
                  styles.stepLabel,
                  isActive && styles.stepLabelActive,
                  isCompleted && styles.stepLabelCompleted,
                ]}
                numberOfLines={1}>
                {step.label}
              </Text>
              {index < totalSteps - 1 && (
                <View
                  style={[
                    styles.connector,
                    isCompleted && styles.connectorCompleted,
                  ]}
                />
              )}
            </View>
          );
        })}
      </View>
      <View style={styles.progressBarContainer}>
        <View
          style={[
            styles.progressBar,
            {width: `${((currentStep) / (totalSteps - 1)) * 100}%`},
          ]}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: SPACING.base,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.white,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  stepsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  stepItem: {
    flex: 1,
    alignItems: 'center',
    position: 'relative',
  },
  stepCircle: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: COLORS.borderLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.xs,
  },
  stepCircleActive: {
    backgroundColor: COLORS.primary,
  },
  stepCircleCompleted: {
    backgroundColor: COLORS.accent,
  },
  stepIcon: {
    fontSize: 14,
    color: COLORS.textMuted,
  },
  stepIconActive: {
    color: COLORS.white,
  },
  stepLabel: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.textMuted,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
  },
  stepLabelActive: {
    color: COLORS.primary,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
  },
  stepLabelCompleted: {
    color: COLORS.accent,
  },
  connector: {
    position: 'absolute',
    top: 16,
    left: '60%',
    right: '-40%',
    height: 2,
    backgroundColor: COLORS.borderLight,
    zIndex: -1,
  },
  connectorCompleted: {
    backgroundColor: COLORS.accent,
  },
  progressBarContainer: {
    height: 3,
    backgroundColor: COLORS.borderLight,
    borderRadius: BORDER_RADIUS.full,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.full,
  },
});
