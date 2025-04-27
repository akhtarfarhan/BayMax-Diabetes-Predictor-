const form = document.getElementById('loginForm');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

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
    console.log(`CSRF Token from cookies (${name}):`, cookieValue);
    return cookieValue;
}

// Fallback: Get CSRF token from the form's hidden input
function getCsrfTokenFromForm() {
    const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
    const token = csrfInput ? csrfInput.value : null;
    console.log('CSRF Token from form:', token);
    return token;
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
    const minLength = password.length >= 6;
    const hasCapital = /[A-Z]/.test(password);
    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    return { minLength, hasCapital, hasSpecial, hasNumber };
};

const getPasswordErrorMessage = (validation) => {
    if (!validation.minLength) return 'Password must be at least 6 characters long';
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
    } else {
        clearError(usernameInput);
    }
    const passwordValidation = validatePassword(passwordInput.value);
    if (!passwordInput.value) {
        setError(passwordInput, 'Password is required');
        isValid = false;
    } else if (!passwordValidation.minLength || !passwordValidation.hasCapital || !passwordValidation.hasSpecial || !passwordValidation.hasNumber) {
        setError(passwordInput, getPasswordErrorMessage(passwordValidation));
        isValid = false;
    } else {
        clearError(passwordInput);
    }
    return isValid;
};

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (validateForm()) {
        const formData = {
            username: usernameInput.value,
            password: passwordInput.value
        };
        console.log('Submitting formData:', formData);

        // Try to get CSRF token from cookies, fall back to form
        let csrfToken = getCookie('csrftoken');
        if (!csrfToken) {
            console.log('Falling back to form for CSRF token');
            csrfToken = getCsrfTokenFromForm();
        }

        if (!csrfToken) {
            setError(usernameInput, 'CSRF token missing. Please refresh the page.');
            return;
        }

        try {
            const response = await fetch('/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(formData)
            });
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Server response:', data);
            if (data.success) {
                console.log('Redirecting to:', data.redirect_url);
                window.location.href = data.redirect_url;
            } else {
                setError(usernameInput, data.error || 'Login failed. Please try again.');
            }
        } catch (error) {
            console.error('Fetch error:', error);
            setError(usernameInput, 'Network error. Please try again.');
        }
    }
});

[usernameInput, passwordInput].forEach(input => {
    input.addEventListener('input', () => {
        if (input === usernameInput && input.value.trim()) {
            clearError(input);
        }
        if (input === passwordInput) {
            const validation = validatePassword(input.value);
            if (input.value && validation.minLength && validation.hasCapital && validation.hasSpecial && validation.hasNumber) {
                clearError(input);
            }
        }
    });
});