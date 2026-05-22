import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Send,
  User,
  Bot,
  Sparkles,
  ArrowLeft,
  File,
  Lightbulb,
  Copy,
  Check,
} from 'lucide-react';
import { chatApi, analysisApi } from '../services/api';
import useStore from '../store/useStore';
import LoadingSpinner from '../components/LoadingSpinner';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

function ChatPage() {
  const { repoId } = useParams();
  const { chatMessages, addChatMessage, clearChatMessages, analysis, setAnalysis } = useStore();
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadAnalysis();
    loadSuggestions();
    
    // Clear messages when component unmounts or repoId changes
    return () => {
      // Keep messages for now
    };
  }, [repoId]);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

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

  const loadSuggestions = async () => {
    setLoadingSuggestions(true);
    try {
      const result = await chatApi.getSuggestions(repoId);
      setSuggestions(result.suggestions || []);
    } catch (err) {
      console.error('Failed to load suggestions:', err);
    } finally {
      setLoadingSuggestions(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    addChatMessage(userMessage);
    setInput('');
    setIsLoading(true);

    try {
      const response = await chatApi.ask(repoId, userMessage.content, chatMessages);
      
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        relatedFiles: response.related_files,
        codeSnippets: response.code_snippets,
      };

      addChatMessage(assistantMessage);
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      addChatMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
  };

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <Link
            to={`/analysis/${repoId}`}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Repository Q&A</h1>
            <p className="text-sm text-gray-500">
              {analysis?.repository_name || 'Loading...'}
            </p>
          </div>
        </div>
        <button
          onClick={clearChatMessages}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Clear chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4">
        {chatMessages.length === 0 ? (
          <WelcomeMessage
            repoName={analysis?.repository_name}
            suggestions={suggestions}
            loadingSuggestions={loadingSuggestions}
            onSuggestionClick={handleSuggestionClick}
          />
        ) : (
          chatMessages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))
        )}
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-600" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-primary-600 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestions */}
      {chatMessages.length > 0 && suggestions.length > 0 && (
        <div className="py-2 border-t border-gray-200">
          <div className="flex items-center space-x-2 overflow-x-auto pb-2">
            <Lightbulb className="w-4 h-4 text-yellow-500 flex-shrink-0" />
            {suggestions.slice(0, 4).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors whitespace-nowrap"
              >
                {suggestion.length > 40 ? suggestion.substring(0, 40) + '...' : suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about this repository..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`p-3 rounded-lg transition-colors ${
              !input.trim() || isLoading
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}

function WelcomeMessage({ repoName, suggestions, loadingSuggestions, onSuggestionClick }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center">
      <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
        <Sparkles className="w-8 h-8 text-primary-600" />
      </div>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">
        Ask me about {repoName || 'this repository'}
      </h2>
      <p className="text-gray-600 max-w-md mb-6">
        I can help you understand the codebase, explain modules and functionalities,
        find specific files, and answer any questions about the project.
      </p>
      
      {loadingSuggestions ? (
        <LoadingSpinner size="sm" text="Loading suggestions..." />
      ) : suggestions.length > 0 ? (
        <div className="w-full max-w-lg">
          <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
          <div className="space-y-2">
            {suggestions.slice(0, 6).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSuggestionClick(suggestion)}
                className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg text-gray-700 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function ChatMessage({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-gray-200' : 'bg-primary-100'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-gray-600" />
        ) : (
          <Bot className="w-5 h-5 text-primary-600" />
        )}
      </div>

      {/* Content */}
      <div
        className={`max-w-[80%] ${
          isUser
            ? 'bg-primary-600 text-white rounded-lg rounded-tr-none px-4 py-3'
            : 'bg-gray-100 rounded-lg rounded-tl-none px-4 py-3'
        } ${message.isError ? 'bg-red-50 text-red-700' : ''}`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  const code = String(children).replace(/\n$/, '');
                  
                  if (!inline && match) {
                    return (
                      <div className="relative group">
                        <button
                          onClick={() => copyToClipboard(code)}
                          className="absolute top-2 right-2 p-1 bg-gray-700 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          {copied ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4 text-gray-300" />
                          )}
                        </button>
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {code}
                        </SyntaxHighlighter>
                      </div>
                    );
                  }
                  
                  return (
                    <code className="bg-gray-200 px-1 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Related Files */}
        {message.relatedFiles && message.relatedFiles.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Related files:</p>
            <div className="flex flex-wrap gap-2">
              {message.relatedFiles.map((file, index) => (
                <span
                  key={index}
                  className="inline-flex items-center space-x-1 px-2 py-1 bg-white rounded text-sm text-gray-600"
                >
                  <File className="w-3 h-3" />
                  <span>{typeof file === 'string' ? file : file.path}</span>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatPage;
