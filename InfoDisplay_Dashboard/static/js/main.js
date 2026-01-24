
const socket = io();

if (window.location.pathname === "/charts") {
    const plotContainer1A = document.getElementById('graph-1a');
    const plotContainer1B = document.getElementById('graph-1b');
    const plotContainer2A = document.getElementById('graph-2a');
    const plotContainer2B = document.getElementById('graph-2b');

    const maxDataPoints = 30

    let xData = []

    let yData1A = []
    let yData1B = []
    let yData2A = []
    let yData2B = []



    const initialData = [{
        x: xData,
        y: yData1A,
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
    Plotly.newPlot(plotContainer1A, initialData, layout, config);
    Plotly.newPlot(plotContainer1B, initialData, layout, config);
    Plotly.newPlot(plotContainer2A, initialData, layout, config);
    Plotly.newPlot(plotContainer2B, initialData, layout, config);

    // ================
    // SOCKET HANDLING
    // ================


    let statusButton = document.getElementById("backendStatus");
    let deviationContainer1 = document.getElementById("deviation1");
    let deviationContainer2 = document.getElementById("deviation2");

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

        yData1A.push(data.y1a);
        yData1B.push(data.y1b);
        yData2A.push(data.y2a);
        yData2B.push(data.y2b);
        
        if (xData.length > maxDataPoints) {
            xData.shift();

            yData1A.shift();
            yData1B.shift();
            yData2A.shift();
            yData2B.shift();
        }

        Plotly.update(plotContainer1A, {
            x: [xData],
            y: [yData1A]
        }, {}, [0]);
        Plotly.update(plotContainer1B, {
            x: [xData],
            y: [yData1B]
        }, {}, [0]);
        Plotly.update(plotContainer2A, {
            x: [xData],
            y: [yData2A]
        }, {}, [0]);
        Plotly.update(plotContainer2B, {
            x: [xData],
            y: [yData2B]
        }, {}, [0]);


        let maxDeviation1 = 0;
        let maxDeviation2 = 0;

        if (data.y1b != 0 || data.y2b != 0) {
            maxDeviation1 = (Math.abs(data.y1b - data.y1a) / data.y1b) * 100
            maxDeviation2 = (Math.abs(data.y2b - data.y2a) / data.y2b) * 100
        }
        
        console.log("Dev1: ", maxDeviation1)
        console.log("Dev2: ", maxDeviation2)

        if (+deviationContainer1.textContent < maxDeviation1) {
            deviationContainer1.textContent = maxDeviation1.toFixed(2)
        }
        if (+deviationContainer2.textContent < maxDeviation2) {
            deviationContainer2.textContent = maxDeviation2.toFixed(2)
        }

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

    
    currentImageHolder = document.getElementById("currentImage");
    const lastImage = localStorage.getItem('lastImage');
    if (lastImage) {
        currentImageHolder.setAttribute('src', lastImage);
    }

    socket.on("new_image", (image) => {
        currentImageHolder.setAttribute('src', `${image.url}`);
        
        localStorage.setItem('lastImage', `${image.url}`);
    });
}
else if (window.location.pathname === "/image-display") {
    socket.on("new_image", (image) => {
        const frame = document.createElement('div');
        frame.className = 'image-frame';
        console.log("Got image in js: ", image.url)
        frame.innerHTML = `
            <img src="${image.url}" loading="lazy">
            <div class="timestamp">${image.timestamp || '00:00:00.000'}</div>
        `;
        grid.appendChild(frame);
    });
}
