import React from 'react';
import {
  View,
  Text,
  Image,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from 'react-native';
import {Evidence} from '../types';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, SHADOWS} from '../constants';

interface EvidenceCardProps {
  evidence: Evidence;
  onReplace?: (evidence: Evidence) => void;
  onRemove?: (evidence: Evidence) => void;
  onEdit?: (evidence: Evidence) => void;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  evidence,
  onReplace,
  onRemove,
  onEdit,
}) => {
  const handleRemove = () => {
    Alert.alert(
      'Remove Evidence',
      `Are you sure you want to remove "${evidence.name}"?`,
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => onRemove?.(evidence),
        },
      ],
    );
  };

  const renderIcon = () => {
    switch (evidence.type) {
      case 'photo':
        return '📷';
      case 'video':
        return '🎥';
      case 'text':
        return '📝';
      default:
        return '📎';
    }
  };

  const renderTypeLabel = () => {
    switch (evidence.type) {
      case 'photo':
        return 'Photo Evidence';
      case 'video':
        return 'Video Evidence';
      case 'text':
        return 'Witness Statement';
      default:
        return 'Evidence';
    }
  };

  const renderPreview = () => {
    if (evidence.type === 'photo' && evidence.uri) {
      return (
        <Image
          source={{uri: evidence.uri}}
          style={styles.imagePreview}
          resizeMode="cover"
          accessibilityLabel={`Photo evidence: ${evidence.name}`}
        />
      );
    }

    if (evidence.type === 'video' && evidence.uri) {
      return (
        <View style={styles.videoPreview}>
          <Text style={styles.videoIcon}>▶️</Text>
          <Text style={styles.videoLabel}>Video attached</Text>
        </View>
      );
    }

    if (evidence.type === 'text' && evidence.text) {
      return (
        <View style={styles.textPreview}>
          <Text style={styles.textContent} numberOfLines={3}>
            "{evidence.text}"
          </Text>
        </View>
      );
    }

    return null;
  };

  const renderActions = () => {
    if (evidence.type === 'text') {
      return (
        <View style={styles.actions}>
          {onEdit && (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => onEdit(evidence)}
              accessibilityRole="button"
              accessibilityLabel={`Edit ${evidence.name}`}>
              <Text style={styles.actionButtonText}>Edit</Text>
            </TouchableOpacity>
          )}
          {onRemove && (
            <TouchableOpacity
              style={[styles.actionButton, styles.actionButtonDanger]}
              onPress={handleRemove}
              accessibilityRole="button"
              accessibilityLabel={`Remove ${evidence.name}`}>
              <Text style={styles.actionButtonDangerText}>Remove</Text>
            </TouchableOpacity>
          )}
        </View>
      );
    }

    return (
      <View style={styles.actions}>
        {onReplace && (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => onReplace(evidence)}
            accessibilityRole="button"
            accessibilityLabel={`Replace ${evidence.name}`}>
            <Text style={styles.actionButtonText}>Replace</Text>
          </TouchableOpacity>
        )}
        {onRemove && (
          <TouchableOpacity
            style={[styles.actionButton, styles.actionButtonDanger]}
            onPress={handleRemove}
            accessibilityRole="button"
            accessibilityLabel={`Remove ${evidence.name}`}>
            <Text style={styles.actionButtonDangerText}>Remove</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  };

  return (
    <View
      style={styles.container}
      accessibilityRole="summary"
      accessibilityLabel={`${renderTypeLabel()}: ${evidence.name}`}>
      <View style={styles.header}>
        <Text style={styles.icon}>{renderIcon()}</Text>
        <Text style={styles.typeLabel}>{renderTypeLabel()}</Text>
      </View>
      {renderPreview()}
      <Text style={styles.fileName} numberOfLines={1}>
        {evidence.name}
      </Text>
      {evidence.size && (
        <Text style={styles.fileSize}>
          {(evidence.size / 1024 / 1024).toFixed(2)} MB
        </Text>
      )}
      {renderActions()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.surface,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.base,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: SPACING.md,
    ...SHADOWS.base,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  icon: {
    fontSize: 18,
    marginRight: SPACING.sm,
  },
  typeLabel: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textPrimary,
  },
  imagePreview: {
    width: '100%',
    height: 160,
    borderRadius: BORDER_RADIUS.sm,
    marginBottom: SPACING.sm,
    backgroundColor: COLORS.borderLight,
  },
  videoPreview: {
    width: '100%',
    height: 100,
    borderRadius: BORDER_RADIUS.sm,
    marginBottom: SPACING.sm,
    backgroundColor: COLORS.borderLight,
    alignItems: 'center',
    justifyContent: 'center',
  },
  videoIcon: {
    fontSize: 28,
    marginBottom: SPACING.xs,
  },
  videoLabel: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textMuted,
  },
  textPreview: {
    backgroundColor: COLORS.primaryFaded,
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.md,
    marginBottom: SPACING.sm,
  },
  textContent: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    fontStyle: 'italic',
    lineHeight: 20,
  },
  fileName: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    marginBottom: SPACING.xs,
  },
  fileSize: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.textMuted,
    marginBottom: SPACING.sm,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: SPACING.sm,
    marginTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.borderLight,
    paddingTop: SPACING.sm,
  },
  actionButton: {
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.base,
    borderRadius: BORDER_RADIUS.sm,
    backgroundColor: COLORS.primaryFaded,
    minWidth: 70,
    alignItems: 'center',
  },
  actionButtonText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.primary,
  },
  actionButtonDanger: {
    backgroundColor: COLORS.errorLight,
  },
  actionButtonDangerText: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.error,
  },
});
