import React from 'react';
import UserDetailsForm from './UserDetailsForm';
import ResumeUpload from './ResumeUpload';
import './App.css';

function App() {
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
        <UserDetailsForm />
        <ResumeUpload />
      </div>
    </div>
  );
}

export default App;
