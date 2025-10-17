// FinQuest Tutorial System
class FinQuestTutorial {
    constructor() {
        this.currentStep = 0;
        this.steps = [
            {
                target: '.navbar-brand',
                title: '🏠 Главная навигация',
                content: 'Это логотип FinQuest. Нажмите на него, чтобы вернуться на главную страницу.',
                position: 'bottom'
            },
            {
                target: '.user-card .card',
                title: '👤 Ваш профиль',
                content: 'Здесь вы видите свой аватар, имя, текущий уровень и прогресс, а также очки, монеты и достижения.',
                position: 'bottom'
            },
            {
                target: '.section-title',
                title: '📚 Темы обучения',
                content: 'Здесь представлены все темы: накопления, безопасность, противодействие мошенничеству и финансовые цели.',
                position: 'bottom'
            },
            {
                target: '.card:first-of-type',
                title: '🎮 Выберите тему',
                content: 'Нажмите на любую карточку темы, чтобы увидеть доступные уровни. Начните с первой темы!',
                position: 'right'
            }
        ];
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
        modal.innerHTML = `
            <div class="welcome-content">
                <div class="welcome-character">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <h3>Добро пожаловать в FinQuest! 🎉</h3>
                <p>Это приложение поможет вам изучить финансовую грамотность в игровой форме.</p>
                <p>Давайте я покажу, как им пользоваться!</p>
                <button class="btn btn-primary btn-lg" onclick="this.parentElement.parentElement.remove(); tutorialInstance.startTutorial();">
                    <i class="fa-solid fa-play me-2"></i>Начать обучение
                </button>
            </div>
        `;
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
        this.overlay.innerHTML = `
            <div class="tutorial-character">
                <div class="character-avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="character-speech">
                    <div class="speech-bubble">
                        <div class="speech-content"></div>
                        <div class="speech-arrow"></div>
                    </div>
                </div>
            </div>
        `;
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
                    <button class="btn btn-sm btn-outline-light" id="prevBtn" disabled>
                        <i class="fa-solid fa-arrow-left"></i> Назад
                    </button>
                    <span class="guide-counter"></span>
                    <button class="btn btn-sm btn-primary" id="nextBtn">
                        Далее <i class="fa-solid fa-arrow-right"></i>
                    </button>
                </div>
                <div class="guide-actions">
                    <button class="btn btn-sm btn-outline-light" id="skipBtn">
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

        // Update character speech
        document.querySelector('.speech-content').textContent = step.content;

        // Update buttons
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const completeBtn = document.getElementById('completeBtn');

        prevBtn.disabled = stepIndex === 0;
        nextBtn.style.display = stepIndex === this.steps.length - 1 ? 'none' : 'inline-block';
        completeBtn.style.display = stepIndex === this.steps.length - 1 ? 'inline-block' : 'none';

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
