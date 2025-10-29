# State Management Setup

**ID:** fro-010  
**Category:** Frontend Development  
**Priority:** HIGH  
**Complexity:** Medium  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Comprehensive workflow for setting up and implementing state management in React applications using modern patterns and tools

**Why:** 
- Centralize application state for easier management
- Share state between components without prop drilling
- Enable predictable state updates and debugging
- Improve application performance with optimized re-renders
- Facilitate easier testing and maintainability

**When to use:**
- Starting a new React project that needs global state
- Refactoring from prop drilling to centralized state
- Adding complex state logic (authentication, shopping cart, etc.)
- Implementing features that need cross-component state sharing
- Migrating from older state management solutions

---

## Prerequisites

**Required:**
- [ ] React project initialized (v18+)
- [ ] Understanding of React hooks (useState, useEffect, useContext)
- [ ] Node.js and npm/yarn installed
- [ ] Understanding of component prop drilling problem

**Check before starting:**
```bash
# Verify React version
npm list react react-dom

# Check Node version
node --version  # Should be >= 18.x

# Verify package.json exists
cat package.json
```

---

## Implementation Steps

### Step 1: Choose State Management Solution

**What:** Select the appropriate state management tool based on your application's needs

**How:**

1. **Decision matrix for state management:**

```typescript
// Assessment questions:
interface StateManagementNeeds {
  // Complexity
  appSize: 'small' | 'medium' | 'large'; // < 10 components, 10-50, > 50
  stateComplexity: 'simple' | 'complex'; // Few pieces vs many interdependent pieces
  
  // Team
  teamSize: number;
  teamExperience: 'beginner' | 'intermediate' | 'advanced';
  
  // Requirements
  needsDevTools: boolean;
  needsTimeTravel: boolean; // Undo/redo functionality
  needsMiddleware: boolean; // Logging, async actions, etc.
  needsTypeScript: boolean;
  
  // Performance
  frequentUpdates: boolean;
  needsOptimization: boolean;
}

// Recommendations based on needs:
const recommendations = {
  // Small apps, simple state
  contextAPI: {
    when: 'appSize === "small" && stateComplexity === "simple"',
    pros: ['Built-in', 'Zero dependencies', 'Simple API'],
    cons: ['Performance issues with frequent updates', 'Verbose'],
  },
  
  // Medium apps, moderate complexity
  zustand: {
    when: 'appSize <= "medium" && !needsTimeTravel',
    pros: ['Minimal boilerplate', 'Good TypeScript support', 'Easy to learn'],
    cons: ['Smaller ecosystem than Redux'],
  },
  
  // Large apps, complex state
  redux: {
    when: 'appSize === "large" || needsDevTools || needsTimeTravel',
    pros: ['Mature ecosystem', 'Excellent dev tools', 'Middleware support'],
    cons: ['More boilerplate', 'Steeper learning curve'],
  },
  
  // Server state (API data)
  reactQuery: {
    when: 'Fetching/caching server data',
    pros: ['Automatic caching', 'Background refetching', 'Optimistic updates'],
    cons: ['Only for server state, not client state'],
  },
  
  // Simple to medium, modern
  jotai: {
    when: 'appSize <= "medium" && needsTypeScript',
    pros: ['Atomic approach', 'Excellent TypeScript', 'Minimal boilerplate'],
    cons: ['Newer, smaller community'],
  },
};
```

2. **Installation commands:**

```bash
# Context API - Built-in, no install needed

# Zustand
npm install zustand

# Redux Toolkit (modern Redux)
npm install @reduxjs/toolkit react-redux

# Jotai
npm install jotai

# React Query (TanStack Query)
npm install @tanstack/react-query

# Recoil
npm install recoil
```

**Verification:**
- [ ] State management library chosen based on app needs
- [ ] Library installed successfully
- [ ] No version conflicts with React

**If This Fails:**
→ Check npm registry access
→ Verify React version compatibility
→ Clear npm cache: `npm cache clean --force`

---

### Step 2: Setup Context API (Built-in Solution)

**What:** Implement Context API for simple, small-scale state management

**How:**

1. **Create a context with TypeScript:**

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// 1. Define state shape
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// 2. Define actions
interface AuthActions {
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
}

// 3. Combine state and actions
type AuthContextType = AuthState & AuthActions;

// 4. Create context with undefined default
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 5. Create provider component
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Actions using useCallback to prevent re-renders
  const login = useCallback(async (email: string, password: string) => {
    setState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // API call
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      
      const user = await response.json();
      
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      setState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }, []);

  const updateUser = useCallback((updates: Partial<User>) => {
    setState(prev => ({
      ...prev,
      user: prev.user ? { ...prev.user, ...updates } : null,
    }));
  }, []);

  const value: AuthContextType = {
    ...state,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// 6. Create custom hook for consuming context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
```

2. **Wrap app with provider:**

```typescript
// App.tsx
import React from 'react';
import { AuthProvider } from './contexts/AuthContext';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  );
}

export default App;
```

3. **Use the context in components:**

```typescript
// components/Dashboard.tsx
import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const Dashboard: React.FC = () => {
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
};
```

4. **Optimize Context API performance:**

```typescript
// contexts/OptimizedContext.tsx
import React, { createContext, useContext, useMemo, ReactNode } from 'react';

// Split state and actions into separate contexts to prevent unnecessary re-renders
const StateContext = createContext<AuthState | undefined>(undefined);
const ActionsContext = createContext<AuthActions | undefined>(undefined);

export const OptimizedAuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Memoize actions so they don't cause re-renders
  const actions = useMemo<AuthActions>(
    () => ({
      login: async (email, password) => {
        // ... implementation
      },
      logout: () => {
        // ... implementation
      },
      updateUser: (updates) => {
        // ... implementation
      },
    }),
    []
  );

  return (
    <ActionsContext.Provider value={actions}>
      <StateContext.Provider value={state}>{children}</StateContext.Provider>
    </ActionsContext.Provider>
  );
};

// Separate hooks for state and actions
export const useAuthState = () => {
  const context = useContext(StateContext);
  if (!context) throw new Error('useAuthState must be used within OptimizedAuthProvider');
  return context;
};

export const useAuthActions = () => {
  const context = useContext(ActionsContext);
  if (!context) throw new Error('useAuthActions must be used within OptimizedAuthProvider');
  return context;
};

// Usage:
// Components that only need actions won't re-render when state changes
const LogoutButton = () => {
  const { logout } = useAuthActions(); // Won't re-render on user changes
  return <button onClick={logout}>Logout</button>;
};

// Components that need state will re-render
const UserProfile = () => {
  const { user } = useAuthState(); // Re-renders when user changes
  return <div>{user?.name}</div>;
};
```

**Verification:**
- [ ] Context provides state to child components
- [ ] Custom hook works without errors
- [ ] Actions update state correctly
- [ ] No unnecessary re-renders

**If This Fails:**
→ Ensure provider wraps components that use context
→ Check that useContext is called within provider
→ Verify TypeScript types are correct

---

### Step 3: Setup Zustand (Recommended for Most Apps)

**What:** Configure Zustand for simple, performant state management

**How:**

1. **Create a Zustand store:**

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        user: null,
        isAuthenticated: false,
        isLoading: false,

        // Actions
        login: async (email, password) => {
          set({ isLoading: true });
          
          try {
            const response = await fetch('/api/auth/login', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email, password }),
            });
            
            const user = await response.json();
            
            set({
              user,
              isAuthenticated: true,
              isLoading: false,
            });
          } catch (error) {
            set({ isLoading: false });
            throw error;
          }
        },

        logout: () => {
          set({
            user: null,
            isAuthenticated: false,
          });
        },

        updateUser: (updates) => {
          const currentUser = get().user;
          if (currentUser) {
            set({ user: { ...currentUser, ...updates } });
          }
        },

        setLoading: (isLoading) => {
          set({ isLoading });
        },
      }),
      {
        name: 'auth-storage', // localStorage key
        partialize: (state) => ({
          // Only persist these fields
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    { name: 'AuthStore' } // DevTools name
  )
);
```

2. **Use Zustand in components:**

```typescript
// components/Dashboard.tsx
import React from 'react';
import { useAuthStore } from '../stores/authStore';

export const Dashboard: React.FC = () => {
  // Select only the state you need (prevents unnecessary re-renders)
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useAuthStore((state) => state.logout);

  // Or use shallow for multiple selections
  const { user, isAuthenticated, logout } = useAuthStore(
    (state) => ({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      logout: state.logout,
    }),
    shallow // From 'zustand/shallow'
  );

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <button onClick={logout}>Logout</button>
    </div>
  );
};
```

3. **Create slices for complex stores:**

```typescript
// stores/slices/cartSlice.ts
import { StateCreator } from 'zustand';

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
}

export interface CartSlice {
  items: CartItem[];
  total: number;
  
  addItem: (item: CartItem) => void;
  removeItem: (itemId: string) => void;
  updateQuantity: (itemId: string, quantity: number) => void;
  clearCart: () => void;
}

export const createCartSlice: StateCreator<CartSlice> = (set, get) => ({
  items: [],
  total: 0,

  addItem: (item) => {
    set((state) => {
      const existingItem = state.items.find((i) => i.id === item.id);
      
      if (existingItem) {
        return {
          items: state.items.map((i) =>
            i.id === item.id
              ? { ...i, quantity: i.quantity + item.quantity }
              : i
          ),
        };
      }
      
      return { items: [...state.items, item] };
    });
    
    // Update total
    const newTotal = get().items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
    set({ total: newTotal });
  },

  removeItem: (itemId) => {
    set((state) => ({
      items: state.items.filter((item) => item.id !== itemId),
    }));
    
    const newTotal = get().items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
    set({ total: newTotal });
  },

  updateQuantity: (itemId, quantity) => {
    set((state) => ({
      items: state.items.map((item) =>
        item.id === itemId ? { ...item, quantity } : item
      ),
    }));
    
    const newTotal = get().items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
    set({ total: newTotal });
  },

  clearCart: () => {
    set({ items: [], total: 0 });
  },
});

// stores/appStore.ts - Combine slices
import { create } from 'zustand';
import { CartSlice, createCartSlice } from './slices/cartSlice';
import { AuthSlice, createAuthSlice } from './slices/authSlice';

type AppStore = CartSlice & AuthSlice;

export const useAppStore = create<AppStore>()((...a) => ({
  ...createCartSlice(...a),
  ...createAuthSlice(...a),
}));
```

**Verification:**
- [ ] Store created successfully
- [ ] Components can read from store
- [ ] Actions update store correctly
- [ ] DevTools show state changes (in browser)
- [ ] Persistence works (refresh browser)

**If This Fails:**
→ Check Zustand is installed correctly
→ Verify middleware is applied in correct order
→ Check browser localStorage for persisted state

---

### Step 4: Setup Redux Toolkit (For Large Apps)

**What:** Configure Redux Toolkit for enterprise-scale state management

**How:**

1. **Create Redux slices:**

```typescript
// features/auth/authSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ email, password }: { email: string; password: string }) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return response.json();
  }
);

// Create slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      state.error = null;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login pending
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      // Login fulfilled
      .addCase(loginUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
        state.isLoading = false;
      })
      // Login rejected
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Login failed';
      });
  },
});

export const { logout, updateUser, clearError } = authSlice.actions;
export default authSlice.reducer;
```

2. **Configure store:**

```typescript
// store/store.ts
import { configureStore } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import authReducer from '../features/auth/authSlice';
import cartReducer from '../features/cart/cartSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cart: cartReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['your/action/type'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// TypeScript types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
```

3. **Provide store to app:**

```typescript
// App.tsx
import React from 'react';
import { Provider } from 'react-redux';
import { store } from './store/store';
import { Dashboard } from './components/Dashboard';

function App() {
  return (
    <Provider store={store}>
      <Dashboard />
    </Provider>
  );
}

export default App;
```

4. **Use Redux in components:**

```typescript
// components/Dashboard.tsx
import React, { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store/store';
import { loginUser, logout } from '../features/auth/authSlice';

export const Dashboard: React.FC = () => {
  const dispatch = useAppDispatch();
  
  // Select state
  const { user, isAuthenticated, isLoading, error } = useAppSelector(
    (state) => state.auth
  );

  const handleLogin = async () => {
    try {
      await dispatch(loginUser({ 
        email: 'user@example.com', 
        password: 'password' 
      })).unwrap();
      // Success
    } catch (err) {
      // Handle error
      console.error('Login failed:', err);
    }
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!isAuthenticated) {
    return (
      <div>
        <button onClick={handleLogin}>Login</button>
      </div>
    );
  }

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};
```

5. **Create selectors for derived state:**

```typescript
// features/auth/authSelectors.ts
import { createSelector } from '@reduxjs/toolkit';
import { RootState } from '../../store/store';

// Basic selectors
export const selectAuth = (state: RootState) => state.auth;
export const selectUser = (state: RootState) => state.auth.user;

// Memoized selectors (computed values)
export const selectIsAdmin = createSelector(
  [selectUser],
  (user) => user?.role === 'admin'
);

export const selectUserInitials = createSelector(
  [selectUser],
  (user) => {
    if (!user) return '';
    return user.name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  }
);

// Usage in components
const isAdmin = useAppSelector(selectIsAdmin);
const initials = useAppSelector(selectUserInitials);
```

**Verification:**
- [ ] Store configured with reducers
- [ ] Redux DevTools working
- [ ] Async actions dispatch correctly
- [ ] Selectors return correct data
- [ ] TypeScript types working

**If This Fails:**
→ Ensure Redux Toolkit is installed
→ Check Provider wraps app
→ Verify reducer is added to store
→ Check browser console for errors

---

### Step 5: Setup React Query (For Server State)

**What:** Configure React Query for API data fetching and caching

**How:**

1. **Setup QueryClient:**

```typescript
// App.tsx
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}

export default App;
```

2. **Create API functions:**

```typescript
// api/users.ts
interface User {
  id: string;
  name: string;
  email: string;
}

export const fetchUsers = async (): Promise<User[]> => {
  const response = await fetch('/api/users');
  if (!response.ok) {
    throw new Error('Failed to fetch users');
  }
  return response.json();
};

export const fetchUser = async (userId: string): Promise<User> => {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
};

export const createUser = async (user: Omit<User, 'id'>): Promise<User> => {
  const response = await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  });
  if (!response.ok) {
    throw new Error('Failed to create user');
  }
  return response.json();
};
```

3. **Use queries in components:**

```typescript
// components/UserList.tsx
import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchUsers, createUser } from '../api/users';

export const UserList: React.FC = () => {
  const queryClient = useQueryClient();

  // Fetch users
  const { 
    data: users, 
    isLoading, 
    error,
    refetch
  } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  // Create user mutation
  const createMutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h2>Users</h2>
      <ul>
        {users?.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
      
      <button 
        onClick={() => createMutation.mutate({ 
          name: 'New User', 
          email: 'new@example.com' 
        })}
        disabled={createMutation.isLoading}
      >
        Add User
      </button>
    </div>
  );
};
```

4. **Advanced patterns:**

```typescript
// Optimistic updates
const updateMutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newUser) => {
    // Cancel outgoing refetches
    await queryClient.cancelQueries({ queryKey: ['users', newUser.id] });

    // Snapshot previous value
    const previousUser = queryClient.getQueryData(['users', newUser.id]);

    // Optimistically update
    queryClient.setQueryData(['users', newUser.id], newUser);

    // Return context with snapshot
    return { previousUser };
  },
  onError: (err, newUser, context) => {
    // Rollback on error
    queryClient.setQueryData(
      ['users', newUser.id],
      context?.previousUser
    );
  },
  onSettled: (data, error, variables) => {
    // Always refetch after error or success
    queryClient.invalidateQueries({ queryKey: ['users', variables.id] });
  },
});

// Dependent queries
const { data: user } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});

const { data: posts } = useQuery({
  queryKey: ['posts', user?.id],
  queryFn: () => fetchUserPosts(user!.id),
  enabled: !!user, // Only run when user exists
});

// Infinite queries (pagination)
const {
  data,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage,
} = useInfiniteQuery({
  queryKey: ['users'],
  queryFn: ({ pageParam = 1 }) => fetchUsers(pageParam),
  getNextPageParam: (lastPage, pages) => lastPage.nextPage,
});
```

**Verification:**
- [ ] React Query provider wraps app
- [ ] Queries fetch data successfully
- [ ] Mutations update data
- [ ] Caching works (network tab)
- [ ] DevTools show queries

**If This Fails:**
→ Check network requests in DevTools
→ Verify API endpoints are correct
→ Ensure QueryClient is provided
→ Check query keys are unique

---

### Step 6: Test State Management

**What:** Write tests to verify state management works correctly

**How:**

```typescript
// __tests__/authStore.test.ts (Zustand)
import { renderHook, act } from '@testing-library/react';
import { useAuthStore } from '../stores/authStore';

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset store before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('initializes with default state', () => {
    const { result } = renderHook(() => useAuthStore());
    
    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });

  it('logs in user', async () => {
    const { result } = renderHook(() => useAuthStore());
    
    await act(async () => {
      await result.current.login('user@example.com', 'password');
    });
    
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user).not.toBeNull();
  });

  it('logs out user', () => {
    const { result } = renderHook(() => useAuthStore());
    
    act(() => {
      useAuthStore.setState({
        user: { id: '1', name: 'Test', email: 'test@example.com', role: 'user' },
        isAuthenticated: true,
      });
    });
    
    act(() => {
      result.current.logout();
    });
    
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.user).toBeNull();
  });
});

// __tests__/authSlice.test.ts (Redux)
import authReducer, { logout, updateUser } from '../features/auth/authSlice';

describe('Auth Slice', () => {
  const initialState = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  };

  it('returns initial state', () => {
    expect(authReducer(undefined, { type: 'unknown' })).toEqual(initialState);
  });

  it('handles logout', () => {
    const previousState = {
      user: { id: '1', name: 'Test', email: 'test@example.com', role: 'user' as const },
      isAuthenticated: true,
      isLoading: false,
      error: null,
    };
    
    expect(authReducer(previousState, logout())).toEqual(initialState);
  });

  it('handles updateUser', () => {
    const previousState = {
      user: { id: '1', name: 'Old Name', email: 'old@example.com', role: 'user' as const },
      isAuthenticated: true,
      isLoading: false,
      error: null,
    };
    
    const result = authReducer(previousState, updateUser({ name: 'New Name' }));
    
    expect(result.user?.name).toBe('New Name');
    expect(result.user?.email).toBe('old@example.com'); // Unchanged
  });
});
```

**Verification:**
```bash
# Run tests
npm test

# With coverage
npm test -- --coverage

# Should see 90%+ coverage for state logic
```

---

## Verification Checklist

After completing state management setup:

- [ ] State management solution chosen and installed
- [ ] Store/context created with proper TypeScript types
- [ ] Components can read from store
- [ ] Actions/mutations update state correctly
- [ ] No unnecessary re-renders (check with React DevTools Profiler)
- [ ] DevTools working (Redux/Zustand/React Query)
- [ ] Persistence working if enabled
- [ ] Tests written and passing
- [ ] No memory leaks
- [ ] Performance is acceptable

---

## Common Issues & Solutions

### Issue: Components Re-render Too Often

**Symptoms:**
- Performance degradation
- Components flashing on every state change
- High CPU usage in DevTools Profiler

**Solution:**
```typescript
// ❌ Bad: Selecting entire state causes re-renders on any change
const state = useAuthStore();

// ✅ Good: Select only what you need
const user = useAuthStore((state) => state.user);
const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

// ✅ Good: Use shallow for multiple selections
import { shallow } from 'zustand/shallow';

const { user, isAuthenticated } = useAuthStore(
  (state) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
  }),
  shallow
);

// For Redux: Use reselect for memoized selectors
import { createSelector } from '@reduxjs/toolkit';

const selectUserData = createSelector(
  [(state) => state.auth.user],
  (user) => ({
    name: user?.name,
    email: user?.email,
  })
);
```

---

### Issue: State Not Persisting

**Symptoms:**
- State resets on page refresh
- localStorage not saving data

**Solution:**
```typescript
// Zustand with persist middleware
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export const useStore = create(
  persist(
    (set) => ({
      // ... state
    }),
    {
      name: 'app-storage', // unique name
      storage: createJSONStorage(() => localStorage), // or sessionStorage
      partialize: (state) => ({ 
        // Only persist these fields
        user: state.user,
      }),
    }
  )
);

// Redux with redux-persist
import { persistStore, persistReducer } from 'redux-persist';
import storage from 'redux-persist/lib/storage';

const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth'], // Only persist auth reducer
};

const persistedReducer = persistReducer(persistConfig, rootReducer);
```

---

### Issue: TypeScript Errors with State Types

**Symptoms:**
- "Type 'undefined' is not assignable to type..."
- Difficulty typing selectors

**Solution:**
```typescript
// Define types explicitly
interface RootState {
  auth: AuthState;
  cart: CartState;
}

// Typed hooks
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// For Zustand, export types
export type AuthStore = ReturnType<typeof useAuthStore.getState>;

// Use satisfies for type safety
const initialState = {
  user: null,
  isAuthenticated: false,
} satisfies AuthState;
```

---

## Best Practices

### DO:
✅ **Choose the right tool** for your app size and complexity
✅ **Keep state minimal** - only store what needs to be shared
✅ **Colocate state** - keep it close to where it's used
✅ **Use TypeScript** for type-safe state management
✅ **Memoize selectors** to prevent unnecessary re-renders
✅ **Split contexts** for frequently updated values
✅ **Test state logic** independently from components
✅ **Use DevTools** to debug state changes
✅ **Document state shape** with interfaces/types
✅ **Handle loading and error states** consistently

### DON'T:
❌ **Don't over-globalize** - not everything needs global state
❌ **Don't store derived data** - compute it with selectors
❌ **Don't mutate state** directly (except in Immer-based solutions)
❌ **Don't forget to clean up** subscriptions and listeners
❌ **Don't use Context for frequently changing values** (unless optimized)
❌ **Don't store server data in client state** (use React Query)
❌ **Don't create circular dependencies** between stores
❌ **Don't ignore performance** - profile and optimize
❌ **Don't skip error handling** in async actions
❌ **Don't use different patterns** inconsistently in same project

---

## Related Workflows

**Prerequisites:**
- [React Component Creation](./react_component_creation.md) - Create components first
- [Project Setup](../development/new_repo_scaffolding.md) - Initialize React project

**Next Steps:**
- [API Integration Patterns](./api_integration_patterns.md) - Connect state to APIs
- [Form Handling Validation](./form_handling_validation.md) - Forms with state
- [Component Testing Strategy](./component_testing_strategy.md) - Test stateful components

**Related:**
- [Performance Optimization](./performance_optimization.md) - Optimize state updates
- [Build Deployment](./build_deployment.md) - Deploy apps with state management

---

## Tags
`react` `state-management` `zustand` `redux` `context-api` `react-query` `typescript` `hooks` `performance` `testing`
