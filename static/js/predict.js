document.addEventListener('DOMContentLoaded', function() {
    // Show/hide pregnancies field based on gender
    const maleRadio = document.getElementById('male');
    const femaleRadio = document.getElementById('female');
    const pregnanciesGroup = document.getElementById('pregnanciesGroup');

    if (maleRadio && femaleRadio && pregnanciesGroup) {
        maleRadio.addEventListener('change', function() {
            if (this.checked) {
                pregnanciesGroup.style.display = 'none';
            }
        });

        femaleRadio.addEventListener('change', function() {
            if (this.checked) {
                pregnanciesGroup.style.display = 'block';
            }
        });

        // Initialize pregnancies field visibility based on default selection
        if (maleRadio.checked) {
            pregnanciesGroup.style.display = 'none';
        } else if (femaleRadio.checked) {
            pregnanciesGroup.style.display = 'block';
        }
    } else {
        console.warn('Gender radio buttons or pregnancies group not found on the page.');
    }

    // Form validation
    const predictionForm = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('resultContainer');
    const resultValue = document.getElementById('resultValue');
    const resultDescription = document.getElementById('resultDescription');
    const newPredictionBtn = document.getElementById('newPredictionBtn');

    if (!predictionForm || !resultContainer || !resultValue || !resultDescription) {
        console.error('Required form elements are missing.');
        return;
    }

    // Validation constraints
    const constraints = {
        age: { min: 18, max: 120 },
        weight: { min: 30, max: 300 },
        height: { min: 100, max: 250 },
        pregnancies: { min: 0, max: 20 },
        glucose: { min: 70, max: 400 },
        bloodPressure: { min: 60, max: 200 },
        skinThickness: { min: 10, max: 100 },
        insulin: { min: 0, max: 846 },
        diabetesPedigree: { min: 0, max: 2.5 }
    };

    // Validate a field
    function validateField(field, min, max) {
        const value = parseFloat(field.value);
        const errorId = field.id + 'Error';
        const errorElement = document.getElementById(errorId);
        
        if (!errorElement) {
            console.warn(`Error element for ${field.id} not found.`);
            return false;
        }

        if (isNaN(value) || value < min || value > max) {
            field.classList.add('error');
            errorElement.classList.add('visible');
            return false;
        } else {
            field.classList.remove('error');
            errorElement.classList.remove('visible');
            return true;
        }
    }

    // Validate on input
    for (const fieldName in constraints) {
        const field = document.getElementById(fieldName);
        if (field) {
            field.addEventListener('input', function() {
                validateField(this, constraints[fieldName].min, constraints[fieldName].max);
            });
        } else {
            console.warn(`Field ${fieldName} not found in the form.`);
        }
    }

    // Form submission
    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate all fields
        let isValid = true;
        for (const fieldName in constraints) {
            const field = document.getElementById(fieldName);
            if (field && (fieldName !== 'pregnancies' || (femaleRadio && femaleRadio.checked))) {
                const fieldValid = validateField(field, constraints[fieldName].min, constraints[fieldName].max);
                isValid = isValid && fieldValid;
            }
        }

        if (isValid) {
            // Collect form data
            const formData = {
                gender: document.querySelector('input[name="gender"]:checked')?.value || '',
                age: document.getElementById('age').value,
                weight: document.getElementById('weight').value, // Removed 'atque'
                height: document.getElementById('height').value,
                pregnancies: femaleRadio && femaleRadio.checked ? document.getElementById('pregnancies')?.value : null,
                glucose: document.getElementById('glucose').value,
                bloodPressure: document.getElementById('bloodPressure').value,
                skinThickness: document.getElementById('skinThickness').value,
                insulin: document.getElementById('insulin').value,
                diabetesPedigree: document.getElementById('diabetesPedigree').value
            };

            // Validate gender selection
            if (!formData.gender) {
                alert('Please select a gender.');
                return;
            }

            // Get the URL from data attributes
            const section = document.querySelector('.prediction-section');
            if (!section) {
                console.error('Prediction section not found.');
                alert('An error occurred. Please try again.');
                return;
            }

            const url = section.classList.contains('predict-unauthenticated')
                ? section.dataset.predictUnauthenticatedUrl
                : section.dataset.predictUrl;

            // Debug: Log the URL and CSRF token
            console.log('Fetching URL:', url);
            console.log('CSRF Token:', getCsrfToken());

            // Send data to server
            fetch(url, {
                method: 'POST',
                headers: { // Removed '-using'
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ data: formData })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Show results inline
                    resultValue.textContent = `${data.risk_level}`;
                    resultDescription.innerHTML = `
                        Your predicted diabetes risk is <strong>${data.risk_level}</strong> 
                        with a <strong>${(data.diabetes_probability * 100).toFixed(1)}% chance of developing diabetes</strong>.
                        <br><strong>BMI:</strong> ${data.bmi.toFixed(1)}
                    `; // Fixed HTML syntax

                    // Display health tips
                    const healthTips = document.getElementById('healthTips');
                    const healthTipsList = document.getElementById('healthTipsList');
                    if (healthTips && healthTipsList && data.health_tips) {
                        healthTipsList.innerHTML = '';
                        data.health_tips.forEach(tip => {
                            const li = document.createElement('li');
                            li.textContent = tip;
                            healthTipsList.appendChild(li);
                        });
                        healthTips.style.display = 'block';
                    }

                    resultContainer.style.display = 'block';
                    predictionForm.parentElement.style.display = 'none';

                    // Dynamically update "Your Information" card if on dashboard page
                    const yourInfoSummary = document.getElementById('yourInfoSummary');
                    if (yourInfoSummary) {
                        // Fetch user name and email from session or server if available
                        const userName = sessionStorage.getItem('user_name') || 'User'; // Fallback if not available
                        const userEmail = sessionStorage.getItem('email') || 'Not provided'; // Fallback if not available
                        yourInfoSummary.innerHTML = `
                            <p>Name: ${userName}</p>
                            <p>Email: ${userEmail}</p>
                            <p>Age: ${formData.age}</p>
                            <p>Gender: ${formData.gender.charAt(0).toUpperCase() + formData.gender.slice(1)}</p>
                        `;
                    }

                    // Redirect to dashboard after 5 seconds using the URL from the server response
                    setTimeout(() => {
                        window.location.href = data.dashboard_url || '/dashboard/';
                    }, 5000);
                } else {
                    alert('Error: ' + (data.message || 'Unknown error occurred'));
                }
            })
            .catch(error => {
                console.error('Fetch Error:', error);
                alert('An error occurred while processing your prediction. Please try again.');
            });
        }
    });

    // New prediction button
    if (newPredictionBtn) {
        newPredictionBtn.addEventListener('click', function() {
            predictionForm.reset();
            predictionForm.parentElement.style.display = 'block';
            resultContainer.style.display = 'none';
            
            // Reset any errors
            const errorElements = document.querySelectorAll('.error');
            errorElements.forEach(function(element) {
                element.classList.remove('error');
            });
            
            const errorMessages = document.querySelectorAll('.error-message');
            errorMessages.forEach(function(element) {
                element.classList.remove('visible');
            });
            
            // Hide pregnancies field if male is selected
            if (maleRadio && maleRadio.checked) {
                pregnanciesGroup.style.display = 'none';
            }

            // Hide health tips
            const healthTips = document.getElementById('healthTips');
            if (healthTips) {
                healthTips.style.display = 'none';
            }
        });
    } else {
        console.warn('New prediction button not found.');
    }

    // Function to get CSRF token
    function getCsrfToken() {
        const csrfInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput && csrfInput.value) {
            return csrfInput.value;
        }
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === name) return value;
        }
        console.warn('CSRF token not found.');
        return '';
    }
});