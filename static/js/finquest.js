// static/js/finquest.js

document.addEventListener('DOMContentLoaded', function () {
    // Плавные переходы для кнопок (мобильный UX)
    const buttons = document.querySelectorAll('button, .btn, a.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', function (e) {
            this.classList.add('disabled');
            this.innerHTML += ' <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            // Разблокировать через 1 сек, если форма не отправлена (защита от двойного клика)
            setTimeout(() => {
                if (this.classList.contains('disabled')) {
                    this.classList.remove('disabled');
                    this.innerHTML = this.innerHTML.replace(' <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>', '');
                }
            }, 1000);
        });
    });

    // Поддержка "назад" на мобильных
    const backButton = document.querySelector('[href$="/"]');
    if (backButton && window.history.length > 2) {
        backButton.addEventListener('click', function (e) {
            e.preventDefault();
            window.history.back();
        });
    }

    // Анимация карточек (опционально)
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(10px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.3s, transform 0.3s';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
});