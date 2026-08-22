import {NativeStackScreenProps} from '@react-navigation/native-stack';

export type RootStackParamList = {
  Home: undefined;
  ClaimIntake: undefined;
  SubmissionSuccess: {
    claimId: string;
    analysisText?: string;
    analysisImage?: {uri: string; name: string; type: string};
  };
};

export type HomeScreenProps = NativeStackScreenProps<RootStackParamList, 'Home'>;
export type ClaimIntakeScreenProps = NativeStackScreenProps<RootStackParamList, 'ClaimIntake'>;
export type SubmissionSuccessScreenProps = NativeStackScreenProps<RootStackParamList, 'SubmissionSuccess'>;
