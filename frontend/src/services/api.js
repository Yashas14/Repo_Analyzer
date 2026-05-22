import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Repository APIs
export const repositoryApi = {
  // Upload a ZIP file
  uploadZip: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/repository/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  },
  
  // Clone a Git repository
  cloneRepo: async (url, branch = 'main') => {
    const response = await api.post('/repository/clone', { url, branch });
    return response.data;
  },
  
  // Get repository structure
  getStructure: async (repoId) => {
    const response = await api.get(`/repository/${repoId}/structure`);
    return response.data;
  },
  
  // Get file content
  getFileContent: async (repoId, filePath) => {
    const response = await api.get(`/repository/${repoId}/file`, {
      params: { file_path: filePath },
    });
    return response.data;
  },
  
  // List all repositories
  listRepositories: async () => {
    const response = await api.get('/repository/list');
    return response.data;
  },
  
  // Delete a repository
  deleteRepository: async (repoId) => {
    const response = await api.delete(`/repository/${repoId}`);
    return response.data;
  },
};

// Analysis APIs
export const analysisApi = {
  // Start analysis
  analyze: async (repoId) => {
    const response = await api.post(`/analysis/${repoId}/analyze`);
    return response.data;
  },
  
  // Get analysis status
  getStatus: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/status`);
    return response.data;
  },
  
  // Get analysis result
  getResult: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/result`);
    return response.data;
  },
  
  // Get functionalities
  getFunctionalities: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/functionalities`);
    return response.data;
  },
  
  // Get modules
  getModules: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/modules`);
    return response.data;
  },
  
  // Get project explanation
  explain: async (repoId) => {
    const response = await api.post(`/analysis/${repoId}/explain`);
    return response.data;
  },
  
  // Get detailed functionality explanation (line-by-line)
  explainFunctionality: async (repoId, functionalityName, maxFiles = 5) => {
    const response = await api.post(`/analysis/${repoId}/explain-functionality`, null, {
      params: { functionality_name: functionalityName, max_files: maxFiles },
    });
    return response.data;
  },
  
  // Get detailed code block explanation (line-by-line)
  explainCode: async (repoId, filePath, startLine = 1, endLine = null) => {
    const params = { file_path: filePath, start_line: startLine };
    if (endLine) params.end_line = endLine;
    
    const response = await api.post(`/analysis/${repoId}/explain-code`, null, {
      params,
    });
    return response.data;
  },
  
  // Get architecture
  getArchitecture: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/architecture`);
    return response.data;
  },
  
  // Get tech stack
  getTechStack: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/tech-stack`);
    return response.data;
  },
  
  // Get dependencies
  getDependencies: async (repoId) => {
    const response = await api.get(`/analysis/${repoId}/dependencies`);
    return response.data;
  },
};

// Chat APIs
export const chatApi = {
  // Ask a question
  ask: async (repoId, message, conversationHistory = []) => {
    const response = await api.post(`/chat/${repoId}/ask`, {
      repository_id: repoId,
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  },
  
  // Get question suggestions
  getSuggestions: async (repoId) => {
    const response = await api.get(`/chat/${repoId}/suggestions`);
    return response.data;
  },
  
  // Explain a file
  explainFile: async (repoId, filePath) => {
    const response = await api.post(`/chat/${repoId}/explain-file`, null, {
      params: { file_path: filePath },
    });
    return response.data;
  },
  
  // Explain a module
  explainModule: async (repoId, moduleName) => {
    const response = await api.post(`/chat/${repoId}/explain-module`, null, {
      params: { module_name: moduleName },
    });
    return response.data;
  },
  
  // Find related files
  findRelatedFiles: async (repoId, query) => {
    const response = await api.post(`/chat/${repoId}/find-files`, null, {
      params: { query },
    });
    return response.data;
  },
};

// Documentation APIs
export const documentationApi = {
  // Generate documentation
  generate: async (repoId, options = {}) => {
    const response = await api.post(`/documentation/${repoId}/generate`, {
      repository_id: repoId,
      include_code_snippets: options.includeCodeSnippets ?? true,
      include_diagrams: options.includeDiagrams ?? true,
      format: options.format ?? 'pdf',
    });
    return response.data;
  },
  
  // Get download URL
  getDownloadUrl: (repoId, format = 'pdf') => {
    return `${API_BASE_URL}/documentation/${repoId}/download?format=${format}`;
  },
  
  // Get preview
  getPreview: async (repoId) => {
    const response = await api.get(`/documentation/${repoId}/preview`);
    return response.data;
  },
  
  // Get markdown documentation
  getMarkdown: async (repoId) => {
    const response = await api.get(`/documentation/${repoId}/markdown`);
    return response.data;
  },
};

export default api;
