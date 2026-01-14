const canvas = document.getElementById('starfield');
const ctx = canvas.getContext('2d');
const progressBar = document.getElementById('progressBar');
const statusMsg = document.getElementById('statusMsg');

let width, height;
let stars = [];
const numStars = 400;
const speed = 0.5;

const messages = [
    "Calculating stellar coordinates...",
    "Warming up warp drives...",
    "Mapping the Andromeda sector...",
    "Bypassing dark matter clusters...",
    "Calibrating oxygen scrubbers...",
    "Establishing quantum link..."
];

class Star {
    constructor() {
        this.init();
    }

    init() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.z = Math.random() * width; // Depth
        this.size = 0.5 + Math.random() * 2;
        this.color = Math.random() > 0.8 ? '#fde047' : '#ffffff';
    }

    update() {
        this.z -= speed;
        if (this.z <= 0) {
            this.init();
            this.z = width;
        }
    }

    draw() {
        let x = (this.x - width / 2) * (width / this.z);
        x += width / 2;
        let y = (this.y - height / 2) * (width / this.z);
        y += height / 2;

        let s = this.size * (width / this.z);
        
        ctx.beginPath();
        ctx.fillStyle = this.color;
        ctx.globalAlpha = Math.min(1, (width - this.z) / (width * 0.8));
        ctx.arc(x, y, s, 0, Math.PI * 2);
        ctx.fill();
    }
}

function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    
    stars = [];
    for (let i = 0; i < numStars; i++) {
        stars.push(new Star());
    }
}

function animate() {
    ctx.fillStyle = '#05070a';
    ctx.fillRect(0, 0, width, height);

    stars.forEach(star => {
        star.update();
        star.draw();
    });

    requestAnimationFrame(animate);
}

// Simulate Progress
let progress = 0;
function updateProgress() {
    if (progress < 100) {
        progress += Math.random() * 1.5;
        if (progress > 100) progress = 100;
        
        progressBar.style.width = `${progress}%`;
        
        // Change message periodically
        if (Math.floor(progress) % 20 === 0 && progress < 95) {
            const msgIndex = Math.floor(progress / 20) % messages.length;
            statusMsg.innerText = messages[msgIndex];
        }

        if (progress === 100) {
            statusMsg.innerText = "Ready for departure.";
            statusMsg.style.color = "#10b981"; // Green-500
        }

        setTimeout(updateProgress, 50 + Math.random() * 100);
    }
}

window.addEventListener('resize', resize);

// Initialize
resize();
animate();
updateProgress();


window.onload = function () {
    const target = sessionStorage.getItem("nextPage");

    if (!target) {
        console.error("No Page Found...")
    return
    }

    this.setTimeout(() => {
        window.location.href = target;

    }, 300);
}