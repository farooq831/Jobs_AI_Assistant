import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status }) => {
  const getStatusConfig = (statusValue) => {
    const normalizedStatus = statusValue?.toLowerCase() || 'pending';
    
    const statusMap = {
      pending: {
        label: 'Pending',
        color: 'secondary',
        icon: 'bi-clock'
      },
      applied: {
        label: 'Applied',
        color: 'primary',
        icon: 'bi-send-check'
      },
      interview: {
        label: 'Interview',
        color: 'info',
        icon: 'bi-calendar-check'
      },
      offer: {
        label: 'Offer',
        color: 'success',
        icon: 'bi-trophy'
      },
      rejected: {
        label: 'Rejected',
        color: 'danger',
        icon: 'bi-x-circle'
      }
    };

    return statusMap[normalizedStatus] || statusMap.pending;
  };

  const config = getStatusConfig(status);

  return (
    <span className={`badge bg-${config.color} status-badge`}>
      <i className={`bi ${config.icon} me-1`}></i>
      {config.label}
    </span>
  );
};

export default StatusBadge;
