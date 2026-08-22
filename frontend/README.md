# ClaimForge Edge — Frontend

## Module: Section 1 — Mobile App + Claim Intake & Evidence Upload

Part of the **ClaimForge Edge** team project. This is the `frontend/` module.
Sibling modules live in `ai-service/` (Gen-AI + conflict detection) and
`firebase/` (rules + integration).

Mobile-first insurance claim submission experience for field agents. Capture claim details, collect photographic evidence, record witness statements, and submit claims to the FastAPI backend for AI-powered verification.

---

## Tech Stack

- **React Native** 0.73 (TypeScript)
- **React Navigation** (Native Stack)
- **react-native-image-picker** (camera + gallery)
- **react-native-safe-area-context** + **react-native-screens**
- **FastAPI HTTP API** (claims, evidence, and analysis)

---

## Setup

### Prerequisites

- Node.js 18+
- React Native CLI
- Android Studio (for Android) or Xcode (for iOS)
- Java 17 (Android)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd ClaimForgeEdge

# Install dependencies
npm install

# iOS only: install pods
cd ios && pod install && cd ..
```

---

## Backend Connection

The frontend sends requests to the FastAPI backend at `http://localhost:8000` on iOS and `http://10.0.2.2:8000` on an Android emulator. Start the backend first:

```bash
cd ../ai-service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Image bytes are sent directly to the backend for processing. The frontend does not upload images to Firebase Storage.

## Native Firebase Configuration

Native Firebase credentials are not required for the current API flow. If native Firebase features are added later, place the credentials here:

### Android

Place `google-services.json` in:

```
android/app/google-services.json
```

### iOS

Place `GoogleService-Info.plist` in:

```
ios/ClaimForgeEdge/GoogleService-Info.plist
```

### Firebase Configuration Steps

1. Create a project at [Firebase Console](https://console.firebase.google.com)
2. Add an Android app (package: `com.claimforgeedge`)
3. Add an iOS app (bundle ID: `com.claimforgeedge`)
4. Download and place the credential files as shown above
5. Enable **Firebase Storage** in the console
6. Uncomment Firebase imports in `src/services/firebaseStorage.ts`

> The app runs without Firebase using built-in placeholders for development.

---

## Run

```bash
# Start Metro bundler
npm start

# Android
npm run android

# iOS
npm run ios
```

### Verified

The Android debug build has been run end-to-end on a Pixel 3a emulator (API 34):
build succeeded, app launched, all four steps, validation, evidence capture,
review, and submission were exercised. `npm run typecheck` passes with no errors.

iOS has **not** been built — that requires macOS + Xcode. The iOS project folder
is generated from the React Native template and needs `pod install` before its
first build.

### Faster emulator builds

Building all four ABIs is slow. For emulator-only work, build just x86_64:

```bash
cd android && ./gradlew assembleDebug -PreactNativeArchitectures=x86_64
```

### Build environment notes

These bit us during setup and are worth knowing:

- **Pinned dependency versions matter.** `react-native-screens` and
  `react-native-safe-area-context` must stay on the versions in `package.json`.
  Caret ranges pull in releases that target React Native 0.76+ and fail to
  compile against 0.73 (`Unresolved reference` in `RNScreensPackage.kt`).
- **NDK + CMake are required.** `react-native-screens` declares an
  unconditional `externalNativeBuild { cmake }`, so the Android NDK
  (`25.1.8937393`) and CMake (`3.22.1`) must be installed even though the New
  Architecture is disabled. Gradle normally auto-installs them; on a slow or
  filtered network that download can stall silently. Installing them via
  Android Studio's SDK Manager up front avoids the problem.
- **JDK 17** is required. Android Studio's bundled runtime
  (`<Android Studio>/jbr`) works — point `JAVA_HOME` at it.

---

## Folder Structure

```
src/
├── components/          # Reusable UI components
│   ├── PrimaryButton.tsx    # Multi-variant button
│   ├── ClaimInput.tsx       # Form input with validation
│   ├── EvidenceCard.tsx     # Evidence preview card
│   ├── EvidenceUploader.tsx # Camera/gallery/video picker
│   ├── ProgressIndicator.tsx # Step progress bar
│   └── EmptyState.tsx       # Empty state placeholder
│
├── screens/             # Application screens
│   ├── HomeScreen.tsx           # Landing page with CTA
│   ├── ClaimIntakeScreen.tsx    # Multi-step claim form
│   └── SubmissionSuccessScreen.tsx # Post-submission state
│
├── navigation/          # React Navigation setup
│   └── AppNavigator.tsx
│
├── services/            # External service integrations
│   ├── firebaseStorage.ts   # Upload/delete evidence files
│   └── claimService.ts      # Submit claims, AI integration point
│
├── hooks/               # Custom React hooks
│   └── useClaimForm.ts      # Form state management
│
├── utils/               # Pure utility functions
│   ├── validation.ts        # Per-step form validation
│   └── formatters.ts        # ID generation, formatting
│
├── types/               # Shared TypeScript interfaces
│   ├── claim.ts             # Claim, Evidence, ClaimAnalysisService
│   └── navigation.ts        # Navigation param types
│
├── constants/           # Design tokens and config
│   ├── theme.ts             # Colors, typography, spacing
│   └── index.ts             # App constants, validation messages
│
└── App.tsx              # Root component
```

---

## Integration Contract

This module produces a `Claim` object that downstream modules consume.

### Data Flow

```
Claim Intake (this module)
       ↓
  Claim Object
       ↓
  AI Analysis Service (Team Member 1)
       ↓
  Conflict Detection
       ↓
  Verdict Dashboard (Team Member 2)
```

### Claim Interface

```typescript
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

export interface Evidence {
  id: string;
  type: 'photo' | 'video' | 'text';
  name: string;
  uri?: string;
  storageUrl?: string;
  text?: string;
  mimeType?: string;
  size?: number;
  createdAt: string;
}

export type ClaimStatus =
  | 'draft'
  | 'submitted'
  | 'analyzing'
  | 'verified'
  | 'rejected'
  | 'pending_review';
```

### AI Integration Point

The AI team should implement the `ClaimAnalysisService` interface:

```typescript
export interface ClaimAnalysisService {
  analyzeClaim(claim: Claim): Promise<ClaimAnalysisResult>;
}

export interface ClaimAnalysisResult {
  claimId: string;
  status: string;
  [key: string]: unknown;
}
```

Usage from `claimService.ts`:

```typescript
import { sendToAnalysis } from './services/claimService';

const result = await sendToAnalysis(submittedClaim, yourAIServiceInstance);
```

### How to Connect the AI Module

1. Import `Claim` and `ClaimAnalysisService` from `src/types`
2. Implement `ClaimAnalysisService.analyzeClaim()`
3. Call `sendToAnalysis(claim, service)` from `src/services/claimService.ts`
4. The Claim Intake UI does **not** need to change

---

## Features

- Multi-step claim intake form with progress indicator
- Photo capture via camera or gallery
- Video evidence selection (optional)
- Written/text evidence input
- Evidence preview, replace, and remove with confirmation
- Client-side validation per step
- Review screen before submission
- Success state with AI integration handoff
- Responsive design for all mobile screen sizes
- Accessible labels and touch targets
- Keyboard-aware form handling
- Platform-aware permissions (Android/iOS)

---

## Assumptions & Limitations

- Firebase native modules are intentionally **unlinked** until credentials exist.
  See `react-native.config.js` — linking them without `google-services.json`
  crashes the app on launch. The service layer runs on placeholders until you
  follow the enable steps in that file.
- Validation errors clear when you press Next, not while typing. Fixing a field
  leaves its message visible until the next validation pass.
- Firebase Storage is prepared but uses local placeholders until credentials are configured
- No offline persistence (future enhancement)
- Video playback preview is minimal (shows attachment indicator)
- No push notifications for claim status updates
- AI/ML analysis, conflict detection, and verdict display are handled by other team members
- Recent claims list on HomeScreen is a placeholder for future Firestore integration
