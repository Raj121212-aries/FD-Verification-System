let currentPriceChart = null;
let currentRatingChart = null;

document.getElementById("analyze-btn").addEventListener("click", async () => {
    const urlInput = document.getElementById("url-input").value;
    
    if(!urlInput) {
        alert("Please enter a valid URL.");
        return;
    }
    
    const loader = document.getElementById("loader");
    const resultSection = document.getElementById("result-section");
    const analyzeBtn = document.getElementById("analyze-btn");
    
    // UI State
    analyzeBtn.disabled = true;
    resultSection.classList.add("hidden");
    loader.classList.remove("hidden");
    
    try {
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: urlInput })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || "Failed to process request");
        }
        
        // Populate Result
        document.getElementById("product-title").textContent = data.product.title;
        document.getElementById("product-price").textContent = data.product.price;
        document.getElementById("product-discount").textContent = data.features.discount + "%";
        
        document.getElementById("product-rating").textContent = data.product.rating;
        document.getElementById("product-reviews").textContent = data.product.reviews;
        
        document.getElementById("product-open-link").href = urlInput;
        
        const badge = document.getElementById("decision-badge");
        if(data.prediction === "Safe" || data.prediction === "Buy") {
            badge.textContent = "Safe to Buy";
            badge.className = "badge safe";
            document.getElementById("confidence-fill").style.background = "var(--success)";
            document.getElementById("confidence-text").style.color = "var(--success)";
        } else if (data.prediction === "Moderate") {
            badge.textContent = "Exercise Caution";
            badge.className = "badge moderate";
            document.getElementById("confidence-fill").style.background = "var(--warning)";
            document.getElementById("confidence-text").style.color = "var(--warning)";
        } else {
            badge.textContent = "Avoid Buying";
            badge.className = "badge danger";
            document.getElementById("confidence-fill").style.background = "var(--danger)";
            document.getElementById("confidence-text").style.color = "var(--danger)";
        }
        
        // Animate Confidence Bar
        setTimeout(() => {
            document.getElementById("confidence-fill").style.width = data.confidence + "%";
        }, 100);
        
        document.getElementById("confidence-text").textContent = data.confidence + "/100 Safe Score";
        
        // --- Populate Product specific Analytics Graphs ---
        if (currentPriceChart) currentPriceChart.destroy();
        if (currentRatingChart) currentRatingChart.destroy();
        
        // Parse current product numerical values
        const currentPriceStr = data.product.price.replace("₹", "").replace(/,/g, "");
        const currentPriceVal = parseFloat(currentPriceStr) || 0;
        const currentRatingVal = data.features.rating || 0;
        
        let altPrices = [];
        let altRatings = [];
        
        if (data.alternatives && data.alternatives.length > 0) {
            data.alternatives.forEach(alt => {
                const pStr = alt.price.replace("₹", "").replace(/,/g, "");
                altPrices.push(parseFloat(pStr) || 0);
                const rStr = alt.rating.split(" ")[0];
                altRatings.push(parseFloat(rStr) || 0);
            });
        }
        
        // Average Calculations
        const avgAltPrice = altPrices.length > 0 ? (altPrices.reduce((a, b) => a + b, 0) / altPrices.length) : currentPriceVal;
        const avgAltRating = altRatings.length > 0 ? (altRatings.reduce((a, b) => a + b, 0) / altRatings.length) : currentRatingVal;
        
        Chart.defaults.color = "#94a3b8";
        Chart.defaults.font.family = "'Inter', sans-serif";

        const ctxPrice = document.getElementById("productPriceChart").getContext("2d");
        currentPriceChart = new Chart(ctxPrice, {
            type: 'bar',
            data: {
                labels: ['This Product', 'Avg Alternatives'],
                datasets: [{
                    label: 'Price (₹)',
                    data: [currentPriceVal, avgAltPrice],
                    backgroundColor: ['#3b82f6', '#94a3b8'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: "rgba(255,255,255,0.1)" } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

        const ctxRating = document.getElementById("productRatingChart").getContext("2d");
        currentRatingChart = new Chart(ctxRating, {
            type: 'bar',
            data: {
                labels: ['This Product', 'Avg Alternatives'],
                datasets: [{
                    label: 'Rating (stars)',
                    data: [currentRatingVal, avgAltRating],
                    backgroundColor: ['#f59e0b', '#94a3b8'],
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, max: 5, grid: { color: "rgba(255,255,255,0.1)" } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

        
        // Populate Safety Pros & Cons
        const prosList = document.getElementById("pros-list");
        const consList = document.getElementById("cons-list");
        prosList.innerHTML = "";
        consList.innerHTML = "";
        
        if (data.safety_evaluation) {
            data.safety_evaluation.pros.forEach(i => {
                let li = document.createElement("li");
                li.textContent = i;
                prosList.appendChild(li);
            });
            data.safety_evaluation.cons.forEach(i => {
                let li = document.createElement("li");
                li.textContent = i;
                consList.appendChild(li);
            });
        }
        
        // Populate Alternatives
        const altsGrid = document.getElementById("alternatives-grid");
        altsGrid.innerHTML = "";
        if (data.alternatives && data.alternatives.length > 0) {
            data.alternatives.forEach(alt => {
                let div = document.createElement("div");
                div.className = "alternative-item";
                div.innerHTML = `
                    ${alt.image ? `<img src="${alt.image}" alt="">` : ""}
                    <div style="font-size: 0.9rem;">${alt.title}</div>
                    <div class="price">${alt.price}</div>
                    <div style="color:var(--warning);font-size:0.8rem;">★ ${alt.rating}</div>
                    <a href="${alt.link}" target="_blank" class="btn-outline" style="padding:0.3rem 0.6rem; margin-top:0.5rem; display:inline-block; font-size:0.8rem;">View</a>
                `;
                altsGrid.appendChild(div);
            });
        } else {
             altsGrid.innerHTML = "<p style='grid-column: 1/-1; color: var(--text-muted);'>No better alternatives found.</p>";
        }
        
        // Show result
        loader.classList.add("hidden");
        resultSection.classList.remove("hidden");
        
    } catch (e) {
        loader.classList.add("hidden");
        alert(e.message);
    } finally {
        analyzeBtn.disabled = false;
        loadHistory();
    }
});

// History Loading
async function loadHistory() {
    try {
        const res = await fetch("/api/history");
        const data = await res.json();
        
        const historySection = document.getElementById("history-section");
        const historyList = document.getElementById("history-list");
        
        if (data && data.length > 0) {
            historySection.classList.remove("hidden");
            historyList.innerHTML = "";
            data.forEach(item => {
                let div = document.createElement("div");
                div.className = "history-item";
                
                let decisionColor = "var(--warning)";
                if (item.decision === "Safe" || item.decision === "Buy") decisionColor = "var(--success)";
                else if (item.decision === "Risky" || item.decision === "Not Buy") decisionColor = "var(--danger)";
                
                div.innerHTML = `
                    <div style="flex:1;">
                        <div class="history-item-title">${item.title}</div>
                        <div class="history-item-details">Price: ${item.price} • Rating: ${item.rating}</div>
                    </div>
                    <div style="text-align:right;">
                        <strong style="color: ${decisionColor}">${item.decision}</strong><br>
                        <a href="${item.url}" target="_blank" style="color:var(--primary); font-size:0.8rem;">Link</a>
                    </div>
                `;
                historyList.appendChild(div);
            });
        }
    } catch(e) {
        console.error("Error loading history:", e);
    }
}

// Load on page ready
window.addEventListener("DOMContentLoaded", loadHistory);
