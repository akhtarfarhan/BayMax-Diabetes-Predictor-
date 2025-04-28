const form = document.getElementById('signupForm');
const usernameInput = document.getElementById('username');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const password2Input = document.getElementById('password2');

// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fallback: Get CSRF token from the form's hidden input
function getCsrfTokenFromForm() {
    const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfInput ? csrfInput.value : null;
}

const setError = (element, message) => {
    const errorElement = document.getElementById(`${element.id}-error`);
    errorElement.textContent = message;
    element.classList.add('error-border');
};

const clearError = (element) => {
    const errorElement = document.getElementById(`${element.id}-error`);
    errorElement.textContent = '';
    element.classList.remove('error-border');
};

const validatePassword = (password) => {
    const minLength = password.length >= 8;
    const hasCapital = /[A-Z]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    return { minLength, hasCapital, hasSpecial, hasNumber };
};

const getPasswordErrorMessage = (validation) => {
    if (!validation.minLength) return 'Password must be at least 8 characters long';
    if (!validation.hasCapital) return 'Password must contain at least one capital letter';
    if (!validation.hasSpecial) return 'Password must contain at least one special character';
    if (!validation.hasNumber) return 'Password must contain at least one number';
    return '';
};

const validateForm = () => {
    let isValid = true;
    if (!usernameInput.value.trim()) {
        setError(usernameInput, 'Username is required');
        isValid = false;
    } else if (usernameInput.value.trim().length < 3) {
        setError(usernameInput, 'Username must be at least 3 characters');
        isValid = false;
    } else {
        clearError(usernameInput);
    }
    if (!emailInput.value.trim()) {
        setError(emailInput, 'Email is required');
        isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(emailInput.value)) {
        setError(emailInput, 'Email is invalid');
        isValid = false;
    } else {
        clearError(emailInput);
    }
    const passwordValidation = validatePassword(passwordInput.value);
    if (!passwordInput.value) {
        setError(passwordInput, 'Password is required');
        isValid = false;
    } else if (!passwordValidation.minLength || !passwordValidation.hasCapital || 
               !passwordValidation.hasSpecial || !passwordValidation.hasNumber) {
        setError(passwordInput, getPasswordErrorMessage(passwordValidation));
        isValid = false;
    } else {
        clearError(passwordInput);
    }
    if (!password2Input.value) {
        setError(password2Input, 'Please re-type your password');
        isValid = false;
    } else if (passwordInput.value !== password2Input.value) {
        setError(password2Input, 'Passwords do not match');
        isValid = false;
    } else {
        clearError(password2Input);
    }
    return isValid;
};

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (validateForm()) {
        const formData = new FormData(form);
        
        // Try to get CSRF token from cookies, fall back to form
        let csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            csrfToken = getCsrfTokenFromForm();
        }

        if (!csrfToken) {
            setError(usernameInput, 'CSRF token missing. Please refresh the page.');
            return;
        }

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server did not return JSON');
            }

            const data = await response.json();
            
            if (data.success) {
                window.location.href = data.redirect_url;
            } else if (data.errors) {
                Object.entries(data.errors).forEach(([field, message]) => {
                    const input = document.getElementById(field);
                    if (input) {
                        setError(input, message);
                    } else {
                        setError(usernameInput, message);
                    }
                });
            } else {
                setError(usernameInput, 'Signup failed. Please try again.');
            }
        } catch (error) {
            setError(usernameInput, 'Network error or server issue. Please try again.');
        }
    }
});

[usernameInput, emailInput, passwordInput, password2Input].forEach(input => {
    input.addEventListener('input', () => {
        if (input === usernameInput && input.value.trim()) {
            clearError(input);
        }
        if (input === emailInput && input.value.trim() && /\S+@\S+\.\S+/.test(input.value)) {
            clearError(input);
        }
        if (input === passwordInput) {
            const validation = validatePassword(input.value);
            if (input.value && validation.minLength && validation.hasCapital && 
                validation.hasSpecial && validation.hasNumber) {
                clearError(input);
            }
        }
        if (input === password2Input && input.value && passwordInput.value === input.value) {
            clearError(input);
        }
    });
});