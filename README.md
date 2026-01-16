# Mobile App Development Prompt: Healthcare User Management System

## Project Overview
Design and develop a comprehensive React Native mobile application for a healthcare user management system. The app should provide user authentication, role-based access control, account verification, and password management features. The backend API is already built with FastAPI and provides RESTful endpoints.

## Technical Stack Requirements
- **Framework**: React Native (latest stable version)
- **Styling**: NativeWind (Tailwind CSS for React Native) - use utility-first CSS classes
- **State Management**: React Query (TanStack Query) for server state management
- **Navigation**: React Navigation (Stack, Tab, or Drawer navigation as appropriate)
- **HTTP Client**: Axios for API calls
- **Storage**: AsyncStorage or SecureStore for token persistence
- **Form Handling**: React Hook Form with validation
- **Date Handling**: date-fns or dayjs
- **TypeScript**: Use TypeScript for type safety

## API Base Configuration
- **Base URL**: `http://localhost:9000` (configurable via environment variables)
- **Authentication**: Bearer token (JWT) in Authorization header
- **Content-Type**: application/json

## Core Features to Implement

### 1. Authentication Flow

#### 1.1 User Registration Screen
- **Fields**:
  - Full Name (text input, required, min 2 characters)
  - Phone Number (text input with country code picker, E.164 format validation, required)
  - Gender (dropdown/radio: Male, Female, Other, required)
  - Birth Date (date picker, optional, format: YYYY-MM-DD)
  - Password (secure text input, required, min 8 characters with validation)
  - Role Selection (optional dropdown, defaults to "patient")
- **Validation**: 
  - Real-time validation with error messages
  - Phone number must match pattern: `^\+[1-9]\d{7,14}$`
  - Password strength indicator
- **API Endpoint**: `POST /users/`
- **After Registration**: 
  - Show success message
  - Automatically navigate to verification screen
  - Display: "Verification code sent to your phone number"

#### 1.2 Account Verification Screen
- **Fields**:
  - Phone Number (pre-filled, read-only)
  - 6-digit verification code input (OTP input component with auto-focus)
- **Features**:
  - Auto-format code input (6 separate boxes or single input)
  - Resend code button (with 60-second cooldown timer)
  - Countdown timer showing code expiration (10 minutes)
- **API Endpoints**: 
  - `POST /users/verify-account` (verify code)
  - `POST /users/resend-verification` (resend code)
- **After Verification**: Navigate to login screen or main app

#### 1.3 Login Screen
- **Fields**:
  - Phone Number (text input with country code, required)
  - Password (secure text input, required)
  - "Remember Me" checkbox (optional)
- **Features**:
  - Forgot Password link
  - Show/hide password toggle
  - Loading state during authentication
- **API Endpoint**: `POST /users/login`
- **Response Handling**: 
  - Store JWT token securely
  - Navigate to appropriate screen based on user role
- **Error Handling**: Display user-friendly error messages

#### 1.4 Forgot Password Flow
- **Step 1 - Request Reset**:
  - Phone number input
  - API: `POST /users/forgot-password`
  - Show success message: "Reset code sent to your phone"
- **Step 2 - Reset Password**:
  - Phone number (pre-filled)
  - 6-digit reset code input
  - New password input (with confirmation)
  - API: `POST /users/reset-password`
  - Navigate to login after success

#### 1.5 Change Password Screen (Authenticated)
- **Fields**:
  - Current password
  - New password
  - Confirm new password
- **Validation**: 
  - New password must match confirmation
  - Password strength requirements
- **API Endpoint**: `POST /users/change-password`
- **Access**: Requires authentication token

### 2. User Profile Management

#### 2.1 Profile Screen
- **Display**:
  - Full Name
  - Phone Number
  - Gender
  - Birth Date
  - Account Status (Verified/Unverified badge)
  - User Roles (display as chips/badges)
  - Account Created Date
- **Actions**:
  - Edit Profile button
  - Change Password button
  - Logout button
- **API Endpoint**: `GET /users/me` (requires authentication)

#### 2.2 Edit Profile Screen
- **Editable Fields**: Full Name, Gender, Birth Date
- **Read-only**: Phone Number, Email (if applicable)
- **API Endpoint**: `PUT /users/{user_id}` (if implemented)
- **Validation**: Same as registration

### 3. Role-Based Navigation & Access Control

#### 3.1 Navigation Structure
- **Unauthenticated Stack**:
  - Login
  - Register
  - Forgot Password
  - Verify Account
- **Authenticated Tabs/Drawer** (based on role):
  - **Patient**: Dashboard, Profile, Appointments (if applicable)
  - **Healthcare Professional**: Dashboard, Patients, Profile, Schedule
  - **Pharmacist**: Dashboard, Prescriptions, Profile, Inventory
  - **Care Taker**: Dashboard, Patients, Profile
  - **Admin**: Dashboard, Users Management, Roles Management, Profile

#### 3.2 Role Management (Admin Only)
- **Roles List Screen**:
  - Display all roles with name, display name, description
  - Active/Inactive status
  - API: `GET /users/roles`
- **Create Role Screen**:
  - Name, Display Name, Description fields
  - API: `POST /users/roles`
- **Edit Role Screen**:
  - Update role details
  - API: `PUT /users/roles/{role_id}`
- **User Role Assignment** (Admin Only):
  - Select user
  - Assign/Remove roles
  - API: `POST /users/{user_id}/roles`, `DELETE /users/{user_id}/roles`

### 4. UI/UX Requirements

#### 4.1 Design System
- **Color Palette**: 
  - Primary: Healthcare blue/green theme
  - Success: Green for verified status
  - Error: Red for errors
  - Warning: Orange/Yellow
  - Neutral: Gray scale
- **Typography**: 
  - Clear hierarchy (Headings, Body, Caption)
  - Readable font sizes (minimum 14px for body)
- **Spacing**: Consistent spacing using Tailwind scale (4, 8, 16, 24, 32px)
- **Components**: 
  - Reusable button components (Primary, Secondary, Danger)
  - Input fields with labels and error states
  - Loading spinners/skeletons
  - Toast notifications for success/error messages
  - Modal dialogs for confirmations

#### 4.2 Accessibility
- Proper labels for screen readers
- Sufficient color contrast
- Touch target sizes (minimum 44x44px)
- Keyboard navigation support

#### 4.3 Responsive Design
- Support for different screen sizes
- Safe area handling for notched devices
- Landscape orientation support (where applicable)

### 5. State Management with React Query

#### 5.1 Query Hooks Structurepescript
// Example structure
- useLogin()
- useRegister()
- useGetCurrentUser()
- useVerifyAccount()
- useForgotPassword()
- useResetPassword()
- useChangePassword()
- useGetRoles() (admin)
- useCreateRole() (admin)
- useAssignRoles() (admin)
