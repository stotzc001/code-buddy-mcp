# Form Handling and Validation

**ID:** fro-006  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Medium  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive workflow for implementing robust form handling and validation in React applications

**Why:** 
- Ensure data quality before submission
- Provide instant feedback to users
- Prevent invalid data from reaching the backend
- Improve user experience with clear error messages
- Reduce server load by catching errors client-side
- Meet accessibility standards for form interactions

**When to use:**
- Building user input forms (login, registration, checkout, etc.)
- Implementing complex multi-step forms
- Adding client-side validation to existing forms
- Creating reusable form components
- Integrating forms with backend APIs

---

## Prerequisites

**Required:**
- [ ] React project with TypeScript
- [ ] Understanding of controlled vs uncontrolled components
- [ ] Knowledge of HTML form elements and attributes
- [ ] Familiarity with validation patterns (email, phone, etc.)

**Check before starting:**
```bash
# Verify React and TypeScript
npm list react react-dom typescript

# Check if form libraries are needed
npm list react-hook-form yup zod

# For UI components (optional)
npm list @radix-ui/react-label @radix-ui/react-select
```

---

## Implementation Steps

### Step 1: Choose Form Management Approach

**What:** Select the appropriate form handling strategy based on form complexity

**How:**

1. **Decision matrix:**

```typescript
// Simple forms (1-5 fields, basic validation)
// → Use React state + manual validation

// Medium forms (5-15 fields, moderate validation)
// → Use React Hook Form

// Complex forms (15+ fields, complex validation, multi-step)
// → Use React Hook Form + Zod/Yup schema validation

// Form builders (dynamic forms from JSON)
// → Use Formik or React Hook Form with dynamic field generation
```

2. **Install dependencies:**

```bash
# React Hook Form (recommended)
npm install react-hook-form

# Validation schemas
npm install zod  # TypeScript-first validation
# or
npm install yup @hookform/resolvers  # JavaScript validation

# For complex UI components (optional)
npm install @radix-ui/react-label @radix-ui/react-select
```

**Verification:**
- [ ] Form library chosen based on requirements
- [ ] Dependencies installed successfully
- [ ] No version conflicts

**If This Fails:**
→ Check npm registry access
→ Verify React version compatibility

---

### Step 2: Build Basic Form with React Hook Form

**What:** Implement a form using React Hook Form for optimal performance and developer experience

**How:**

1. **Simple login form:**

```typescript
// components/LoginForm.tsx
import React from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export const LoginForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    defaultValues: {
      email: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit: SubmitHandler<LoginFormData> = async (data) => {
    try {
      console.log('Form data:', data);
      // API call here
      await new Promise((resolve) => setTimeout(resolve, 1000));
      alert('Login successful!');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="login-form">
      <div className="form-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Invalid email address',
            },
          })}
          aria-invalid={errors.email ? 'true' : 'false'}
        />
        {errors.email && (
          <span className="error-message" role="alert">
            {errors.email.message}
          </span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          {...register('password', {
            required: 'Password is required',
            minLength: {
              value: 8,
              message: 'Password must be at least 8 characters',
            },
          })}
          aria-invalid={errors.password ? 'true' : 'false'}
        />
        {errors.password && (
          <span className="error-message" role="alert">
            {errors.password.message}
          </span>
        )}
      </div>

      <div className="form-field checkbox">
        <label>
          <input type="checkbox" {...register('rememberMe')} />
          Remember me
        </label>
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Logging in...' : 'Log In'}
      </button>
    </form>
  );
};
```

2. **Registration form with more fields:**

```typescript
// components/RegistrationForm.tsx
import React from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';

interface RegistrationFormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  dateOfBirth: string;
  agreeToTerms: boolean;
}

export const RegistrationForm: React.FC = () => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting, isDirty, isValid },
  } = useForm<RegistrationFormData>({
    mode: 'onChange', // Validate on change
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      confirmPassword: '',
      dateOfBirth: '',
      agreeToTerms: false,
    },
  });

  // Watch password for confirm password validation
  const password = watch('password');

  const onSubmit: SubmitHandler<RegistrationFormData> = async (data) => {
    try {
      // Remove confirmPassword before sending to API
      const { confirmPassword, ...registrationData } = data;
      console.log('Registration data:', registrationData);
      
      // API call
      await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registrationData),
      });
      
      alert('Registration successful!');
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="registration-form">
      <div className="form-row">
        <div className="form-field">
          <label htmlFor="firstName">First Name *</label>
          <input
            id="firstName"
            type="text"
            {...register('firstName', {
              required: 'First name is required',
              minLength: {
                value: 2,
                message: 'First name must be at least 2 characters',
              },
              maxLength: {
                value: 50,
                message: 'First name must be less than 50 characters',
              },
            })}
          />
          {errors.firstName && (
            <span className="error-message">{errors.firstName.message}</span>
          )}
        </div>

        <div className="form-field">
          <label htmlFor="lastName">Last Name *</label>
          <input
            id="lastName"
            type="text"
            {...register('lastName', {
              required: 'Last name is required',
              minLength: {
                value: 2,
                message: 'Last name must be at least 2 characters',
              },
            })}
          />
          {errors.lastName && (
            <span className="error-message">{errors.lastName.message}</span>
          )}
        </div>
      </div>

      <div className="form-field">
        <label htmlFor="email">Email *</label>
        <input
          id="email"
          type="email"
          {...register('email', {
            required: 'Email is required',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: 'Invalid email address',
            },
          })}
        />
        {errors.email && (
          <span className="error-message">{errors.email.message}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="password">Password *</label>
        <input
          id="password"
          type="password"
          {...register('password', {
            required: 'Password is required',
            minLength: {
              value: 8,
              message: 'Password must be at least 8 characters',
            },
            pattern: {
              value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
              message:
                'Password must contain uppercase, lowercase, number, and special character',
            },
          })}
        />
        {errors.password && (
          <span className="error-message">{errors.password.message}</span>
        )}
        <small>Must be at least 8 characters with mixed case, number, and symbol</small>
      </div>

      <div className="form-field">
        <label htmlFor="confirmPassword">Confirm Password *</label>
        <input
          id="confirmPassword"
          type="password"
          {...register('confirmPassword', {
            required: 'Please confirm your password',
            validate: (value) =>
              value === password || 'Passwords do not match',
          })}
        />
        {errors.confirmPassword && (
          <span className="error-message">{errors.confirmPassword.message}</span>
        )}
      </div>

      <div className="form-field">
        <label htmlFor="dateOfBirth">Date of Birth *</label>
        <input
          id="dateOfBirth"
          type="date"
          {...register('dateOfBirth', {
            required: 'Date of birth is required',
            validate: (value) => {
              const date = new Date(value);
              const today = new Date();
              const age = today.getFullYear() - date.getFullYear();
              return age >= 18 || 'You must be at least 18 years old';
            },
          })}
        />
        {errors.dateOfBirth && (
          <span className="error-message">{errors.dateOfBirth.message}</span>
        )}
      </div>

      <div className="form-field checkbox">
        <label>
          <input
            type="checkbox"
            {...register('agreeToTerms', {
              required: 'You must agree to the terms and conditions',
            })}
          />
          I agree to the Terms and Conditions *
        </label>
        {errors.agreeToTerms && (
          <span className="error-message">{errors.agreeToTerms.message}</span>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting || !isDirty || !isValid}
      >
        {isSubmitting ? 'Creating Account...' : 'Create Account'}
      </button>
    </form>
  );
};
```

**Verification:**
- [ ] Form renders correctly
- [ ] Validation triggers on appropriate events
- [ ] Error messages display clearly
- [ ] Submit button disabled when invalid
- [ ] Loading state shows during submission

**If This Fails:**
→ Check register syntax matches React Hook Form docs
→ Verify field names match interface
→ Ensure form validation rules are correct

---

### Step 3: Add Schema Validation with Zod

**What:** Use Zod for type-safe, reusable validation schemas

**How:**

```typescript
// schemas/userSchema.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters'),
  rememberMe: z.boolean().optional(),
});

export const registrationSchema = z
  .object({
    firstName: z
      .string()
      .min(2, 'First name must be at least 2 characters')
      .max(50, 'First name must be less than 50 characters'),
    lastName: z
      .string()
      .min(2, 'Last name must be at least 2 characters')
      .max(50, 'Last name must be less than 50 characters'),
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Invalid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/,
        'Password must contain uppercase, lowercase, number, and special character'
      ),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
    dateOfBirth: z
      .string()
      .min(1, 'Date of birth is required')
      .refine((date) => {
        const age = new Date().getFullYear() - new Date(date).getFullYear();
        return age >= 18;
      }, 'You must be at least 18 years old'),
    agreeToTerms: z
      .boolean()
      .refine((val) => val === true, 'You must agree to the terms'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

// Infer TypeScript types from schema
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegistrationFormData = z.infer<typeof registrationSchema>;

// Custom validation functions
export const passwordStrength = (password: string): {
  score: number;
  feedback: string;
} => {
  let score = 0;
  
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[@$!%*?&]/.test(password)) score++;

  const feedback = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'];
  
  return {
    score,
    feedback: feedback[Math.min(score, 5)],
  };
};
```

**Using Zod with React Hook Form:**

```typescript
// components/LoginFormWithZod.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, LoginFormData } from '../schemas/userSchema';

export const LoginFormWithZod: React.FC = () => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    console.log('Valid data:', data);
    // API call
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register('email')} />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input id="password" type="password" {...register('password')} />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <div>
        <label>
          <input type="checkbox" {...register('rememberMe')} />
          Remember me
        </label>
      </div>

      <button type="submit" disabled={isSubmitting}>
        Log In
      </button>
    </form>
  );
};
```

**Verification:**
- [ ] Schema validates correctly
- [ ] TypeScript types inferred from schema
- [ ] Custom refinements work
- [ ] Error messages are clear

---

### Step 4: Implement Advanced Form Patterns

**What:** Build complex form features like dynamic fields, conditional validation, and multi-step forms

**How:**

1. **Dynamic field arrays:**

```typescript
// components/SkillsForm.tsx
import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';

interface Skill {
  name: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  yearsOfExperience: number;
}

interface SkillsFormData {
  skills: Skill[];
}

export const SkillsForm: React.FC = () => {
  const { register, control, handleSubmit } = useForm<SkillsFormData>({
    defaultValues: {
      skills: [{ name: '', level: 'beginner', yearsOfExperience: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'skills',
  });

  const onSubmit = (data: SkillsFormData) => {
    console.log('Skills:', data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <h3>Skills</h3>
      
      {fields.map((field, index) => (
        <div key={field.id} className="skill-entry">
          <input
            {...register(`skills.${index}.name` as const, {
              required: 'Skill name is required',
            })}
            placeholder="Skill name"
          />

          <select {...register(`skills.${index}.level` as const)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <input
            type="number"
            {...register(`skills.${index}.yearsOfExperience` as const, {
              valueAsNumber: true,
              min: 0,
            })}
            placeholder="Years"
          />

          <button type="button" onClick={() => remove(index)}>
            Remove
          </button>
        </div>
      ))}

      <button
        type="button"
        onClick={() =>
          append({ name: '', level: 'beginner', yearsOfExperience: 0 })
        }
      >
        Add Skill
      </button>

      <button type="submit">Submit</button>
    </form>
  );
};
```

2. **Multi-step form:**

```typescript
// components/MultiStepForm.tsx
import React, { useState } from 'react';
import { useForm, UseFormReturn } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Step schemas
const step1Schema = z.object({
  firstName: z.string().min(1, 'Required'),
  lastName: z.string().min(1, 'Required'),
  email: z.string().email('Invalid email'),
});

const step2Schema = z.object({
  address: z.string().min(1, 'Required'),
  city: z.string().min(1, 'Required'),
  zipCode: z.string().regex(/^\d{5}$/, 'Must be 5 digits'),
});

const step3Schema = z.object({
  cardNumber: z.string().regex(/^\d{16}$/, 'Must be 16 digits'),
  expiryDate: z.string().regex(/^\d{2}\/\d{2}$/, 'Format: MM/YY'),
  cvv: z.string().regex(/^\d{3}$/, 'Must be 3 digits'),
});

// Combined schema for final submission
const fullSchema = step1Schema.merge(step2Schema).merge(step3Schema);

type FormData = z.infer<typeof fullSchema>;

const steps = [
  { title: 'Personal Info', schema: step1Schema },
  { title: 'Address', schema: step2Schema },
  { title: 'Payment', schema: step3Schema },
];

export const MultiStepForm: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);

  const {
    register,
    handleSubmit,
    trigger,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(steps[currentStep].schema),
    mode: 'onChange',
  });

  const nextStep = async () => {
    const isValid = await trigger();
    if (isValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = (data: FormData) => {
    console.log('Final submission:', data);
    // API call
  };

  return (
    <div className="multi-step-form">
      {/* Progress indicator */}
      <div className="progress">
        {steps.map((step, index) => (
          <div
            key={index}
            className={`step ${index === currentStep ? 'active' : ''} ${
              index < currentStep ? 'completed' : ''
            }`}
          >
            {step.title}
          </div>
        ))}
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)}>
        {currentStep === 0 && (
          <div>
            <h3>Personal Information</h3>
            <input {...register('firstName')} placeholder="First Name" />
            {errors.firstName && <span>{errors.firstName.message}</span>}

            <input {...register('lastName')} placeholder="Last Name" />
            {errors.lastName && <span>{errors.lastName.message}</span>}

            <input {...register('email')} type="email" placeholder="Email" />
            {errors.email && <span>{errors.email.message}</span>}
          </div>
        )}

        {currentStep === 1 && (
          <div>
            <h3>Address</h3>
            <input {...register('address')} placeholder="Street Address" />
            {errors.address && <span>{errors.address.message}</span>}

            <input {...register('city')} placeholder="City" />
            {errors.city && <span>{errors.city.message}</span>}

            <input {...register('zipCode')} placeholder="ZIP Code" />
            {errors.zipCode && <span>{errors.zipCode.message}</span>}
          </div>
        )}

        {currentStep === 2 && (
          <div>
            <h3>Payment</h3>
            <input {...register('cardNumber')} placeholder="Card Number" />
            {errors.cardNumber && <span>{errors.cardNumber.message}</span>}

            <input {...register('expiryDate')} placeholder="MM/YY" />
            {errors.expiryDate && <span>{errors.expiryDate.message}</span>}

            <input {...register('cvv')} placeholder="CVV" />
            {errors.cvv && <span>{errors.cvv.message}</span>}
          </div>
        )}

        {/* Navigation */}
        <div className="navigation">
          {currentStep > 0 && (
            <button type="button" onClick={prevStep}>
              Previous
            </button>
          )}

          {currentStep < steps.length - 1 ? (
            <button type="button" onClick={nextStep}>
              Next
            </button>
          ) : (
            <button type="submit">Submit</button>
          )}
        </div>
      </form>
    </div>
  );
};
```

3. **Conditional validation:**

```typescript
// components/ConditionalForm.tsx
import React from 'react';
import { useForm } from 'react-hook-form';

interface ConditionalFormData {
  accountType: 'personal' | 'business';
  businessName?: string;
  taxId?: string;
  // ... other fields
}

export const ConditionalForm: React.FC = () => {
  const { register, watch, handleSubmit, formState: { errors } } =
    useForm<ConditionalFormData>();

  const accountType = watch('accountType');

  const onSubmit = (data: ConditionalFormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Account Type</label>
        <select {...register('accountType')}>
          <option value="personal">Personal</option>
          <option value="business">Business</option>
        </select>
      </div>

      {accountType === 'business' && (
        <>
          <div>
            <label>Business Name</label>
            <input
              {...register('businessName', {
                required:
                  accountType === 'business' ? 'Business name is required' : false,
              })}
            />
            {errors.businessName && <span>{errors.businessName.message}</span>}
          </div>

          <div>
            <label>Tax ID</label>
            <input
              {...register('taxId', {
                required: accountType === 'business' ? 'Tax ID is required' : false,
                pattern: {
                  value: /^\d{2}-\d{7}$/,
                  message: 'Format: XX-XXXXXXX',
                },
              })}
            />
            {errors.taxId && <span>{errors.taxId.message}</span>}
          </div>
        </>
      )}

      <button type="submit">Submit</button>
    </form>
  );
};
```

**Verification:**
- [ ] Dynamic fields add/remove correctly
- [ ] Multi-step navigation works
- [ ] Validation applies per step
- [ ] Conditional fields show/hide properly

---

### Step 5: Handle File Uploads

**What:** Implement file upload with validation and preview

**How:**

```typescript
// components/FileUploadForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';

interface FileUploadFormData {
  avatar: FileList;
  documents: FileList;
}

export const FileUploadForm: React.FC = () => {
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FileUploadFormData>();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setAvatarPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const onSubmit = async (data: FileUploadFormData) => {
    const formData = new FormData();
    
    // Single file
    if (data.avatar[0]) {
      formData.append('avatar', data.avatar[0]);
    }

    // Multiple files
    Array.from(data.documents).forEach((file) => {
      formData.append('documents', file);
    });

    // API call
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      console.log('Upload result:', result);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Avatar (Single Image)</label>
        <input
          type="file"
          accept="image/*"
          {...register('avatar', {
            required: 'Avatar is required',
            validate: {
              fileSize: (files) =>
                files[0]?.size < 5000000 || 'File must be less than 5MB',
              fileType: (files) =>
                ['image/jpeg', 'image/png', 'image/gif'].includes(files[0]?.type) ||
                'Only JPEG, PNG, and GIF allowed',
            },
            onChange: handleAvatarChange,
          })}
        />
        {errors.avatar && <span>{errors.avatar.message}</span>}
        
        {avatarPreview && (
          <img src={avatarPreview} alt="Preview" style={{ width: 100 }} />
        )}
      </div>

      <div>
        <label>Documents (Multiple PDFs)</label>
        <input
          type="file"
          accept=".pdf"
          multiple
          {...register('documents', {
            validate: {
              maxFiles: (files) =>
                files.length <= 5 || 'Maximum 5 files allowed',
              totalSize: (files) => {
                const total = Array.from(files).reduce(
                  (acc, file) => acc + file.size,
                  0
                );
                return total < 10000000 || 'Total size must be less than 10MB';
              },
            },
          })}
        />
        {errors.documents && <span>{errors.documents.message}</span>}
      </div>

      <button type="submit">Upload</button>
    </form>
  );
};
```

**Verification:**
- [ ] File selection works
- [ ] Validation applies correctly
- [ ] Preview displays for images
- [ ] FormData constructed properly

---

### Step 6: Add Server-Side Validation Feedback

**What:** Display server validation errors in the form

**How:**

```typescript
// components/FormWithServerValidation.tsx
import React from 'react';
import { useForm } from 'react-hook-form';

interface FormData {
  username: string;
  email: string;
}

interface ApiError {
  field: string;
  message: string;
}

export const FormWithServerValidation: React.FC = () => {
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormData>();

  const onSubmit = async (data: FormData) => {
    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();

        // Handle validation errors from server
        if (errorData.errors) {
          errorData.errors.forEach((error: ApiError) => {
            setError(error.field as keyof FormData, {
              type: 'server',
              message: error.message,
            });
          });
          return;
        }

        throw new Error('Submission failed');
      }

      alert('Success!');
    } catch (error) {
      setError('root', {
        type: 'server',
        message: 'An unexpected error occurred',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {errors.root && (
        <div className="error-banner">{errors.root.message}</div>
      )}

      <div>
        <label>Username</label>
        <input {...register('username', { required: 'Username is required' })} />
        {errors.username && <span>{errors.username.message}</span>}
      </div>

      <div>
        <label>Email</label>
        <input {...register('email', { required: 'Email is required' })} />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        Submit
      </button>
    </form>
  );
};
```

**Verification:**
- [ ] Server errors display in form
- [ ] Field-specific errors show correctly
- [ ] General errors display at form level

---

### Step 7: Style and Enhance Form UX

**What:** Add visual feedback, accessibility, and polish

**How:**

```css
/* styles/forms.css */

.form-field {
  margin-bottom: 1.5rem;
}

.form-field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Error states */
.form-field input[aria-invalid="true"] {
  border-color: #ef4444;
}

.form-field input[aria-invalid="true"]:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #ef4444;
}

/* Success states */
.form-field input:valid:not(:placeholder-shown) {
  border-color: #10b981;
}

/* Loading states */
button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Required field indicator */
label::after {
  content: " *";
  color: #ef4444;
}

label.optional::after {
  content: " (optional)";
  color: #6b7280;
  font-weight: normal;
}
```

**Accessibility enhancements:**

```typescript
// components/AccessibleForm.tsx
<form onSubmit={handleSubmit(onSubmit)} noValidate>
  <div className="form-field">
    <label htmlFor="email">
      Email Address
      <span className="sr-only">required</span>
    </label>
    
    <input
      id="email"
      type="email"
      {...register('email')}
      aria-invalid={errors.email ? 'true' : 'false'}
      aria-describedby={errors.email ? 'email-error' : undefined}
      autoComplete="email"
    />
    
    {errors.email && (
      <span id="email-error" className="error-message" role="alert">
        {errors.email.message}
      </span>
    )}
  </div>

  {/* Screen reader announcements */}
  <div aria-live="polite" aria-atomic="true" className="sr-only">
    {Object.keys(errors).length > 0 &&
      `Form has ${Object.keys(errors).length} error(s)`}
  </div>

  <button
    type="submit"
    disabled={isSubmitting}
    aria-busy={isSubmitting}
  >
    {isSubmitting ? 'Submitting...' : 'Submit'}
  </button>
</form>
```

**Verification:**
- [ ] Form is keyboard navigable
- [ ] Error messages announced to screen readers
- [ ] Focus styles visible
- [ ] Required fields marked clearly
- [ ] Loading states indicated

---

## Verification Checklist

After completing form implementation:

- [ ] All fields validate correctly
- [ ] Error messages are clear and helpful
- [ ] Form submits data in correct format
- [ ] Loading states show during submission
- [ ] Success/error feedback provided
- [ ] Form is keyboard accessible
- [ ] Screen reader compatible
- [ ] Mobile responsive
- [ ] Password fields have show/hide toggle
- [ ] File uploads work with validation
- [ ] Multi-step forms navigate correctly
- [ ] Dynamic fields add/remove properly

---

## Common Issues & Solutions

### Issue: Form Not Submitting

**Symptoms:**
- handleSubmit doesn't fire
- Console shows no errors
- Button click does nothing

**Solution:**
```typescript
// Check: Is button inside form?
<form onSubmit={handleSubmit(onSubmit)}>
  <button type="submit">Submit</button> {/* ✅ Correct */}
</form>

// Not this:
<form>
  <button onClick={handleSubmit(onSubmit)}>Submit</button> {/* ❌ Wrong */}
</form>

// Check: Do you have validation errors?
console.log(errors); // Will show why form won't submit
```

---

### Issue: Validation Not Triggering

**Symptoms:**
- Errors don't show
- Form submits invalid data

**Solution:**
```typescript
// Set validation mode
const { ... } = useForm({
  mode: 'onBlur',     // Validate on blur
  // or
  mode: 'onChange',   // Validate on change
  // or
  mode: 'onSubmit',   // Validate only on submit (default)
});

// Manually trigger validation
const isValid = await trigger('fieldName');
```

---

### Issue: Controlled Input Warning

**Symptoms:**
- Warning: "component is changing an uncontrolled input to be controlled"

**Solution:**
```typescript
// Provide defaultValues
const { register } = useForm({
  defaultValues: {
    email: '',  // ✅ Correct
    // not
    email: undefined,  // ❌ Wrong
  },
});
```

---

## Best Practices

### DO:
✅ **Use React Hook Form** for better performance
✅ **Validate on blur** for better UX (not on every keystroke)
✅ **Show clear error messages** that explain how to fix
✅ **Disable submit during submission** to prevent double-submit
✅ **Use schema validation** (Zod/Yup) for reusable rules
✅ **Implement accessibility** (labels, ARIA, keyboard nav)
✅ **Provide visual feedback** for loading and success states
✅ **Auto-focus** first field or first error
✅ **Save form progress** for long forms
✅ **Test with real user data** including edge cases

### DON'T:
❌ **Don't validate on every keystroke** (annoying for users)
❌ **Don't use vague error messages** ("Invalid input")
❌ **Don't forget to sanitize** data before sending to API
❌ **Don't store sensitive data** in uncontrolled components
❌ **Don't skip accessibility** attributes
❌ **Don't allow submit** when form is invalid
❌ **Don't forget loading states** during async operations
❌ **Don't ignore server validation** errors
❌ **Don't make all fields required** without good reason
❌ **Don't use placeholder as label** replacement

---

## Related Workflows

**Prerequisites:**
- [React Component Creation](./react_component_creation.md) - Component basics
- [State Management Setup](./state_management_setup.md) - Managing form state

**Next Steps:**
- [API Integration Patterns](./api_integration_patterns.md) - Submit forms to API
- [Component Testing Strategy](./component_testing_strategy.md) - Test forms

**Related:**
- [Accessibility Workflow](./accessibility_workflow.md) - Accessible forms
- [E2E Testing Workflow](./e2e_testing_workflow.md) - Test form flows

---

## Tags
`forms` `validation` `react-hook-form` `zod` `yup` `typescript` `ux` `accessibility` `file-upload` `multi-step`
