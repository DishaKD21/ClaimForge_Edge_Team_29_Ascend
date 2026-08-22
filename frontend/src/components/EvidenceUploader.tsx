import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Platform,
  PermissionsAndroid,
} from 'react-native';
import {launchCamera, launchImageLibrary, Asset} from 'react-native-image-picker';
import {Evidence} from '../types';
import {COLORS, TYPOGRAPHY, SPACING, BORDER_RADIUS, EVIDENCE_CONFIG} from '../constants';
import {generateId} from '../utils/formatters';

interface EvidenceUploaderProps {
  onEvidenceAdded: (evidence: Evidence) => void;
  existingEvidence: Evidence[];
}

export const EvidenceUploader: React.FC<EvidenceUploaderProps> = ({
  onEvidenceAdded,
  existingEvidence,
}) => {
  const [isUploading, setIsUploading] = useState(false);

  const requestCameraPermission = async (): Promise<boolean> => {
    if (Platform.OS === 'android') {
      try {
        const granted = await PermissionsAndroid.request(
          PermissionsAndroid.PERMISSIONS.CAMERA,
          {
            title: 'Camera Permission',
            message:
              'ClaimForge Edge needs camera access to capture evidence photos.',
            buttonPositive: 'Allow',
            buttonNegative: 'Deny',
          },
        );
        return granted === PermissionsAndroid.RESULTS.GRANTED;
      } catch {
        return false;
      }
    }
    return true;
  };

  const validateFile = (asset: Asset): string | null => {
    const sizeMB = (asset.fileSize || 0) / 1024 / 1024;
    const isVideo = asset.type?.startsWith('video/');
    if (isVideo) {
      Alert.alert('Unsupported Evidence', 'Only image and text evidence are supported.');
      return null;
    }

    if (!isVideo && sizeMB > EVIDENCE_CONFIG.maxPhotoSizeMB) {
      return `Image file is too large. Maximum size is ${EVIDENCE_CONFIG.maxPhotoSizeMB}MB.`;
    }

    if (existingEvidence.length >= EVIDENCE_CONFIG.maxEvidenceItems) {
      return `Maximum ${EVIDENCE_CONFIG.maxEvidenceItems} evidence items allowed.`;
    }

    return null;
  };

  const handleAsset = (asset: Asset, source: string) => {
    const error = validateFile(asset);
    if (error) {
      Alert.alert('Upload Error', error);
      return;
    }

    const isVideo = asset.type?.startsWith('video/');
    const evidence: Evidence = {
      id: generateId(),
      type: 'photo',
      name: asset.fileName || `${source}_${Date.now()}.jpg`,
      uri: asset.uri,
      mimeType: asset.type,
      size: asset.fileSize,
      createdAt: new Date().toISOString(),
    };

    onEvidenceAdded(evidence);
  };

  const handleTakePhoto = async () => {
    const hasPermission = await requestCameraPermission();
    if (!hasPermission) {
      Alert.alert(
        'Permission Denied',
        'Camera permission is required to take photos. Please enable it in your device settings.',
      );
      return;
    }

    setIsUploading(true);
    try {
      const result = await launchCamera({
        mediaType: 'photo',
        quality: 0.8,
        maxWidth: 1920,
        maxHeight: 1920,
        saveToPhotos: false,
      });

      if (result.assets && result.assets.length > 0) {
        handleAsset(result.assets[0], 'camera');
      }
    } catch {
      Alert.alert('Error', 'Failed to open camera. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectImage = async () => {
    setIsUploading(true);
    try {
      const result = await launchImageLibrary({
        mediaType: 'photo',
        quality: 0.8,
        maxWidth: 1920,
        maxHeight: 1920,
        selectionLimit: 1,
      });

      if (result.assets && result.assets.length > 0) {
        handleAsset(result.assets[0], 'gallery');
      }
    } catch {
      Alert.alert('Error', 'Failed to open photo library. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const photoCount = existingEvidence.filter(e => e.type === 'photo').length;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add Evidence</Text>
      <Text style={styles.subtitle}>
        Capture or select photos as claim evidence.
      </Text>

      <View style={styles.uploaderGrid}>
        <TouchableOpacity
          style={[styles.uploadOption, isUploading && styles.uploadOptionDisabled]}
          onPress={handleTakePhoto}
          disabled={isUploading}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Take a photo with camera">
          <Text style={styles.uploadIcon}>📷</Text>
          <Text style={styles.uploadLabel}>Take Photo</Text>
          <Text style={styles.uploadHint}>Use camera</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.uploadOption, isUploading && styles.uploadOptionDisabled]}
          onPress={handleSelectImage}
          disabled={isUploading}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Select image from gallery">
          <Text style={styles.uploadIcon}>🖼️</Text>
          <Text style={styles.uploadLabel}>Gallery</Text>
          <Text style={styles.uploadHint}>Select image</Text>
        </TouchableOpacity>

      </View>

      {photoCount > 0 && (
        <View style={styles.countRow}>
          {photoCount > 0 && (
            <View style={styles.countBadge}>
              <Text style={styles.countText}>
                📷 {photoCount} photo{photoCount !== 1 ? 's' : ''}
              </Text>
            </View>
          )}
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: SPACING.lg,
  },
  title: {
    fontSize: TYPOGRAPHY.fontSize.md,
    fontWeight: TYPOGRAPHY.fontWeight.semibold,
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    color: COLORS.textSecondary,
    marginBottom: SPACING.base,
  },
  uploaderGrid: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  uploadOption: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.sm,
    borderWidth: 1.5,
    borderColor: COLORS.border,
    borderStyle: 'dashed',
    borderRadius: BORDER_RADIUS.md,
    backgroundColor: COLORS.background,
  },
  uploadOptionDisabled: {
    opacity: 0.5,
  },
  uploadIcon: {
    fontSize: 28,
    marginBottom: SPACING.sm,
  },
  uploadLabel: {
    fontSize: TYPOGRAPHY.fontSize.sm,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
    color: COLORS.textPrimary,
    marginBottom: 2,
  },
  uploadHint: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.textMuted,
  },
  countRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
    marginTop: SPACING.md,
  },
  countBadge: {
    backgroundColor: COLORS.accentFaded,
    paddingVertical: SPACING.xs,
    paddingHorizontal: SPACING.sm,
    borderRadius: BORDER_RADIUS.sm,
  },
  countText: {
    fontSize: TYPOGRAPHY.fontSize.xs,
    color: COLORS.accent,
    fontWeight: TYPOGRAPHY.fontWeight.medium,
  },
});
