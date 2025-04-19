document.addEventListener('DOMContentLoaded', function() {
    // Show/hide pregnancies field based on gender
    const maleRadio = document.getElementById('male');
    const femaleRadio = document.getElementById('female');
    const pregnanciesGroup = document.getElementById('pregnanciesGroup');

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

    // Form validation
    const predictionForm = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('resultContainer');
    const resultValue = document.getElementById('resultValue');
    const resultDescription = document.getElementById('resultDescription');
    const newPredictionBtn = document.getElementById('newPredictionBtn');

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
        }
    }

    // Form submission
    predictionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate all fields
        let isValid = true;
        for (const fieldName in constraints) {
            const field = document.getElementById(fieldName);
            if (field && (fieldName !== 'pregnancies' || femaleRadio.checked)) {
                const fieldValid = validateField(field, constraints[fieldName].min, constraints[fieldName].max);
                isValid = isValid && fieldValid;
            }
        }

        if (isValid) {
            // Collect form data
            const formData = {
                gender: document.querySelector('input[name="gender"]:checked').value,
                age: document.getElementById('age').value,
                weight: document.getElementById('weight').value,
                height: document.getElementById('height').value,
                pregnancies: femaleRadio.checked ? document.getElementById('pregnancies').value : null,
                glucose: document.getElementById('glucose').value,
                bloodPressure: document.getElementById('bloodPressure').value,
                skinThickness: document.getElementById('skinThickness').value,
                insulin: document.getElementById('insulin').value,
                diabetesPedigree: document.getElementById('diabetesPedigree').value
            };

            // Send data to server
            fetch('/predict/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ data: formData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show result briefly before redirecting
                    resultValue.textContent = `${data.risk_level}`;
                    resultDescription.innerHTML = `
                        Your predicted diabetes risk is <strong>${data.risk_level}</strong> 
                        (${(data.probability * 100).toFixed(1)}% probability). 
                        Redirecting to dashboard...
                    `;
                    resultContainer.style.display = 'block';
                    predictionForm.parentElement.style.display = 'none';
            
                    // Redirect to dashboard after 2 seconds
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 9000);
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => console.error('Error:', error));
        }
    });

    // New prediction button
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
        if (maleRadio.checked) {
            pregnanciesGroup.style.display = 'none';
        }
    });

    // Mobile menu functionality
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', function() {
            navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
        });

        // Reset mobile menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navLinks.style.display = 'flex';
            } else {
                navLinks.style.display = 'none';
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
});

// Add event listener for the new field
const diabetesPedigreeField = document.getElementById('diabetesPedigree');
if (diabetesPedigreeField) {
    diabetesPedigreeField.addEventListener('input', function() {
        validateField(this, constraints.diabetesPedigree.min, constraints.diabetesPedigree.max);
    });
}