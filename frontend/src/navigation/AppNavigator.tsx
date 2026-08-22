import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {RootStackParamList} from '../types/navigation';
import {HomeScreen} from '../screens/HomeScreen';
import {ClaimIntakeScreen} from '../screens/ClaimIntakeScreen';
import {SubmissionSuccessScreen} from '../screens/SubmissionSuccessScreen';
import {COLORS, TYPOGRAPHY} from '../constants';

const Stack = createNativeStackNavigator<RootStackParamList>();

export const AppNavigator: React.FC = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: COLORS.white,
          },
          headerTintColor: COLORS.primary,
          headerTitleStyle: {
            fontWeight: TYPOGRAPHY.fontWeight.semibold,
            fontSize: TYPOGRAPHY.fontSize.md,
          },
          headerShadowVisible: false,
          headerBackTitleVisible: false,
          animation: 'slide_from_right',
          contentStyle: {
            backgroundColor: COLORS.background,
          },
        }}>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{headerShown: false}}
        />
        <Stack.Screen
          name="ClaimIntake"
          component={ClaimIntakeScreen}
          options={{
            title: 'New Claim',
            headerShown: false,
          }}
        />
        <Stack.Screen
          name="SubmissionSuccess"
          component={SubmissionSuccessScreen}
          options={{
            title: 'Submitted',
            headerShown: false,
            gestureEnabled: false,
          }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};
