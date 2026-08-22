/**
 * Core Claim data model for ClaimForge Edge.
 * This interface is the integration contract between the Claim Intake module
 * and downstream modules (Gen-AI Analysis, Conflict Detection, Verdict).
 *
 * DO NOT modify this structure without coordinating with all team members.
 */

import {Evidence} from './evidence';

export type ClaimStatus =
  | 'draft'
  | 'submitted'
  | 'analyzing'
  | 'verified'
  | 'rejected'
  | 'pending_review';

export interface Claim {
  claimId: string;
  policyNumber: string;
  claimantName: string;
  incidentDate: string;
  incidentLocation: string;
  incidentDescription: string;
  witness: WitnessInfo;
  evidence: Evidence[];
  status: ClaimStatus;
  createdAt: string;
  updatedAt: string;
}

export interface WitnessInfo {
  name: string;
  statement: string;
}

/**
 * Integration interface for the downstream AI Analysis module.
 * The AI team should implement this to receive claims for processing.
 */
export interface ClaimAnalysisService {
  analyzeClaim(claim: Claim): Promise<ClaimAnalysisResult>;
}

/**
 * Placeholder result type - the AI team will define the actual structure.
 */
export interface ClaimAnalysisResult {
  claimId: string;
  status: string;
  [key: string]: unknown;
}
