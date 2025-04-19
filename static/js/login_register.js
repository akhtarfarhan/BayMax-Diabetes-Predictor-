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

  const usernamePattern = /^[a-zA-Z0-9_.-@]{3,20}$/;
  const reservedWords = ['admin', 'root', 'test', 'baymax', 'system'];
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,20}$/;

  // Username validation
  usernameInput.addEventListener('input', function () {
      const value = this.value.trim();
      if (!value) {
          usernameError.textContent = 'Username is required.';
          usernameError.style.display = 'block';
      } else if (reservedWords.includes(value.toLowerCase())) {
          usernameError.textContent = 'This username is reserved.';
          usernameError.style.display = 'block';
      } else if (!usernamePattern.test(value)) {
          usernameError.textContent = 'Username must be 3-20 characters long and contain only letters, numbers, _, -, ., or @.';
          usernameError.style.display = 'block';
      } else if (/\s/.test(value)) {
          usernameError.textContent = 'Username cannot contain spaces.';
          usernameError.style.display = 'block';
      } else {
          usernameError.style.display = 'none';
      }
  });

  // Email validation
  emailInput.addEventListener('input', function () {
      const value = this.value.trim();
      if (!value) {
          emailError.textContent = 'Email is required.';
          emailError.style.display = 'block';
      } else if (!emailPattern.test(value)) {
          emailError.textContent = 'Please enter a valid email address.';
          emailError.style.display = 'block';
      } else {
          emailError.style.display = 'none';
      }
  });

  // Password validation
  passwordInput.addEventListener('input', function () {
      const value = this.value;
      const usernameValue = usernameInput.value.trim();
      if (!value) {
          passwordError.textContent = 'Password is required.';
          passwordError.style.display = 'block';
      } else if (value.toLowerCase() === usernameValue.toLowerCase() && usernameValue) {
          passwordError.textContent = 'Password cannot be the same as username.';
          passwordError.style.display = 'block';
      } else if (!passwordPattern.test(value)) {
          passwordError.textContent = 'Password must be 8-20 characters, with at least one uppercase, one lowercase, one number, and one special character (!@#$%^&*).';
          passwordError.style.display = 'block';
      } else {
          passwordError.style.display = 'none';
      }
      updatePasswordStrength(value);
  });

  // Retype password validation
  retypePasswordInput.addEventListener('input', function () {
      if (this.value !== passwordInput.value) {
          retypePasswordError.textContent = 'Passwords do not match.';
          retypePasswordError.style.display = 'block';
      } else {
          retypePasswordError.style.display = 'none';
      }
  });

  // Password strength indicator
  function updatePasswordStrength(password) {
      const strengthMeter = document.createElement('div');
      strengthMeter.className = 'password-strength';
      strengthMeter.style.marginTop = '0.5rem';
      strengthMeter.style.height = '5px';
      strengthMeter.style.borderRadius = '2px';

      const strengthText = document.createElement('span');
      strengthText.style.fontSize = '0.875rem';
      strengthText.style.marginTop = '0.25rem';
      strengthText.style.display = 'block';

      let strength = 0;
      if (password.length >= 8) strength++;
      if (/[A-Z]/.test(password)) strength++;
      if (/[a-z]/.test(password)) strength++;
      if (/\d/.test(password)) strength++;
      if (/[!@#$%^&*]/.test(password)) strength++;

      if (strength <= 2) {
          strengthMeter.style.backgroundColor = 'red';
          strengthText.textContent = 'Weak';
      } else if (strength <= 4) {
          strengthMeter.style.backgroundColor = 'orange';
          strengthText.textContent = 'Medium';
      } else {
          strengthMeter.style.backgroundColor = 'green';
          strengthText.textContent = 'Strong';
      }

      const existingMeter = passwordInput.parentElement.querySelector('.password-strength');
      if (existingMeter) existingMeter.remove();
      const existingText = passwordInput.parentElement.querySelector('span');
      if (existingText) existingText.remove();
      passwordInput.parentElement.appendChild(strengthMeter);
      passwordInput.parentElement.appendChild(strengthText);
  }

  // Password visibility toggle
  const togglePassword = document.createElement('button');
  togglePassword.type = 'button';
  togglePassword.textContent = 'Show';
  togglePassword.style.position = 'absolute';
  togglePassword.style.right = '10px';
  togglePassword.style.top = '50%';
  togglePassword.style.transform = 'translateY(-50%)';
  togglePassword.style.background = 'none';
  togglePassword.style.border = 'none';
  togglePassword.style.cursor = 'pointer';
  passwordInput.parentElement.style.position = 'relative';
  passwordInput.parentElement.appendChild(togglePassword);

  togglePassword.addEventListener('click', function () {
      const type = passwordInput.type === 'password' ? 'text' : 'password';
      passwordInput.type = type;
      this.textContent = type === 'password' ? 'Show' : 'Hide';
  });

  // Form submission validation
  signupForm.addEventListener('submit', function (e) {
      let isValid = true;

      // Validate username
      const usernameValue = usernameInput.value.trim();
      if (!usernamePattern.test(usernameValue) || reservedWords.includes(usernameValue.toLowerCase()) || /\s/.test(usernameValue)) {
          isValid = false;
          usernameError.style.display = 'block';
      }

      // Validate email
      const emailValue = emailInput.value.trim();
      if (!emailPattern.test(emailValue)) {
          isValid = false;
          emailError.style.display = 'block';
      }

      // Validate password
      const passwordValue = passwordInput.value;
      if (!passwordPattern.test(passwordValue) || (passwordValue.toLowerCase() === usernameValue.toLowerCase() && usernameValue)) {
          isValid = false;
          passwordError.style.display = 'block';
      }

      // Validate retype password
      if (passwordValue !== retypePasswordInput.value) {
          isValid = false;
          retypePasswordError.style.display = 'block';
      }

      if (!isValid) {
          e.preventDefault();
      }
  });

  // Navigation with animation
  window.navigate = function(event, url, direction) {
      event.preventDefault();
      const container = document.querySelector('.container');
      container.classList.add(`slide-out-${direction}`);
      setTimeout(() => {
          window.location.href = url;
      }, 750);
  };
});