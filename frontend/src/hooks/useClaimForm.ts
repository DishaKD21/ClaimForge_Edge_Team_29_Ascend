/**
 * Custom hook for managing claim form state.
 * Centralizes all form logic away from the UI components.
 */

import {useState, useCallback} from 'react';
import {Claim, Evidence} from '../types';
import {generateId, generateClaimId} from '../utils/formatters';

interface ClaimFormData {
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

interface UseClaimFormReturn {
  formData: ClaimFormData;
  updateField: (field: keyof Omit<ClaimFormData, 'witness' | 'evidence'>, value: string) => void;
  updateWitness: (field: 'name' | 'statement', value: string) => void;
  addEvidence: (evidence: Evidence) => void;
  removeEvidence: (evidence: Evidence) => void;
  replaceEvidence: (evidence: Evidence) => void;
  updateTextEvidence: (text: string) => void;
  resetForm: () => void;
  getClaimObject: () => Claim;
}

const initialFormData: ClaimFormData = {
  claimId: '',
  policyNumber: '',
  claimantName: '',
  incidentDate: '',
  incidentLocation: '',
  incidentDescription: '',
  witness: {
    name: '',
    statement: '',
  },
  evidence: [],
};

export function useClaimForm(): UseClaimFormReturn {
  const [formData, setFormData] = useState<ClaimFormData>({
    ...initialFormData,
    claimId: generateClaimId(),
  });

  const updateField = useCallback(
    (field: keyof Omit<ClaimFormData, 'witness' | 'evidence'>, value: string) => {
      setFormData((prev) => ({...prev, [field]: value}));
    },
    [],
  );

  const updateWitness = useCallback(
    (field: 'name' | 'statement', value: string) => {
      setFormData((prev) => ({
        ...prev,
        witness: {...prev.witness, [field]: value},
      }));
    },
    [],
  );

  const addEvidence = useCallback((evidence: Evidence) => {
    setFormData((prev) => ({
      ...prev,
      evidence: [...prev.evidence, evidence],
    }));
  }, []);

  const removeEvidence = useCallback((evidence: Evidence) => {
    setFormData((prev) => ({
      ...prev,
      evidence: prev.evidence.filter((e) => e.id !== evidence.id),
    }));
  }, []);

  const replaceEvidence = useCallback((evidence: Evidence) => {
    // For replace, we remove the old item — the EvidenceUploader will add the new one.
    // The UI should trigger image picker then call addEvidence with the new item.
    setFormData((prev) => ({
      ...prev,
      evidence: prev.evidence.filter((e) => e.id !== evidence.id),
    }));
  }, []);

  const updateTextEvidence = useCallback((text: string) => {
    setFormData((prev) => {
      const existingTextIndex = prev.evidence.findIndex((e) => e.type === 'text');

      if (!text.trim()) {
        // Remove text evidence if empty
        if (existingTextIndex >= 0) {
          return {
            ...prev,
            evidence: prev.evidence.filter((e) => e.type !== 'text'),
          };
        }
        return prev;
      }

      if (existingTextIndex >= 0) {
        // Update existing text evidence
        const updated = [...prev.evidence];
        updated[existingTextIndex] = {
          ...updated[existingTextIndex],
          text,
          name: 'Written Evidence',
        };
        return {...prev, evidence: updated};
      }

      // Add new text evidence
      const newTextEvidence: Evidence = {
        id: generateId(),
        type: 'text',
        name: 'Written Evidence',
        text,
        createdAt: new Date().toISOString(),
      };
      return {...prev, evidence: [...prev.evidence, newTextEvidence]};
    });
  }, []);

  const resetForm = useCallback(() => {
    setFormData({...initialFormData, claimId: generateClaimId()});
  }, []);

  const getClaimObject = useCallback((): Claim => {
    const now = new Date().toISOString();
    return {
      claimId: formData.claimId,
      policyNumber: formData.policyNumber,
      claimantName: formData.claimantName,
      incidentDate: formData.incidentDate,
      incidentLocation: formData.incidentLocation,
      incidentDescription: formData.incidentDescription,
      witness: {
        name: formData.witness.name,
        statement: formData.witness.statement,
      },
      evidence: formData.evidence,
      status: 'draft',
      createdAt: now,
      updatedAt: now,
    };
  }, [formData]);

  return {
    formData,
    updateField,
    updateWitness,
    addEvidence,
    removeEvidence,
    replaceEvidence,
    updateTextEvidence,
    resetForm,
    getClaimObject,
  };
}
