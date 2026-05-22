import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import AnalysisPage from './pages/AnalysisPage';
import ChatPage from './pages/ChatPage';
import DocumentationPage from './pages/DocumentationPage';
import RepositoriesPage from './pages/RepositoriesPage';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/repositories" element={<RepositoriesPage />} />
          <Route path="/analysis/:repoId" element={<AnalysisPage />} />
          <Route path="/chat/:repoId" element={<ChatPage />} />
          <Route path="/documentation/:repoId" element={<DocumentationPage />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
