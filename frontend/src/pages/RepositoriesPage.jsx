import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FolderGit2,
  Trash2,
  BarChart3,
  MessageSquare,
  FileText,
  Clock,
  File,
  AlertCircle,
  Plus,
} from 'lucide-react';
import { repositoryApi } from '../services/api';
import useStore from '../store/useStore';
import LoadingSpinner from '../components/LoadingSpinner';

function RepositoriesPage() {
  const [repositories, setRepositories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const navigate = useNavigate();
  const { setCurrentRepo } = useStore();

  useEffect(() => {
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    setIsLoading(true);
    try {
      const result = await repositoryApi.listRepositories();
      setRepositories(result.repositories || []);
    } catch (err) {
      console.error('Failed to load repositories:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (repoId) => {
    try {
      await repositoryApi.deleteRepository(repoId);
      setRepositories(repositories.filter((r) => r.id !== repoId));
      setDeleteConfirm(null);
    } catch (err) {
      console.error('Failed to delete repository:', err);
    }
  };

  const handleSelect = (repo) => {
    setCurrentRepo(repo);
    navigate(`/analysis/${repo.id}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" text="Loading repositories..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Repositories</h1>
          <p className="text-gray-600">Manage your analyzed repositories</p>
        </div>
        <Link
          to="/"
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Add Repository</span>
        </Link>
      </div>

      {/* Repository List */}
      {repositories.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <FolderGit2 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No repositories yet</h3>
          <p className="text-gray-600 mb-4">
            Upload a ZIP file or clone a Git repository to get started
          </p>
          <Link
            to="/"
            className="inline-flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Your First Repository</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {repositories.map((repo) => (
            <div
              key={repo.id}
              className="bg-white rounded-lg border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
            >
              {/* Card Header */}
              <div
                onClick={() => handleSelect(repo)}
                className="p-4 cursor-pointer"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary-50 rounded-lg">
                      <FolderGit2 className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{repo.name}</h3>
                      <p className="text-sm text-gray-500 capitalize">
                        {repo.source === 'git_clone' ? 'Git Clone' : 'ZIP Upload'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <File className="w-4 h-4" />
                    <span>{repo.file_count || 0} files</span>
                  </span>
                </div>
              </div>

              {/* Card Actions */}
              <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Link
                    to={`/analysis/${repo.id}`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="View Analysis"
                  >
                    <BarChart3 className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/chat/${repo.id}`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Chat"
                  >
                    <MessageSquare className="w-4 h-4" />
                  </Link>
                  <Link
                    to={`/documentation/${repo.id}`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    title="Generate Documentation"
                  >
                    <FileText className="w-4 h-4" />
                  </Link>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setDeleteConfirm(repo.id);
                  }}
                  className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-red-100 rounded-full">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Delete Repository</h3>
            </div>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete this repository? This action cannot be undone
              and all analysis data will be lost.
            </p>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirm)}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RepositoriesPage;
