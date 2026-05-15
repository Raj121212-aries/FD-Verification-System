let pieChart, histogramChart, lineChart, scatterChart;

Chart.defaults.color = "#94a3b8";
Chart.defaults.font.family = "'Inter', sans-serif";

function initCharts() {
    const pieCtx = document.getElementById("pieChart").getContext("2d");
    pieChart = new Chart(pieCtx, {
        type: 'doughnut',
        data: {
            labels: ["Safe", "Moderate", "Risky"],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    const histCtx = document.getElementById("histogramChart").getContext("2d");
    histogramChart = new Chart(histCtx, {
        type: 'bar',
        data: {
            labels: ["0-1", "1-2", "2-3", "3-4", "4-5"],
            datasets: [{
                label: 'Number of Products',
                data: [0, 0, 0, 0, 0],
                backgroundColor: "#3b82f6",
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.1)" } }, x: { grid: { display: false } } }
        }
    });

    const lineCtx = document.getElementById("lineChart").getContext("2d");
    lineChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Scans Per Day',
                data: [],
                borderColor: "#8b5cf6",
                backgroundColor: "rgba(139, 92, 246, 0.2)",
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.1)" } }, x: { grid: { color: "rgba(255,255,255,0.1)" } } }
        }
    });

    const scatterCtx = document.getElementById("scatterChart").getContext("2d");
    scatterChart = new Chart(scatterCtx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Safe',
                    data: [],
                    backgroundColor: "#10b981"
                },
                {
                    label: 'Moderate',
                    data: [],
                    backgroundColor: "#f59e0b"
                },
                {
                    label: 'Risky',
                    data: [],
                    backgroundColor: "#ef4444"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { 
                y: { title: { display: true, text: 'Discount %' }, grid: { color: "rgba(255,255,255,0.1)" } },
                x: { display: false }
            }
        }
    });
}

async function updateData() {
    try {
        const response = await fetch("/analytics");
        if(!response.ok) return;
        
        const data = await response.json();
        
        // Update Total Items
        document.getElementById("total-items").textContent = data.total_items;
        
        // Update Pie
        let safeCount = (data.pie_chart["Safe"] || 0) + (data.pie_chart["Buy"] || 0);
        let moderateCount = (data.pie_chart["Moderate"] || 0);
        let riskyCount = (data.pie_chart["Risky"] || 0) + (data.pie_chart["Not Buy"] || 0);
        
        pieChart.data.datasets[0].data = [safeCount, moderateCount, riskyCount];
        pieChart.update();
        
        // Update Histogram
        histogramChart.data.datasets[0].data = Object.values(data.histogram);
        histogramChart.update();
        
        // Update Line
        lineChart.data.labels = data.line_chart.labels;
        lineChart.data.datasets[0].data = data.line_chart.values;
        lineChart.update();
        
        // Update Scatter
        const safeScatter = (data.scatter.safe || []).map((v, i) => ({ x: i, y: v }));
        const moderateScatter = (data.scatter.moderate || []).map((v, i) => ({ x: i + safeScatter.length, y: v }));
        const riskyScatter = (data.scatter.risky || []).map((v, i) => ({ x: i + safeScatter.length + moderateScatter.length, y: v }));
        
        scatterChart.data.datasets[0].data = safeScatter;
        scatterChart.data.datasets[1].data = moderateScatter;
        scatterChart.data.datasets[2].data = riskyScatter;
        scatterChart.update();
        
    } catch(e) {
        console.error("Dashboard update failed:", e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    updateData(); // Initial load
    
    // Auto refresh every 5 seconds
    setInterval(updateData, 5000);
});
