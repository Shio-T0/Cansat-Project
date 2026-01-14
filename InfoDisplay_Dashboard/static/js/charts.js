// Zoom functionality for the floating widget
function toggleZoom(el) {
    el.classList.toggle('zoomed-in');
    const iframe = el.querySelector('iframe');
    
    if (el.classList.contains('zoomed-in')) {
        iframe.classList.remove('pointer-events-none');
    } else {
        iframe.classList.add('pointer-events-none');
    }
}

// Mock AI logic (Hook your Python backend fetch here)
const input = document.getElementById('ai-query-input');
const output = document.getElementById('ai-chat-output');

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;

        // User Message
        const userDiv = document.createElement('div');
        userDiv.className = 'bg-slate-800 rounded-lg p-3 text-sm ml-4 border border-slate-700';
        userDiv.innerHTML = `<p class="text-slate-200">${query}</p>`;
        output.appendChild(userDiv);
        
        input.value = '';
        output.scrollTop = output.scrollHeight;

        // AI Response (Placeholder for your backend call)
        setTimeout(() => {
            const aiDiv = document.createElement('div');
            aiDiv.className = 'bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3 text-sm mr-4';
            aiDiv.innerHTML = `<p class="text-indigo-200">Analyzing the provided coordinates... Requesting data from Python backend for: "${query}"</p>`;
            output.appendChild(aiDiv);
            output.scrollTop = output.scrollHeight;
        }, 600);
    }
});

// Background Star Animation (Small Detail)
document.addEventListener('mousemove', (e) => {
    const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
    const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
    document.body.style.backgroundPosition = `${moveX}px ${moveY}px`;
});
