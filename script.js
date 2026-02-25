/* ============================================
   GlucosenseAI — Scripts
   Typewriter animation, scroll reveals, FAQ
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ─────────────────────────────────────────
    // TYPEWRITER ANIMATION — Hero Title
    // Letters appear one after another.
    // Re-triggers when scrolling back into view.
    // ─────────────────────────────────────────

    const heroTitle = document.getElementById('hero-title');
    const titleText = 'GlucosenseAI';
    let typewriterTimeout = null;
    let isAnimating = false;

    // Create letter spans
    function buildLetters() {
        heroTitle.innerHTML = '';
        for (let i = 0; i < titleText.length; i++) {
            const span = document.createElement('span');
            span.classList.add('letter');
            span.textContent = titleText[i];
            heroTitle.appendChild(span);
        }
    }

    function animateLetters() {
        if (isAnimating) return;
        isAnimating = true;

        const letters = heroTitle.querySelectorAll('.letter');

        // Reset all letters
        letters.forEach(letter => {
            letter.classList.remove('visible');
        });

        // Animate one by one
        letters.forEach((letter, index) => {
            typewriterTimeout = setTimeout(() => {
                letter.classList.add('visible');
                if (index === letters.length - 1) {
                    isAnimating = false;
                }
            }, 100 + index * 80);
        });
    }

    function resetLetters() {
        if (typewriterTimeout) {
            clearTimeout(typewriterTimeout);
        }
        isAnimating = false;
        const letters = heroTitle.querySelectorAll('.letter');
        letters.forEach(letter => {
            letter.classList.remove('visible');
        });
    }

    buildLetters();

    // Observe hero section for visibility
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateLetters();
            } else {
                resetLetters();
            }
        });
    }, {
        threshold: 0.5
    });

    heroObserver.observe(document.getElementById('hero'));

    // ─────────────────────────────────────────
    // SCROLL REVEAL — Fade-in elements
    // ─────────────────────────────────────────

    const revealElements = document.querySelectorAll('.reveal');

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(el => {
        revealObserver.observe(el);
    });

    // ─────────────────────────────────────────
    // FAQ ACCORDION
    // ─────────────────────────────────────────

    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all
            faqItems.forEach(faq => faq.classList.remove('active'));

            // Toggle current
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // ─────────────────────────────────────────
    // SMOOTH SCROLL — Anchor links
    // ─────────────────────────────────────────

    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

});
