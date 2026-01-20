const { useLayoutEffect } = require("react");

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

/*
    AI Logic
*/

async function getAIResponse(query) {
    res = await fetch("/get-ai-data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query,
        })
    })
    let data = res.json();
    return data;
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



        // AI Response
        const aiDiv = document.createElement('div');
        aiDiv.className = 'bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3 text-sm mr-4';
        aiDiv.innerHTML = `<p>Thinking...</p>`;
        output.appendChild(aiDiv);
        output.scrollTop = output.scrollHeight;

        getAIResponse(query).then(response => {
            aiDiv.innerHTML = `<p>${response.message}</p>`;
        })
    }
});

// Background Star Animation (Small Detail)
document.addEventListener('mousemove', (e) => {
    const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
    const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
    document.body.style.backgroundPosition = `${moveX}px ${moveY}px`;
});



/*
    Plot Generator
*/
const plotContainer = document.getElementById('graph-1a');

const initialData = [{
    x: [],
    y: [],
    mode: 'lines+markers',
    name: 'Live Stream',
    line: { color: '#4f46e5', width: 3, shape: 'spline' },
    marker: { size: 8, color: '#4f46e5', opacity: 0.7 },
    fill: 'tozeroy',
    fillcolor: 'rgba(79, 70, 229, 0.1)'
}];

const layout = {
    autosize: true,
    margin: { l: 50, r: 20, t: 20, b: 50 },
    xaxis: { title: 'Timestamp', gridcolor: '#f3f4f6', zeroline: false },
    yaxis: { title: 'Value', gridcolor: '#f3f4f6', zeroline: false },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    hovermode: 'x unified'
};

const config = { responsive: true, displayModeBar: false };
Plotly.newPlot(plotContainer, initialData, layout, config);

// FIX: Ensure this variable name matches the one used in the listener
const socket = io(); 

socket.on("new_data", (data) => {
    // Ensure data.x and data.y exist
    if (data.x !== undefined && data.y !== undefined) {
        const update = {
            x: [[data.x]],
            y: [[data.y]]
        };
        Plotly.extendTraces(plotContainer, update, [0]);
    }
});