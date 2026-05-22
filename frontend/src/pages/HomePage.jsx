import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  GitBranch, 
  Sparkles, 
  FileSearch, 
  MessageSquare, 
  FileText,
  ArrowRight,
  Code,
  Layers,
  Zap
} from 'lucide-react';
import FileUpload from '../components/FileUpload';
import GitClone from '../components/GitClone';
import { repositoryApi, analysisApi } from '../services/api';
import useStore from '../store/useStore';

function HomePage() {
  const [activeTab, setActiveTab] = useState('upload');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();
  const { setCurrentRepo, addRepository } = useStore();

  const handleUpload = async (file, onProgress) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await repositoryApi.uploadZip(file, onProgress);
      setSuccess(true);
      setCurrentRepo(result);
      addRepository(result);
      
      // Start analysis
      await analysisApi.analyze(result.repository_id);
      
      // Navigate to analysis page
      setTimeout(() => {
        navigate(`/analysis/${result.repository_id}`);
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload repository');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClone = async (url, branch) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await repositoryApi.cloneRepo(url, branch);
      setSuccess(true);
      setCurrentRepo(result);
      addRepository(result);
      
      // Start analysis
      await analysisApi.analyze(result.repository_id);
      
      // Navigate to analysis page
      setTimeout(() => {
        navigate(`/analysis/${result.repository_id}`);
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to clone repository');
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: FileSearch,
      title: 'Automated Analysis',
      description: 'Analyze complete repository structure, identify modules, and detect relationships',
    },
    {
      icon: Layers,
      title: 'Functionality Extraction',
      description: 'Automatically identify and map all functionalities to relevant files',
    },
    {
      icon: Sparkles,
      title: 'AI Explanations',
      description: 'Get detailed explanations of what, why, and how your project works',
    },
    {
      icon: MessageSquare,
      title: 'Interactive Q&A',
      description: 'Ask natural language questions about your repository',
    },
    {
      icon: FileText,
      title: 'Documentation Export',
      description: 'Generate comprehensive PDF documentation with one click',
    },
    {
      icon: Zap,
      title: 'Fast Processing',
      description: 'Quick analysis powered by advanced AI models',
    },
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center space-y-6 py-8">
        <div className="inline-flex items-center space-x-2 bg-primary-50 text-primary-700 px-4 py-2 rounded-full text-sm font-medium">
          <Sparkles className="w-4 h-4" />
          <span>AI-Powered Repository Analysis</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
          Understand Any Codebase
          <br />
          <span className="text-primary-600">In Minutes</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload your repository and let AI analyze, explain, and document your entire codebase.
          Perfect for onboarding, code reviews, and knowledge transfer.
        </p>
      </section>

      {/* Input Section */}
      <section className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 text-sm font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50/50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Upload className="w-5 h-5" />
              <span>Upload ZIP</span>
            </button>
            <button
              onClick={() => setActiveTab('clone')}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 text-sm font-medium transition-colors ${
                activeTab === 'clone'
                  ? 'text-primary-600 border-b-2 border-primary-600 bg-primary-50/50'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <GitBranch className="w-5 h-5" />
              <span>Clone Repository</span>
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'upload' ? (
              <FileUpload
                onUpload={handleUpload}
                isLoading={isLoading}
                error={error}
                success={success}
              />
            ) : (
              <GitClone
                onClone={handleClone}
                isLoading={isLoading}
                error={error}
                success={success}
              />
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
          Powerful Features for Code Understanding
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-white p-6 rounded-xl border border-gray-200 hover:border-primary-200 hover:shadow-md transition-all"
              >
                <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-8 bg-gradient-to-br from-primary-50 to-purple-50 rounded-2xl p-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { step: 1, title: 'Upload', description: 'Upload ZIP or clone from Git' },
            { step: 2, title: 'Analyze', description: 'AI analyzes the entire codebase' },
            { step: 3, title: 'Explore', description: 'Browse modules and ask questions' },
            { step: 4, title: 'Export', description: 'Download PDF documentation' },
          ].map((item, index) => (
            <div key={index} className="relative">
              <div className="bg-white p-6 rounded-xl text-center">
                <div className="w-10 h-10 bg-primary-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 font-bold">
                  {item.step}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.description}</p>
              </div>
              {index < 3 && (
                <ArrowRight className="hidden md:block absolute top-1/2 -right-3 transform -translate-y-1/2 w-6 h-6 text-primary-300" />
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-8">
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Perfect For</h2>
        <div className="flex flex-wrap justify-center gap-4">
          {[
            'New Developer Onboarding',
            'Code Reviews & Audits',
            'Knowledge Transfer',
            'Open Source Understanding',
            'Legacy System Documentation',
            'Technical Due Diligence',
          ].map((useCase, index) => (
            <div
              key={index}
              className="bg-white px-6 py-3 rounded-full border border-gray-200 text-gray-700 font-medium hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              {useCase}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default HomePage;
