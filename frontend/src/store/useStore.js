import { create } from 'zustand';

const useStore = create((set, get) => ({
  // Current repository state
  currentRepo: null,
  setCurrentRepo: (repo) => set({ currentRepo: repo }),
  
  // Analysis state
  analysis: null,
  analysisLoading: false,
  analysisError: null,
  setAnalysis: (analysis) => set({ analysis, analysisLoading: false, analysisError: null }),
  setAnalysisLoading: (loading) => set({ analysisLoading: loading }),
  setAnalysisError: (error) => set({ analysisError: error, analysisLoading: false }),
  
  // Chat state
  chatMessages: [],
  addChatMessage: (message) => set((state) => ({
    chatMessages: [...state.chatMessages, message]
  })),
  clearChatMessages: () => set({ chatMessages: [] }),
  
  // Repositories list
  repositories: [],
  setRepositories: (repos) => set({ repositories: repos }),
  addRepository: (repo) => set((state) => ({
    repositories: [...state.repositories, repo]
  })),
  removeRepository: (repoId) => set((state) => ({
    repositories: state.repositories.filter(r => r.id !== repoId)
  })),
  
  // UI state
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  
  // Reset state
  reset: () => set({
    currentRepo: null,
    analysis: null,
    analysisLoading: false,
    analysisError: null,
    chatMessages: [],
  }),
}));

export default useStore;
