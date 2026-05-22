import { useState } from 'react';
import { GitBranch, Globe, Loader2, AlertCircle, CheckCircle, Key, Link } from 'lucide-react';

function GitClone({ onClone, isLoading, error, success }) {
  const [url, setUrl] = useState('');
  const [branch, setBranch] = useState('main');
  const [urlType, setUrlType] = useState(null); // 'ssh' | 'https' | null

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (url && onClone) {
      await onClone(url, branch);
    }
  };

  // Detect URL type and validate
  const detectUrlType = (urlString) => {
    if (!urlString) return null;
    urlString = urlString.trim();
    
    // SSH format: git@github.com:user/repo.git
    if (urlString.startsWith('git@') && urlString.includes(':')) {
      return 'ssh';
    }
    
    // HTTPS format: https://github.com/user/repo.git
    if (urlString.startsWith('http://') || urlString.startsWith('https://')) {
      return 'https';
    }
    
    return null;
  };

  const isValidUrl = (urlString) => {
    if (!urlString) return false;
    urlString = urlString.trim();
    
    // Check for Git URL patterns - supports both SSH and HTTPS
    const gitPatterns = [
      // HTTPS patterns
      /^https?:\/\/.*\.git$/,
      /^https?:\/\/github\.com\/.+\/.+/,
      /^https?:\/\/gitlab\.com\/.+\/.+/,
      /^https?:\/\/bitbucket\.org\/.+\/.+/,
      // SSH patterns
      /^git@[\w.-]+:[\w.-]+\/[\w.-]+(\.git)?$/,
      /^git@github\.com:[\w.-]+\/[\w.-]+(\.git)?$/,
      /^git@gitlab\.com:[\w.-]+\/[\w.-]+(\.git)?$/,
      /^git@bitbucket\.org:[\w.-]+\/[\w.-]+(\.git)?$/,
    ];
    
    return gitPatterns.some((pattern) => pattern.test(urlString));
  };

  const handleUrlChange = (e) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    setUrlType(detectUrlType(newUrl));
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* URL Input */}
        <div>
          <label htmlFor="repoUrl" className="block text-sm font-medium text-gray-700 mb-2">
            Repository URL
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              {urlType === 'ssh' ? (
                <Key className="h-5 w-5 text-orange-500" />
              ) : urlType === 'https' ? (
                <Link className="h-5 w-5 text-green-500" />
              ) : (
                <Globe className="h-5 w-5 text-gray-400" />
              )}
            </div>
            <input
              type="text"
              id="repoUrl"
              value={url}
              onChange={handleUrlChange}
              placeholder="https://github.com/username/repository.git"
              className={`block w-full pl-10 pr-3 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors ${
                url && !isValidUrl(url) 
                  ? 'border-red-300 bg-red-50' 
                  : url && isValidUrl(url)
                    ? 'border-green-300 bg-green-50'
                    : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {urlType && (
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                <span className={`text-xs font-medium px-2 py-1 rounded ${
                  urlType === 'ssh' 
                    ? 'bg-orange-100 text-orange-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {urlType.toUpperCase()}
                </span>
              </div>
            )}
          </div>
          
          {/* URL Format Help */}
          <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Supported URL formats:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
              <div className="flex items-center space-x-2">
                <Link className="w-4 h-4 text-green-600" />
                <code className="bg-green-50 text-green-700 px-2 py-1 rounded">https://github.com/user/repo.git</code>
              </div>
              <div className="flex items-center space-x-2">
                <Key className="w-4 h-4 text-orange-600" />
                <code className="bg-orange-50 text-orange-700 px-2 py-1 rounded">git@github.com:user/repo.git</code>
              </div>
            </div>
          </div>
        </div>

        {/* Branch Input */}
        <div>
          <label htmlFor="branch" className="block text-sm font-medium text-gray-700 mb-2">
            Branch (optional)
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <GitBranch className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              id="branch"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              placeholder="main"
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!url || isLoading}
          className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
            !url || isLoading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700'
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Cloning repository...</span>
            </>
          ) : (
            <>
              <GitBranch className="w-5 h-5" />
              <span>Clone & Analyze</span>
            </>
          )}
        </button>
      </form>

      {/* Error State */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-700 font-medium">Clone failed</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Success State */}
      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-700">Repository cloned successfully!</span>
        </div>
      )}

      {/* URL Type Info */}
      {urlType === 'ssh' && (
        <div className="mt-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <Key className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-orange-800 font-medium">SSH URL Detected</p>
              <p className="text-orange-700 text-sm mt-1">
                Make sure you have SSH keys configured with your Git provider.
                If cloning fails, try using the HTTPS URL instead.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Popular Repositories */}
      <div className="mt-6">
        <p className="text-sm font-medium text-gray-700 mb-3">Try with popular repositories:</p>
        <div className="flex flex-wrap gap-2">
          {[
            { name: 'React', url: 'https://github.com/facebook/react' },
            { name: 'Vue', url: 'https://github.com/vuejs/vue' },
            { name: 'FastAPI', url: 'https://github.com/tiangolo/fastapi' },
            { name: 'Express', url: 'https://github.com/expressjs/express' },
            { name: 'Django', url: 'https://github.com/django/django' },
          ].map((repo) => (
            <button
              key={repo.name}
              onClick={() => {
                setUrl(repo.url);
                setUrlType('https');
              }}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              {repo.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default GitClone;
