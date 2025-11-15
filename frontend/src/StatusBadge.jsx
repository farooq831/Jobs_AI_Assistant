import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status }) => {
  const getStatusClass = (status) => {
    const statusLower = status?.toLowerCase() || 'pending';
    const classMap = {
      'pending': 'status-pending',
      'applied': 'status-applied',
      'interview': 'status-interview',
      'offer': 'status-offer',
      'rejected': 'status-rejected'
    };
    return classMap[statusLower] || 'status-pending';
  };

  const getStatusIcon = (status) => {
    const statusLower = status?.toLowerCase() || 'pending';
    const iconMap = {
      'pending': 'bi-clock',
      'applied': 'bi-send',
      'interview': 'bi-calendar-check',
      'offer': 'bi-check-circle',
      'rejected': 'bi-x-circle'
    };
    return iconMap[statusLower] || 'bi-clock';
  };

  const formatStatus = (status) => {
    if (!status) return 'Pending';
    return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
  };

  return (
    <span className={`status-badge ${getStatusClass(status)}`}>
      <i className={`bi ${getStatusIcon(status)} me-1`}></i>
      {formatStatus(status)}
    </span>
  );
};

export default StatusBadge;
