# API Integration Patterns

**ID:** fro-002  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Medium  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive patterns and best practices for integrating frontend applications with backend APIs

**Why:** 
- Establish consistent API communication patterns
- Handle loading, error, and success states properly
- Implement caching and request optimization
- Ensure type safety with TypeScript
- Enable testing and mocking of API calls
- Improve user experience with proper state management

**When to use:**
- Connecting React app to REST or GraphQL APIs
- Implementing authentication and authorization
- Building data-driven applications
- Refactoring API calls for better maintainability
- Setting up new API integrations

---

## Prerequisites

**Required:**
- [ ] React project with TypeScript
- [ ] Backend API available (REST/GraphQL)
- [ ] Understanding of HTTP methods and status codes
- [ ] Knowledge of async/await and Promises
- [ ] State management solution (Context/Redux/Zustand)

**Check before starting:**
```bash
# Verify React and TypeScript
npm list react react-dom typescript

# Check if API client library is needed
npm list axios @tanstack/react-query

# Test API endpoint availability
curl -X GET https://api.example.com/health
```

---

## Implementation Steps

### Step 1: Setup API Client

**What:** Create a centralized API client with configuration for base URL, headers, and interceptors

**How:**

1. **Fetch API approach (native):**

```typescript
// api/client.ts
interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  private buildURL(endpoint: string, params?: Record<string, any>): string {
    const url = new URL(endpoint, this.baseURL);
    
    if (params) {
      Object.keys(params).forEach((key) =>
        url.searchParams.append(key, String(params[key]))
      );
    }
    
    return url.toString();
  }

  private async request<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<T> {
    const { params, ...fetchConfig } = config;
    
    // Get auth token from storage
    const token = localStorage.getItem('auth_token');
    
    const headers = {
      ...this.defaultHeaders,
      ...(token && { Authorization: `Bearer ${token}` }),
      ...config.headers,
    };

    const url = this.buildURL(endpoint, params);

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        headers,
      });

      // Handle HTTP errors
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new ApiError(
          response.status,
          error.message || response.statusText,
          error
        );
      }

      // Handle empty responses
      if (response.status === 204) {
        return null as T;
      }

      return response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(0, 'Network error', error);
    }
  }

  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch<T>(
    endpoint: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }
}

// Custom error class
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }

  isAuthError(): boolean {
    return this.status === 401 || this.status === 403;
  }

  isValidationError(): boolean {
    return this.status === 400 || this.status === 422;
  }

  isNotFoundError(): boolean {
    return this.status === 404;
  }

  isServerError(): boolean {
    return this.status >= 500;
  }
}

// Create and export client instance
export const apiClient = new ApiClient(
  process.env.REACT_APP_API_URL || 'https://api.example.com'
);
```

2. **Axios approach (recommended for complex needs):**

```typescript
// api/axiosClient.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';

class AxiosApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Log request in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Request:', config.method?.toUpperCase(), config.url);
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response in development
        if (process.env.NODE_ENV === 'development') {
          console.log('API Response:', response.status, response.config.url);
        }
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & {
          _retry?: boolean;
        };

        // Handle 401 - Refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            const response = await axios.post('/api/auth/refresh', {
              refresh_token: refreshToken,
            });

            const { access_token } = response.data;
            localStorage.setItem('auth_token', access_token);

            // Retry original request
            return this.client(originalRequest);
          } catch (refreshError) {
            // Redirect to login
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      return new ApiError(
        error.response.status,
        error.response.data?.message || error.message,
        error.response.data
      );
    } else if (error.request) {
      // Request made but no response
      return new ApiError(0, 'Network error - no response from server');
    } else {
      // Error in request setup
      return new ApiError(0, error.message);
    }
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async patch<T>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> {
    const response = await this.client.patch<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const axiosClient = new AxiosApiClient(
  process.env.REACT_APP_API_URL || 'https://api.example.com'
);
```

**Verification:**
- [ ] API client created and exported
- [ ] Base URL configured from environment variable
- [ ] Headers set correctly
- [ ] Interceptors working (test with console.log)

**If This Fails:**
→ Check environment variables are set
→ Verify API URL is accessible
→ Test with curl or Postman first

---

### Step 2: Define API Types and Interfaces

**What:** Create TypeScript types for API requests and responses

**How:**

```typescript
// types/api.ts

// Generic API response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

// Paginated response
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// Error response
export interface ErrorResponse {
  message: string;
  errors?: Record<string, string[]>;
  code?: string;
}

// types/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'admin' | 'user';
  createdAt: string;
  updatedAt: string;
}

export interface CreateUserDto {
  email: string;
  name: string;
  password: string;
}

export interface UpdateUserDto {
  email?: string;
  name?: string;
  avatar?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

// types/product.ts
export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  stock: number;
  images: string[];
  category: string;
  createdAt: string;
  updatedAt: string;
}

export interface ProductFilters {
  category?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
  inStock?: boolean;
}
```

**Verification:**
- [ ] All API entities have TypeScript interfaces
- [ ] Request DTOs defined
- [ ] Response types match API documentation
- [ ] Generic types used where appropriate

---

### Step 3: Create API Service Functions

**What:** Build typed service functions that encapsulate API calls

**How:**

```typescript
// services/userService.ts
import { apiClient } from '../api/client';
import {
  User,
  CreateUserDto,
  UpdateUserDto,
  PaginatedResponse,
} from '../types';

export class UserService {
  private readonly basePath = '/users';

  async getUsers(
    page: number = 1,
    limit: number = 10
  ): Promise<PaginatedResponse<User>> {
    return apiClient.get<PaginatedResponse<User>>(this.basePath, {
      params: { page, limit },
    });
  }

  async getUserById(userId: string): Promise<User> {
    return apiClient.get<User>(`${this.basePath}/${userId}`);
  }

  async createUser(data: CreateUserDto): Promise<User> {
    return apiClient.post<User>(this.basePath, data);
  }

  async updateUser(userId: string, data: UpdateUserDto): Promise<User> {
    return apiClient.patch<User>(`${this.basePath}/${userId}`, data);
  }

  async deleteUser(userId: string): Promise<void> {
    return apiClient.delete<void>(`${this.basePath}/${userId}`);
  }

  async uploadAvatar(userId: string, file: File): Promise<User> {
    const formData = new FormData();
    formData.append('avatar', file);

    return apiClient.post<User>(`${this.basePath}/${userId}/avatar`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
}

// Export singleton instance
export const userService = new UserService();

// services/authService.ts
import { apiClient } from '../api/client';
import { LoginRequest, LoginResponse, User } from '../types';

export class AuthService {
  private readonly basePath = '/auth';

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>(
      `${this.basePath}/login`,
      credentials
    );

    // Store tokens
    localStorage.setItem('auth_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);

    return response;
  }

  async logout(): Promise<void> {
    await apiClient.post<void>(`${this.basePath}/logout`);
    
    // Clear tokens
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>(`${this.basePath}/me`);
  }

  async refreshToken(): Promise<{ access_token: string }> {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await apiClient.post<{ access_token: string }>(
      `${this.basePath}/refresh`,
      { refresh_token: refreshToken }
    );

    localStorage.setItem('auth_token', response.access_token);
    return response;
  }

  async register(data: {
    email: string;
    name: string;
    password: string;
  }): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>(`${this.basePath}/register`, data);
  }

  async resetPassword(email: string): Promise<void> {
    return apiClient.post<void>(`${this.basePath}/reset-password`, { email });
  }
}

export const authService = new AuthService();

// services/productService.ts
import { apiClient } from '../api/client';
import { Product, ProductFilters, PaginatedResponse } from '../types';

export class ProductService {
  private readonly basePath = '/products';

  async getProducts(
    filters: ProductFilters = {},
    page: number = 1,
    limit: number = 20
  ): Promise<PaginatedResponse<Product>> {
    return apiClient.get<PaginatedResponse<Product>>(this.basePath, {
      params: {
        ...filters,
        page,
        limit,
      },
    });
  }

  async getProductById(productId: string): Promise<Product> {
    return apiClient.get<Product>(`${this.basePath}/${productId}`);
  }

  async searchProducts(query: string): Promise<Product[]> {
    return apiClient.get<Product[]>(`${this.basePath}/search`, {
      params: { q: query },
    });
  }

  async getFeaturedProducts(): Promise<Product[]> {
    return apiClient.get<Product[]>(`${this.basePath}/featured`);
  }
}

export const productService = new ProductService();
```

**Verification:**
- [ ] Service functions are typed
- [ ] Error handling in place
- [ ] Authentication handled automatically
- [ ] Can call services from components

**If This Fails:**
→ Check API client is properly configured
→ Verify types match API responses
→ Test with API documentation/Postman

---

### Step 4: Integrate with React Components (React Query Pattern)

**What:** Use React Query for optimal data fetching, caching, and synchronization

**How:**

```typescript
// hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../services/userService';
import { CreateUserDto, UpdateUserDto } from '../types';

// Query keys
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  list: (filters: any) => [...userKeys.lists(), filters] as const,
  details: () => [...userKeys.all, 'detail'] as const,
  detail: (id: string) => [...userKeys.details(), id] as const,
};

// Fetch users list
export const useUsers = (page: number = 1, limit: number = 10) => {
  return useQuery({
    queryKey: userKeys.list({ page, limit }),
    queryFn: () => userService.getUsers(page, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Fetch single user
export const useUser = (userId: string) => {
  return useQuery({
    queryKey: userKeys.detail(userId),
    queryFn: () => userService.getUserById(userId),
    enabled: !!userId, // Only fetch if userId exists
  });
};

// Create user mutation
export const useCreateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateUserDto) => userService.createUser(data),
    onSuccess: () => {
      // Invalidate and refetch users list
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Update user mutation
export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UpdateUserDto }) =>
      userService.updateUser(userId, data),
    onMutate: async ({ userId, data }) => {
      // Cancel outgoing queries
      await queryClient.cancelQueries({ queryKey: userKeys.detail(userId) });

      // Snapshot previous value
      const previousUser = queryClient.getQueryData(userKeys.detail(userId));

      // Optimistically update
      queryClient.setQueryData(userKeys.detail(userId), (old: any) => ({
        ...old,
        ...data,
      }));

      return { previousUser };
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousUser) {
        queryClient.setQueryData(
          userKeys.detail(variables.userId),
          context.previousUser
        );
      }
    },
    onSettled: (data, error, variables) => {
      // Refetch after mutation
      queryClient.invalidateQueries({ 
        queryKey: userKeys.detail(variables.userId) 
      });
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Delete user mutation
export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => userService.deleteUser(userId),
    onSuccess: (_, userId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: userKeys.detail(userId) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
};

// Upload avatar mutation
export const useUploadAvatar = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, file }: { userId: string; file: File }) =>
      userService.uploadAvatar(userId, file),
    onSuccess: (data, variables) => {
      // Update user cache
      queryClient.setQueryData(userKeys.detail(variables.userId), data);
    },
  });
};
```

**Using in components:**

```typescript
// components/UserList.tsx
import React from 'react';
import { useUsers, useDeleteUser } from '../hooks/useUsers';

export const UserList: React.FC = () => {
  const [page, setPage] = React.useState(1);
  
  const { data, isLoading, error, isFetching } = useUsers(page, 10);
  const deleteMutation = useDeleteUser();

  if (isLoading) {
    return <div>Loading users...</div>;
  }

  if (error) {
    return <div>Error loading users: {error.message}</div>;
  }

  const handleDelete = async (userId: string) => {
    if (window.confirm('Are you sure?')) {
      try {
        await deleteMutation.mutateAsync(userId);
        alert('User deleted successfully');
      } catch (err) {
        alert('Failed to delete user');
      }
    }
  };

  return (
    <div>
      <h2>Users {isFetching && '(Updating...)'}</h2>
      
      <ul>
        {data?.data.map((user) => (
          <li key={user.id}>
            {user.name} ({user.email})
            <button 
              onClick={() => handleDelete(user.id)}
              disabled={deleteMutation.isLoading}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>

      <div>
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        
        <span>
          Page {page} of {data?.pagination.totalPages}
        </span>
        
        <button
          onClick={() => setPage(p => p + 1)}
          disabled={page === data?.pagination.totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
};

// components/UserProfile.tsx
import React from 'react';
import { useUser, useUpdateUser, useUploadAvatar } from '../hooks/useUsers';

interface UserProfileProps {
  userId: string;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const { data: user, isLoading, error } = useUser(userId);
  const updateMutation = useUpdateUser();
  const uploadMutation = useUploadAvatar();
  
  const [name, setName] = React.useState('');

  React.useEffect(() => {
    if (user) {
      setName(user.name);
    }
  }, [user]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await updateMutation.mutateAsync({
        userId,
        data: { name },
      });
      alert('Profile updated successfully');
    } catch (err) {
      alert('Failed to update profile');
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      await uploadMutation.mutateAsync({ userId, file });
      alert('Avatar uploaded successfully');
    } catch (err) {
      alert('Failed to upload avatar');
    }
  };

  if (isLoading) return <div>Loading profile...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div>
      <h2>User Profile</h2>
      
      {user.avatar && <img src={user.avatar} alt={user.name} />}
      
      <div>
        <label>
          Upload Avatar:
          <input 
            type="file" 
            accept="image/*"
            onChange={handleAvatarUpload}
            disabled={uploadMutation.isLoading}
          />
        </label>
        {uploadMutation.isLoading && <span>Uploading...</span>}
      </div>

      <form onSubmit={handleUpdate}>
        <div>
          <label>
            Name:
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
        </div>
        
        <div>
          <label>
            Email:
            <input type="email" value={user.email} disabled />
          </label>
        </div>

        <button 
          type="submit"
          disabled={updateMutation.isLoading}
        >
          {updateMutation.isLoading ? 'Updating...' : 'Update Profile'}
        </button>
      </form>
    </div>
  );
};
```

**Verification:**
- [ ] Data fetches on component mount
- [ ] Loading states display correctly
- [ ] Errors handled gracefully
- [ ] Mutations update cache optimistically
- [ ] No unnecessary API calls (check Network tab)

---

### Step 5: Implement Error Handling and Loading States

**What:** Create reusable components and patterns for handling API states

**How:**

```typescript
// components/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    
    // Send to error tracking service (Sentry, etc.)
    // logErrorToService(error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// components/ApiStateHandler.tsx
import React from 'react';
import { UseQueryResult } from '@tanstack/react-query';
import { ApiError } from '../api/client';

interface ApiStateHandlerProps<T> {
  query: UseQueryResult<T>;
  loadingComponent?: React.ReactNode;
  errorComponent?: (error: Error) => React.ReactNode;
  children: (data: T) => React.ReactNode;
}

export function ApiStateHandler<T>({
  query,
  loadingComponent,
  errorComponent,
  children,
}: ApiStateHandlerProps<T>) {
  const { data, isLoading, error } = query;

  if (isLoading) {
    return <>{loadingComponent || <DefaultLoader />}</>;
  }

  if (error) {
    if (errorComponent) {
      return <>{errorComponent(error)}</>;
    }
    return <DefaultError error={error} />;
  }

  if (!data) {
    return <div>No data available</div>;
  }

  return <>{children(data)}</>;
}

// Default components
const DefaultLoader = () => (
  <div className="loader">
    <div className="spinner" />
    <p>Loading...</p>
  </div>
);

const DefaultError: React.FC<{ error: Error }> = ({ error }) => {
  const apiError = error as ApiError;

  return (
    <div className="error">
      <h3>Error</h3>
      <p>{error.message}</p>
      
      {apiError.isAuthError?.() && (
        <p>Please log in to continue.</p>
      )}
      
      {apiError.isServerError?.() && (
        <p>Server error. Please try again later.</p>
      )}
      
      <button onClick={() => window.location.reload()}>
        Try Again
      </button>
    </div>
  );
};

// Usage:
export const UserListWithHandler: React.FC = () => {
  const usersQuery = useUsers(1, 10);

  return (
    <ApiStateHandler
      query={usersQuery}
      loadingComponent={<div>Loading users...</div>}
      errorComponent={(error) => (
        <div>Failed to load users: {error.message}</div>
      )}
    >
      {(data) => (
        <ul>
          {data.data.map((user) => (
            <li key={user.id}>{user.name}</li>
          ))}
        </ul>
      )}
    </ApiStateHandler>
  );
};
```

**Verification:**
- [ ] Loading states show while fetching
- [ ] Errors display user-friendly messages
- [ ] Network errors handled gracefully
- [ ] Auth errors redirect to login

---

### Step 6: Add Request Caching and Deduplication

**What:** Optimize API calls by preventing duplicate requests and caching responses

**How:**

```typescript
// React Query handles most caching automatically, but here are advanced patterns:

// hooks/useOptimizedProducts.ts
import { useQueries, useQuery } from '@tanstack/react-query';
import { productService } from '../services/productService';

// Parallel queries with different cache times
export const useProductData = (productId: string) => {
  return useQueries({
    queries: [
      {
        queryKey: ['product', productId],
        queryFn: () => productService.getProductById(productId),
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
      {
        queryKey: ['product-reviews', productId],
        queryFn: () => productService.getProductReviews(productId),
        staleTime: 10 * 60 * 1000, // 10 minutes (reviews change less often)
      },
      {
        queryKey: ['product-related', productId],
        queryFn: () => productService.getRelatedProducts(productId),
        staleTime: 30 * 60 * 1000, // 30 minutes (related products rarely change)
      },
    ],
  });
};

// Prefetch data for better UX
export const usePrefetchProduct = () => {
  const queryClient = useQueryClient();

  return (productId: string) => {
    queryClient.prefetchQuery({
      queryKey: ['product', productId],
      queryFn: () => productService.getProductById(productId),
      staleTime: 5 * 60 * 1000,
    });
  };
};

// Usage: Prefetch on hover
const ProductCard = ({ productId }: { productId: string }) => {
  const prefetch = usePrefetchProduct();

  return (
    <div onMouseEnter={() => prefetch(productId)}>
      <Link to={`/products/${productId}`}>View Product</Link>
    </div>
  );
};

// Dependent queries (fetch B only after A completes)
export const useUserWithOrders = (userId: string) => {
  const userQuery = useQuery({
    queryKey: ['user', userId],
    queryFn: () => userService.getUserById(userId),
  });

  const ordersQuery = useQuery({
    queryKey: ['user-orders', userId],
    queryFn: () => orderService.getUserOrders(userId),
    enabled: !!userQuery.data, // Only fetch if user exists
  });

  return {
    user: userQuery.data,
    orders: ordersQuery.data,
    isLoading: userQuery.isLoading || ordersQuery.isLoading,
  };
};
```

**Verification:**
- [ ] Duplicate requests are deduped (check Network tab)
- [ ] Data served from cache when available
- [ ] Background refetching works
- [ ] Prefetching improves perceived performance

---

### Step 7: Test API Integration

**What:** Write tests for API service functions and React hooks

**How:**

```typescript
// __tests__/userService.test.ts
import { userService } from '../services/userService';
import { apiClient } from '../api/client';

jest.mock('../api/client');

describe('UserService', () => {
  afterEach(() => {
    jest.clearAllMocks();
  });

  it('fetches users', async () => {
    const mockUsers = {
      data: [{ id: '1', name: 'Test User', email: 'test@example.com' }],
      pagination: { page: 1, limit: 10, total: 1, totalPages: 1 },
    };

    (apiClient.get as jest.Mock).mockResolvedValue(mockUsers);

    const result = await userService.getUsers(1, 10);

    expect(apiClient.get).toHaveBeenCalledWith('/users', {
      params: { page: 1, limit: 10 },
    });
    expect(result).toEqual(mockUsers);
  });

  it('creates user', async () => {
    const newUser = { email: 'new@example.com', name: 'New User', password: 'pass123' };
    const createdUser = { id: '2', ...newUser };

    (apiClient.post as jest.Mock).mockResolvedValue(createdUser);

    const result = await userService.createUser(newUser);

    expect(apiClient.post).toHaveBeenCalledWith('/users', newUser);
    expect(result).toEqual(createdUser);
  });
});

// __tests__/useUsers.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useUsers } from '../hooks/useUsers';
import { userService } from '../services/userService';

jest.mock('../services/userService');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useUsers', () => {
  it('fetches users successfully', async () => {
    const mockData = {
      data: [{ id: '1', name: 'Test', email: 'test@example.com' }],
      pagination: { page: 1, limit: 10, total: 1, totalPages: 1 },
    };

    (userService.getUsers as jest.Mock).mockResolvedValue(mockData);

    const { result } = renderHook(() => useUsers(1, 10), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockData);
  });

  it('handles errors', async () => {
    const error = new Error('API Error');
    (userService.getUsers as jest.Mock).mockRejectedValue(error);

    const { result } = renderHook(() => useUsers(1, 10), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toEqual(error);
  });
});
```

**Verification:**
```bash
# Run tests
npm test

# With coverage
npm test -- --coverage

# Should have 80%+ coverage for API services
```

---

## Verification Checklist

After completing API integration:

- [ ] API client configured with base URL and headers
- [ ] All API endpoints have typed service functions
- [ ] React Query hooks created for data fetching
- [ ] Loading and error states handled in UI
- [ ] Authentication token management working
- [ ] Request/response interceptors functioning
- [ ] Caching and deduplication working
- [ ] Optimistic updates implemented for mutations
- [ ] Error boundary catches API errors
- [ ] Tests written and passing
- [ ] No unnecessary API calls in production

---

## Common Issues & Solutions

### Issue: CORS Errors

**Symptoms:**
- "Access-Control-Allow-Origin" error in console
- API calls fail with network error
- Works in Postman but not in browser

**Solution:**
```typescript
// Development: Use proxy in package.json (Create React App)
{
  "proxy": "http://localhost:3000"
}

// Or configure in vite.config.ts (Vite)
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});

// Production: Backend must set CORS headers
app.use(cors({
  origin: ['https://myapp.com'],
  credentials: true,
}));
```

---

### Issue: Token Expiration Not Handled

**Symptoms:**
- 401 errors after some time
- User suddenly logged out
- API calls fail after token expires

**Solution:**
Already covered in Step 1 with refresh token logic in Axios interceptor.

---

### Issue: Too Many API Calls

**Symptoms:**
- Network tab shows duplicate requests
- API rate limit exceeded
- Slow performance

**Solution:**
```typescript
// Use React Query's intelligent caching
const { data } = useQuery({
  queryKey: ['users', page],
  queryFn: () => fetchUsers(page),
  staleTime: 5 * 60 * 1000, // Don't refetch for 5 minutes
  cacheTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
  refetchOnWindowFocus: false, // Don't refetch on focus
  refetchOnMount: false, // Don't refetch on mount if data exists
});

// Debounce search queries
import { useDebouncedValue } from '@mantine/hooks';

const SearchComponent = () => {
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebouncedValue(search, 500);

  const { data } = useQuery({
    queryKey: ['search', debouncedSearch],
    queryFn: () => searchProducts(debouncedSearch),
    enabled: debouncedSearch.length > 0,
  });
};
```

---

## Best Practices

### DO:
✅ **Use TypeScript** for type-safe API calls
✅ **Centralize API configuration** in one client
✅ **Handle errors gracefully** with user-friendly messages
✅ **Use React Query** for server state management
✅ **Implement request/response interceptors** for common logic
✅ **Cache aggressively** to reduce API calls
✅ **Show loading states** for better UX
✅ **Implement optimistic updates** for better perceived performance
✅ **Test API integration** thoroughly
✅ **Log errors** to monitoring service (Sentry, etc.)

### DON'T:
❌ **Don't store API tokens in plain text**
❌ **Don't ignore HTTP status codes**
❌ **Don't make API calls on every render**
❌ **Don't forget to cancel requests** on component unmount
❌ **Don't put API logic in components** (use services)
❌ **Don't hardcode API URLs** (use environment variables)
❌ **Don't skip error handling**
❌ **Don't forget request timeout**
❌ **Don't log sensitive data** in production
❌ **Don't trust user input** before sending to API

---

## Related Workflows

**Prerequisites:**
- [State Management Setup](./state_management_setup.md) - State foundation
- [React Component Creation](./react_component_creation.md) - Component basics

**Next Steps:**
- [Form Handling Validation](./form_handling_validation.md) - Forms with API integration
- [Component Testing Strategy](./component_testing_strategy.md) - Test API calls

**Related:**
- [Performance Optimization](./performance_optimization.md) - Optimize API performance
- [Build Deployment](./build_deployment.md) - Deploy with API configuration

---

## Tags
`api` `rest` `graphql` `axios` `fetch` `react-query` `typescript` `http` `integration` `error-handling` `caching` `testing`
