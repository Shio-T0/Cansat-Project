/**
 * CONFIGURATION
 * Update the URL to your Python backend endpoint.
 */
const ENDPOINT = 'http://localhost:5000/api/images';

const grid = document.getElementById('gallery-grid');
const statusEl = document.getElementById('connection-status');

/**
 * FETCH LOGIC
 * Expected Python response: JSON array of objects e.g. [{ url: "...", timestamp: "..." }]
 */
async function updateGallery() {
    try {
        const response = await fetch(ENDPOINT);
        if (!response.ok) throw new Error('Offline');
        
        const data = await response.json();
        renderImages(data);
        setConnection(true);
    } catch (err) {
        console.warn("Backend not reached. Using fallback demo visuals.");
        setConnection(false);
        loadFallback();
    }
}





/**
 * BACKGROUND AMBIENCE
 */
function initBackground() {
    const canvas = document.getElementById('star-canvas');
    const ctx = canvas.getContext('2d');
    let w, h, stars = [];

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    for (let i = 0; i < 150; i++) {
        stars.push({
            x: Math.random() * w,
            y: Math.random() * h,
            size: Math.random() * 1.5,
            blink: Math.random() * 0.05
        });
    }

    function animate() {
        ctx.clearRect(0, 0, w, h);
        stars.forEach(s => {
            const opacity = 0.2 + Math.abs(Math.sin(Date.now() * s.blink * 0.02) * 0.8);
            ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.size, 0, Math.PI * 2);
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
}

// Initialize everything
window.onload = () => {
    initBackground();
    updateGallery();
    // Polling: Auto-refresh every 30 seconds
    setInterval(updateGallery, 30000);
};