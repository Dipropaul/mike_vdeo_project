"""
Job Queue Manager for Video Generation
Handles queueing and tracking of video generation jobs
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobQueue:
    """
    Simple file-based job queue manager
    Stores jobs in JSON file for persistence
    """
    
    def __init__(self, queue_file: str = "outputs/job_queue.json"):
        """Initialize job queue"""
        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize queue file if it doesn't exist
        if not self.queue_file.exists():
            self._save_queue({"jobs": {}, "queue": []})
    
    def _load_queue(self) -> Dict:
        """Load queue from file"""
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"jobs": {}, "queue": []}
    
    def _save_queue(self, data: Dict):
        """Save queue to file"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_job(self, video_data: Dict) -> str:
        """
        Add a new job to the queue
        
        Args:
            video_data: Video generation parameters
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        data = self._load_queue()
        
        job = {
            'id': job_id,
            'status': JobStatus.QUEUED,
            'progress': 0,
            'message': 'Job queued',
            'video_data': video_data,
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        data['jobs'][job_id] = job
        data['queue'].append(job_id)
        
        self._save_queue(data)
        
        return job_id
    
    def get_next_job(self) -> Optional[Dict]:
        """
        Get next job from queue
        
        Returns:
            Job dict or None if queue is empty
        """
        data = self._load_queue()
        
        # Find first queued job
        for job_id in data['queue']:
            job = data['jobs'].get(job_id)
            if job and job['status'] == JobStatus.QUEUED:
                return job
        
        return None
    
    def update_job(self, job_id: str, updates: Dict):
        """
        Update job status and details
        
        Args:
            job_id: Job identifier
            updates: Dictionary with fields to update
        """
        data = self._load_queue()
        
        if job_id not in data['jobs']:
            raise ValueError(f"Job {job_id} not found")
        
        job = data['jobs'][job_id]
        job.update(updates)
        
        self._save_queue(data)
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """
        Get job by ID
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job dict or None
        """
        data = self._load_queue()
        return data['jobs'].get(job_id)
    
    def get_all_jobs(self) -> List[Dict]:
        """
        Get all jobs
        
        Returns:
            List of all jobs
        """
        data = self._load_queue()
        return list(data['jobs'].values())
    
    def get_queued_jobs(self) -> List[Dict]:
        """
        Get all queued jobs
        
        Returns:
            List of queued jobs
        """
        data = self._load_queue()
        return [
            job for job in data['jobs'].values()
            if job['status'] == JobStatus.QUEUED
        ]
    
    def get_processing_jobs(self) -> List[Dict]:
        """
        Get all processing jobs
        
        Returns:
            List of processing jobs
        """
        data = self._load_queue()
        return [
            job for job in data['jobs'].values()
            if job['status'] == JobStatus.PROCESSING
        ]
    
    def get_queue_position(self, job_id: str) -> int:
        """
        Get position of job in queue
        
        Args:
            job_id: Job identifier
            
        Returns:
            Position (0-indexed) or -1 if not found or not queued
        """
        queued_jobs = self.get_queued_jobs()
        for i, job in enumerate(queued_jobs):
            if job['id'] == job_id:
                return i
        return -1
    
    def cleanup_old_jobs(self, days: int = 7):
        """
        Remove completed/failed jobs older than specified days
        
        Args:
            days: Number of days to keep jobs
        """
        from datetime import timedelta
        
        data = self._load_queue()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        jobs_to_remove = []
        
        for job_id, job in data['jobs'].items():
            if job['status'] in [JobStatus.COMPLETED, JobStatus.FAILED]:
                completed_at = job.get('completed_at')
                if completed_at:
                    job_date = datetime.fromisoformat(completed_at)
                    if job_date < cutoff_date:
                        jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del data['jobs'][job_id]
            if job_id in data['queue']:
                data['queue'].remove(job_id)
        
        self._save_queue(data)
        
        return len(jobs_to_remove)
