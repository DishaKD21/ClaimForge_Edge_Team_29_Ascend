export {
  COLORS,
  TYPOGRAPHY,
  SPACING,
  BORDER_RADIUS,
  SHADOWS,
  BUTTON_STYLES,
  INPUT_STYLES,
  CARD_STYLES,
  LAYOUT,
} from './theme';

export const APP_NAME = 'ClaimForge Edge';
export const APP_DESCRIPTION =
  'Mobile claim intake and evidence collection for insurance field agents.';

export const VALIDATION_MESSAGES = {
  required: (field: string) => `${field} is required`,
  minLength: (field: string, min: number) =>
    `${field} must be at least ${min} characters`,
  invalidDate: 'Please enter a valid date',
  evidenceMinimum:
    'At least two types of evidence are required (e.g., Photo + Text)',
  fileTooLarge: (maxMB: number) => `File size must be less than ${maxMB}MB`,
  invalidFormat: 'Unsupported file format',
};

export const EVIDENCE_CONFIG = {
  maxPhotoSizeMB: 10,
  maxVideoSizeMB: 50,
  supportedImageTypes: ['image/jpeg', 'image/png', 'image/heic', 'image/webp'],
  supportedVideoTypes: ['video/mp4', 'video/quicktime', 'video/x-msvideo'],
  maxEvidenceItems: 10,
} as const;

export const CLAIM_STEPS = [
  {key: 'info', label: 'Claim Info', icon: '📋'},
  {key: 'witness', label: 'Witness', icon: '👤'},
  {key: 'evidence', label: 'Evidence', icon: '📎'},
  {key: 'review', label: 'Review', icon: '✓'},
] as const;
