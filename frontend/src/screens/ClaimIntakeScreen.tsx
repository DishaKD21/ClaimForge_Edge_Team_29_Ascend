import React, {useState, useCallback} from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  StatusBar,
  Alert,
} from 'react-native';
import {ClaimIntakeScreenProps} from '../types/navigation';
import {Evidence} from '../types';
import {
  PrimaryButton,
  ClaimInput,
  EvidenceCard,
  EvidenceUploader,
  ProgressIndicator,
  EmptyState,
} from '../components';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS} from '../constants';
import {useClaimForm} from '../hooks/useClaimForm';
import {validateStep} from '../utils/validation';
import {submitClaim} from '../services/claimService';

const TOTAL_STEPS = 4;

export const ClaimIntakeScreen: React.FC<ClaimIntakeScreenProps> = ({navigation}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});

  const {
    formData,
    updateField,
    updateWitness,
    addEvidence,
    removeEvidence,
    replaceEvidence,
    updateTextEvidence,
    getClaimObject,
  } = useClaimForm();

  const handleNext = useCallback(() => {
    const errors = validateStep(currentStep, formData);
    if (Object.keys(errors).length > 0) {
      setStepErrors(errors);
      return;
    }
    setStepErrors({});
    setCurrentStep(prev => Math.min(prev + 1, TOTAL_STEPS - 1));
  }, [currentStep, formData]);

  const handleBack = useCallback(() => {
    setStepErrors({});
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);

  const handleSubmit = async () => {
    // Final validation
    const errors = validateStep(3, formData);
    if (Object.keys(errors).length > 0) {
      setStepErrors(errors);
      Alert.alert(
        'Validation Error',
        'Please fix the issues before submitting.',
      );
      return;
    }

    setIsSubmitting(true);
    try {
      const claim = getClaimObject();
      const submittedClaim = await submitClaim(claim);
      const imageEvidence = claim.evidence.find(
        evidence => evidence.type === 'photo' && evidence.uri,
      );
      navigation.replace('SubmissionSuccess', {
        claimId: submittedClaim.claimId,
        analysisText: claim.evidence
          .filter(evidence => evidence.type === 'text')
          .map(evidence => evidence.text)
          .filter(Boolean)
          .join('\n'),
        analysisImage: imageEvidence?.uri
          ? {
              uri: imageEvidence.uri,
              name: imageEvidence.name,
              type: imageEvidence.mimeType || 'image/jpeg',
            }
          : undefined,
      });
    } catch {
      Alert.alert(
        'Submission Failed',
        'An error occurred while submitting your claim. Please try again.',
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditEvidence = (evidence: Evidence) => {
    if (evidence.type === 'text') {
      // Navigate back to evidence step to edit
      setCurrentStep(2);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return renderClaimInfoStep();
      case 1:
        return renderWitnessStep();
      case 2:
        return renderEvidenceStep();
      case 3:
        return renderReviewStep();
      default:
        return null;
    }
  };

  const renderClaimInfoStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Claim Information</Text>
      <Text style={styles.stepSubtitle}>
        Enter the basic details about this insurance claim.
      </Text>

      <ClaimInput
        label="Claim ID"
        value={formData.claimId}
        onChangeText={(text) => updateField('claimId', text)}
        placeholder="e.g., CF-2024-001"
        error={stepErrors.claimId}
        required
        autoCapitalize="characters"
      />
      <ClaimInput
        label="Policy Number"
        value={formData.policyNumber}
        onChangeText={(text) => updateField('policyNumber', text)}
        placeholder="e.g., POL-12345678"
        error={stepErrors.policyNumber}
        required
        autoCapitalize="characters"
      />
      <ClaimInput
        label="Claimant Name"
        value={formData.claimantName}
        onChangeText={(text) => updateField('claimantName', text)}
        placeholder="Full name of the claimant"
        error={stepErrors.claimantName}
        required
        autoCapitalize="words"
      />
      <ClaimInput
        label="Incident Date"
        value={formData.incidentDate}
        onChangeText={(text) => updateField('incidentDate', text)}
        placeholder="YYYY-MM-DD"
        error={stepErrors.incidentDate}
        required
        keyboardType="numbers-and-punctuation"
      />
      <ClaimInput
        label="Incident Location"
        value={formData.incidentLocation}
        onChangeText={(text) => updateField('incidentLocation', text)}
        placeholder="Address or location of the incident"
        error={stepErrors.incidentLocation}
        required
      />
      <ClaimInput
        label="Incident Description"
        value={formData.incidentDescription}
        onChangeText={(text) => updateField('incidentDescription', text)}
        placeholder="Describe what happened in detail..."
        error={stepErrors.incidentDescription}
        required
        multiline
        numberOfLines={4}
      />
    </View>
  );

  const renderWitnessStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Witness Information</Text>
      <Text style={styles.stepSubtitle}>
        Record witness details and their statement about the incident.
      </Text>

      <ClaimInput
        label="Witness Name"
        value={formData.witness.name}
        onChangeText={(text) => updateWitness('name', text)}
        placeholder="Full name of the witness"
        error={stepErrors.witnessName}
        autoCapitalize="words"
      />
      <ClaimInput
        label="Witness Statement"
        value={formData.witness.statement}
        onChangeText={(text) => updateWitness('statement', text)}
        placeholder="Record the witness's account of the incident..."
        error={stepErrors.witnessStatement}
        required
        multiline
        numberOfLines={6}
      />
    </View>
  );

  const renderEvidenceStep = () => {
    const textEvidence = formData.evidence.find(e => e.type === 'text');

    return (
      <View style={styles.stepContent}>
        <Text style={styles.stepTitle}>Evidence Collection</Text>
        <Text style={styles.stepSubtitle}>
          Upload photos or add text evidence. At least two types of
          evidence are required.
        </Text>

        {stepErrors.evidence && (
          <View style={styles.errorBanner}>
            <Text style={styles.errorBannerText}>{stepErrors.evidence}</Text>
          </View>
        )}

        {/* Photo/Video Upload */}
        <EvidenceUploader
          onEvidenceAdded={addEvidence}
          existingEvidence={formData.evidence}
        />

        {/* Text Evidence */}
        <View style={styles.textEvidenceSection}>
          <Text style={styles.sectionLabel}>Written Evidence</Text>
          <ClaimInput
            label="Additional Evidence Description"
            value={textEvidence?.text || ''}
            onChangeText={(text) => updateTextEvidence(text)}
            placeholder="Describe any additional evidence or observations..."
            multiline
            numberOfLines={4}
          />
        </View>

        {/* Evidence List */}
        {formData.evidence.length > 0 && (
          <View style={styles.evidenceList}>
            <Text style={styles.sectionLabel}>
              Collected Evidence ({formData.evidence.length})
            </Text>
            {formData.evidence.map((item) => (
              <EvidenceCard
                key={item.id}
                evidence={item}
                onRemove={removeEvidence}
                onReplace={replaceEvidence}
                onEdit={handleEditEvidence}
              />
            ))}
          </View>
        )}

        {formData.evidence.length === 0 && (
          <EmptyState
            icon="📎"
            title="No Evidence Yet"
            message="Use the options above to add photos, videos, or written evidence."
          />
        )}
      </View>
    );
  };

  const renderReviewStep = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Review & Submit</Text>
      <Text style={styles.stepSubtitle}>
        Review all claim details before submission.
      </Text>

      {stepErrors.evidence && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorBannerText}>{stepErrors.evidence}</Text>
        </View>
      )}

      {/* Claim Details Card */}
      <View style={styles.reviewCard}>
        <Text style={styles.reviewCardTitle}>Claim Details</Text>
        <ReviewRow label="Claim ID" value={formData.claimId} />
        <ReviewRow label="Policy Number" value={formData.policyNumber} />
        <ReviewRow label="Claimant" value={formData.claimantName} />
        <ReviewRow label="Incident Date" value={formData.incidentDate} />
        <ReviewRow label="Location" value={formData.incidentLocation} />
        <ReviewRow
          label="Description"
          value={formData.incidentDescription}
          multiline
        />
      </View>

      {/* Witness Card */}
      <View style={styles.reviewCard}>
        <Text style={styles.reviewCardTitle}>Witness Information</Text>
        <ReviewRow label="Witness Name" value={formData.witness.name || 'Not provided'} />
        <ReviewRow
          label="Statement"
          value={formData.witness.statement}
          multiline
        />
      </View>

      {/* Evidence Card */}
      <View style={styles.reviewCard}>
        <Text style={styles.reviewCardTitle}>
          Evidence ({formData.evidence.length} items)
        </Text>
        {formData.evidence.map((item) => (
          <EvidenceCard
            key={item.id}
            evidence={item}
            onRemove={removeEvidence}
            onEdit={handleEditEvidence}
          />
        ))}
        {formData.evidence.length === 0 && (
          <Text style={styles.noEvidenceText}>No evidence collected</Text>
        )}
        <PrimaryButton
          title="Add More Evidence"
          variant="ghost"
          icon="+"
          onPress={() => setCurrentStep(2)}
        />
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.white} />
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}>
        {/* Progress Header */}
        <ProgressIndicator currentStep={currentStep} totalSteps={TOTAL_STEPS} />

        {/* Content */}
        <ScrollView
          style={styles.flex}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled">
          {renderStep()}
        </ScrollView>

        {/* Bottom Navigation */}
        <View style={styles.bottomBar}>
          {currentStep > 0 ? (
            <PrimaryButton
              title="Back"
              variant="secondary"
              onPress={handleBack}
              style={styles.navButton}
            />
          ) : (
            <PrimaryButton
              title="Cancel"
              variant="ghost"
              onPress={() => navigation.goBack()}
              style={styles.navButton}
            />
          )}

          {currentStep < TOTAL_STEPS - 1 ? (
            <PrimaryButton
              title="Next"
              onPress={handleNext}
              style={styles.navButton}
            />
          ) : (
            <PrimaryButton
              title="Submit Claim"
              onPress={handleSubmit}
              loading={isSubmitting}
              disabled={isSubmitting}
              style={styles.navButton}
            />
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

// --- Review Row sub-component ---
interface ReviewRowProps {
  label: string;
  value: string;
  multiline?: boolean;
}

const ReviewRow: React.FC<ReviewRowProps> = ({label, value, multiline}) => (
  <View style={[reviewStyles.row, multiline && reviewStyles.rowMultiline]}>
    <Text style={reviewStyles.label}>{label}</Text>
    <Text
      style={[reviewStyles.value, multiline && reviewStyles.valueMultiline]}
      numberOfLines={multiline ? undefined : 1}>
      {value || '—'}
    </Text>
  </View>
);

const reviewStyles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.borderLight,
  },
  rowMultiline: {
    flexDirection: 'column',
    alignItems: 'flex-start',
  },
  label: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textMuted,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    marginRight: SPACING.md,
  },
  value: {
    fontSize: TYPOGRAPHY.fontSize.base,
    color: COLORS.textPrimary,
    flex: 1,
    textAlign: 'right',
  },
  valueMultiline: {
    textAlign: 'left',
    flex: undefined,
    marginTop: SPACING.xs,
    lineHeight: 22,
  },
});

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: COLORS.white,
  },
  flex: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: SPACING.xl,
  },
  stepContent: {
    padding: SPACING.base,
  },
  stepTitle: {
    fontSize: TYPOGRAPHY.fontSize.xl,
    fontWeight: TYPOGRAPHY.fontWeight.bold,
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  stepSubtitle: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xl,
    lineHeight: 20,
  },
  bottomBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: SPACING.base,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    backgroundColor: COLORS.white,
    gap: SPACING.sm,
  },
  navButton: {
    flex: 1,
  },
  errorBanner: {
    backgroundColor: COLORS.errorLight,
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.md,
    marginBottom: SPACING.base,
  },
  errorBannerText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.error,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
  },
  textEvidenceSection: {
    marginTop: SPACING.lg,
    marginBottom: SPACING.base,
  },
  sectionLabel: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textPrimary,
    marginBottom: SPACING.md,
  },
  evidenceList: {
    marginTop: SPACING.base,
  },
  reviewCard: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.base,
    marginBottom: SPACING.base,
    borderWidth: 1,
    borderColor: COLORS.border,
    ...SHADOWS.sm,
  },
  reviewCardTitle: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.primary,
    marginBottom: SPACING.md,
    paddingBottom: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  noEvidenceText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textMuted,
    textAlign: 'center',
    paddingVertical: SPACING.base,
  },
});
