

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

const maxDataPoints = 30

let xData = []
let yData = []


const initialData = [{
    x: xData,
    y: yData,
    mode: 'lines+markers',
    name: 'Live Stream',
    line: { color: '#4f46e5', width: 3, shape: 'spline' },
    marker: { size: 8, color: '#3778f0ff', opacity: 1 },
    fill: 'tozeroy',
    fillcolor: 'rgba(79, 70, 229, 0.1)'
}];

const layout = {
    autosize: true,
    margin: { l: 15, r: 15, t: 10, b: 15 },
    xaxis: { title: 'Timestamp', gridcolor: '#f3f4f677', zeroline: false },
    yaxis: { title: 'Value', gridcolor: '#f3f4f677', zeroline: false },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    hovermode: 'x unified',
    hoverlabel: {
        bgcolor: "#1e1e1e5a",
        font: {color: "#fff"}
    }
};

const config = { responsive: true, displayModeBar: false };
Plotly.newPlot(plotContainer, initialData, layout, config);

const socket = io.connect(); 

let statusButton = document.getElementById("backendStatus");

socket.on("connect", () => {
    console.log("Connected to Backend");
    console.log('Socket ID:', socket.id);
    statusButton.textContent = "● Link Ativado e funcional";
})
socket.on("disconnect", () => {
    console.log("Backend Disconnected");
    statusButton.textContent = "● Link não operacional";
})

socket.on("new_data", (data) => {
    console.log("New data Triggered");
    console.log("Received data: ", data);
    xData.push(data.x);
    yData.push(data.y);
    
    if (xData.length > maxDataPoints) {
        xData.shift();
        yData.shift();
    }

    Plotly.update(plotContainer, {
        x: [xData],
        y: [yData]
    }, {}, [0]);
});

statusButton.addEventListener('click', () => {
    console.log("Pressed, emiting");
    socket.emit('start_stream');
    console.log("finished emiting");
});
statusButton.addEventListener('dblclick', () => {
    socket.emit('stop_stream');
});

socket.on("status", (msg) => {
    console.log("Status: ", msg.message);
});
