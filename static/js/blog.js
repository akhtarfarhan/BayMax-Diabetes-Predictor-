document.addEventListener('DOMContentLoaded', function () {
    // Mobile Menu Toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');

    if (mobileMenuButton && navLinks) {
        mobileMenuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            console.log('Mobile menu toggled:', navLinks.classList.contains('active') ? 'Open' : 'Closed');
        });
    } else {
        console.error('Mobile menu elements not found:', { mobileMenuButton, navLinks });
    }

    // Theme Toggle
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    if (themeToggle && themeIcon) {
        // Load saved theme from localStorage
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeUI(savedTheme);
        console.log('Initial theme loaded:', savedTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeUI(newTheme);
            console.log('Theme toggled to:', newTheme);
        });
    } else {
        console.error('Theme toggle elements not found:', { themeToggle, themeIcon });
    }

    function updateThemeUI(theme) {
        if (theme === 'light') {
            themeIcon.innerHTML = `
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            `;
        } else {
            themeIcon.innerHTML = `
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            `;
        }
    }

    // Blog Creation Chatbox
    const blogCreationButton = document.getElementById('blogCreationButton');
    const blogCreationWindow = document.getElementById('blogCreationWindow');
    const closeCreationButton = document.getElementById('closeCreationButton');
    const blogTitle = document.getElementById('blogTitle');
    const blogContent = document.getElementById('blogContent');
    const blogImage = document.getElementById('blogImage');
    const imagePreview = document.getElementById('imagePreview');
    const submitBlogButton = document.getElementById('submitBlogButton');
    const blogGrid = document.querySelector('.blog-grid');

    if (blogCreationButton && blogCreationWindow && closeCreationButton) {
        blogCreationButton.addEventListener('click', () => {
            blogCreationWindow.classList.toggle('active');
            if (blogCreationWindow.classList.contains('active')) {
                blogTitle.focus();
            }
            console.log('Blog creation window toggled:', blogCreationWindow.classList.contains('active') ? 'Open' : 'Closed');
        });

        closeCreationButton.addEventListener('click', () => {
            blogCreationWindow.classList.remove('active');
            console.log('Blog creation window closed');
        });
    } else {
        console.error('Blog creation elements not found:', { blogCreationButton, blogCreationWindow, closeCreationButton });
    }

    // Preview image when selected
    if (blogImage && imagePreview) {
        blogImage.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                    console.log('Image preview updated:', imagePreview.src);
                };
                reader.readAsDataURL(file);
            } else {
                imagePreview.style.display = 'none';
                console.log('Image preview cleared');
            }
        });
    } else {
        console.error('Image preview elements not found:', { blogImage, imagePreview });
    }

    // Submit blog via AJAX
    if (submitBlogButton && blogGrid) {
        submitBlogButton.addEventListener('click', () => {
            const title = blogTitle.value.trim();
            const content = blogContent.value.trim();
            const file = blogImage.files[0];

            if (title && content) {
                const formData = new FormData();
                formData.append('data', JSON.stringify({ title, content }));
                if (file) {
                    formData.append('image', file);
                }

                fetch('/blog/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const newBlogCard = document.createElement('article');
                        newBlogCard.classList.add('blog-card');
                        newBlogCard.innerHTML = `
                            <img src="${data.image_url || '{% static "images/diabetes-image.png" %}'}" alt="${data.title}">
                            <div class="blog-card-content">
                                <h2>${data.title}</h2>
                                <p>${data.content}</p>
                                <div class="blog-meta">
                                    <span>${data.author_display} on ${data.created_at}</span>
                                </div>
                            </div>
                        `;

                        newBlogCard.style.opacity = '0';
                        newBlogCard.style.transform = 'translateY(20px)';
                        blogGrid.insertBefore(newBlogCard, blogGrid.firstChild);

                        setTimeout(() => {
                            newBlogCard.style.transition = 'all 0.5s ease';
                            newBlogCard.style.opacity = '1';
                            newBlogCard.style.transform = 'translateY(0)';
                        }, 100);

                        blogTitle.value = '';
                        blogContent.value = '';
                        blogImage.value = '';
                        imagePreview.style.display = 'none';
                        blogCreationWindow.classList.remove('active');

                        alert('Your blog post has been submitted successfully!');
                        console.log('Blog submitted successfully:', data);
                    } else {
                        alert(data.message || 'Failed to submit blog post.');
                        console.error('Blog submission failed:', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error submitting blog:', error);
                    alert('An error occurred while submitting your blog.');
                });
            } else {
                alert('Please fill in all required fields (title and content)!');
                console.warn('Blog submission aborted: Missing title or content');
            }
        });
    } else {
        console.error('Blog submission elements not found:', { submitBlogButton, blogGrid });
    }

    // Allow Ctrl + Enter to submit
    if (blogContent) {
        blogContent.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                submitBlogButton.click();
                console.log('Ctrl + Enter triggered blog submission');
            }
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
});