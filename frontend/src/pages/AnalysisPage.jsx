import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Folder,
  File,
  Code,
  Layers,
  Package,
  GitBranch,
  MessageSquare,
  FileText,
  RefreshCw,
  ChevronRight,
  Sparkles,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Eye,
  BookOpen,
  Lightbulb,
  Zap,
  ArrowRight,
  Copy,
  Check,
} from 'lucide-react';
import { analysisApi, repositoryApi } from '../services/api';
import useStore from '../store/useStore';
import LoadingSpinner from '../components/LoadingSpinner';
import FileTree from '../components/FileTree';
import ReactMarkdown from 'react-markdown';

function AnalysisPage() {
  const { repoId } = useParams();
  const navigate = useNavigate();
  const { analysis, setAnalysis, analysisLoading, setAnalysisLoading, analysisError, setAnalysisError } = useStore();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [structure, setStructure] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [explanationLoading, setExplanationLoading] = useState(false);

  useEffect(() => {
    loadAnalysis();
    loadStructure();
  }, [repoId]);

  const loadAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const result = await analysisApi.getResult(repoId);
      setAnalysis(result);
    } catch (err) {
      // If analysis not found, try to run it
      if (err.response?.status === 404) {
        try {
          const result = await analysisApi.analyze(repoId);
          setAnalysis(result);
        } catch (analyzeErr) {
          setAnalysisError(analyzeErr.response?.data?.detail || 'Failed to analyze repository');
        }
      } else {
        setAnalysisError(err.response?.data?.detail || 'Failed to load analysis');
      }
    }
  };

  const loadStructure = async () => {
    try {
      const result = await repositoryApi.getStructure(repoId);
      setStructure(result);
    } catch (err) {
      console.error('Failed to load structure:', err);
    }
  };

  const loadExplanation = async () => {
    setExplanationLoading(true);
    try {
      const result = await analysisApi.explain(repoId);
      setExplanation(result);
    } catch (err) {
      console.error('Failed to load explanation:', err);
    } finally {
      setExplanationLoading(false);
    }
  };

  const refreshAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const result = await analysisApi.analyze(repoId);
      setAnalysis(result);
    } catch (err) {
      setAnalysisError(err.response?.data?.detail || 'Failed to refresh analysis');
    }
  };

  if (analysisLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Analyzing repository..." />
      </div>
    );
  }

  if (analysisError) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Analysis Error</h2>
        <p className="text-gray-600 mb-4">{analysisError}</p>
        <button
          onClick={refreshAnalysis}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" text="Loading analysis..." />
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Layers },
    { id: 'modules', name: 'Modules', icon: Folder },
    { id: 'functionalities', name: 'Functionalities', icon: Code },
    { id: 'dependencies', name: 'Dependencies', icon: Package },
    { id: 'structure', name: 'File Structure', icon: GitBranch },
    { id: 'explanation', name: 'AI Explanation', icon: Sparkles },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{analysis.repository_name}</h1>
          <p className="text-gray-600">Repository Analysis</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={refreshAnalysis}
            className="flex items-center space-x-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
          <Link
            to={`/chat/${repoId}`}
            className="flex items-center space-x-2 px-4 py-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Ask Questions</span>
          </Link>
          <Link
            to={`/documentation/${repoId}`}
            className="flex items-center space-x-2 px-4 py-2 text-primary-600 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <FileText className="w-4 h-4" />
            <span>Generate Docs</span>
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={File}
          label="Total Files"
          value={analysis.structure?.total_files || 0}
        />
        <StatCard
          icon={Code}
          label="Lines of Code"
          value={analysis.structure?.total_lines?.toLocaleString() || 0}
        />
        <StatCard
          icon={Folder}
          label="Modules"
          value={analysis.modules?.length || 0}
        />
        <StatCard
          icon={Package}
          label="Dependencies"
          value={analysis.dependencies?.length || 0}
        />
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-4 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  if (tab.id === 'explanation' && !explanation) {
                    loadExplanation();
                  }
                }}
                className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {activeTab === 'overview' && <OverviewTab analysis={analysis} />}
        {activeTab === 'modules' && <ModulesTab modules={analysis.modules} />}
        {activeTab === 'functionalities' && <FunctionalitiesTab functionalities={analysis.functionalities} />}
        {activeTab === 'dependencies' && <DependenciesTab dependencies={analysis.dependencies} />}
        {activeTab === 'structure' && <StructureTab structure={structure} repoId={repoId} />}
        {activeTab === 'explanation' && (
          <ExplanationTab 
            explanation={explanation} 
            loading={explanationLoading} 
            onLoad={loadExplanation} 
          />
        )}
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="bg-white p-4 rounded-lg border border-gray-200">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-primary-50 rounded-lg">
          <Icon className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <p className="text-sm text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ analysis }) {
  return (
    <div className="space-y-6">
      {/* Summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Summary</h3>
        <div className="prose prose-sm max-w-none text-gray-600">
          <ReactMarkdown>{analysis.summary || 'No summary available.'}</ReactMarkdown>
        </div>
      </div>

      {/* Tech Stack */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Technology Stack</h3>
        <div className="flex flex-wrap gap-2">
          {analysis.tech_stack?.length > 0 ? (
            analysis.tech_stack.map((tech, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
              >
                {tech}
              </span>
            ))
          ) : (
            <p className="text-gray-500">No technology stack detected</p>
          )}
        </div>
      </div>

      {/* Languages */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Languages</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(analysis.structure?.languages || {}).map(([lang, count]) => (
            <div key={lang} className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium text-gray-900">{lang}</p>
              <p className="text-sm text-gray-500">{count} files</p>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Architecture</h3>
        <div className="prose prose-sm max-w-none text-gray-600">
          <ReactMarkdown>{analysis.architecture || 'No architecture analysis available.'}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

function ModulesTab({ modules }) {
  if (!modules || modules.length === 0) {
    return <p className="text-gray-500">No modules identified</p>;
  }

  return (
    <div className="space-y-4">
      {modules.map((module, index) => (
        <div key={index} className="p-4 border border-gray-200 rounded-lg hover:border-primary-200 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-gray-900">{module.name}</h4>
              <p className="text-sm text-gray-500">{module.path}</p>
            </div>
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-sm rounded">
              {module.file_count || module.files?.length || 0} files
            </span>
          </div>
          {module.files && module.files.length > 0 && (
            <div className="mt-3">
              <p className="text-sm text-gray-600 mb-2">Key files:</p>
              <div className="flex flex-wrap gap-2">
                {module.files.slice(0, 5).map((file, i) => (
                  <code key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">
                    {file.split('/').pop()}
                  </code>
                ))}
                {module.files.length > 5 && (
                  <span className="text-xs text-gray-500">+{module.files.length - 5} more</span>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function FunctionalitiesTab({ functionalities }) {
  const { repoId } = useParams();
  const [expandedFunc, setExpandedFunc] = useState(null);
  const [detailedExplanation, setDetailedExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [copiedCode, setCopiedCode] = useState(null);

  const loadDetailedExplanation = async (funcName) => {
    if (expandedFunc === funcName && detailedExplanation) {
      setExpandedFunc(null);
      return;
    }
    
    setExpandedFunc(funcName);
    setLoadingExplanation(true);
    setDetailedExplanation(null);
    
    try {
      const result = await analysisApi.explainFunctionality(repoId, funcName);
      setDetailedExplanation(result);
    } catch (err) {
      console.error('Failed to load detailed explanation:', err);
      setDetailedExplanation({ 
        error: err.response?.data?.detail || 'Failed to load explanation' 
      });
    } finally {
      setLoadingExplanation(false);
    }
  };

  const copyCode = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  if (!functionalities || functionalities.length === 0) {
    return <p className="text-gray-500">No functionalities identified</p>;
  }

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start space-x-3">
          <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900">Line-by-Line Code Explanation</h4>
            <p className="text-sm text-blue-700 mt-1">
              Click on any functionality below to get a detailed, line-by-line explanation of the code.
              The AI will explain WHAT each line does, WHY it's written that way, and HOW it connects to other parts.
            </p>
          </div>
        </div>
      </div>

      {functionalities.map((func, index) => (
        <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
          {/* Functionality Header - Clickable */}
          <div 
            className={`p-4 cursor-pointer transition-colors ${
              expandedFunc === func.name 
                ? 'bg-primary-50 border-b border-primary-200' 
                : 'hover:bg-gray-50'
            }`}
            onClick={() => loadDetailedExplanation(func.name)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-gray-900">{func.name}</h4>
                  {expandedFunc === func.name ? (
                    <ChevronUp className="w-4 h-4 text-primary-600" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>
                <p className="text-gray-600 mt-1">{func.description}</p>
              </div>
              <button
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  expandedFunc === func.name
                    ? 'bg-primary-600 text-white'
                    : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
                }`}
              >
                <Eye className="w-4 h-4" />
                <span>{expandedFunc === func.name ? 'Hide' : 'Explain Code'}</span>
              </button>
            </div>
            
            {func.core_logic && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700">Core Logic:</p>
                <p className="text-sm text-gray-600">{func.core_logic}</p>
              </div>
            )}
            
            {func.files && func.files.length > 0 && (
              <div className="mt-3">
                <p className="text-sm font-medium text-gray-700 mb-1">Related files:</p>
                <div className="flex flex-wrap gap-2">
                  {func.files.map((file, i) => (
                    <code key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">
                      {file}
                    </code>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Detailed Explanation - Expandable */}
          {expandedFunc === func.name && (
            <div className="border-t border-gray-200">
              {loadingExplanation ? (
                <div className="p-8 flex items-center justify-center">
                  <LoadingSpinner size="md" text="Analyzing code line by line..." />
                </div>
              ) : detailedExplanation?.error ? (
                <div className="p-6 text-center">
                  <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                  <p className="text-red-600">{detailedExplanation.error}</p>
                </div>
              ) : detailedExplanation ? (
                <DetailedExplanationView 
                  explanation={detailedExplanation} 
                  copiedCode={copiedCode}
                  onCopyCode={copyCode}
                />
              ) : null}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function DetailedExplanationView({ explanation, copiedCode, onCopyCode }) {
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const exp = explanation.explanation || {};
  const filesAnalyzed = explanation.files_analyzed || [];
  const fileExplanations = exp.file_explanations || [];

  return (
    <div className="bg-gray-50">
      {/* Overview Section */}
      <div className="p-6 border-b border-gray-200 bg-white">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h5 className="font-semibold text-gray-900 flex items-center space-x-2 mb-2">
              <BookOpen className="w-4 h-4 text-primary-600" />
              <span>Overview</span>
            </h5>
            <p className="text-gray-600 text-sm">{exp.overview || 'No overview available'}</p>
          </div>
          <div>
            <h5 className="font-semibold text-gray-900 flex items-center space-x-2 mb-2">
              <Lightbulb className="w-4 h-4 text-yellow-600" />
              <span>Purpose</span>
            </h5>
            <p className="text-gray-600 text-sm">{exp.purpose || 'No purpose available'}</p>
          </div>
        </div>
        
        {exp.how_it_works && (
          <div className="mt-4">
            <h5 className="font-semibold text-gray-900 flex items-center space-x-2 mb-2">
              <Zap className="w-4 h-4 text-orange-600" />
              <span>How It Works</span>
            </h5>
            <p className="text-gray-600 text-sm">{exp.how_it_works}</p>
          </div>
        )}

        {exp.data_flow && (
          <div className="mt-4">
            <h5 className="font-semibold text-gray-900 flex items-center space-x-2 mb-2">
              <ArrowRight className="w-4 h-4 text-green-600" />
              <span>Data Flow</span>
            </h5>
            <p className="text-gray-600 text-sm">{exp.data_flow}</p>
          </div>
        )}
      </div>

      {/* File Tabs */}
      {fileExplanations.length > 0 && (
        <div className="border-b border-gray-200 bg-white">
          <div className="flex overflow-x-auto">
            {fileExplanations.map((file, idx) => (
              <button
                key={idx}
                onClick={() => setActiveFileIndex(idx)}
                className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeFileIndex === idx
                    ? 'border-primary-600 text-primary-600 bg-primary-50'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                <code>{file.file_path?.split('/').pop() || `File ${idx + 1}`}</code>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Active File Explanation */}
      {fileExplanations[activeFileIndex] && (
        <FileExplanationView 
          file={fileExplanations[activeFileIndex]} 
          copiedCode={copiedCode}
          onCopyCode={onCopyCode}
        />
      )}

      {/* Patterns & Best Practices */}
      <div className="p-6 bg-white border-t border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {exp.patterns_used && exp.patterns_used.length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-2">🎯 Design Patterns</h5>
              <ul className="space-y-1">
                {exp.patterns_used.map((pattern, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start space-x-2">
                    <span className="text-primary-500">•</span>
                    <span>{pattern}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {exp.best_practices && exp.best_practices.length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-2">✅ Best Practices</h5>
              <ul className="space-y-1">
                {exp.best_practices.map((practice, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start space-x-2">
                    <span className="text-green-500">•</span>
                    <span>{practice}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {exp.potential_improvements && exp.potential_improvements.length > 0 && (
            <div>
              <h5 className="font-semibold text-gray-900 mb-2">💡 Potential Improvements</h5>
              <ul className="space-y-1">
                {exp.potential_improvements.map((improvement, i) => (
                  <li key={i} className="text-sm text-gray-600 flex items-start space-x-2">
                    <span className="text-yellow-500">•</span>
                    <span>{improvement}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FileExplanationView({ file, copiedCode, onCopyCode }) {
  return (
    <div className="p-6">
      {/* File Header */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 text-sm text-gray-500 mb-1">
          <File className="w-4 h-4" />
          <code>{file.file_path}</code>
        </div>
        <p className="text-gray-700">{file.file_purpose}</p>
      </div>

      {/* Code Blocks with Explanations */}
      <div className="space-y-6">
        {file.code_blocks?.map((block, blockIdx) => (
          <div key={blockIdx} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            {/* Code Block Header */}
            <div className="flex items-center justify-between px-4 py-2 bg-gray-100 border-b border-gray-200">
              <span className="text-sm font-medium text-gray-600">
                Lines {block.lines}
              </span>
              <button
                onClick={() => onCopyCode(block.code, `${file.file_path}-${blockIdx}`)}
                className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700"
              >
                {copiedCode === `${file.file_path}-${blockIdx}` ? (
                  <>
                    <Check className="w-3 h-3 text-green-500" />
                    <span className="text-green-500">Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3 h-3" />
                    <span>Copy</span>
                  </>
                )}
              </button>
            </div>
            
            {/* Code */}
            <div className="bg-gray-900 p-4 overflow-x-auto">
              <pre className="text-sm text-gray-100 font-mono whitespace-pre-wrap">
                {block.code}
              </pre>
            </div>
            
            {/* Explanation */}
            <div className="p-4 space-y-3">
              <div>
                <h6 className="text-sm font-semibold text-gray-900 mb-1">📝 Explanation</h6>
                <p className="text-sm text-gray-600">{block.explanation}</p>
              </div>
              
              {block.why && (
                <div>
                  <h6 className="text-sm font-semibold text-gray-900 mb-1">🤔 Why This Approach?</h6>
                  <p className="text-sm text-gray-600">{block.why}</p>
                </div>
              )}
              
              {block.concepts && block.concepts.length > 0 && (
                <div>
                  <h6 className="text-sm font-semibold text-gray-900 mb-1">📚 Concepts Used</h6>
                  <div className="flex flex-wrap gap-2">
                    {block.concepts.map((concept, i) => (
                      <span key={i} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Key Takeaways */}
      {file.key_takeaways && file.key_takeaways.length > 0 && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <h6 className="font-semibold text-green-900 mb-2">🎓 Key Takeaways</h6>
          <ul className="space-y-1">
            {file.key_takeaways.map((takeaway, i) => (
              <li key={i} className="text-sm text-green-700 flex items-start space-x-2">
                <span>•</span>
                <span>{takeaway}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function DependenciesTab({ dependencies }) {
  if (!dependencies || dependencies.length === 0) {
    return <p className="text-gray-500">No dependencies detected</p>;
  }

  const grouped = dependencies.reduce((acc, dep) => {
    const type = dep.type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(dep);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([type, deps]) => (
        <div key={type}>
          <h4 className="font-semibold text-gray-900 capitalize mb-3">
            {type} Dependencies ({deps.length})
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 font-medium text-gray-600">Package</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-600">Version</th>
                </tr>
              </thead>
              <tbody>
                {deps.map((dep, index) => (
                  <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3 font-mono text-gray-900">{dep.name}</td>
                    <td className="py-2 px-3 text-gray-600">{dep.version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}

function StructureTab({ structure, repoId }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);
  const [codeExplanation, setCodeExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  const handleFileSelect = async (filePath) => {
    setSelectedFile(filePath);
    setLoadingContent(true);
    setCodeExplanation(null);
    setShowExplanation(false);
    try {
      const result = await repositoryApi.getFileContent(repoId, filePath);
      setFileContent(result.content);
    } catch (err) {
      setFileContent('Failed to load file content');
    } finally {
      setLoadingContent(false);
    }
  };

  const explainSelectedCode = async () => {
    if (!selectedFile || !fileContent) return;
    
    setLoadingExplanation(true);
    setShowExplanation(true);
    try {
      const result = await analysisApi.explainCode(repoId, selectedFile);
      setCodeExplanation(result);
    } catch (err) {
      console.error('Failed to explain code:', err);
      setCodeExplanation({ error: err.response?.data?.detail || 'Failed to explain code' });
    } finally {
      setLoadingExplanation(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <FileTree
          structure={structure?.structure}
          onFileSelect={handleFileSelect}
          selectedFile={selectedFile}
        />
      </div>
      <div>
        {selectedFile ? (
          <div className="space-y-4">
            <div className="bg-gray-900 rounded-lg overflow-hidden">
              <div className="px-4 py-2 bg-gray-800 text-gray-300 text-sm font-mono flex items-center justify-between">
                <span>{selectedFile}</span>
                {fileContent && !loadingContent && (
                  <button
                    onClick={explainSelectedCode}
                    disabled={loadingExplanation}
                    className="flex items-center space-x-1 px-3 py-1 bg-primary-600 text-white text-xs rounded hover:bg-primary-700 disabled:opacity-50 transition-colors"
                  >
                    <Sparkles className="w-3 h-3" />
                    <span>{loadingExplanation ? 'Analyzing...' : 'Explain Code'}</span>
                  </button>
                )}
              </div>
              <div className="p-4 overflow-auto max-h-96">
                {loadingContent ? (
                  <LoadingSpinner size="sm" text="Loading..." />
                ) : (
                  <pre className="text-gray-100 text-sm font-mono whitespace-pre-wrap">
                    {fileContent?.split('\n').map((line, i) => (
                      <div key={i} className="flex">
                        <span className="text-gray-500 w-10 flex-shrink-0 text-right pr-4 select-none">
                          {i + 1}
                        </span>
                        <span>{line}</span>
                      </div>
                    ))}
                  </pre>
                )}
              </div>
            </div>

            {/* Code Explanation */}
            {showExplanation && (
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="px-4 py-3 bg-primary-50 border-b border-primary-200 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-primary-600" />
                  <span className="font-medium text-primary-900">AI Code Explanation</span>
                </div>
                <div className="p-4">
                  {loadingExplanation ? (
                    <LoadingSpinner size="sm" text="Analyzing code line by line..." />
                  ) : codeExplanation?.error ? (
                    <div className="text-red-600 text-sm">{codeExplanation.error}</div>
                  ) : codeExplanation?.explanation ? (
                    <CodeExplanationView explanation={codeExplanation.explanation} />
                  ) : null}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500">
            Select a file to view its contents
          </div>
        )}
      </div>
    </div>
  );
}

function CodeExplanationView({ explanation }) {
  return (
    <div className="space-y-4">
      {/* Summary */}
      <div>
        <h5 className="font-medium text-gray-900 mb-1">Summary</h5>
        <p className="text-sm text-gray-600">{explanation.summary}</p>
      </div>

      {/* Overall Flow */}
      {explanation.overall_flow && (
        <div>
          <h5 className="font-medium text-gray-900 mb-1">Code Flow</h5>
          <p className="text-sm text-gray-600">{explanation.overall_flow}</p>
        </div>
      )}

      {/* Line by Line */}
      {explanation.line_explanations && explanation.line_explanations.length > 0 && (
        <div>
          <h5 className="font-medium text-gray-900 mb-2">Line-by-Line Explanation</h5>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {explanation.line_explanations.map((line, i) => (
              <div key={i} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-start space-x-3">
                  <span className="text-xs font-mono bg-gray-200 px-2 py-0.5 rounded text-gray-600">
                    L{line.line_number}
                  </span>
                  <div className="flex-1">
                    <code className="text-xs bg-gray-800 text-gray-100 px-2 py-1 rounded block mb-2">
                      {line.code}
                    </code>
                    <p className="text-sm text-gray-700"><strong>What:</strong> {line.what}</p>
                    {line.why && line.why !== 'AI provider needed' && (
                      <p className="text-sm text-gray-600 mt-1"><strong>Why:</strong> {line.why}</p>
                    )}
                    {line.concepts && line.concepts.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {line.concepts.map((concept, j) => (
                          <span key={j} className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                            {concept}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Key Concepts */}
      {explanation.key_concepts && explanation.key_concepts.length > 0 && (
        <div>
          <h5 className="font-medium text-gray-900 mb-2">Key Concepts</h5>
          <div className="flex flex-wrap gap-2">
            {explanation.key_concepts.map((concept, i) => (
              <span key={i} className="px-2 py-1 bg-primary-50 text-primary-700 text-sm rounded">
                {concept}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Common Pitfalls */}
      {explanation.common_pitfalls && explanation.common_pitfalls.length > 0 && (
        <div>
          <h5 className="font-medium text-gray-900 mb-2">⚠️ Watch Out For</h5>
          <ul className="space-y-1">
            {explanation.common_pitfalls.map((pitfall, i) => (
              <li key={i} className="text-sm text-gray-600 flex items-start space-x-2">
                <span className="text-yellow-500">•</span>
                <span>{pitfall}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function ExplanationTab({ explanation, loading, onLoad }) {
  if (loading) {
    return <LoadingSpinner size="md" text="Generating AI explanation..." />;
  }

  if (!explanation) {
    return (
      <div className="text-center py-8">
        <Sparkles className="w-12 h-12 text-primary-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Explanation</h3>
        <p className="text-gray-600 mb-4">
          Get a comprehensive AI-generated explanation of your project
        </p>
        <button
          onClick={onLoad}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Generate Explanation
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Section title="What does this project do?" content={explanation.what} />
      <Section title="Why was it developed?" content={explanation.why} />
      <Section title="How does it work?" content={explanation.how} />
      <Section title="Architecture" content={explanation.architecture} />
      <Section title="Workflow" content={explanation.workflow} />
      
      {explanation.functionalities && explanation.functionalities.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Functionalities Explained</h3>
          <div className="space-y-3">
            {explanation.functionalities.map((func, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium text-gray-900">{func.name}</h4>
                <p className="text-gray-600 text-sm mt-1">{func.explanation || func.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function Section({ title, content }) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <div className="prose prose-sm max-w-none text-gray-600">
        <ReactMarkdown>{content || 'Not available'}</ReactMarkdown>
      </div>
    </div>
  );
}

export default AnalysisPage;
