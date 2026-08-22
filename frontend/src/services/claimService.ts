/**
 * Claim Service
 * Handles claim submission and preparation for downstream processing.
 *
 * Integration Architecture:
 *   Claim Intake UI
 *        ↓
 *   claimService.submitClaim()
 *        ↓
 *   Firebase / Backend API (future)
 *        ↓
 *   AI Analysis Service (another team member)
 *        ↓
 *   Conflict Detection → Verdict
 *
 * This service is the clean boundary between the Intake module and
 * downstream modules. Replace the implementation without changing the UI.
 */

import {Claim, ClaimAnalysisService, ClaimAnalysisResult} from '../types';
import {
  analyzeClaim as analyzeClaimApi,
  createClaim,
  getClaim,
  getClaimEvidence,
  uploadImageEvidence,
  uploadTextEvidence,
} from './apiClient';

/**
 * Submit a complete claim for processing.
 *
 * Current behavior: validates the claim, uploads evidence placeholders,
 * and returns the finalized claim object.
 *
 * Future behavior: will persist to Firestore and trigger the AI pipeline.
 *
 * @param claim - The complete Claim object from the intake form
 * @returns The submitted claim with updated status and storage URLs
 */
export async function submitClaim(claim: Claim): Promise<Claim> {
  // 1. Validate the claim before submission
  if (!claim.claimId || !claim.policyNumber || !claim.claimantName) {
    throw new Error('Claim is missing required fields.');
  }

  if (claim.evidence.length < 2) {
    throw new Error('At least two evidence items are required.');
  }

  const backendClaim = await createClaim({
    customerName: claim.claimantName,
    description: claim.incidentDescription,
    incidentDate: claim.incidentDate,
    incidentTime: '00:00',
    location: claim.incidentLocation,
  });

  for (const evidence of claim.evidence) {
    if (evidence.type === 'text') {
      if (evidence.text?.trim()) {
        await uploadTextEvidence(backendClaim.claimId, evidence.text.trim());
      }
      continue;
    }

    if (evidence.type !== 'photo' || !evidence.uri) {
      throw new Error('Only text and image evidence can be submitted.');
    }

    await uploadImageEvidence(backendClaim.claimId, {
      uri: evidence.uri,
      name: evidence.name,
      type: evidence.mimeType || 'image/jpeg',
    });
  }

  return {
    ...claim,
    claimId: backendClaim.claimId,
    status: 'submitted',
    updatedAt: new Date().toISOString(),
  };
}

/**
 * Retrieve a claim by ID (future implementation).
 */
export async function getClaimById(claimId: string): Promise<Claim | null> {
  try {
    const [backendClaim, backendEvidence] = await Promise.all([
      getClaim(claimId),
      getClaimEvidence(claimId),
    ]);

    return {
      claimId: String(backendClaim.claimId),
      policyNumber: '',
      claimantName: String(backendClaim.customerName || ''),
      incidentDate: String(backendClaim.incidentDate || ''),
      incidentLocation: String(backendClaim.location || ''),
      incidentDescription: String(backendClaim.description || ''),
      witness: {name: '', statement: ''},
      evidence: backendEvidence.map((evidence) => ({
        id: evidence.id,
        type: evidence.type === 'image' ? 'photo' : 'text',
        name: evidence.fileName || 'Written Evidence',
        text: evidence.content,
        mimeType: evidence.mimeType,
        createdAt: evidence.uploadedAt || new Date().toISOString(),
      })),
      status: 'submitted',
      createdAt: String(backendClaim.createdAt || ''),
      updatedAt: String(backendClaim.createdAt || ''),
    };
  } catch (error) {
    if (error instanceof Error && error.message.includes('404')) {
      return null;
    }
    throw error;
  }
}

/**
 * Pass a submitted claim to the AI Analysis module.
 *
 * This is the integration point for Team Member 1 (Gen-AI + Conflict Detection).
 * They should provide an implementation of ClaimAnalysisService.
 *
 * Usage:
 *   const aiService: ClaimAnalysisService = new TheirAIService();
 *   const result = await sendToAnalysis(claim, aiService);
 */
export async function sendToAnalysis(
  claim: Claim,
  analysisService: ClaimAnalysisService,
): Promise<ClaimAnalysisResult> {
  if (claim.status !== 'submitted') {
    throw new Error('Only submitted claims can be sent for analysis.');
  }

  return analysisService.analyzeClaim(claim);
}

export async function analyzeClaim(
  claimId: string,
  options?: {text?: string; image?: {uri: string; name: string; type: string}},
): Promise<ClaimAnalysisResult> {
  const analysis = await analyzeClaimApi(claimId, options);
  return {
    claimId: analysis.claimId,
    status: 'completed',
    ...analysis.result,
  };
}
