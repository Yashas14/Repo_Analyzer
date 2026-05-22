import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FileText,
  Download,
  ArrowLeft,
  File,
  Code,
  Image,
  CheckCircle,
  Loader2,
  Eye,
} from 'lucide-react';
import { documentationApi, analysisApi } from '../services/api';
import useStore from '../store/useStore';
import LoadingSpinner from '../components/LoadingSpinner';
import ReactMarkdown from 'react-markdown';

function DocumentationPage() {
  const { repoId } = useParams();
  const { analysis, setAnalysis } = useStore();
  
  const [format, setFormat] = useState('pdf');
  const [includeCodeSnippets, setIncludeCodeSnippets] = useState(true);
  const [includeDiagrams, setIncludeDiagrams] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGenerated, setIsGenerated] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [preview, setPreview] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    loadAnalysis();
  }, [repoId]);

  const loadAnalysis = async () => {
    if (!analysis || analysis.repository_id !== repoId) {
      try {
        const result = await analysisApi.getResult(repoId);
        setAnalysis(result);
      } catch (err) {
        console.error('Failed to load analysis:', err);
      }
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setIsGenerated(false);
    
    try {
      const result = await documentationApi.generate(repoId, {
        format,
        includeCodeSnippets,
        includeDiagrams,
      });
      
      setDownloadUrl(documentationApi.getDownloadUrl(repoId, format));
      setIsGenerated(true);
    } catch (err) {
      console.error('Failed to generate documentation:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePreview = async () => {
    setPreviewLoading(true);
    setShowPreview(true);
    
    try {
      const result = await documentationApi.getMarkdown(repoId);
      setPreview(result.markdown);
    } catch (err) {
      console.error('Failed to load preview:', err);
      setPreview('Failed to load preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.open(downloadUrl, '_blank');
    }
  };

  const formatOptions = [
    { value: 'pdf', label: 'PDF Document', icon: FileText, description: 'Best for printing and sharing' },
    { value: 'markdown', label: 'Markdown', icon: Code, description: 'Ideal for GitHub/GitLab' },
    { value: 'html', label: 'HTML', icon: File, description: 'Web-ready documentation' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link
          to={`/analysis/${repoId}`}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Generate Documentation</h1>
          <p className="text-gray-600">
            {analysis?.repository_name || 'Repository'}
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Options Panel */}
        <div className="md:col-span-2 space-y-6">
          {/* Format Selection */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Output Format</h2>
            <div className="space-y-3">
              {formatOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <label
                    key={option.value}
                    className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                      format === option.value
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="format"
                      value={option.value}
                      checked={format === option.value}
                      onChange={(e) => setFormat(e.target.value)}
                      className="sr-only"
                    />
                    <div className={`p-2 rounded-lg mr-4 ${
                      format === option.value ? 'bg-primary-100' : 'bg-gray-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        format === option.value ? 'text-primary-600' : 'text-gray-500'
                      }`} />
                    </div>
                    <div className="flex-1">
                      <p className={`font-medium ${
                        format === option.value ? 'text-primary-700' : 'text-gray-900'
                      }`}>
                        {option.label}
                      </p>
                      <p className="text-sm text-gray-500">{option.description}</p>
                    </div>
                    {format === option.value && (
                      <CheckCircle className="w-5 h-5 text-primary-600" />
                    )}
                  </label>
                );
              })}
            </div>
          </div>

          {/* Options */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Options</h2>
            <div className="space-y-4">
              <label className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Include Code Snippets</p>
                  <p className="text-sm text-gray-500">Add relevant code examples</p>
                </div>
                <input
                  type="checkbox"
                  checked={includeCodeSnippets}
                  onChange={(e) => setIncludeCodeSnippets(e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </label>
              <label className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">Include Diagrams</p>
                  <p className="text-sm text-gray-500">Generate architecture diagrams</p>
                </div>
                <input
                  type="checkbox"
                  checked={includeDiagrams}
                  onChange={(e) => setIncludeDiagrams(e.target.checked)}
                  className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
              </label>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <button
              onClick={handleGenerate}
              disabled={isGenerating}
              className={`flex-1 flex items-center justify-center space-x-2 py-3 rounded-lg font-medium transition-colors ${
                isGenerating
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'
              }`}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <FileText className="w-5 h-5" />
                  <span>Generate Documentation</span>
                </>
              )}
            </button>
            <button
              onClick={handlePreview}
              className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Eye className="w-5 h-5" />
            </button>
          </div>

          {/* Success State */}
          {isGenerated && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div className="flex-1">
                  <p className="font-medium text-green-800">Documentation Generated!</p>
                  <p className="text-sm text-green-600">Your documentation is ready for download</p>
                </div>
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Info Panel */}
        <div className="space-y-6">
          {/* What's Included */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="font-semibold text-gray-900 mb-4">What's Included</h3>
            <ul className="space-y-3 text-sm text-gray-600">
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Project overview and summary</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Technology stack breakdown</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Architecture description</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Module documentation</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Functionality explanations</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>Dependencies list</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <span>File structure overview</span>
              </li>
            </ul>
          </div>

          {/* Project Stats */}
          {analysis && (
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Project Stats</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Total Files</span>
                  <span className="font-medium">{analysis.structure?.total_files || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Lines of Code</span>
                  <span className="font-medium">{analysis.structure?.total_lines?.toLocaleString() || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Modules</span>
                  <span className="font-medium">{analysis.modules?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Dependencies</span>
                  <span className="font-medium">{analysis.dependencies?.length || 0}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Documentation Preview</h3>
              <button
                onClick={() => setShowPreview(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                ✕
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)]">
              {previewLoading ? (
                <LoadingSpinner size="md" text="Loading preview..." />
              ) : (
                <div className="prose prose-sm max-w-none markdown-content">
                  <ReactMarkdown>{preview || 'No preview available'}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentationPage;
