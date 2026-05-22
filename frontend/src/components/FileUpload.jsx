import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

function FileUpload({ onUpload, isLoading, error, success }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/zip': ['.zip'],
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const handleUpload = async () => {
    if (selectedFile && onUpload) {
      await onUpload(selectedFile, (progress) => {
        setUploadProgress(progress);
      });
    }
  };

  const removeFile = () => {
    setSelectedFile(null);
    setUploadProgress(0);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="w-full">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
        } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={isLoading} />
        <div className="flex flex-col items-center space-y-4">
          <div className={`p-4 rounded-full ${isDragActive ? 'bg-primary-100' : 'bg-gray-100'}`}>
            <Upload className={`w-8 h-8 ${isDragActive ? 'text-primary-600' : 'text-gray-400'}`} />
          </div>
          {isDragActive ? (
            <p className="text-primary-600 font-medium">Drop the ZIP file here...</p>
          ) : (
            <>
              <div>
                <p className="text-gray-700 font-medium">
                  Drag & drop your repository ZIP file here
                </p>
                <p className="text-sm text-gray-500 mt-1">or click to browse</p>
              </div>
              <p className="text-xs text-gray-400">Maximum file size: 100MB</p>
            </>
          )}
        </div>
      </div>

      {/* Selected File */}
      {selectedFile && !success && (
        <div className="mt-4 p-4 bg-white border border-gray-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-50 rounded-lg">
                <File className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <p className="font-medium text-gray-800">{selectedFile.name}</p>
                <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            {!isLoading && (
              <button
                onClick={removeFile}
                className="p-1 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            )}
          </div>

          {/* Progress Bar */}
          {isLoading && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-gray-600">Uploading...</span>
                <span className="text-primary-600 font-medium">{uploadProgress}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-600 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Upload Button */}
          {!isLoading && (
            <button
              onClick={handleUpload}
              className="mt-4 w-full py-2.5 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors flex items-center justify-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>Upload & Analyze</span>
            </button>
          )}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="mt-4 p-4 bg-primary-50 border border-primary-200 rounded-lg flex items-center space-x-3">
          <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
          <span className="text-primary-700">Processing repository...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Success State */}
      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center space-x-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <span className="text-green-700">Repository uploaded successfully!</span>
        </div>
      )}
    </div>
  );
}

export default FileUpload;
