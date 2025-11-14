import React, { useState } from 'react';
import UserDetailsForm from './UserDetailsForm';
import ResumeUpload from './ResumeUpload';
import JobDashboard from './JobDashboard';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <JobDashboard />;
      case 'profile':
        return <UserDetailsForm />;
      case 'resume':
        return <ResumeUpload />;
      default:
        return <JobDashboard />;
    }
  };

  return (
    <div className="App">
      <div className="container-fluid">
        {/* Header */}
        <div className="row">
          <div className="col-12">
            <header className="bg-primary text-white text-center py-4 mb-0">
              <h1>AI Job Application Assistant</h1>
              <p className="mb-0">Find your perfect job match</p>
            </header>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="row">
          <div className="col-12">
            <nav className="nav nav-tabs bg-light">
              <button
                className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                <i className="bi bi-grid-3x3-gap me-2"></i>
                Dashboard
              </button>
              <button
                className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => setActiveTab('profile')}
              >
                <i className="bi bi-person me-2"></i>
                Profile
              </button>
              <button
                className={`nav-link ${activeTab === 'resume' ? 'active' : ''}`}
                onClick={() => setActiveTab('resume')}
              >
                <i className="bi bi-file-text me-2"></i>
                Resume
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="row">
          <div className="col-12">
            <div className="tab-content py-4">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
