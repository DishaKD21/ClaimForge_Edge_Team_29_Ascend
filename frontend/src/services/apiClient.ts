import {Platform} from 'react-native';

// Android emulators reach the host machine through 10.0.2.2.
const API_BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';

export interface ApiClaimResponse {
  claimId: string;
  message: string;
}

export interface ApiEvidenceResponse {
  id: string;
  claimId: string;
  type: 'image' | 'text';
  fileName?: string;
  mimeType?: string;
  content?: string;
  uploadedAt?: string;
}

export interface ApiAnalysisResponse {
  id: string;
  claimId: string;
  result: Record<string, unknown>;
  createdAt: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  const responseText = await response.text();
  let body: unknown;

  try {
    body = responseText ? JSON.parse(responseText) : null;
  } catch {
    body = responseText;
  }

  if (!response.ok) {
    const detail =
      typeof body === 'object' && body !== null && 'detail' in body
        ? String((body as {detail: unknown}).detail)
        : `Request failed with status ${response.status}`;
    throw new Error(detail);
  }

  return body as T;
}

export function checkApiHealth() {
  return request<{status: string; firebase: string}>('/health');
}

export function createClaim(payload: {
  customerName: string;
  description: string;
  incidentDate: string;
  incidentTime: string;
  location: string;
}) {
  return request<ApiClaimResponse>('/api/v1/claims', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  });
}

export function getClaim(claimId: string) {
  return request<Record<string, unknown>>(`/api/v1/claims/${encodeURIComponent(claimId)}`);
}

export function uploadTextEvidence(claimId: string, content: string) {
  const formData = new FormData();
  formData.append('type', 'text');
  formData.append('content', content);

  return request<ApiEvidenceResponse>(
    `/api/v1/claims/${encodeURIComponent(claimId)}/evidence`,
    {method: 'POST', body: formData},
  );
}

export function uploadImageEvidence(
  claimId: string,
  image: {uri: string; name: string; type: string},
) {
  const formData = new FormData();
  formData.append('type', 'image');
  formData.append('file', image as unknown as Blob);

  return request<ApiEvidenceResponse>(
    `/api/v1/claims/${encodeURIComponent(claimId)}/evidence`,
    {method: 'POST', body: formData},
  );
}

export function getClaimEvidence(claimId: string) {
  return request<ApiEvidenceResponse[]>(
    `/api/v1/claims/${encodeURIComponent(claimId)}/evidence`,
  );
}

export function analyzeClaim(
  claimId: string,
  options?: {text?: string; image?: {uri: string; name: string; type: string}},
) {
  const formData = new FormData();
  if (options?.text) {
    formData.append('text', options.text);
  }
  if (options?.image) {
    formData.append('image', options.image as unknown as Blob);
  }

  return request<ApiAnalysisResponse>(
    `/api/v1/claims/${encodeURIComponent(claimId)}/analyze`,
    {method: 'POST', body: formData},
  );
}
