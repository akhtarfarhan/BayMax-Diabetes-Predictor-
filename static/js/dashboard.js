document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');

    mobileMenuButton.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
});

console.log("this one is httin")
// Navbar scroll effect
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Mobile menu functionality
const mobileMenuButton = document.querySelector('.mobile-menu-button');
const navLinks = document.querySelector('.nav-links');

mobileMenuButton.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

// Reset mobile menu on window resize
window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        navLinks.classList.remove('active');
    }
});

// Chatbot Toggle
const chatbotButton = document.getElementById('chatbotButton');
const chatbotWindow = document.getElementById('chatbotWindow');
const closeButton = document.getElementById('closeButton');

chatbotButton.addEventListener('click', () => {
    chatbotWindow.classList.toggle('active');
});

closeButton.addEventListener('click', () => {
    chatbotWindow.classList.remove('active');
});

// Send Message
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');
const chatbotBody = document.getElementById('chatbotBody');

sendButton.addEventListener('click', () => {
    const message = chatInput.value.trim();
    if (message) {
        const userMessage = document.createElement('div');
        userMessage.classList.add('message', 'user-message');
        userMessage.innerHTML = `<p>${message}</p>`;
        chatbotBody.appendChild(userMessage);

        chatInput.value = '';
        chatbotBody.scrollTop = chatbotBody.scrollHeight;

        setTimeout(() => {
            const botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot-message');
            botMessage.innerHTML = `<p>Thanks for your message! How can I assist you further?</p>`;
            chatbotBody.appendChild(botMessage);
            chatbotBody.scrollTop = chatbotBody.scrollHeight;
        }, 1000);
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendButton.click();
    }
});

// Handle final submission
const submitButton = document.getElementById('submitPrediction');
if (submitButton) {
    submitButton.addEventListener('click', () => {
        let isValid = true;
        for (const [key, value] of Object.entries(formData)) {
            if (key !== 'gender' && (!ranges[key] || parseFloat(value) < ranges[key].min || parseFloat(value) > ranges[key].max)) {
                isValid = false;
                const range = ranges[key];
                alert(`Invalid value for ${key}: ${value}. Must be between ${range.min} and ${range.max} ${range.unit}.`);
                break;
            }
        }
        if (isValid) {
            console.log('Final Form Data:', formData);
            fetch('/predict/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(), // Add a function to get CSRF token
                },
                body: JSON.stringify({ data: formData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect_url; // Redirect to dashboard
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });
}

// Function to get CSRF token from cookies
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return '';
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart.js
    const ctx = document.getElementById('glucoseChart');
    if (!ctx) return; // Exit if no predictions exist

    const chartCtx = ctx.getContext('2d');

    // Fetch glucose data from the backend
    fetch('/api/glucose-data/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        // Assuming data is an array of objects with { date: "YYYY-MM-DD", glucose: number }
        // Convert dates to numerical values for x-axis (days since first date)
        const firstDate = new Date(data[0].date);
        const scatterData = data.map(item => {
            const date = new Date(item.date);
            const daysSinceStart = (date - firstDate) / (1000 * 60 * 60 * 24); // Convert to days
            return { x: daysSinceStart, y: item.glucose };
        });

        // Calculate trend line (linear regression)
        const n = scatterData.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        for (let i = 0; i < n; i++) {
            sumX += scatterData[i].x;
            sumY += scatterData[i].y;
            sumXY += scatterData[i].x * scatterData[i].y;
            sumXX += scatterData[i].x * scatterData[i].x;
        }
        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        // Trend line data
        const trendLineData = [
            { x: 0, y: intercept },
            { x: scatterData[n-1].x, y: slope * scatterData[n-1].x + intercept }
        ];

        // Initialize Chart.js
        new Chart(chartCtx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Glucose Levels',
                        data: scatterData,
                        backgroundColor: 'rgba(255, 206, 86, 0.7)', // Yellow points
                        borderColor: 'rgba(255, 206, 86, 1)',
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false
                    },
                    {
                        label: 'Trend Line',
                        data: trendLineData,
                        type: 'line',
                        fill: false,
                        borderColor: 'rgba(0, 0, 0, 0.8)', // Black trend line
                        borderWidth: 2,
                        pointRadius: 0,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Days Since First Measurement',
                            color: 'var(--primary)',
                            font: { size: 14 }
                        },
                        grid: { display: false },
                        min: 0,
                        max: scatterData[n-1].x + 10
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Glucose (mg/dL)',
                            color: 'var(--primary)',
                            font: { size: 14 }
                        },
                        beginAtZero: true,
                        suggestedMax: 200,
                        grid: { color: 'rgba(0, 0, 0, 0.1)' }
                    }
                },
                plugins: {
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'var(--primary)',
                        titleColor: 'var(--white)',
                        bodyColor: 'var(--white)',
                        borderColor: 'var(--mint)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `Glucose: ${context.parsed.y} mg/dL`;
                            }
                        }
                    },
                    legend: {
                        display: false // Hide legend for cleaner look
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error fetching glucose data:', error);
    });

    // Function to get CSRF token from cookies
    function getCsrfToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return value;
        }
        return '';
    }
});

document.addEventListener('DOMContentLoaded', function () {
    // Send Message
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatbotBody = document.getElementById('chatbotBody');

    sendButton.addEventListener('click', () => {
        const message = chatInput.value.trim();
        if (message) {
            const userMessage = document.createElement('div');
            userMessage.classList.add('message', 'user-message');
            userMessage.innerHTML = `<p>${message}</p>`;
            chatbotBody.appendChild(userMessage);

            chatInput.value = '';
            chatbotBody.scrollTop = chatbotBody.scrollHeight;

            setTimeout(() => {
                const botMessage = document.createElement('div');
                botMessage.classList.add('message', 'bot-message');
                botMessage.innerHTML = `<p>Thanks for your message! How can I assist you further?</p>`;
                chatbotBody.appendChild(botMessage);
                chatbotBody.scrollTop = chatbotBody.scrollHeight;
            }, 1000);
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart.js
    const ctx = document.getElementById('glucoseChart');
    if (!ctx) return; // Exit if no predictions exist

    const chartCtx = ctx.getContext('2d');

    // Fetch glucose data from the backend
    fetch('/api/glucose-data/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => response.json())
    .then(data => {
        // Convert dates to numerical values for x-axis (days since first date)
        const firstDate = new Date(data[0].date);
        const scatterData = data.map(item => {
            const date = new Date(item.date);
            const daysSinceStart = (date - firstDate) / (1000 * 60 * 60 * 24); // Convert to days
            return { x: daysSinceStart, y: item.glucose };
        });

        // Calculate trend line (linear regression)
        const n = scatterData.length;
        let sumX = 0, sumY = 0, sumXY = 0, sumXX = 0;
        for (let i = 0; i < n; i++) {
            sumX += scatterData[i].x;
            sumY += scatterData[i].y;
            sumXY += scatterData[i].x * scatterData[i].y;
            sumXX += scatterData[i].x * scatterData[i].x;
        }
        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        // Trend line data
        const trendLineData = [
            { x: 0, y: intercept },
            { x: scatterData[n-1].x, y: slope * scatterData[n-1].x + intercept }
        ];

        // Get theme colors
        const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
        const scatterColor = isDarkMode ? 'rgba(255, 206, 86, 0.9)' : 'rgba(255, 206, 86, 0.7)';
        const trendLineColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';

        // Initialize Chart.js
        new Chart(chartCtx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Glucose Levels',
                        data: scatterData,
                        backgroundColor: scatterColor,
                        borderColor: scatterColor,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        showLine: false
                    },
                    {
                        label: 'Trend Line',
                        data: trendLineData,
                        type: 'line',
                        fill: false,
                        borderColor: trendLineColor,
                        borderWidth: 2,
                        pointRadius: 0,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: {
                            display: true,
                            text: 'Days Since First Measurement',
                            color: 'var(--primary)',
                            font: { size: 14 }
                        },
                        grid: { display: false },
                        min: 0,
                        max: scatterData[n-1].x + 10
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Glucose (mg/dL)',
                            color: 'var(--primary)',
                            font: { size: 14 }
                        },
                        beginAtZero: true,
                        suggestedMax: 200,
                        grid: { color: gridColor }
                    }
                },
                plugins: {
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'var(--primary)',
                        titleColor: 'var(--white)',
                        bodyColor: 'var(--white)',
                        borderColor: 'var(--mint)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                return `Glucose: ${context.parsed.y} mg/dL`;
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error fetching glucose data:', error);
    });

    // Function to get CSRF token from cookies
    function getCsrfToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return value;
        }
        return '';
    }
});