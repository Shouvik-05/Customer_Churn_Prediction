document.addEventListener('DOMContentLoaded', function () {

    // Close mobile menu when a link is clicked
    const navLinks = document.querySelector('.navbar-links');
    if (navLinks) {
        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('open');
            });
        });
    }

    // Animate probability bar on result page
    const probFill = document.querySelector('.probability-fill');
    if (probFill) {
        const targetWidth = probFill.style.width;
        probFill.style.width = '0%';
        setTimeout(function () {
            probFill.style.width = targetWidth;
        }, 100);
    }

    // Form submit button loading state
    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('.submit-btn');
            if (btn) {
                btn.textContent = 'Predicting...';
                btn.disabled = true;
                btn.style.opacity = '0.7';
            }
        });
    });

    // Close navbar when clicking outside
    document.addEventListener('click', function (e) {
        if (navLinks && navLinks.classList.contains('open')) {
            if (!e.target.closest('.navbar')) {
                navLinks.classList.remove('open');
            }
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

});
