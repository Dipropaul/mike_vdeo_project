// Character counter for script textarea
const scriptTextarea = document.getElementById('script');
const charCount = document.getElementById('charCount');

if (scriptTextarea && charCount) {
    scriptTextarea.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
}

// Form submission
const videoForm = document.getElementById('videoForm');
const createBtn = document.getElementById('createBtn');
const statusMessage = document.getElementById('statusMessage');
const statusText = document.getElementById('statusText');
const progressBar = document.getElementById('progressBar');

if (videoForm) {
    videoForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Collect form data
        const formData = {
            title: document.getElementById('title').value,
            category: document.getElementById('category').value,
            format: document.querySelector('input[name="format"]:checked').value,
            style: document.querySelector('input[name="style"]:checked').value,
            voice: document.querySelector('input[name="voice"]:checked').value,
            script: document.getElementById('script').value,
            keywords: document.getElementById('keywords').value,
            negative_keywords: document.getElementById('negative_keywords').value
        };
        
        // Validate
        if (formData.script.length > 1500) {
            alert('Script is too long! Maximum 1500 characters.');
            return;
        }
        
        // Disable form
        createBtn.disabled = true;
        statusMessage.style.display = 'block';
        statusText.textContent = 'Starting video generation...';
        progressBar.style.width = '0%';
        
        try {
            // Submit to API
            const response = await fetch('/api/create-video', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Poll for job status
                const jobId = result.job_id;
                pollJobStatus(jobId);
            } else {
                throw new Error(result.error || 'Failed to create video');
            }
            
        } catch (error) {
            statusText.textContent = `Error: ${error.message}`;
            createBtn.disabled = false;
            setTimeout(() => {
                statusMessage.style.display = 'none';
            }, 5000);
        }
    });
}

async function pollJobStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/job-status/${jobId}`);
            const status = await response.json();
            
            statusText.textContent = status.message;
            progressBar.style.width = `${status.progress}%`;
            
            if (status.status === 'completed') {
                clearInterval(interval);
                statusText.textContent = '✓ Video generation complete!';
                progressBar.style.width = '100%';
                
                setTimeout(() => {
                    const videoId = status.video.id;
                    const videoTitle = status.video.title;
                    const downloadUrl = `/api/download/${videoId}`;
                    
                    // Show success message with download link
                    const message = `Video "${videoTitle}" has been created successfully!\n\nClick OK to download your video.`;
                    if (confirm(message)) {
                        window.location.href = downloadUrl;
                    }
                    
                    videoForm.reset();
                    createBtn.disabled = false;
                    statusMessage.style.display = 'none';
                    charCount.textContent = '0';
                }, 2000);
                
            } else if (status.status === 'failed') {
                clearInterval(interval);
                statusText.textContent = `✗ ${status.message}`;
                createBtn.disabled = false;
                
                setTimeout(() => {
                    statusMessage.style.display = 'none';
                }, 5000);
            }
            
        } catch (error) {
            clearInterval(interval);
            statusText.textContent = `Error: ${error.message}`;
            createBtn.disabled = false;
        }
    }, 2000); // Poll every 2 seconds
}

// Load configuration on page load
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        console.log('App configuration loaded:', config);
    } catch (error) {
        console.error('Failed to load configuration:', error);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadConfig();
});
