document.addEventListener('DOMContentLoaded', function() {
    // Get authentication status from body data attribute
    var isAuthenticated = document.body.getAttribute('data-user-authenticated') === 'true';
    var userName = document.body.getAttribute('data-user-name') || '';
    
    console.log('User authenticated:', isAuthenticated);
    console.log('User name:', userName);
    
    // Function to show login alert - Bright Theme
    function showLoginAlert() {
        Swal.fire({
            title: 'Login Required',
            text: 'Please log in to enroll for this course. Don\'t have an account? Register now!',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#667eea',
            cancelButtonColor: '#6c757d',
            confirmButtonText: '<i class="fa-solid fa-right-to-bracket"></i> Login',
            cancelButtonText: '<i class="fa-regular fa-times"></i> Cancel',
            background: 'white',
            color: '#1a1a2e',
            backdrop: 'rgba(0, 0, 0, 0.4)'
        }).then(function(result) {
            if (result.isConfirmed) {
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
            }
        });
    }
    
    // Function to show loading alert
    function showLoadingAlert() {
        Swal.fire({
            title: 'Processing...',
            text: 'Please wait while we process your enrollment.',
            allowOutsideClick: false,
            didOpen: function() {
                Swal.showLoading();
            },
            background: 'white',
            color: '#1a1a2e'
        });
    }
    
    // Function to show success alert - Bright Theme
    function showSuccessAlert(message) {
        Swal.fire({
            title: 'Enrollment Successful! 🎉',
            text: message || 'You have successfully enrolled in the ICT & Software Development Program. Check your email for details.',
            icon: 'success',
            confirmButtonColor: '#667eea',
            confirmButtonText: '<i class="fa-regular fa-circle-check"></i> Great!',
            background: 'white',
            color: '#1a1a2e',
            backdrop: 'rgba(0, 0, 0, 0.4)',
            timer: 4000,
            timerProgressBar: true
        });
    }
    
    // Function to show error alert - Bright Theme
    function showErrorAlert(message) {
        Swal.fire({
            title: 'Enrollment Failed',
            text: message || 'Something went wrong. Please try again later.',
            icon: 'error',
            confirmButtonColor: '#ef4444',
            confirmButtonText: '<i class="fa-regular fa-times"></i> Try Again',
            background: 'white',
            color: '#1a1a2e',
            backdrop: 'rgba(0, 0, 0, 0.4)'
        });
    }
    
    // Function to handle enrollment
    async function processEnrollment() {
        try {
            // Get CSRF token from cookie
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
            
            const csrftoken = getCookie('csrftoken');
            
            const response = await fetch('/courses/enroll/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    course_id: 1,
                    course_name: 'ICT & Software Development Program'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showSuccessAlert(data.message);
            } else {
                showErrorAlert(data.message);
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorAlert('Network error. Please check your connection and try again.');
        }
    }
    
    // Main enroll click handler
    function onEnrollClick(event) {
        event.preventDefault();
        
        if (!isAuthenticated) {
            showLoginAlert();
        } else {
            // Show loading then process enrollment
            showLoadingAlert();
            setTimeout(function() {
                Swal.close();
                processEnrollment();
            }, 500);
        }
    }
    
    // Attach event listeners to enroll buttons
    var heroEnrollBtn = document.querySelector('.enroll-btn-hero');
    var ctaEnrollBtn = document.querySelector('.enroll-btn-cta');
    
    if (heroEnrollBtn) {
        heroEnrollBtn.addEventListener('click', onEnrollClick);
    }
    
    if (ctaEnrollBtn) {
        ctaEnrollBtn.addEventListener('click', onEnrollClick);
    }
});