import { useState } from 'react';
import { ChevronRight, ChevronDown, File, Folder, FolderOpen } from 'lucide-react';

function FileTree({ structure, onFileSelect, selectedFile }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="p-3 bg-gray-50 border-b border-gray-200">
        <h3 className="font-medium text-gray-800">File Structure</h3>
      </div>
      <div className="p-2 max-h-96 overflow-y-auto">
        {structure && structure.length > 0 ? (
          <TreeNode nodes={structure} onFileSelect={onFileSelect} selectedFile={selectedFile} />
        ) : (
          <p className="text-gray-500 text-sm p-2">No files found</p>
        )}
      </div>
    </div>
  );
}

function TreeNode({ nodes, level = 0, onFileSelect, selectedFile }) {
  return (
    <ul className="space-y-0.5">
      {nodes.map((node, index) => (
        <TreeItem
          key={`${node.path}-${index}`}
          node={node}
          level={level}
          onFileSelect={onFileSelect}
          selectedFile={selectedFile}
        />
      ))}
    </ul>
  );
}

function TreeItem({ node, level, onFileSelect, selectedFile }) {
  const [isOpen, setIsOpen] = useState(level < 2);
  const isDirectory = node.type === 'directory';
  const hasChildren = isDirectory && node.children && node.children.length > 0;
  const isSelected = selectedFile === node.path;

  const getFileIcon = (extension) => {
    const iconColors = {
      '.js': 'text-yellow-500',
      '.jsx': 'text-blue-400',
      '.ts': 'text-blue-600',
      '.tsx': 'text-blue-500',
      '.py': 'text-green-500',
      '.java': 'text-red-500',
      '.json': 'text-yellow-600',
      '.md': 'text-gray-600',
      '.css': 'text-purple-500',
      '.scss': 'text-pink-500',
      '.html': 'text-orange-500',
    };
    return iconColors[extension] || 'text-gray-400';
  };

  const handleClick = () => {
    if (isDirectory) {
      setIsOpen(!isOpen);
    } else if (onFileSelect) {
      onFileSelect(node.path);
    }
  };

  return (
    <li>
      <div
        className={`flex items-center space-x-1 py-1 px-2 rounded cursor-pointer transition-colors ${
          isSelected
            ? 'bg-primary-100 text-primary-700'
            : 'hover:bg-gray-100 text-gray-700'
        }`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={handleClick}
      >
        {/* Expand/Collapse Icon */}
        {isDirectory ? (
          hasChildren ? (
            isOpen ? (
              <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
            )
          ) : (
            <span className="w-4" />
          )
        ) : (
          <span className="w-4" />
        )}

        {/* File/Folder Icon */}
        {isDirectory ? (
          isOpen ? (
            <FolderOpen className="w-4 h-4 text-yellow-500 flex-shrink-0" />
          ) : (
            <Folder className="w-4 h-4 text-yellow-500 flex-shrink-0" />
          )
        ) : (
          <File className={`w-4 h-4 flex-shrink-0 ${getFileIcon(node.extension)}`} />
        )}

        {/* Name */}
        <span className="text-sm truncate">{node.name}</span>

        {/* File Size */}
        {!isDirectory && node.size && (
          <span className="text-xs text-gray-400 ml-auto">
            {formatFileSize(node.size)}
          </span>
        )}
      </div>

      {/* Children */}
      {isDirectory && isOpen && hasChildren && (
        <TreeNode
          nodes={node.children}
          level={level + 1}
          onFileSelect={onFileSelect}
          selectedFile={selectedFile}
        />
      )}
    </li>
  );
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export default FileTree;
