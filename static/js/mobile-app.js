// ============================================
// МОБИЛЬНОЕ ПРИЛОЖЕНИЕ - JavaScript
// ============================================

// Регистрация Service Worker для PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(registration => {
        console.log('SW registered:', registration);
      })
      .catch(error => {
        console.log('SW registration failed:', error);
      });
  });
}

// Обработка установки PWA
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Показываем кнопку установки
  const installBtn = document.getElementById('installBtn');
  if (installBtn) {
    installBtn.style.display = 'block';
    installBtn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response: ${outcome}`);
        deferredPrompt = null;
        installBtn.style.display = 'none';
      }
    });
  }
});

// ============================================
// SWIPE GESTURES (Жесты свайпа)
// ============================================

class SwipeDetector {
  constructor(element, options = {}) {
    this.element = element;
    this.threshold = options.threshold || 50;
    this.restraint = options.restraint || 100;
    this.allowedTime = options.allowedTime || 300;
    
    this.startX = 0;
    this.startY = 0;
    this.distX = 0;
    this.distY = 0;
    this.startTime = 0;
    this.elapsedTime = 0;
    
    this.onLeft = options.onLeft || (() => {});
    this.onRight = options.onRight || (() => {});
    this.onUp = options.onUp || (() => {});
    this.onDown = options.onDown || (() => {});
    
    this.init();
  }
  
  init() {
    this.element.addEventListener('touchstart', (e) => {
      const touch = e.changedTouches[0];
      this.startX = touch.pageX;
      this.startY = touch.pageY;
      this.startTime = new Date().getTime();
    }, { passive: true });
    
    this.element.addEventListener('touchend', (e) => {
      const touch = e.changedTouches[0];
      this.distX = touch.pageX - this.startX;
      this.distY = touch.pageY - this.startY;
      this.elapsedTime = new Date().getTime() - this.startTime;
      
      if (this.elapsedTime <= this.allowedTime) {
        if (Math.abs(this.distX) >= this.threshold && Math.abs(this.distY) <= this.restraint) {
          // Горизонтальный свайп
          if (this.distX < 0) {
            this.onLeft();
          } else {
            this.onRight();
          }
        } else if (Math.abs(this.distY) >= this.threshold && Math.abs(this.distX) <= this.restraint) {
          // Вертикальный свайп
          if (this.distY < 0) {
            this.onUp();
          } else {
            this.onDown();
          }
        }
      }
    }, { passive: true });
  }
}

// Инициализация свайпов для карточек категорий
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.category-card, .topic-card, .main-category-card');
  
  cards.forEach(card => {
    new SwipeDetector(card, {
      onLeft: () => {
        // Визуальный feedback при свайпе влево
        card.style.transform = 'translateX(-10px)';
        setTimeout(() => {
          card.style.transform = '';
        }, 200);
      },
      onRight: () => {
        // Визуальный feedback при свайпе вправо
        card.style.transform = 'translateX(10px)';
        setTimeout(() => {
          card.style.transform = '';
        }, 200);
      }
    });
  });
});

// ============================================
// PULL TO REFRESH (Потянуть для обновления)
// ============================================

class PullToRefresh {
  constructor() {
    this.startY = 0;
    this.pulling = false;
    this.threshold = 80;
    this.indicator = null;
    
    this.init();
  }
  
  init() {
    // Создаем индикатор
    this.indicator = document.createElement('div');
    this.indicator.className = 'pull-to-refresh';
    this.indicator.innerHTML = '<i class="fa-solid fa-spinner pull-to-refresh-icon"></i>';
    document.body.insertBefore(this.indicator, document.body.firstChild);
    
    let scrollTop = 0;
    
    document.addEventListener('touchstart', (e) => {
      scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      if (scrollTop === 0) {
        this.startY = e.touches[0].pageY;
        this.pulling = true;
      }
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
      if (this.pulling && scrollTop === 0) {
        const y = e.touches[0].pageY;
        const distance = y - this.startY;
        
        if (distance > 0 && distance < this.threshold * 2) {
          this.indicator.style.top = `${-60 + (distance / 2)}px`;
        }
      }
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      if (this.pulling) {
        const y = e.changedTouches[0].pageY;
        const distance = y - this.startY;
        
        if (distance > this.threshold) {
          this.indicator.classList.add('active');
          // Перезагружаем страницу
          setTimeout(() => {
            window.location.reload();
          }, 300);
        } else {
          this.indicator.style.top = '-60px';
        }
        
        this.pulling = false;
      }
    }, { passive: true });
  }
}

// Инициализируем Pull to Refresh только в мобильной версии
if (document.body.classList.contains('mobile-view')) {
  new PullToRefresh();
}

// ============================================
// HAPTIC FEEDBACK (Тактильная обратная связь)
// ============================================

function triggerHaptic(intensity = 'light') {
  if ('vibrate' in navigator) {
    switch (intensity) {
      case 'light':
        navigator.vibrate(10);
        break;
      case 'medium':
        navigator.vibrate(20);
        break;
      case 'heavy':
        navigator.vibrate([30, 10, 30]);
        break;
      case 'success':
        navigator.vibrate([10, 20, 10]);
        break;
      case 'error':
        navigator.vibrate([50, 30, 50]);
        break;
    }
  }
}

// Добавляем haptic feedback к кнопкам
document.addEventListener('DOMContentLoaded', () => {
  const buttons = document.querySelectorAll('.btn, .bottom-nav-item, .category-card, .topic-card');
  
  buttons.forEach(button => {
    button.addEventListener('touchstart', () => {
      triggerHaptic('light');
    }, { passive: true });
  });
  
  // Для важных кнопок - более сильная вибрация
  const importantButtons = document.querySelectorAll('.btn-primary, .btn-success, .btn-danger');
  
  importantButtons.forEach(button => {
    button.addEventListener('touchstart', () => {
      triggerHaptic('medium');
    }, { passive: true });
  });
});

// ============================================
// АКТИВНАЯ СТРАНИЦА В НИЖНЕЙ НАВИГАЦИИ
// ============================================

function updateBottomNav() {
  const currentPath = window.location.pathname;
  const navItems = document.querySelectorAll('.bottom-nav-item');
  
  navItems.forEach(item => {
    const href = item.getAttribute('href');
    item.classList.remove('active');
    
    if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
      item.classList.add('active');
    }
  });
}

// Обновляем при загрузке страницы
document.addEventListener('DOMContentLoaded', updateBottomNav);

// ============================================
// SMOOTH SCROLL
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('a[href^="#"]');
  
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href !== '#') {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      }
    });
  });
});

// ============================================
// ПРЕДОТВРАЩЕНИЕ ДВОЙНОГО ТАПА ДЛЯ ЗУМА
// ============================================

let lastTouchEnd = 0;
document.addEventListener('touchend', (e) => {
  const now = Date.now();
  if (now - lastTouchEnd <= 300) {
    e.preventDefault();
  }
  lastTouchEnd = now;
}, { passive: false });

// ============================================
// СКРЫТИЕ АДРЕСНОЙ СТРОКИ
// ============================================

window.addEventListener('load', () => {
  setTimeout(() => {
    window.scrollTo(0, 1);
  }, 100);
});

// ============================================
// ОБРАБОТКА ОРИЕНТАЦИИ ЭКРАНА
// ============================================

function handleOrientationChange() {
  const orientation = window.orientation || screen.orientation.angle;
  
  if (Math.abs(orientation) === 90) {
    // Ландшафтная ориентация
    console.log('Landscape mode');
  } else {
    // Портретная ориентация
    console.log('Portrait mode');
  }
}

window.addEventListener('orientationchange', handleOrientationChange);
screen.orientation.addEventListener('change', handleOrientationChange);

// ============================================
// ОНЛАЙН/ОФФЛАЙН СТАТУС
// ============================================

function updateOnlineStatus() {
  if (navigator.onLine) {
    console.log('Online');
    // Можно показать уведомление "Вы онлайн"
  } else {
    console.log('Offline');
    // Показываем уведомление "Нет соединения"
    alert('Нет подключения к интернету. Некоторые функции могут быть недоступны.');
  }
}

window.addEventListener('online', updateOnlineStatus);
window.addEventListener('offline', updateOnlineStatus);

// ============================================
// АВТОМАТИЧЕСКОЕ СКРЫТИЕ НИЖНЕЙ НАВИГАЦИИ ПРИ ПРОКРУТКЕ
// ============================================

let lastScrollTop = 0;
const bottomNav = document.querySelector('.bottom-nav');

if (bottomNav) {
  window.addEventListener('scroll', () => {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    if (scrollTop > lastScrollTop && scrollTop > 100) {
      // Прокрутка вниз - скрываем навигацию
      bottomNav.style.transform = 'translateY(100%)';
    } else {
      // Прокрутка вверх - показываем навигацию
      bottomNav.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = scrollTop;
  }, { passive: true });
}

// ============================================
// ЛОКАЛЬНОЕ ХРАНИЛИЩЕ ДЛЯ OFFLINE РЕЖИМА
// ============================================

function saveToLocalStorage(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (e) {
    console.error('LocalStorage error:', e);
  }
}

function getFromLocalStorage(key) {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (e) {
    console.error('LocalStorage error:', e);
    return null;
  }
}

// ============================================
// PERFORMANCE OPTIMIZATION
// ============================================

// Отключаем hover эффекты на touch устройствах
if ('ontouchstart' in window) {
  document.body.classList.add('touch-device');
}

// Lazy loading для изображений
document.addEventListener('DOMContentLoaded', () => {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        observer.unobserve(img);
      }
    });
  });
  
  images.forEach(img => imageObserver.observe(img));
});

console.log('FinQuest Mobile App initialized ✨');

