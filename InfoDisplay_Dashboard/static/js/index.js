
// Generate stars dynamically
const starContainer = document.getElementById('stars');
const starCount = 150;

for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    
    const x = Math.random() * 100;
    const y = Math.random() * 100;
    const size = Math.random() * 2.5;
    const duration = 2 + Math.random() * 4;
    const delay = Math.random() * 5;

    star.style.left = `${x}%`;
    star.style.top = `${y}%`;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;
    star.style.setProperty('--duration', `${duration}s`);
    star.style.animationDelay = `${delay}s`;

    starContainer.appendChild(star);
}

// Handle button interactions
function showMessage(text) {
    const box = document.getElementById('messageBox');
    const content = document.getElementById('messageContent');
    content.innerText = text;
    box.style.display = 'block';
    
    setTimeout(() => {
        box.style.display = 'none';
    }, 2500);
}