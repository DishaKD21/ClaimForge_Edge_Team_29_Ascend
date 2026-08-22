import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  StatusBar,
} from 'react-native';
import {HomeScreenProps} from '../types/navigation';
import {PrimaryButton} from '../components';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS} from '../constants';

export const HomeScreen: React.FC<HomeScreenProps> = ({navigation}) => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.white} />
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.logoContainer}>
            <Text style={styles.logoIcon}>🛡️</Text>
            <View>
              <Text style={styles.appName}>ClaimForge Edge</Text>
              <Text style={styles.appTagline}>Insurance Claim Intake</Text>
            </View>
          </View>
        </View>

        {/* Hero Section */}
        <View style={styles.heroSection}>
          <Text style={styles.heroTitle}>
            Mobile Claim{'\n'}Evidence Collection
          </Text>
          <Text style={styles.heroDescription}>
            Capture claim details, collect photographic evidence, and submit
            claims for AI-powered verification — all from the field.
          </Text>
        </View>

        {/* CTA */}
        <View style={styles.ctaSection}>
          <PrimaryButton
            title="Create New Claim"
            icon="+"
            onPress={() => navigation.navigate('ClaimIntake')}
            accessibilityLabel="Create a new insurance claim"
          />
        </View>

        {/* Features Cards */}
        <View style={styles.featuresSection}>
          <Text style={styles.sectionTitle}>How It Works</Text>
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>📋</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Claim Information</Text>
              <Text style={styles.featureDesc}>
                Enter policy details, claimant info, and incident description.
              </Text>
            </View>
          </View>
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>📷</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Evidence Collection</Text>
              <Text style={styles.featureDesc}>
                Capture photos, record witness statements, and attach video
                evidence.
              </Text>
            </View>
          </View>
          <View style={styles.featureCard}>
            <Text style={styles.featureIcon}>🤖</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>AI Verification</Text>
              <Text style={styles.featureDesc}>
                Submit for automated analysis, conflict detection, and verdict
                generation.
              </Text>
            </View>
          </View>
        </View>

        {/* Recent Claims Placeholder */}
        <View style={styles.recentSection}>
          <Text style={styles.sectionTitle}>Recent Claims</Text>
          <View style={styles.emptyRecent}>
            <Text style={styles.emptyIcon}>📂</Text>
            <Text style={styles.emptyText}>No recent claims</Text>
            <Text style={styles.emptySubtext}>
              Claims you submit will appear here.
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.white,
  },
  scrollView: {
    flex: 1,
  },
  content: {
    paddingBottom: SPACING['4xl'],
  },
  header: {
    paddingHorizontal: SPACING.base,
    paddingTop: SPACING.base,
    paddingBottom: SPACING.sm,
  },
  logoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.md,
  },
  logoIcon: {
    fontSize: 32,
  },
  appName: {
    fontSize: TYPOGRAPHY.fontSize.lg,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.textPrimary,
  },
  appTagline: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.textMuted,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
  },
  heroSection: {
    paddingHorizontal: SPACING.base,
    paddingTop: SPACING['2xl'],
    paddingBottom: SPACING.xl,
  },
  heroTitle: {
    fontSize: TYPOGRAPHY.fontSize['3xl'],
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.textPrimary,
    lineHeight: 38,
    marginBottom: SPACING.md,
  },
  heroDescription: {
    fontSize: TYPOGRAPHY.fontSize.base,
    color: COLORS.textSecondary,
    lineHeight: 24,
  },
  ctaSection: {
    paddingHorizontal: SPACING.base,
    paddingBottom: SPACING['2xl'],
  },
  featuresSection: {
    paddingHorizontal: SPACING.base,
    paddingBottom: SPACING.xl,
  },
  sectionTitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textPrimary,
    marginBottom: SPACING.base,
  },
  featureCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    padding: SPACING.base,
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: SPACING.sm,
    ...SHADOWS.sm,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: SPACING.md,
    marginTop: 2,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  featureDesc: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    lineHeight: 20,
  },
  recentSection: {
    paddingHorizontal: SPACING.base,
    paddingTop: SPACING.base,
  },
  emptyRecent: {
    alignItems: 'center',
    paddingVertical: SPACING['2xl'],
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.lg,
    borderWidth: 1,
    borderColor: COLORS.borderLight,
  },
  emptyIcon: {
    fontSize: 32,
    marginBottom: SPACING.sm,
  },
  emptyText: {
    fontSize: TYPOGRAPHY.fontSize.base,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xs,
  },
  emptySubtext: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textMuted,
  },
});
