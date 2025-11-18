import { create } from 'zustand'

export const useAuthStore = create((set) => {
  // Load from localStorage on init
  const storedAuth = localStorage.getItem('auth-storage')
  const initialState = storedAuth 
    ? JSON.parse(storedAuth) 
    : { user: null, isAuthenticated: false }

  return {
    ...initialState,
    
    login: (userData) => {
      const newState = { user: userData, isAuthenticated: true }
      set(newState)
      localStorage.setItem('auth-storage', JSON.stringify(newState))
    },
    
    logout: () => {
      const newState = { user: null, isAuthenticated: false }
      set(newState)
      localStorage.setItem('auth-storage', JSON.stringify(newState))
    },
    
    register: (userData) => {
      const newState = { user: userData, isAuthenticated: true }
      set(newState)
      localStorage.setItem('auth-storage', JSON.stringify(newState))
    },
  }
})
