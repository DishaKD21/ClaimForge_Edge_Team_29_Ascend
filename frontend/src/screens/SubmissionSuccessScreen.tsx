import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  StatusBar,
  Alert,
} from 'react-native';
import {SubmissionSuccessScreenProps} from '../types/navigation';
import {PrimaryButton} from '../components';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS} from '../constants';
import {analyzeClaim} from '../services/claimService';

export const SubmissionSuccessScreen: React.FC<SubmissionSuccessScreenProps> = ({
  navigation,
  route,
}) => {
  const {claimId, analysisText, analysisImage} = route.params;
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    try {
      const result = await analyzeClaim(claimId, {
        text: analysisText,
        image: analysisImage,
      });
      Alert.alert('Analysis Complete', JSON.stringify(result, null, 2));
    } catch (error) {
      Alert.alert(
        'Analysis Unavailable',
        error instanceof Error ? error.message : 'Unable to analyze this claim.',
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.white} />
      <View style={styles.container}>
        <View style={styles.content}>
          {/* Success icon */}
          <View style={styles.successCircle}>
            <Text style={styles.successIcon}>✓</Text>
          </View>

          <Text style={styles.title}>Claim Submitted</Text>
          <Text style={styles.subtitle}>
            Your evidence has been successfully collected.
          </Text>

          {/* Claim ID card */}
          <View style={styles.claimIdCard}>
            <Text style={styles.claimIdLabel}>Claim ID</Text>
            <Text style={styles.claimIdValue}>{claimId}</Text>
          </View>

          {/* Status */}
          <View style={styles.statusBadge}>
            <Text style={styles.statusDot}>●</Text>
            <Text style={styles.statusText}>Ready for AI verification</Text>
          </View>

          {/* Info */}
          <Text style={styles.infoText}>
            Your claim will be processed by our AI analysis engine for conflict
            detection and verification. You will receive updates on the claim
            status.
          </Text>
        </View>

        {/* Actions */}
        <View style={styles.actions}>
          <PrimaryButton
            title="Analyze Claim"
            onPress={handleAnalyze}
            loading={isAnalyzing}
            disabled={isAnalyzing}
          />
          <PrimaryButton
            title="Back to Home"
            onPress={() => navigation.navigate('Home')}
          />
          <PrimaryButton
            title="Create Another Claim"
            variant="secondary"
            onPress={() => navigation.navigate('ClaimIntake')}
          />
        </View>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.white,
  },
  container: {
    flex: 1,
    justifyContent: 'space-between',
    padding: SPACING.base,
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: SPACING.xl,
  },
  successCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: COLORS.accentFaded,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: SPACING.xl,
  },
  successIcon: {
    fontSize: 36,
    color: COLORS.accent,
    fontWeight: '700',
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize['2xl'],
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.textPrimary,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: TYPOGRAPHY.fontSize.base,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  claimIdCard: {
    backgroundColor: COLORS.primaryFaded,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.base,
    alignItems: 'center',
    marginBottom: SPACING.base,
    width: '100%',
  },
  claimIdLabel: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.textMuted,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    marginBottom: SPACING.xs,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  claimIdValue: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.primary,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.accentFaded,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.base,
    borderRadius: BORDER_RADIUS.full,
    marginBottom: SPACING.xl,
  },
  statusDot: {
    color: COLORS.accent,
    fontSize: 10,
    marginRight: SPACING.sm,
  },
  statusText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.accent,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
  },
  infoText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textMuted,
    textAlign: 'center',
    lineHeight: 20,
  },
  actions: {
    gap: SPACING.sm,
    paddingTop: SPACING.base,
  },
});
