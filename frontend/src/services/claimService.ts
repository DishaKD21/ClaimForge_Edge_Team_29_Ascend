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
import {uploadMultipleEvidence} from './firebaseStorage';

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

  // 2. Upload media evidence to storage
  const mediaEvidence = claim.evidence.filter((e) => e.uri && e.type !== 'text');
  if (mediaEvidence.length > 0) {
    try {
      const uploadResults = await uploadMultipleEvidence(mediaEvidence);
      // Map storage URLs back to evidence items
      let uploadIndex = 0;
      claim.evidence = claim.evidence.map((e) => {
        if (e.uri && e.type !== 'text' && uploadIndex < uploadResults.length) {
          const result = uploadResults[uploadIndex];
          uploadIndex++;
          return {...e, storageUrl: result.storageUrl};
        }
        return e;
      });
    } catch {
      throw new Error('Failed to upload evidence files. Please try again.');
    }
  }

  // 3. Mark as submitted
  const submittedClaim: Claim = {
    ...claim,
    status: 'submitted',
    updatedAt: new Date().toISOString(),
  };

  // 4. Persist to backend (future implementation)
  // ─── Uncomment when Firebase/backend is ready ──────────────────────────
  //
  // import firestore from '@react-native-firebase/firestore';
  // await firestore().collection('claims').doc(claim.claimId).set(submittedClaim);
  //
  // ───────────────────────────────────────────────────────────────────────

  // Simulate network latency
  await new Promise((resolve) => setTimeout(resolve, 800));

  return submittedClaim;
}

/**
 * Retrieve a claim by ID (future implementation).
 */
export async function getClaimById(claimId: string): Promise<Claim | null> {
  // ─── Future: Firestore lookup ─────────────────────────────────────────
  //
  // const doc = await firestore().collection('claims').doc(claimId).get();
  // return doc.exists ? (doc.data() as Claim) : null;
  //
  // ──────────────────────────────────────────────────────────────────────

  void claimId;
  return null;
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
