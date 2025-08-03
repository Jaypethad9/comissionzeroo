    document.addEventListener('DOMContentLoaded', function () {
        const faqItems = document.querySelectorAll('.faq-item');

        faqItems.forEach(item => {
            item.querySelector('.faq-question').addEventListener('click', () => {
                // Optional: Close others
                faqItems.forEach(i => {
                    if (i !== item) i.classList.remove('active');
                });

                // Toggle current
                item.classList.toggle('active');
            });
        });
    });