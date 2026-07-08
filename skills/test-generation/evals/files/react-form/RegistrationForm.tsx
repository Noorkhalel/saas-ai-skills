import React, { useState, useCallback, useEffect } from 'react';

/**
 * Registration form with async username availability check.
 *
 * Features:
 * - Real-time username availability check (debounced 500ms)
 * - Email format validation
 * - Password strength requirements (min 8 chars, 1 uppercase, 1 number)
 * - Password confirmation matching
 * - Form-level and field-level validation
 * - Loading states during availability check and submission
 * - Error states for API failures
 */

interface RegistrationFormProps {
  onSubmit: (data: RegistrationData) => Promise<void>;
  checkUsername: (username: string) => Promise<boolean>; // true = available
}

interface RegistrationData {
  username: string;
  email: string;
  password: string;
}

interface FieldErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export function RegistrationForm({ onSubmit, checkUsername }: RegistrationFormProps) {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const [errors, setErrors] = useState<FieldErrors>({});
  const [usernameStatus, setUsernameStatus] = useState<'idle' | 'checking' | 'available' | 'taken'>('idle');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Debounced username availability check
  useEffect(() => {
    if (username.length < 3) {
      setUsernameStatus('idle');
      return;
    }

    setUsernameStatus('checking');
    const timer = setTimeout(async () => {
      try {
        const available = await checkUsername(username);
        setUsernameStatus(available ? 'available' : 'taken');
      } catch {
        setUsernameStatus('idle');
        setErrors(prev => ({ ...prev, username: 'Could not check availability' }));
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [username, checkUsername]);

  const validateField = useCallback((field: string, value: string): string | undefined => {
    switch (field) {
      case 'username':
        if (!value) return 'Username is required';
        if (value.length < 3) return 'Username must be at least 3 characters';
        if (value.length > 30) return 'Username must be 30 characters or less';
        if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Username can only contain letters, numbers, hyphens, and underscores';
        return undefined;

      case 'email':
        if (!value) return 'Email is required';
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Please enter a valid email address';
        return undefined;

      case 'password':
        if (!value) return 'Password is required';
        if (value.length < 8) return 'Password must be at least 8 characters';
        if (!/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter';
        if (!/\d/.test(value)) return 'Password must contain at least one number';
        return undefined;

      case 'confirmPassword':
        if (!value) return 'Please confirm your password';
        if (value !== password) return 'Passwords do not match';
        return undefined;

      default:
        return undefined;
    }
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);

    // Validate all fields
    const newErrors: FieldErrors = {
      username: validateField('username', username),
      email: validateField('email', email),
      password: validateField('password', password),
      confirmPassword: validateField('confirmPassword', confirmPassword),
    };

    // Check username availability
    if (usernameStatus === 'taken') {
      newErrors.username = 'This username is already taken';
    }

    setErrors(newErrors);

    const hasErrors = Object.values(newErrors).some(e => e !== undefined);
    if (hasErrors) return;

    setIsSubmitting(true);
    try {
      await onSubmit({ username, email, password });
      setSubmitSuccess(true);
    } catch (err: any) {
      setSubmitError(err.message || 'Registration failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <div role="status">
        <h2>Registration Successful!</h2>
        <p>Welcome, {username}! Please check your email to verify your account.</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} aria-label="Registration form">
      <h1>Create Account</h1>

      {submitError && (
        <div role="alert" aria-live="polite">
          {submitError}
        </div>
      )}

      <div>
        <label htmlFor="username">Username</label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={e => setUsername(e.target.value)}
          onBlur={() => setErrors(prev => ({ ...prev, username: validateField('username', username) }))}
          aria-describedby={errors.username ? 'username-error' : undefined}
          aria-invalid={!!errors.username}
        />
        {usernameStatus === 'checking' && <span aria-live="polite">Checking availability...</span>}
        {usernameStatus === 'available' && <span aria-live="polite">Username is available</span>}
        {usernameStatus === 'taken' && <span aria-live="polite">Username is already taken</span>}
        {errors.username && <span id="username-error" role="alert">{errors.username}</span>}
      </div>

      <div>
        <label htmlFor="email">Email address</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          onBlur={() => setErrors(prev => ({ ...prev, email: validateField('email', email) }))}
          aria-describedby={errors.email ? 'email-error' : undefined}
          aria-invalid={!!errors.email}
        />
        {errors.email && <span id="email-error" role="alert">{errors.email}</span>}
      </div>

      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          onBlur={() => setErrors(prev => ({ ...prev, password: validateField('password', password) }))}
          aria-describedby={errors.password ? 'password-error' : undefined}
          aria-invalid={!!errors.password}
        />
        {errors.password && <span id="password-error" role="alert">{errors.password}</span>}
      </div>

      <div>
        <label htmlFor="confirm-password">Confirm password</label>
        <input
          id="confirm-password"
          type="password"
          value={confirmPassword}
          onChange={e => setConfirmPassword(e.target.value)}
          onBlur={() => setErrors(prev => ({ ...prev, confirmPassword: validateField('confirmPassword', confirmPassword) }))}
          aria-describedby={errors.confirmPassword ? 'confirm-password-error' : undefined}
          aria-invalid={!!errors.confirmPassword}
        />
        {errors.confirmPassword && <span id="confirm-password-error" role="alert">{errors.confirmPassword}</span>}
      </div>

      <button type="submit" disabled={isSubmitting || usernameStatus === 'checking'}>
        {isSubmitting ? 'Creating account...' : 'Create Account'}
      </button>
    </form>
  );
}
