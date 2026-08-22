/**
 * Firebase Storage Service
 * Handles all evidence file uploads and deletions.
 *
 * SETUP REQUIRED:
 * 1. Create a Firebase project at https://console.firebase.google.com
 * 2. Add your google-services.json (Android) to android/app/
 * 3. Add your GoogleService-Info.plist (iOS) to ios/ClaimForgeEdge/
 * 4. Uncomment the Firebase imports below once configured
 *
 * The UI layer calls these functions — it never interacts with Firebase directly.
 */

import {Evidence} from '../types';

// ─── Uncomment when Firebase is configured ───────────────────────────────────
// import storage from '@react-native-firebase/storage';
// ─────────────────────────────────────────────────────────────────────────────

export interface UploadProgress {
  bytesTransferred: number;
  totalBytes: number;
  percentage: number;
}

export interface UploadResult {
  storageUrl: string;
  storagePath: string;
}

/**
 * Upload a single piece of evidence to Firebase Storage.
 *
 * @param evidence - The Evidence object containing uri and metadata
 * @param onProgress - Optional callback for upload progress updates
 * @returns Promise resolving to the storage URL and path
 *
 * Architecture:
 *   EvidenceUploader component
 *        ↓
 *   firebaseStorage.uploadEvidence()
 *        ↓
 *   Firebase Storage bucket
 */
export async function uploadEvidence(
  evidence: Evidence,
  onProgress?: (progress: UploadProgress) => void,
): Promise<UploadResult> {
  if (!evidence.uri) {
    throw new Error('Evidence URI is required for upload.');
  }

  const storagePath = buildStoragePath(evidence);

  // ─── Firebase implementation (uncomment when configured) ─────────────────
  //
  // const reference = storage().ref(storagePath);
  // const task = reference.putFile(evidence.uri);
  //
  // if (onProgress) {
  //   task.on('state_changed', (snapshot) => {
  //     onProgress({
  //       bytesTransferred: snapshot.bytesTransferred,
  //       totalBytes: snapshot.totalBytes,
  //       percentage: Math.round(
  //         (snapshot.bytesTransferred / snapshot.totalBytes) * 100,
  //       ),
  //     });
  //   });
  // }
  //
  // await task;
  // const downloadUrl = await reference.getDownloadURL();
  //
  // return {
  //   storageUrl: downloadUrl,
  //   storagePath,
  // };
  // ──────────────────────────────────────────────────────────────────────────

  // Placeholder: simulate upload for development without Firebase
  return new Promise((resolve) => {
    let transferred = 0;
    const total = evidence.size || 1024 * 100;
    const interval = setInterval(() => {
      transferred += total * 0.2;
      if (transferred >= total) {
        transferred = total;
        clearInterval(interval);
        resolve({
          storageUrl: `https://firebasestorage.placeholder.com/${storagePath}`,
          storagePath,
        });
      }
      onProgress?.({
        bytesTransferred: transferred,
        totalBytes: total,
        percentage: Math.round((transferred / total) * 100),
      });
    }, 200);
  });
}

/**
 * Delete evidence from Firebase Storage.
 *
 * @param storagePath - The path within the storage bucket
 */
export async function deleteEvidence(storagePath: string): Promise<void> {
  if (!storagePath) {
    throw new Error('Storage path is required for deletion.');
  }

  // ─── Firebase implementation (uncomment when configured) ─────────────────
  //
  // const reference = storage().ref(storagePath);
  // await reference.delete();
  //
  // ──────────────────────────────────────────────────────────────────────────

  // Placeholder: simulate deletion
  return new Promise((resolve) => {
    setTimeout(resolve, 300);
  });
}

/**
 * Upload multiple evidence items.
 *
 * @param evidenceList - Array of Evidence objects to upload
 * @param onItemProgress - Optional callback with (index, progress)
 * @returns Array of upload results
 */
export async function uploadMultipleEvidence(
  evidenceList: Evidence[],
  onItemProgress?: (index: number, progress: UploadProgress) => void,
): Promise<UploadResult[]> {
  const results: UploadResult[] = [];

  for (let i = 0; i < evidenceList.length; i++) {
    const evidence = evidenceList[i];
    if (evidence.uri) {
      const result = await uploadEvidence(evidence, (progress) => {
        onItemProgress?.(i, progress);
      });
      results.push(result);
    }
  }

  return results;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildStoragePath(evidence: Evidence): string {
  const timestamp = Date.now();
  const sanitizedName = evidence.name.replace(/[^a-zA-Z0-9._-]/g, '_');
  return `claims/evidence/${evidence.type}/${timestamp}_${sanitizedName}`;
}
