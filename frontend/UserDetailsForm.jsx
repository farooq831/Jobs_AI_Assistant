import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

const UserDetailsForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    location: '',
    salaryMin: '',
    salaryMax: '',
    jobTitles: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  // Client-side validation
  const validateForm = () => {
    const newErrors = {};

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    } else if (formData.name.trim().length > 100) {
      newErrors.name = 'Name must not exceed 100 characters';
    }

    // Location validation
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    } else if (formData.location.trim().length < 2) {
      newErrors.location = 'Location must be at least 2 characters';
    }

    // Salary validation
    const salaryMin = parseFloat(formData.salaryMin);
    const salaryMax = parseFloat(formData.salaryMax);

    if (!formData.salaryMin) {
      newErrors.salaryMin = 'Minimum salary is required';
    } else if (isNaN(salaryMin) || salaryMin < 0) {
      newErrors.salaryMin = 'Invalid minimum salary';
    }

    if (!formData.salaryMax) {
      newErrors.salaryMax = 'Maximum salary is required';
    } else if (isNaN(salaryMax) || salaryMax < 0) {
      newErrors.salaryMax = 'Invalid maximum salary';
    }

    if (!newErrors.salaryMin && !newErrors.salaryMax && salaryMin > salaryMax) {
      newErrors.salaryMin = 'Minimum salary cannot exceed maximum salary';
      newErrors.salaryMax = 'Maximum salary must be greater than minimum salary';
    }

    // Job titles validation
    if (!formData.jobTitles.trim()) {
      newErrors.jobTitles = 'At least one job title is required';
    } else {
      const titles = formData.jobTitles.split(',').map(t => t.trim()).filter(t => t);
      if (titles.length === 0) {
        newErrors.jobTitles = 'At least one valid job title is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitSuccess(false);

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      // Prepare data for submission
      const submitData = {
        name: formData.name.trim(),
        location: formData.location.trim(),
        salary_min: parseFloat(formData.salaryMin),
        salary_max: parseFloat(formData.salaryMax),
        job_titles: formData.jobTitles.split(',').map(t => t.trim()).filter(t => t)
      };

      const response = await fetch('http://localhost:5000/api/user-details', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitSuccess(true);
        // Reset form after successful submission
        setFormData({
          name: '',
          location: '',
          salaryMin: '',
          salaryMax: '',
          jobTitles: ''
        });
        setErrors({});
      } else {
        // Handle server validation errors
        if (data.errors) {
          setErrors(data.errors);
        } else {
          setErrors({ form: data.message || 'An error occurred' });
        }
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setErrors({ form: 'Failed to connect to server. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-8">
          <div className="card shadow">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">User Details</h3>
              <p className="mb-0 small">Enter your job search preferences</p>
            </div>
            <div className="card-body">
              {submitSuccess && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                  <strong>Success!</strong> Your details have been saved successfully.
                  <button
                    type="button"
                    className="btn-close"
                    onClick={() => setSubmitSuccess(false)}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              {errors.form && (
                <div className="alert alert-danger" role="alert">
                  {errors.form}
                </div>
              )}

              <form onSubmit={handleSubmit} noValidate>
                {/* Name Field */}
                <div className="mb-3">
                  <label htmlFor="name" className="form-label">
                    Full Name <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.name ? 'is-invalid' : ''}`}
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Enter your full name"
                    required
                  />
                  {errors.name && (
                    <div className="invalid-feedback">{errors.name}</div>
                  )}
                </div>

                {/* Location Field */}
                <div className="mb-3">
                  <label htmlFor="location" className="form-label">
                    Location <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className={`form-control ${errors.location ? 'is-invalid' : ''}`}
                    id="location"
                    name="location"
                    value={formData.location}
                    onChange={handleChange}
                    placeholder="e.g., New York, NY or Remote"
                    required
                  />
                  {errors.location && (
                    <div className="invalid-feedback">{errors.location}</div>
                  )}
                  <small className="form-text text-muted">
                    Enter your preferred job location or "Remote" for remote positions
                  </small>
                </div>

                {/* Salary Range */}
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label htmlFor="salaryMin" className="form-label">
                      Minimum Salary ($) <span className="text-danger">*</span>
                    </label>
                    <input
                      type="number"
                      className={`form-control ${errors.salaryMin ? 'is-invalid' : ''}`}
                      id="salaryMin"
                      name="salaryMin"
                      value={formData.salaryMin}
                      onChange={handleChange}
                      placeholder="e.g., 50000"
                      min="0"
                      step="1000"
                      required
                    />
                    {errors.salaryMin && (
                      <div className="invalid-feedback">{errors.salaryMin}</div>
                    )}
                  </div>
                  <div className="col-md-6">
                    <label htmlFor="salaryMax" className="form-label">
                      Maximum Salary ($) <span className="text-danger">*</span>
                    </label>
                    <input
                      type="number"
                      className={`form-control ${errors.salaryMax ? 'is-invalid' : ''}`}
                      id="salaryMax"
                      name="salaryMax"
                      value={formData.salaryMax}
                      onChange={handleChange}
                      placeholder="e.g., 80000"
                      min="0"
                      step="1000"
                      required
                    />
                    {errors.salaryMax && (
                      <div className="invalid-feedback">{errors.salaryMax}</div>
                    )}
                  </div>
                </div>

                {/* Job Titles Field */}
                <div className="mb-4">
                  <label htmlFor="jobTitles" className="form-label">
                    Job Titles <span className="text-danger">*</span>
                  </label>
                  <textarea
                    className={`form-control ${errors.jobTitles ? 'is-invalid' : ''}`}
                    id="jobTitles"
                    name="jobTitles"
                    value={formData.jobTitles}
                    onChange={handleChange}
                    placeholder="e.g., Software Engineer, Full Stack Developer, Python Developer"
                    rows="3"
                    required
                  ></textarea>
                  {errors.jobTitles && (
                    <div className="invalid-feedback">{errors.jobTitles}</div>
                  )}
                  <small className="form-text text-muted">
                    Enter job titles separated by commas
                  </small>
                </div>

                {/* Submit Button */}
                <div className="d-grid gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary btn-lg"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Submitting...
                      </>
                    ) : (
                      'Submit Details'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserDetailsForm;
