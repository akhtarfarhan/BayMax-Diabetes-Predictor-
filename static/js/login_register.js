document.addEventListener('DOMContentLoaded', function () {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const signinForm = document.getElementById('signinForm');
    
    // Display Django messages as error messages if present
    const djangoMessages = document.querySelectorAll('.error-messages .error');
    if (djangoMessages.length > 0) {
        // Focus on username field if there are error messages
        usernameInput.focus();
    }
  
    // Username validation
    usernameInput.addEventListener('input', function () {
        const value = this.value.trim();
        if (!value) {
            usernameError.textContent = 'Username is required.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else {
            // Check if username exists via AJAX
            checkUsername(value);
        }
    });
  
    // Password validation
    passwordInput.addEventListener('input', function() {
        const value = this.value.trim();
        if (!value) {
            passwordError.textContent = 'Password is required.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else if (value.length < 8) {
            passwordError.textContent = 'Password must be at least 8 characters.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else {
            passwordError.textContent = 'Password format is valid';
            passwordError.style.color = 'green';
            passwordError.style.display = 'block';
        }
    });
  
    // Function to check username availability
    function checkUsername(username) {
        fetch('/check_username/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({username: username})
        })
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                usernameError.textContent = 'Username is valid';
                usernameError.style.color = 'green';
                usernameError.style.display = 'block';
            } else {
                usernameError.textContent = 'Invalid username';
                usernameError.style.color = 'red';
                usernameError.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            usernameError.textContent = 'Error checking username.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        });
    }
  
    // Helper function to get CSRF token
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
  
    // Form submission validation - simplified to allow server-side validation
    signinForm.addEventListener('submit', function (e) {
        let isValid = true;
  
        // Basic validation
        const usernameValue = usernameInput.value.trim();
        if (!usernameValue) {
            isValid = false;
            usernameError.textContent = 'Username is required.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        }
  
        const passwordValue = passwordInput.value;
        if (!passwordValue) {
            isValid = false;
            passwordError.textContent = 'Password is required.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        }
  
        if (!isValid) {
            e.preventDefault();
        }
        // Allow form submission even with invalid username/password
        // so server can handle authentication and show proper errors
    });
});



// signup
document.addEventListener('DOMContentLoaded', function () {
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const retypePasswordInput = document.getElementById('retype_password');
    
    const usernameError = document.getElementById('usernameError');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const retypePasswordError = document.getElementById('retypePasswordError');
    
    const signupForm = document.getElementById('signupForm');
    
    // Show error messages by default
    usernameError.style.display = 'block';
    emailError.style.display = 'block';
    passwordError.style.display = 'block';
    retypePasswordError.style.display = 'block';
    
    // Initially hide the error messages if they're empty
    if (!usernameError.textContent) usernameError.style.display = 'none';
    if (!emailError.textContent) emailError.style.display = 'none';
    if (!passwordError.textContent) passwordError.style.display = 'none';
    if (!retypePasswordError.textContent) retypePasswordError.style.display = 'none';
    
    // Username validation
    usernameInput.addEventListener('input', function() {
        const value = this.value.trim();
        const usernamePattern = /^[a-zA-Z0-9_.\-@]{3,20}$/;
        const reservedWords = ['admin', 'root', 'test', 'baymax', 'system'];
        
        if (!value) {
            usernameError.textContent = 'Username is required.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else if (value.length < 3) {
            usernameError.textContent = 'Username must be at least 3 characters.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else if (value.length > 20) {
            usernameError.textContent = 'Username cannot exceed 20 characters.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else if (!usernamePattern.test(value)) {
            usernameError.textContent = 'Username can only contain letters, numbers, and _.-@';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else if (value.includes(' ')) {
            usernameError.textContent = 'Username cannot contain spaces.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else if (reservedWords.includes(value.toLowerCase())) {
            usernameError.textContent = 'This username is reserved.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        } else {
            // Check if username already exists via AJAX
            checkUsernameAvailability(value);
        }
    });
    
    // Email validation
    emailInput.addEventListener('input', function() {
        const value = this.value.trim();
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        
        if (!value) {
            emailError.textContent = 'Email is required.';
            emailError.style.color = 'red';
            emailError.style.display = 'block';
        } else if (!emailPattern.test(value)) {
            emailError.textContent = 'Please enter a valid email address.';
            emailError.style.color = 'red';
            emailError.style.display = 'block';
        } else {
            // Check if email already exists via AJAX
            checkEmailAvailability(value);
        }
    });
    
    // Password validation
    passwordInput.addEventListener('input', function() {
        const value = this.value;
        const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,20}$/;
        const commonPasswords = ['password', '12345678', 'qwerty'];
        
        if (!value) {
            passwordError.textContent = 'Password is required.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else if (value.length < 8) {
            passwordError.textContent = 'Password must be at least 8 characters.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else if (value.length > 20) {
            passwordError.textContent = 'Password cannot exceed 20 characters.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else if (!passwordPattern.test(value)) {
            passwordError.textContent = 'Password must include uppercase, lowercase, number, and special character (!@#$%^&*).';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else if (commonPasswords.includes(value.toLowerCase()) || value.toLowerCase().includes(usernameInput.value.toLowerCase())) {
            passwordError.textContent = 'Password is too common or contains your username.';
            passwordError.style.color = 'red';
            passwordError.style.display = 'block';
        } else {
            passwordError.textContent = 'Password meets requirements.';
            passwordError.style.color = 'green';
            passwordError.style.display = 'block';
            
            // Check if retype password matches
            if (retypePasswordInput.value) {
                validatePasswordMatch();
            }
        }
    });
    
    // Confirm password validation
    retypePasswordInput.addEventListener('input', validatePasswordMatch);
    
    function validatePasswordMatch() {
        const password = passwordInput.value;
        const retypePassword = retypePasswordInput.value;
        
        if (!retypePassword) {
            retypePasswordError.textContent = 'Please confirm your password.';
            retypePasswordError.style.color = 'red';
            retypePasswordError.style.display = 'block';
        } else if (password !== retypePassword) {
            retypePasswordError.textContent = 'Passwords do not match.';
            retypePasswordError.style.color = 'red';
            retypePasswordError.style.display = 'block';
        } else {
            retypePasswordError.textContent = 'Passwords match.';
            retypePasswordError.style.color = 'green';
            retypePasswordError.style.display = 'block';
        }
    }
    
    // Check username availability via AJAX
    function checkUsernameAvailability(username) {
        fetch('/check_signup_username/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({username: username})
        })
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                usernameError.textContent = 'Username is available.';
                usernameError.style.color = 'green';
                usernameError.style.display = 'block';
            } else {
                usernameError.textContent = 'Username already taken.';
                usernameError.style.color = 'red';
                usernameError.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            usernameError.textContent = 'Error checking username.';
            usernameError.style.color = 'red';
            usernameError.style.display = 'block';
        });
    }
    
    // Check email availability via AJAX
    function checkEmailAvailability(email) {
        fetch('/check_signup_email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({email: email})
        })
        .then(response => response.json())
        .then(data => {
            if (data.available) {
                emailError.textContent = 'Email is available.';
                emailError.style.color = 'green';
                emailError.style.display = 'block';
            } else {
                emailError.textContent = 'Email already registered.';
                emailError.style.color = 'red';
                emailError.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            emailError.textContent = 'Error checking email.';
            emailError.style.color = 'red';
            emailError.style.display = 'block';
        });
    }
    
    // Helper function to get CSRF token
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
    
    // Form submission validation
    signupForm.addEventListener('submit', function(e) {
        let isValid = true;
        
        // Validate username
        if (usernameError.style.color !== 'green') {
            isValid = false;
        }
        
        // Validate email
        if (emailError.style.color !== 'green') {
            isValid = false;
        }
        
        // Validate password
        if (passwordError.style.color !== 'green') {
            isValid = false;
        }
        
        // Validate password confirmation
        if (retypePasswordError.style.color !== 'green') {
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            alert('Please fix the errors before submitting.');
        }
    });
});