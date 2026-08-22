/**
 * React Native CLI configuration.
 *
 * ─── Firebase autolinking ────────────────────────────────────────────────────
 * The @react-native-firebase packages are declared in package.json because the
 * storage service layer is built against them, but every Firebase call site is
 * currently commented out (see src/services/firebaseStorage.ts).
 *
 * If these native modules are autolinked WITHOUT a google-services.json /
 * GoogleService-Info.plist present, the app crashes on launch with
 * "Default FirebaseApp is not initialized in this process".
 *
 * So we keep them unlinked for now. This is what lets the app run with the
 * built-in placeholder upload implementation.
 *
 * TO ENABLE FIREBASE:
 *   1. Add android/app/google-services.json
 *   2. Add ios/ClaimForgeEdge/GoogleService-Info.plist
 *   3. Apply the Google Services Gradle plugin (see README)
 *   4. Delete the `dependencies` block below
 *   5. Uncomment the Firebase code in src/services/firebaseStorage.ts
 *   6. Rebuild (npm run android)
 * ─────────────────────────────────────────────────────────────────────────────
 */

module.exports = {
  dependencies: {
    '@react-native-firebase/app': {
      platforms: {android: null, ios: null},
    },
    '@react-native-firebase/storage': {
      platforms: {android: null, ios: null},
    },
  },
};
