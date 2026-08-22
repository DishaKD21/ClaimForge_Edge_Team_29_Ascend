/**
 * Client-side validation utilities for claim intake forms.
 */

import {Evidence} from '../types';

interface FormData {
  claimId: string;
  policyNumber: string;
  claimantName: string;
  incidentDate: string;
  incidentLocation: string;
  incidentDescription: string;
  witness: {
    name: string;
    statement: string;
  };
  evidence: Evidence[];
}

type ValidationErrors = Record<string, string>;

/**
 * Validate form fields for a specific step.
 *
 * @param step - Current step index (0-3)
 * @param formData - Current form data
 * @returns Object with field keys mapped to error messages (empty = valid)
 */
export function validateStep(step: number, formData: FormData): ValidationErrors {
  switch (step) {
    case 0:
      return validateClaimInfo(formData);
    case 1:
      return validateWitnessInfo(formData);
    case 2:
      return validateEvidence(formData);
    case 3:
      return validateAll(formData);
    default:
      return {};
  }
}

function validateClaimInfo(formData: FormData): ValidationErrors {
  const errors: ValidationErrors = {};

  if (!formData.claimId.trim()) {
    errors.claimId = 'Claim ID is required';
  }

  if (!formData.policyNumber.trim()) {
    errors.policyNumber = 'Policy Number is required';
  }

  if (!formData.claimantName.trim()) {
    errors.claimantName = 'Claimant Name is required';
  } else if (formData.claimantName.trim().length < 2) {
    errors.claimantName = 'Claimant Name must be at least 2 characters';
  }

  if (!formData.incidentDate.trim()) {
    errors.incidentDate = 'Incident Date is required';
  } else if (!isValidDateFormat(formData.incidentDate.trim())) {
    errors.incidentDate = 'Please enter a valid date (YYYY-MM-DD)';
  }

  if (!formData.incidentLocation.trim()) {
    errors.incidentLocation = 'Incident Location is required';
  }

  if (!formData.incidentDescription.trim()) {
    errors.incidentDescription = 'Incident Description is required';
  } else if (formData.incidentDescription.trim().length < 10) {
    errors.incidentDescription =
      'Description must be at least 10 characters';
  }

  return errors;
}

function validateWitnessInfo(formData: FormData): ValidationErrors {
  const errors: ValidationErrors = {};

  if (!formData.witness.statement.trim()) {
    errors.witnessStatement = 'Witness Statement is required';
  } else if (formData.witness.statement.trim().length < 10) {
    errors.witnessStatement = 'Statement must be at least 10 characters';
  }

  return errors;
}

function validateEvidence(formData: FormData): ValidationErrors {
  const errors: ValidationErrors = {};

  const evidenceTypes = new Set(formData.evidence.map((e) => e.type));
  if (evidenceTypes.size < 2) {
    errors.evidence =
      'At least two types of evidence are required (e.g., Photo + Text)';
  }

  return errors;
}

function validateAll(formData: FormData): ValidationErrors {
  return {
    ...validateClaimInfo(formData),
    ...validateWitnessInfo(formData),
    ...validateEvidence(formData),
  };
}

/**
 * Basic YYYY-MM-DD date format validation.
 */
function isValidDateFormat(date: string): boolean {
  const regex = /^\d{4}-\d{2}-\d{2}$/;
  if (!regex.test(date)) {
    return false;
  }

  const [year, month, day] = date.split('-').map(Number);
  const dateObj = new Date(year, month - 1, day);

  return (
    dateObj.getFullYear() === year &&
    dateObj.getMonth() === month - 1 &&
    dateObj.getDate() === day
  );
}
