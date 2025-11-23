// FinQuest Tutorial System
class FinQuestTutorial {
    constructor() {
        this.currentStep = 0;
        this.isMobile = document.body.classList.contains('mobile-view') || window.innerWidth <= 768;
        
        // Разные подсказки для мобильных и десктопа
        const desktopSteps = [
            {
                target: '.user-card',
                title: '👋 Добро пожаловать!',
                content: 'Это ваша карточка профиля. Здесь отображается ваш аватар, имя и текущий статус в игре.',
                position: 'bottom'
            },
            {
                target: '.badge.bg-primary',
                title: '⭐ Очки опыта',
                content: 'Очки начисляются за прохождение уровней. Чем сложнее уровень и выше результат, тем больше очков!',
                position: 'bottom'
            },
            {
                target: '.badge.bg-warning',
                title: '🪙 Монеты',
                content: 'Монеты можно тратить на подсказки во время прохождения уровней. Зарабатывайте их, выполняя задания!',
                position: 'bottom'
            },
            {
                target: '.badge.bg-success',
                title: '🏆 Достижения',
                content: 'Получайте достижения за различные успехи: прохождение тем, серии дней обучения и особые задания!',
                position: 'bottom'
            },
            {
                target: '.main-category-card:first-child',
                title: '📚 Категории обучения',
                content: 'Выберите категорию для изучения. Начните с "Основы финансов" — там самые важные базовые темы!',
                position: 'right'
            },
            {
                target: '.category-stats',
                title: '📊 Прогресс обучения',
                content: 'Здесь видно, сколько уровней вы уже прошли в каждой категории. Стремитесь к 100%!',
                position: 'top'
            },
            {
                target: 'a[href*="notifications"]',
                title: '🔔 Уведомления',
                content: 'Здесь появятся уведомления о новых достижениях, наградах и важных событиях.',
                position: 'bottom'
            },
            {
                target: 'a[href*="profile"]',
                title: '⚙️ Профиль и настройки',
                content: 'В профиле можно изменить аватар, посмотреть статистику и настроить приложение под себя.',
                position: 'bottom'
            }
        ];
        
        // Короткие подсказки для мобильных устройств
        const mobileSteps = [
            {
                target: '.welcome-section',
                title: '👋 Привет!',
                content: 'Это твой профиль с аватаром и статусом.',
                position: 'bottom'
            },
            {
                target: '.stat-card:first-child',
                title: '⭐ Очки',
                content: 'Зарабатывай очки за прохождение уровней!',
                position: 'bottom'
            },
            {
                target: '.stat-card:nth-child(2)',
                title: '🪙 Монеты',
                content: 'Трать монеты на подсказки в игре.',
                position: 'bottom'
            },
            {
                target: '.stat-card:last-child',
                title: '🏆 Достижения',
                content: 'Получай награды за успехи!',
                position: 'bottom'
            },
            {
                target: '.bottom-nav-item:first-child',
                title: '🏠 Главная',
                content: 'Здесь твоя статистика и прогресс.',
                position: 'top'
            },
            {
                target: '.bottom-nav-item:nth-child(2)',
                title: '📚 Обучение',
                content: 'Выбери категорию и начни учиться!',
                position: 'top'
            },
            {
                target: '.bottom-nav-item:nth-child(3)',
                title: '🏆 Достижения',
                content: 'Смотри все свои награды здесь.',
                position: 'top'
            },
            {
                target: '.bottom-nav-item:last-child',
                title: '👤 Профиль',
                content: 'Настрой аватар и посмотри статистику.',
                position: 'top'
            }
        ];
        
        this.steps = this.isMobile ? mobileSteps : desktopSteps;
        this.isActive = false;
        this.overlay = null;
        this.tooltip = null;
        this.guide = null;
    }

    start() {
        if (this.isActive) return;
        
        // Проверяем, показывался ли уже туториал
        if (localStorage.getItem('finquest_tutorial_completed')) {
            return;
        }

        this.isActive = true;
        this.showWelcomeModal();
    }

    showWelcomeModal() {
        const modal = document.createElement('div');
        modal.className = 'tutorial-welcome-modal';
        
        // Разный контент для мобильных и десктопа
        const welcomeContent = this.isMobile ? `
            <div class="welcome-content">
                <div class="welcome-character">
                    <div class="character-avatar-large">
                        <i class="fa-solid fa-graduation-cap"></i>
                    </div>
                </div>
                <h2 class="welcome-title">Добро пожаловать! 🎉</h2>
                <div class="welcome-description">
                    <p><strong>FinQuest</strong> — обучение финансам в игровой форме!</p>
                    <div class="welcome-features">
                        <div class="feature-item">
                            <i class="fa-solid fa-gamepad"></i>
                            <span>Игровое обучение</span>
                        </div>
                        <div class="feature-item">
                            <i class="fa-solid fa-trophy"></i>
                            <span>Награды</span>
                        </div>
                    </div>
                    <p class="mt-3">Покажу, как пользоваться!</p>
                </div>
                <button class="btn btn-primary btn-lg welcome-btn" onclick="this.parentElement.parentElement.remove(); tutorialInstance.startTutorial();">
                    <i class="fa-solid fa-rocket me-2"></i>Поехали!
                </button>
                <button class="btn btn-outline-secondary btn-sm mt-2" onclick="this.parentElement.parentElement.remove(); tutorialInstance.complete();">
                    Пропустить
                </button>
            </div>
        ` : `
            <div class="welcome-content">
                <div class="welcome-character">
                    <div class="character-avatar-large">
                        <i class="fa-solid fa-graduation-cap"></i>
                    </div>
                </div>
                <h2 class="welcome-title">Добро пожаловать в FinQuest! 🎉</h2>
                <div class="welcome-description">
                    <p><strong>FinQuest</strong> — это увлекательное приложение для изучения финансовой грамотности!</p>
                    <div class="welcome-features">
                        <div class="feature-item">
                            <i class="fa-solid fa-gamepad"></i>
                            <span>Обучение в игровой форме</span>
                        </div>
                        <div class="feature-item">
                            <i class="fa-solid fa-trophy"></i>
                            <span>Достижения и награды</span>
                        </div>
                        <div class="feature-item">
                            <i class="fa-solid fa-chart-line"></i>
                            <span>Отслеживание прогресса</span>
                        </div>
                        <div class="feature-item">
                            <i class="fa-solid fa-brain"></i>
                            <span>Практические навыки</span>
                        </div>
                    </div>
                    <p class="mt-3">Давайте я покажу, как пользоваться приложением!</p>
                </div>
                <button class="btn btn-primary btn-lg welcome-btn" onclick="this.parentElement.parentElement.remove(); tutorialInstance.startTutorial();">
                    <i class="fa-solid fa-rocket me-2"></i>Начать знакомство
                </button>
                <button class="btn btn-outline-secondary btn-sm mt-2" onclick="this.parentElement.parentElement.remove(); tutorialInstance.complete();">
                    Пропустить
                </button>
            </div>
        `;
        
        modal.innerHTML = welcomeContent;
        document.body.appendChild(modal);
    }

    startTutorial() {
        this.createOverlay();
        this.createGuide();
        this.showStep(0);
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tutorial-overlay';
        document.body.appendChild(this.overlay);
    }

    createGuide() {
        this.guide = document.createElement('div');
        this.guide.className = 'tutorial-guide';
        this.guide.innerHTML = `
            <div class="guide-content">
                <h4 class="guide-title"></h4>
                <p class="guide-text"></p>
                <div class="guide-navigation">
                    <button class="btn btn-outline-secondary btn-sm mt-2" id="prevBtn" disabled>
                        <i class="fa-solid fa-arrow-left"></i> Назад
                    </button>
                    <span class="guide-counter"></span>
                    <button class="btn btn-sm btn-primary" id="nextBtn">
                        Далее <i class="fa-solid fa-arrow-right"></i>
                    </button>
                </div>
                <div class="guide-actions">
                    <button class="btn btn-outline-secondary btn-sm mt-2" id="skipBtn">
                        <i class="fa-solid fa-times"></i> Пропустить
                    </button>
                    <button class="btn btn-sm btn-success" id="completeBtn" style="display: none;">
                        <i class="fa-solid fa-check"></i> Понятно!
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(this.guide);

        // Event listeners
        document.getElementById('prevBtn').addEventListener('click', () => this.prevStep());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextStep());
        document.getElementById('skipBtn').addEventListener('click', () => this.skip());
        document.getElementById('completeBtn').addEventListener('click', () => this.complete());
    }

    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) {
            this.complete();
            return;
        }

        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];
        const target = document.querySelector(step.target);

        if (!target) {
            console.warn(`Tutorial step ${stepIndex}: Element not found: ${step.target}`);
            // Пропускаем этот шаг и переходим к следующему
            setTimeout(() => this.showStep(stepIndex + 1), 100);
            return;
        }

        // Highlight target
        this.highlightTarget(target);

        // Update guide content
        document.querySelector('.guide-title').textContent = step.title;
        document.querySelector('.guide-text').textContent = step.content;
        document.querySelector('.guide-counter').textContent = `${stepIndex + 1} из ${this.steps.length}`;

        // Update buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const skipBtn = document.getElementById('skipBtn');
        const completeBtn = document.getElementById('completeBtn');

        prevBtn.disabled = stepIndex === 0;
        
        if (stepIndex === this.steps.length - 1) {
            // Последний шаг - скрываем все кнопки кроме "Готов начать обучение!"
            nextBtn.style.display = 'none';
            prevBtn.style.display = 'none';
            skipBtn.style.display = 'none';
            completeBtn.style.display = 'inline-block';
            completeBtn.innerHTML = '<i class="fa-solid fa-check me-2"></i>Готов начать обучение!';
            completeBtn.className = 'btn btn-success btn-lg';
        } else {
            // Обычные шаги - показываем все кнопки
            nextBtn.style.display = 'inline-block';
            prevBtn.style.display = 'inline-block';
            skipBtn.style.display = 'inline-block';
            completeBtn.style.display = 'none';
        }

        // Position guide
        this.positionGuide(target, step.position);
    }

    highlightTarget(target) {
        // Remove previous highlights
        document.querySelectorAll('.tutorial-highlight').forEach(el => el.remove());

        const rect = target.getBoundingClientRect();
        const highlight = document.createElement('div');
        highlight.className = 'tutorial-highlight';
        highlight.style.cssText = `
            position: fixed;
            top: ${rect.top - 4}px;
            left: ${rect.left - 4}px;
            width: ${rect.width + 8}px;
            height: ${rect.height + 8}px;
            border: 3px solid #ffc107;
            border-radius: 8px;
            background: rgba(255, 193, 7, 0.1);
            pointer-events: none;
            z-index: 1000;
            animation: tutorialPulse 2s ease-in-out infinite;
        `;
        document.body.appendChild(highlight);
    }

    positionGuide(target, position) {
        const rect = target.getBoundingClientRect();
        const guide = this.guide;
        const guideRect = guide.getBoundingClientRect();

        let top, left;

        switch (position) {
            case 'top':
                top = rect.top - guideRect.height - 20;
                left = rect.left + (rect.width / 2) - (guideRect.width / 2);
                break;
            case 'bottom':
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (guideRect.width / 2);
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (guideRect.height / 2);
                left = rect.left - guideRect.width - 20;
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (guideRect.height / 2);
                left = rect.right + 20;
                break;
            default:
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (guideRect.width / 2);
        }

        // Ensure guide stays within viewport
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        if (left < 20) left = 20;
        if (left + guideRect.width > viewportWidth - 20) {
            left = viewportWidth - guideRect.width - 20;
        }
        if (top < 20) top = 20;
        if (top + guideRect.height > viewportHeight - 20) {
            top = viewportHeight - guideRect.height - 20;
        }

        guide.style.cssText = `
            position: fixed;
            top: ${top}px;
            left: ${left}px;
            z-index: 1001;
        `;
    }

    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        }
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }

    skip() {
        this.complete();
    }

    complete() {
        localStorage.setItem('finquest_tutorial_completed', 'true');
        this.cleanup();
    }

    cleanup() {
        if (this.overlay) {
            this.overlay.remove();
            this.overlay = null;
        }
        if (this.guide) {
            this.guide.remove();
            this.guide = null;
        }
        document.querySelectorAll('.tutorial-highlight').forEach(el => el.remove());
        this.isActive = false;
    }
}

// Global tutorial instance
let tutorialInstance = null;

// Initialize tutorial when page loads
document.addEventListener('DOMContentLoaded', function() {
    tutorialInstance = new FinQuestTutorial();
    
    // Check if this is the first visit by looking for the trigger element
    const firstVisitTrigger = document.getElementById('first-visit-trigger');
    if (firstVisitTrigger) {
        // This is the first visit, start tutorial automatically
        setTimeout(() => {
            tutorialInstance.start();
        }, 1000);
    }

});

// Global function to restart tutorial
function restartTutorial() {
    if (tutorialInstance) {
        tutorialInstance.cleanup();
    }
    localStorage.removeItem('finquest_tutorial_completed');
    tutorialInstance = new FinQuestTutorial();
    tutorialInstance.start();
}
