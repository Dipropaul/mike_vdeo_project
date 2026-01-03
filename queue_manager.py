"""
Queue Management CLI Tool
Manage and monitor the job queue
"""
import argparse
from job_queue import JobQueue
from datetime import datetime
import json


def format_timestamp(iso_string):
    """Format ISO timestamp to readable string"""
    if not iso_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return iso_string


def list_jobs(queue, status=None):
    """List all jobs or filter by status"""
    jobs = queue.get_all_jobs()
    
    if status:
        jobs = [j for j in jobs if j['status'] == status]
    
    if not jobs:
        print("No jobs found.")
        return
    
    print(f"\n{'='*100}")
    print(f"{'ID':<38} {'Status':<12} {'Progress':<10} {'Created':<20} {'Title':<20}")
    print(f"{'='*100}")
    
    for job in jobs:
        job_id = job['id'][:36]
        status = job['status']
        progress = f"{job['progress']}%"
        created = format_timestamp(job['created_at'])
        title = job['video_data'].get('title', 'N/A')[:18]
        
        print(f"{job_id:<38} {status:<12} {progress:<10} {created:<20} {title:<20}")
    
    print(f"{'='*100}")
    print(f"Total: {len(jobs)} jobs")


def show_queue(queue):
    """Show current queue status"""
    queued = queue.get_queued_jobs()
    processing = queue.get_processing_jobs()
    
    print(f"\n{'='*60}")
    print("QUEUE STATUS")
    print(f"{'='*60}")
    print(f"Queued: {len(queued)}")
    print(f"Processing: {len(processing)}")
    print(f"{'='*60}")
    
    if queued:
        print("\nQUEUED JOBS:")
        for i, job in enumerate(queued):
            title = job['video_data'].get('title', 'N/A')
            print(f"  {i+1}. {title} ({job['id'][:8]}...)")
    
    if processing:
        print("\nPROCESSING JOBS:")
        for job in processing:
            title = job['video_data'].get('title', 'N/A')
            progress = job['progress']
            print(f"  - {title} ({progress}%) - {job.get('message', 'N/A')}")


def show_job(queue, job_id):
    """Show detailed job information"""
    job = queue.get_job(job_id)
    
    if not job:
        print(f"Job {job_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print("JOB DETAILS")
    print(f"{'='*60}")
    print(f"ID: {job['id']}")
    print(f"Status: {job['status']}")
    print(f"Progress: {job['progress']}%")
    print(f"Message: {job.get('message', 'N/A')}")
    print(f"Created: {format_timestamp(job['created_at'])}")
    print(f"Started: {format_timestamp(job.get('started_at'))}")
    print(f"Completed: {format_timestamp(job.get('completed_at'))}")
    print(f"\nVideo Data:")
    print(f"  Title: {job['video_data'].get('title', 'N/A')}")
    print(f"  Format: {job['video_data'].get('format', 'N/A')}")
    print(f"  Style: {job['video_data'].get('style', 'N/A')}")
    print(f"  Voice: {job['video_data'].get('voice', 'N/A')}")
    
    if job['status'] == 'completed' and job.get('result'):
        print(f"\nResult:")
        print(f"  Video ID: {job['result'].get('id', 'N/A')}")
        print(f"  Path: {job['result'].get('path', 'N/A')}")
    
    if job['status'] == 'failed' and job.get('error'):
        print(f"\nError:")
        print(f"  {job['error'][:200]}...")


def cleanup_jobs(queue, days):
    """Clean up old jobs"""
    removed = queue.cleanup_old_jobs(days)
    print(f"Removed {removed} old jobs (older than {days} days)")


def main():
    parser = argparse.ArgumentParser(description='Manage ClipForge job queue')
    parser.add_argument('command', choices=['list', 'queue', 'show', 'cleanup'],
                       help='Command to execute')
    parser.add_argument('--status', choices=['queued', 'processing', 'completed', 'failed'],
                       help='Filter jobs by status')
    parser.add_argument('--job-id', help='Job ID for show command')
    parser.add_argument('--days', type=int, default=7,
                       help='Days to keep jobs for cleanup command')
    
    args = parser.parse_args()
    
    queue = JobQueue()
    
    if args.command == 'list':
        list_jobs(queue, args.status)
    elif args.command == 'queue':
        show_queue(queue)
    elif args.command == 'show':
        if not args.job_id:
            print("Error: --job-id required for show command")
            return
        show_job(queue, args.job_id)
    elif args.command == 'cleanup':
        cleanup_jobs(queue, args.days)


if __name__ == '__main__':
    main()
