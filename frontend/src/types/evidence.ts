/**
 * Evidence data model for ClaimForge Edge.
 *
 * Part of the integration contract shared with the AI Analysis and
 * Verdict modules. Coordinate before changing this structure.
 */

export type EvidenceType = 'photo' | 'video' | 'text';

export interface Evidence {
  id: string;
  type: EvidenceType;
  name: string;
  uri?: string;
  storageUrl?: string;
  text?: string;
  mimeType?: string;
  size?: number;
  createdAt: string;
}
