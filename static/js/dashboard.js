document.addEventListener('DOMContentLoaded', function() {
    console.log('dashboard.js loaded and executed successfully');
});

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
document.addEventListener('DOMContentLoaded', function () {
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                navLinks.classList.remove('active');
            }
        });
    }
});

// Chatbot Toggle
const chatbotButton = document.getElementById('chatbotButton');
const chatbotWindow = document.getElementById('chatbotWindow');
const closeButton = document.getElementById('closeButton');

if (chatbotButton && chatbotWindow && closeButton) {
    chatbotButton.addEventListener('click', () => {
        chatbotWindow.classList.toggle('active');
    });

    closeButton.addEventListener('click', () => {
        chatbotWindow.classList.remove('active');
    });
}

// Send Message
document.addEventListener('DOMContentLoaded', function () {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatbotBody = document.getElementById('chatbotBody');

    if (chatInput && sendButton && chatbotBody) {
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
    }
});

// Glucose Chart
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('glucoseChart');
    if (!ctx) {
        console.log('Glucose chart canvas not found');
        return;
    }

    const chartCtx = ctx.getContext('2d');

    fetch('/api/glucose-data/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
        }
    })
    .then(response => {
        if (!response.ok) {
            response.text().then(text => {
                console.error('Fetch response:', text);
            });
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Glucose data received:', data);
        if (!data || !Array.isArray(data) || data.length === 0) {
            console.log('No glucose data available');
            ctx.style.display = 'none';
            const cardContent = ctx.closest('.card-content');
            if (cardContent) {
                cardContent.innerHTML = '<p>No glucose data available yet. Make a prediction to see your trends.</p>';
            }
            return;
        }

        // Convert dates to numerical values for x-axis (days since first date)
        const dates = data.map(item => new Date(item.date));
        const firstDate = new Date(Math.min(...dates.map(date => new Date(date).getTime())));
        const glucoseData = data.map(item => ({
            x: Math.floor((new Date(item.date) - firstDate) / (1000 * 60 * 60 * 24)), // Days since first date
            y: item.glucose
        }));

        // Get the latest glucose value for annotation
        const latestGlucose = glucoseData[glucoseData.length - 1].y;

        // Get theme colors
        const isDarkMode = document.documentElement.getAttribute('data-theme') === 'dark';
        const lineColor = isDarkMode ? 'rgba(255, 206, 86, 0.9)' : 'rgba(255, 206, 86, 0.7)';
        const trendColor = isDarkMode ? 'rgba(255, 255, 255, 0.8)' : 'rgba(0, 0, 0, 0.8)';
        const gridColor = isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)';
        const annotationColor = isDarkMode ? 'rgba(255, 255, 255, 0.9)' : 'rgba(0, 0, 0, 0.9)';

        // Initialize Chart.js with line chart and annotation
        new Chart(chartCtx, {
            type: 'line',
            data: {
                datasets: [{
                    label: 'Glucose Levels',
                    data: glucoseData,
                    borderColor: lineColor,
                    backgroundColor: lineColor,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
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
                        max: glucoseData[glucoseData.length - 1].x + 1
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
                    annotation: {
                        annotations: [{
                            type: 'line',
                            mode: 'vertical',
                            scaleID: 'x',
                            value: glucoseData[glucoseData.length - 1].x,
                            borderColor: annotationColor,
                            borderWidth: 2,
                            label: {
                                enabled: true,
                                content: `Glucose: ${latestGlucose} mg/dL`,
                                position: 'top',
                                backgroundColor: annotationColor,
                                color: isDarkMode ? 'black' : 'white',
                                font: { size: 12 }
                            }
                        }]
                    },
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
                        display: true
                    }
                }
            }
        });
    })
    .catch(error => {
        console.error('Error fetching glucose data:', error);
        ctx.style.display = 'none';
        const cardContent = ctx.closest('.card-content');
        if (cardContent) {
            cardContent.innerHTML = '<p>Error loading glucose trends. Please try again later.</p>';
        }
    });
});

// Function to get CSRF token
function getCsrfToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return value;
    }
    return '';
}