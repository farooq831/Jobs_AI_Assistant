"""
Application Status Model for Job Application Tracker

This module defines the core status model for tracking job applications including:
- ApplicationStatus enum with valid status values
- StatusTransition class for managing status changes
- StatusHistory for tracking status change history
- Validation and business logic for status transitions
- Utility functions for status management

Author: AI Job Application Assistant
Date: November 2025
Version: 1.0.0
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import json
from dataclasses import dataclass, field, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ApplicationStatus(Enum):
    """
    Enumeration of valid job application statuses
    
    Attributes:
        PENDING: Application not yet submitted
        APPLIED: Application has been submitted
        INTERVIEW: Interview stage (phone screen, on-site, etc.)
        OFFER: Offer received
        REJECTED: Application rejected
    """
    PENDING = "Pending"
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"
    
    @classmethod
    def from_string(cls, status_str: str) -> 'ApplicationStatus':
        """
        Convert a string to ApplicationStatus enum
        
        Args:
            status_str: Status string (case-insensitive)
            
        Returns:
            ApplicationStatus enum value
            
        Raises:
            ValueError: If status string is invalid
        """
        if not status_str:
            raise ValueError("Status string cannot be empty")
        
        # Normalize the string
        normalized = status_str.strip().title()
        
        # Try to match
        for status in cls:
            if status.value == normalized:
                return status
        
        # If no match found
        valid_statuses = [s.value for s in cls]
        raise ValueError(
            f"Invalid status: '{status_str}'. Valid statuses are: {', '.join(valid_statuses)}"
        )
    
    @classmethod
    def get_all_statuses(cls) -> List[str]:
        """Get list of all valid status strings"""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid_status(cls, status_str: str) -> bool:
        """Check if a status string is valid"""
        try:
            cls.from_string(status_str)
            return True
        except ValueError:
            return False
    
    def __str__(self):
        return self.value


@dataclass
class StatusTransition:
    """
    Represents a single status transition/change
    
    Attributes:
        from_status: Previous status (None for initial status)
        to_status: New status
        timestamp: When the transition occurred
        notes: Optional notes about the transition
        user_id: Optional user who made the change
    """
    from_status: Optional[ApplicationStatus]
    to_status: ApplicationStatus
    timestamp: datetime = field(default_factory=datetime.now)
    notes: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "from_status": self.from_status.value if self.from_status else None,
            "to_status": self.to_status.value,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
            "user_id": self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusTransition':
        """Create StatusTransition from dictionary"""
        return cls(
            from_status=ApplicationStatus.from_string(data["from_status"]) if data.get("from_status") else None,
            to_status=ApplicationStatus.from_string(data["to_status"]),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"],
            notes=data.get("notes"),
            user_id=data.get("user_id")
        )
    
    def is_valid_transition(self) -> bool:
        """
        Check if this is a valid status transition
        
        Valid transitions:
        - Any status can go to Rejected
        - Pending -> Applied, Interview, Offer
        - Applied -> Interview, Offer
        - Interview -> Offer
        - Offer -> Applied (if declined and reapplying)
        """
        if self.from_status is None:
            # Initial status is always valid
            return True
        
        # Can always reject
        if self.to_status == ApplicationStatus.REJECTED:
            return True
        
        # Can't go back to Pending
        if self.to_status == ApplicationStatus.PENDING:
            return False
        
        # Define valid forward transitions
        valid_transitions = {
            ApplicationStatus.PENDING: [ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER],
            ApplicationStatus.APPLIED: [ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER],
            ApplicationStatus.INTERVIEW: [ApplicationStatus.OFFER],
            ApplicationStatus.OFFER: [ApplicationStatus.APPLIED],  # Can reapply if declined
            ApplicationStatus.REJECTED: [ApplicationStatus.APPLIED]  # Can reapply after rejection
        }
        
        return self.to_status in valid_transitions.get(self.from_status, [])


@dataclass
class StatusHistory:
    """
    Manages the complete history of status changes for a job application
    
    Attributes:
        job_id: Unique identifier for the job
        transitions: List of status transitions
        current_status: Current application status
        created_at: When the tracking started
        updated_at: Last update timestamp
    """
    job_id: str
    transitions: List[StatusTransition] = field(default_factory=list)
    current_status: ApplicationStatus = ApplicationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_transition(
        self,
        new_status: ApplicationStatus,
        notes: Optional[str] = None,
        user_id: Optional[str] = None,
        validate: bool = True
    ) -> bool:
        """
        Add a new status transition
        
        Args:
            new_status: New status to transition to
            notes: Optional notes about the transition
            user_id: Optional user making the change
            validate: Whether to validate the transition
            
        Returns:
            True if transition was added, False if invalid
        """
        transition = StatusTransition(
            from_status=self.current_status,
            to_status=new_status,
            timestamp=datetime.now(),
            notes=notes,
            user_id=user_id
        )
        
        if validate and not transition.is_valid_transition():
            logger.warning(
                f"Invalid status transition for job {self.job_id}: "
                f"{self.current_status.value} -> {new_status.value}"
            )
            return False
        
        self.transitions.append(transition)
        self.current_status = new_status
        self.updated_at = datetime.now()
        
        logger.info(
            f"Status transition for job {self.job_id}: "
            f"{transition.from_status.value if transition.from_status else 'None'} -> {new_status.value}"
        )
        
        return True
    
    def get_status_at_date(self, target_date: datetime) -> Optional[ApplicationStatus]:
        """Get the status that was active at a specific date"""
        if target_date < self.created_at:
            return None
        
        current = ApplicationStatus.PENDING
        for transition in self.transitions:
            if transition.timestamp <= target_date:
                current = transition.to_status
            else:
                break
        
        return current
    
    def get_transition_count(self) -> int:
        """Get the total number of status transitions"""
        return len(self.transitions)
    
    def get_days_in_current_status(self) -> int:
        """Get the number of days in the current status"""
        if not self.transitions:
            delta = datetime.now() - self.created_at
        else:
            last_transition = self.transitions[-1]
            delta = datetime.now() - last_transition.timestamp
        
        return delta.days
    
    def get_status_duration(self, status: ApplicationStatus) -> int:
        """
        Get total days spent in a specific status
        
        Args:
            status: The status to calculate duration for
            
        Returns:
            Total days spent in that status
        """
        total_days = 0
        start_time = None
        
        for i, transition in enumerate(self.transitions):
            if transition.to_status == status:
                start_time = transition.timestamp
            elif start_time:
                # Status changed from target status
                duration = transition.timestamp - start_time
                total_days += duration.days
                start_time = None
        
        # If still in the status
        if start_time and self.current_status == status:
            duration = datetime.now() - start_time
            total_days += duration.days
        
        return total_days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "transitions": [t.to_dict() for t in self.transitions],
            "current_status": self.current_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusHistory':
        """Create StatusHistory from dictionary"""
        return cls(
            job_id=data["job_id"],
            transitions=[StatusTransition.from_dict(t) for t in data.get("transitions", [])],
            current_status=ApplicationStatus.from_string(data["current_status"]),
            created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"],
            updated_at=datetime.fromisoformat(data["updated_at"]) if isinstance(data["updated_at"], str) else data["updated_at"]
        )


class ApplicationStatusManager:
    """
    High-level manager for application status tracking
    
    Provides utilities for:
    - Managing status histories for multiple jobs
    - Bulk status updates
    - Statistics and reporting
    - Validation
    """
    
    def __init__(self):
        """Initialize the status manager"""
        self.histories: Dict[str, StatusHistory] = {}
    
    def create_history(self, job_id: str, initial_status: ApplicationStatus = ApplicationStatus.PENDING) -> StatusHistory:
        """
        Create a new status history for a job
        
        Args:
            job_id: Unique job identifier
            initial_status: Initial status (default: PENDING)
            
        Returns:
            StatusHistory object
        """
        if job_id in self.histories:
            logger.warning(f"History already exists for job {job_id}")
            return self.histories[job_id]
        
        history = StatusHistory(job_id=job_id, current_status=initial_status)
        
        # Add initial transition if not PENDING
        if initial_status != ApplicationStatus.PENDING:
            history.add_transition(initial_status, notes="Initial status", validate=False)
        
        self.histories[job_id] = history
        logger.info(f"Created status history for job {job_id} with initial status {initial_status.value}")
        
        return history
    
    def get_history(self, job_id: str) -> Optional[StatusHistory]:
        """Get status history for a job"""
        return self.histories.get(job_id)
    
    def update_status(
        self,
        job_id: str,
        new_status: ApplicationStatus,
        notes: Optional[str] = None,
        user_id: Optional[str] = None,
        create_if_missing: bool = True
    ) -> bool:
        """
        Update status for a job
        
        Args:
            job_id: Job identifier
            new_status: New status
            notes: Optional notes
            user_id: Optional user ID
            create_if_missing: Create history if it doesn't exist
            
        Returns:
            True if update succeeded
        """
        history = self.histories.get(job_id)
        
        if not history:
            if create_if_missing:
                history = self.create_history(job_id)
            else:
                logger.error(f"No history found for job {job_id}")
                return False
        
        return history.add_transition(new_status, notes, user_id)
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform bulk status updates
        
        Args:
            updates: List of update dicts with job_id, status, notes, user_id
            
        Returns:
            Results summary
        """
        results = {
            "total": len(updates),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for update in updates:
            try:
                job_id = update.get("job_id")
                status_str = update.get("status")
                
                if not job_id or not status_str:
                    results["failed"] += 1
                    results["errors"].append({
                        "job_id": job_id,
                        "error": "Missing job_id or status"
                    })
                    continue
                
                new_status = ApplicationStatus.from_string(status_str)
                success = self.update_status(
                    job_id,
                    new_status,
                    notes=update.get("notes"),
                    user_id=update.get("user_id")
                )
                
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "job_id": job_id,
                        "error": "Invalid transition"
                    })
                    
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "job_id": update.get("job_id"),
                    "error": str(e)
                })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about application statuses"""
        if not self.histories:
            return {
                "total_jobs": 0,
                "status_counts": {},
                "average_transitions": 0,
                "average_days_in_current_status": 0
            }
        
        status_counts = {}
        total_transitions = 0
        total_days = 0
        
        for history in self.histories.values():
            status = history.current_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            total_transitions += history.get_transition_count()
            total_days += history.get_days_in_current_status()
        
        num_jobs = len(self.histories)
        
        return {
            "total_jobs": num_jobs,
            "status_counts": status_counts,
            "average_transitions": round(total_transitions / num_jobs, 2),
            "average_days_in_current_status": round(total_days / num_jobs, 2)
        }
    
    def get_jobs_by_status(self, status: ApplicationStatus) -> List[str]:
        """Get list of job IDs with a specific status"""
        return [
            job_id for job_id, history in self.histories.items()
            if history.current_status == status
        ]
    
    def export_to_json(self, filepath: str) -> bool:
        """
        Export all status histories to JSON file
        
        Args:
            filepath: Path to output file
            
        Returns:
            True if successful
        """
        try:
            data = {
                "exported_at": datetime.now().isoformat(),
                "total_jobs": len(self.histories),
                "histories": [h.to_dict() for h in self.histories.values()]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.histories)} status histories to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export to {filepath}: {e}")
            return False
    
    def import_from_json(self, filepath: str) -> bool:
        """
        Import status histories from JSON file
        
        Args:
            filepath: Path to input file
            
        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for history_data in data.get("histories", []):
                history = StatusHistory.from_dict(history_data)
                self.histories[history.job_id] = history
            
            logger.info(f"Imported {len(data.get('histories', []))} status histories from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import from {filepath}: {e}")
            return False


# Utility functions

def validate_status(status_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a status string
    
    Args:
        status_str: Status string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ApplicationStatus.from_string(status_str)
        return True, None
    except ValueError as e:
        return False, str(e)


def get_valid_next_statuses(current_status: str) -> List[str]:
    """
    Get list of valid next statuses from current status
    
    Args:
        current_status: Current status string
        
    Returns:
        List of valid next status strings
    """
    try:
        status = ApplicationStatus.from_string(current_status)
    except ValueError:
        return []
    
    valid_next = []
    
    for next_status in ApplicationStatus:
        transition = StatusTransition(from_status=status, to_status=next_status)
        if transition.is_valid_transition():
            valid_next.append(next_status.value)
    
    return valid_next


def create_status_summary(history: StatusHistory) -> Dict[str, Any]:
    """
    Create a summary of a status history
    
    Args:
        history: StatusHistory object
        
    Returns:
        Summary dictionary
    """
    return {
        "job_id": history.job_id,
        "current_status": history.current_status.value,
        "total_transitions": history.get_transition_count(),
        "days_in_current_status": history.get_days_in_current_status(),
        "created_at": history.created_at.isoformat(),
        "updated_at": history.updated_at.isoformat(),
        "timeline": [
            {
                "from": t.from_status.value if t.from_status else None,
                "to": t.to_status.value,
                "date": t.timestamp.strftime("%Y-%m-%d %H:%M"),
                "notes": t.notes
            }
            for t in history.transitions
        ]
    }


# Example usage
if __name__ == "__main__":
    print("Application Status Model - Example Usage\n")
    print("=" * 60)
    
    # 1. Using ApplicationStatus enum
    print("\n1. Valid Statuses:")
    print(f"   {', '.join(ApplicationStatus.get_all_statuses())}")
    
    # 2. Status validation
    print("\n2. Status Validation:")
    test_statuses = ["Applied", "interview", "OFFER", "invalid"]
    for status_str in test_statuses:
        is_valid, error = validate_status(status_str)
        print(f"   '{status_str}': {'✓ Valid' if is_valid else f'✗ {error}'}")
    
    # 3. Create status manager
    print("\n3. Creating Status Manager:")
    manager = ApplicationStatusManager()
    
    # 4. Track a job application
    print("\n4. Tracking Job Application:")
    job_id = "job_123"
    manager.create_history(job_id)
    print(f"   Created history for {job_id}")
    
    # 5. Update statuses
    print("\n5. Status Updates:")
    updates = [
        ("Applied", "Submitted application"),
        ("Interview", "Phone screen scheduled"),
        ("Offer", "Received offer letter")
    ]
    
    for status_str, notes in updates:
        status = ApplicationStatus.from_string(status_str)
        manager.update_status(job_id, status, notes=notes)
        print(f"   → {status_str}: {notes}")
    
    # 6. Get summary
    print("\n6. Application Summary:")
    history = manager.get_history(job_id)
    if history:
        summary = create_status_summary(history)
        print(f"   Job ID: {summary['job_id']}")
        print(f"   Current Status: {summary['current_status']}")
        print(f"   Total Transitions: {summary['total_transitions']}")
        print(f"   Days in Current Status: {summary['days_in_current_status']}")
    
    # 7. Statistics
    print("\n7. Overall Statistics:")
    stats = manager.get_statistics()
    print(f"   Total Jobs Tracked: {stats['total_jobs']}")
    print(f"   Status Distribution: {stats['status_counts']}")
    
    print("\n" + "=" * 60)
    print("Application Status Model Demo Complete!")
