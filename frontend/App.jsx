import React, { useState } from 'react';
import UserDetailsForm from './UserDetailsForm';
import ResumeUpload from './ResumeUpload';
import JobDashboard from './JobDashboard';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="App">
      <div className="container-fluid">
        <div className="row">
          <div className="col-12">
            <header className="bg-primary text-white text-center py-4 mb-4">
              <h1>AI Job Application Assistant</h1>
              <p className="mb-0">Find your perfect job match</p>
            </header>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="row mb-4">
          <div className="col-12">
            <ul className="nav nav-tabs">
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
                  onClick={() => setActiveTab('dashboard')}
                >
                  <i className="bi bi-grid-3x3-gap me-2"></i>
                  Job Dashboard
                </button>
              </li>
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                  onClick={() => setActiveTab('profile')}
                >
                  <i className="bi bi-person me-2"></i>
                  User Profile
                </button>
              </li>
              <li className="nav-item">
                <button
                  className={`nav-link ${activeTab === 'resume' ? 'active' : ''}`}
                  onClick={() => setActiveTab('resume')}
                >
                  <i className="bi bi-file-text me-2"></i>
                  Resume Upload
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === 'dashboard' && <JobDashboard />}
          {activeTab === 'profile' && <UserDetailsForm />}
          {activeTab === 'resume' && <ResumeUpload />}
        </div>
      </div>
    </div>
  );
}

export default App;
