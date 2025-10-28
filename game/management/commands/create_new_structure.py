# МОДУЛЬНАЯ СТРУКТУРА
# Вопросы находятся в словаре subcategory_questions внутри метода create_questions
# В будущем можно выделить в отдельные файлы: questions_basics.py, questions_security.py, etc.
# Для использования: from .questions_basics import get_basics_questions

from django.core.management.base import BaseCommand
from game.models import Topic, Level, Achievement
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Создает новую структуру: 4 категории × 4 подкатегории × 3 уровня'

    def handle(self, *args, **options):
        # Очищаем старые данные
        Level.objects.all().delete()
        Topic.objects.all().delete()
        Achievement.objects.all().delete()
        
        self.stdout.write('Старые данные удалены')
        
        # Создаем основные категории
        categories = [
            {
                'name': 'Основы финансов',
                'main_category': 'basics',
                'description': 'Изучите базовые принципы управления деньгами',
                'subcategories': [
                    {
                        'name': 'Бюджетирование',
                        'description': 'Планирование и контроль расходов',
                        'levels': [
                            {'name': 'Создание бюджета', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Контроль расходов', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Оптимизация бюджета', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Сбережения',
                        'description': 'Накопление и сохранение денег',
                        'levels': [
                            {'name': 'Простые сбережения', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Стратегии накопления', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Долгосрочные цели', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Кредиты и займы',
                        'description': 'Ответственное использование кредитов',
                        'levels': [
                            {'name': 'Виды кредитов', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Расчет переплаты', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Кредитная история', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Банковские услуги',
                        'description': 'Работа с банками и финансовыми продуктами',
                        'levels': [
                            {'name': 'Виды счетов', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Банковские карты', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Интернет-банкинг', 'difficulty': 'hard', 'questions': 10}
                        ]
                    }
                ]
            },
            {
                'name': 'Безопасность',
                'main_category': 'security',
                'description': 'Защитите себя от мошенников и финансовых рисков',
                'subcategories': [
                    {
                        'name': 'Финансовое мошенничество',
                        'description': 'Распознавание и защита от мошенников',
                        'levels': [
                            {'name': 'Виды мошенничества', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Защита данных', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Кибербезопасность', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Страхование',
                        'description': 'Защита от финансовых рисков',
                        'levels': [
                            {'name': 'Виды страхования', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Выбор полиса', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Страховые случаи', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Финансовая грамотность',
                        'description': 'Права и обязанности потребителей',
                        'levels': [
                            {'name': 'Потребительские права', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Финансовые споры', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Защита интересов', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Цифровая безопасность',
                        'description': 'Безопасность в цифровом мире',
                        'levels': [
                            {'name': 'Безопасные пароли', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Двухфакторная аутентификация', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Фишинг и скам', 'difficulty': 'hard', 'questions': 10}
                        ]
                    }
                ]
            },
            {
                'name': 'Инвестиции',
                'main_category': 'investments',
                'description': 'Научитесь приумножать свои сбережения',
                'subcategories': [
                    {
                        'name': 'Основы инвестирования',
                        'description': 'Базовые принципы инвестирования',
                        'levels': [
                            {'name': 'Что такое инвестиции', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Риски и доходность', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Диверсификация', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Фондовый рынок',
                        'description': 'Торговля акциями и облигациями',
                        'levels': [
                            {'name': 'Акции и облигации', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Анализ компаний', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Технический анализ', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Пассивные инвестиции',
                        'description': 'ETF, ПИФы и другие инструменты',
                        'levels': [
                            {'name': 'Индексные фонды', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'ETF и ПИФы', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Робо-советники', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Альтернативные инвестиции',
                        'description': 'Недвижимость, криптовалюты и другие',
                        'levels': [
                            {'name': 'Недвижимость', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Криптовалюты', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Венчурные инвестиции', 'difficulty': 'hard', 'questions': 10}
                        ]
                    }
                ]
            },
            {
                'name': 'Планирование',
                'main_category': 'planning',
                'description': 'Достигайте своих финансовых целей',
                'subcategories': [
                    {
                        'name': 'Финансовые цели',
                        'description': 'Постановка и достижение целей',
                        'levels': [
                            {'name': 'SMART-цели', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Планирование целей', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Мониторинг прогресса', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Пенсионное планирование',
                        'description': 'Подготовка к пенсии',
                        'levels': [
                            {'name': 'Государственная пенсия', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Накопительная пенсия', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Частное пенсионное обеспечение', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Налоговое планирование',
                        'description': 'Оптимизация налогов',
                        'levels': [
                            {'name': 'Налоговые вычеты', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'ИИС и ЛДВ', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Оптимизация налогов', 'difficulty': 'hard', 'questions': 10}
                        ]
                    },
                    {
                        'name': 'Наследственное планирование',
                        'description': 'Передача имущества наследникам',
                        'levels': [
                            {'name': 'Составление завещания', 'difficulty': 'easy', 'questions': 6},
                            {'name': 'Наследственное право', 'difficulty': 'medium', 'questions': 8},
                            {'name': 'Семейные фонды', 'difficulty': 'hard', 'questions': 10}
                        ]
                    }
                ]
            }
        ]
        
        # Создаем категории и подкатегории
        for cat_data in categories:
            category = Topic.objects.create(
                name=cat_data['name'],
                main_category=cat_data['main_category'],
                description=cat_data['description'],
                is_subcategory=False
            )
            
            for subcat_data in cat_data['subcategories']:
                subcategory = Topic.objects.create(
                    name=subcat_data['name'],
                    main_category=cat_data['main_category'],
                    description=subcat_data['description'],
                    is_subcategory=True,
                    parent_category=category
                )
                
                # Создаем уровни для подкатегории
                for i, level_data in enumerate(subcat_data['levels']):
                    # Создаем вопросы для уровня
                    questions = self.create_questions(level_data['questions'], level_data['difficulty'], subcategory.name)
                    
                    Level.objects.create(
                        topic=subcategory,
                        title=level_data['name'],
                        description=f"Уровень {level_data['name']} для темы {subcategory.name}",
                        type='quiz',
                        difficulty=1 if level_data['difficulty'] == 'easy' else 2 if level_data['difficulty'] == 'medium' else 3,
                        order_in_topic=i + 1,
                        content=questions,
                        reward_points=10 if level_data['difficulty'] == 'easy' else 15 if level_data['difficulty'] == 'medium' else 20,
                        reward_coins=5 if level_data['difficulty'] == 'easy' else 8 if level_data['difficulty'] == 'medium' else 12
                    )
        
        # Создаем достижения
        achievements = [
            {
                'name': 'Первые шаги',
                'description': 'Ответили на первый вопрос',
                'category': 'progress',
                'points_reward': 10,
                'coins_reward': 5
            },
            {
                'name': 'Легенда финансовой грамотности',
                'description': 'Прошли все уровни во всех категориях',
                'category': 'special',
                'points_reward': 1000,
                'coins_reward': 500
            }
        ]
        
        for achievement_data in achievements:
            Achievement.objects.create(**achievement_data)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Создано: {Topic.objects.filter(is_subcategory=False).count()} категорий, '
                f'{Topic.objects.filter(is_subcategory=True).count()} подкатегорий, '
                f'{Level.objects.count()} уровней, '
                f'{Achievement.objects.count()} достижений'
            )
        )

    def create_questions(self, count, difficulty, subcategory_name):
        """Создает вопросы для уровня в зависимости от подкатегории"""
        
        # Словарь с вопросами для каждой подкатегории
        subcategory_questions = {
            # Категория: Основы финансов
            'Бюджетирование': {
            'easy': [
                {
                    'question': 'Что такое бюджет?',
                    'type': 'single',
                    'options': [
                        {'text': 'План доходов и расходов', 'correct': True},
                        {'text': 'Сумма денег в кошельке', 'correct': False},
                        {'text': 'Банковский счет', 'correct': False},
                        {'text': 'Кредитная карта', 'correct': False}
                    ],
                    'hint': 'Бюджет помогает контролировать финансы'
                },
                {
                        'question': 'Какой процент дохода рекомендуется откладывать?',
                    'type': 'single',
                    'options': [
                            {'text': '10-20%', 'correct': True},
                            {'text': '50%', 'correct': False},
                            {'text': '5%', 'correct': False},
                            {'text': '100%', 'correct': False}
                        ],
                        'hint': 'Правило 50/30/20 предполагает 20% на сбережения'
                    },
                    {
                        'question': 'Какие расходы относятся к фиксированным?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Аренда жилья', 'correct': True},
                            {'text': 'Коммунальные услуги', 'correct': True},
                            {'text': 'Покупка одежды', 'correct': False},
                            {'text': 'Страховка', 'correct': True},
                            {'text': 'Развлечения', 'correct': False}
                        ],
                        'hint': 'Фиксированные расходы не меняются ежемесячно'
                    },
                    {
                        'question': 'Сопоставьте термины с определениями',
                    'type': 'matching',
                        'left_items': ['Бюджет', 'Дефицит', 'Профицит', 'Расходы'],
                        'right_items': ['Превышение расходов над доходами', 'План доходов и расходов', 'Превышение доходов над расходами', 'Траты денег'],
                        'correct_matches': [[0, 1], [1, 0], [2, 2], [3, 3]],
                        'hint': 'Бюджет - это план, дефицит - нехватка, профицит - избыток'
                    },
                    {
                        'question': 'Расположите этапы создания бюджета в правильном порядке',
                    'type': 'sorting',
                    'items': [
                            {'id': 0, 'text': 'Определение доходов'},
                            {'id': 1, 'text': 'Учет текущих расходов'},
                            {'id': 2, 'text': 'Категоризация трат'},
                            {'id': 3, 'text': 'Постановка целей'},
                            {'id': 4, 'text': 'Распределение бюджета'}
                    ],
                    'correct_order': [0, 1, 2, 3, 4],
                        'hint': 'Сначала доходы, потом расходы, затем планирование'
                }
            ],
            'medium': [
                {
                        'question': 'Что такое правило 50/30/20?',
                    'type': 'single',
                    'options': [
                            {'text': '50% - нужды, 30% - желания, 20% - сбережения', 'correct': True},
                            {'text': '50% - доходы, 30% - расходы, 20% - налоги', 'correct': False},
                            {'text': '50% - накопления, 30% - инвестиции, 20% - расходы', 'correct': False},
                            {'text': 'Всё вышеперечисленное', 'correct': False}
                        ],
                        'hint': 'Это метод распределения дохода на категории'
                    },
                    {
                        'question': 'Как отслеживать расходы эффективно?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Использовать приложения для учета', 'correct': True},
                            {'text': 'Вести ежемесячный учет расходов', 'correct': True},
                            {'text': 'Запоминать все траты', 'correct': False},
                            {'text': 'Сохранять чеки', 'correct': True},
                            {'text': 'Игнорировать мелкие покупки', 'correct': False}
                        ],
                        'hint': 'Систематичность - ключ к контролю'
                    },
                    {
                        'question': 'Сопоставьте методы бюджетирования с их описаниями',
                    'type': 'matching',
                        'left_items': ['Zero-based', 'Envelope method', '50/30/20 rule', 'Automatic budgeting'],
                        'right_items': ['Обоснование каждой траты', 'Наличные на категории', 'Процентное распределение', 'Автоматические переводы'],
                    'correct_matches': [[0, 0], [1, 1], [2, 2], [3, 3]],
                        'hint': 'Разные методы помогают по-разному контролировать финансы'
                },
                {
                        'question': 'Расположите этапы оптимизации бюджета в правильном порядке',
                    'type': 'sorting',
                    'items': [
                            {'id': 0, 'text': 'Анализ текущих трат'},
                            {'id': 1, 'text': 'Выявление избыточных расходов'},
                            {'id': 2, 'text': 'Пересмотр категорий'},
                            {'id': 3, 'text': 'Сокращение расходов'},
                            {'id': 4, 'text': 'Мониторинг результатов'}
                    ],
                    'correct_order': [0, 1, 2, 3, 4],
                        'hint': 'Сначала анализируем, затем действуем'
                }
            ],
            'hard': [
                {
                        'question': 'Что такое zero-based budgeting?',
                    'type': 'single',
                    'options': [
                            {'text': 'Бюджет, где каждая трата обоснована', 'correct': True},
                            {'text': 'Бюджет без расходов', 'correct': False},
                            {'text': 'Бюджет с нулевым остатком', 'correct': False},
                            {'text': 'Годовой бюджет', 'correct': False}
                        ],
                        'hint': 'Каждая копейка имеет целевое назначение'
                    },
                    {
                        'question': 'Сопоставьте финансовые показатели с их формулами',
                        'type': 'matching',
                        'left_items': ['Финансовая свобода', 'Норма сбережений', 'Коэффициент расходов', 'Оборачиваемость бюджета'],
                        'right_items': ['Накопления / Годовые расходы', 'Сбережения / Доходы', 'Расходы / Доходы', 'Доходы / Бюджет'],
                        'correct_matches': [[0, 0], [1, 1], [2, 2], [3, 3]],
                        'hint': 'Каждый показатель показывает разные аспекты финансов'
                    },
                    {
                        'question': 'Расположите стратегии снижения расходов от эффективной к менее эффективной',
                        'type': 'sorting',
                        'items': [
                            {'id': 0, 'text': 'Отказ от несущественных трат'},
                            {'id': 1, 'text': 'Пересмотр подписок и сервисов'},
                            {'id': 2, 'text': 'Использование кэшбэков'},
                            {'id': 3, 'text': 'Сравнение цен'},
                            {'id': 4, 'text': 'Сокращение развлечений'}
                        ],
                        'correct_order': [0, 1, 2, 3, 4],
                        'hint': 'Сначала убираем лишнее, затем оптимизируем необходимое'
                    }
                ]
            },
            'Сбережения': {
                'easy': [
                {
                    'question': 'Что такое сбережения?',
                    'type': 'single',
                    'options': [
                        {'text': 'Деньги, отложенные на будущее', 'correct': True},
                        {'text': 'Ежедневные расходы', 'correct': False},
                        {'text': 'Кредитные деньги', 'correct': False},
                        {'text': 'Зарплата', 'correct': False}
                    ],
                    'hint': 'Сбережения - это часть дохода, которую не тратят сразу'
                },
                {
                        'question': 'Какой размер резервного фонда рекомендуется?',
                        'type': 'single',
                        'options': [
                            {'text': '3-6 месячных окладов', 'correct': True},
                            {'text': '1 месяц', 'correct': False},
                            {'text': '1 год', 'correct': False},
                            {'text': '10% от дохода', 'correct': False}
                        ],
                        'hint': 'Резервный фонд защищает от непредвиденных ситуаций'
                    },
                    {
                        'question': 'Где лучше хранить резервный фонд?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Банковский вклад', 'correct': True},
                            {'text': 'Домашняя копилка', 'correct': False},
                            {'text': 'Банковский счет с легким доступом', 'correct': True},
                            {'text': 'Акции', 'correct': False},
                            {'text': 'Срочный депозит', 'correct': True}
                        ],
                        'hint': 'Резервный фонд должен быть доступен'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое капитализация процентов?',
                        'type': 'single',
                        'options': [
                            {'text': 'Присоединение процентов к сумме вклада', 'correct': True},
                            {'text': 'Выплата процентов отдельно', 'correct': False},
                            {'text': 'Банковская комиссия', 'correct': False},
                            {'text': 'Налог на доходы', 'correct': False}
                        ],
                        'hint': 'Позволяет получать проценты на проценты'
                    },
                    {
                        'question': 'Какие стратегии помогают увеличить сбережения?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Автоматические переводы на депозит', 'correct': True},
                            {'text': 'Откладывание в начале месяца', 'correct': True},
                            {'text': 'Откладывание остатка в конце месяца', 'correct': False},
                            {'text': 'Постановка конкретных целей', 'correct': True},
                            {'text': 'Тратить до получения следующей зарплаты', 'correct': False}
                        ],
                        'hint': 'Лучше откладывать сначала, а не по остаточному принципу'
                    },
                    {
                        'question': 'Сопоставьте виды вкладов с их характеристиками',
                    'type': 'matching',
                        'left_items': ['Срочный вклад', 'До востребования', 'С капитализацией', 'Пополняемый'],
                        'right_items': ['Фиксированный срок, высокая ставка', 'Высокая ликвидность', 'Проценты на проценты', 'Можно дополнять'],
                    'correct_matches': [[0, 0], [1, 1], [2, 2], [3, 3]],
                        'hint': 'У каждого типа вклада свои особенности'
                },
                {
                        'question': 'Расположите шаги создания резервного фонда в правильном порядке',
                    'type': 'sorting',
                    'items': [
                            {'id': 0, 'text': 'Определение размера фонда'},
                            {'id': 1, 'text': 'Выбор места хранения'},
                            {'id': 2, 'text': 'Открытие счета'},
                            {'id': 3, 'text': 'Автоматическое пополнение'},
                            {'id': 4, 'text': 'Мониторинг достижения цели'}
                        ],
                        'correct_order': [0, 1, 2, 3, 4],
                        'hint': 'Сначала планируем, затем создаем и пополняем'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое эскалационное накопление?',
                        'type': 'single',
                        'options': [
                            {'text': 'Постепенное увеличение суммы накоплений', 'correct': True},
                            {'text': 'Быстрое накопление', 'correct': False},
                            {'text': 'Накопление с процентами', 'correct': False},
                            {'text': 'Инвестирование', 'correct': False}
                        ],
                        'hint': 'Стратегия постепенного увеличения сбережений'
                    },
                    {
                        'question': 'Сопоставьте стратегии накопления с их описаниями',
                        'type': 'matching',
                        'left_items': ['Pay yourself first', 'Sinking fund', 'Laddering', 'Escalation'],
                        'right_items': ['Сначала откладываете', 'Целевое накопление', 'Лестница вкладов', 'Постепенное увеличение'],
                        'correct_matches': [[0, 0], [1, 1], [2, 2], [3, 3]],
                        'hint': 'Разные стратегии подходят для разных целей'
                    },
                    {
                        'question': 'Расположите инвестиционные инструменты от безопасных к рискованным',
                        'type': 'sorting',
                        'items': [
                            {'id': 0, 'text': 'Банковский вклад'},
                            {'id': 1, 'text': 'Облигации'},
                            {'id': 2, 'text': 'Индексные фонды'},
                            {'id': 3, 'text': 'Акции'},
                            {'id': 4, 'text': 'Венчурные инвестиции'}
                        ],
                        'correct_order': [0, 1, 2, 3, 4],
                        'hint': 'Больше риск - больше потенциальная доходность'
                    }
                ]
            },
            'Кредиты и займы': {
                'easy': [
                    {
                        'question': 'Что такое полная стоимость кредита (ПСК)?',
                        'type': 'single',
                        'options': [
                            {'text': 'Все расходы по кредиту в годовых процентах', 'correct': True},
                            {'text': 'Только процентная ставка', 'correct': False},
                            {'text': 'Основной долг', 'correct': False},
                            {'text': 'Размер займа', 'correct': False}
                        ],
                        'hint': 'ПСК включает все платежи по кредиту'
                    },
                    {
                        'question': 'Какие кредиты считаются залоговыми?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Ипотека', 'correct': True},
                            {'text': 'Автокредит', 'correct': True},
                            {'text': 'Потребительский без залога', 'correct': False},
                            {'text': 'Кредит под залог недвижимости', 'correct': True},
                            {'text': 'Кредитная карта', 'correct': False}
                        ],
                        'hint': 'Залоговый кредит подразумевает обеспечение'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое дифференцированный платеж?',
                        'type': 'single',
                        'options': [
                            {'text': 'Равномерное уменьшение суммы платежа', 'correct': True},
                            {'text': 'Равные платежи на протяжении всего срока', 'correct': False},
                            {'text': 'Платежи по выбору заемщика', 'correct': False},
                            {'text': 'Разовые платежи', 'correct': False}
                        ],
                        'hint': 'Основной долг выплачивается равными долями'
                    },
                    {
                        'question': 'Что влияет на кредитную историю?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Своевременность платежей', 'correct': True},
                            {'text': 'Количество открытых кредитов', 'correct': True},
                            {'text': 'Сумма кредитов', 'correct': True},
                            {'text': 'Цвет кошелька', 'correct': False},
                            {'text': 'Просроченные платежи', 'correct': True}
                        ],
                        'hint': 'История отражает вашу кредитную дисциплину'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое кредитные каникулы?',
                        'type': 'single',
                        'options': [
                            {'text': 'Временное снижение или отсрочка платежей', 'correct': True},
                            {'text': 'Пропуск платежей', 'correct': False},
                            {'text': 'Погашение кредита досрочно', 'correct': False},
                            {'text': 'Отказ от кредита', 'correct': False}
                        ],
                        'hint': 'Предоставляется банком при форс-мажорных обстоятельствах'
                    }
                ]
            },
            'Банковские услуги': {
                'easy': [
                    {
                        'question': 'Чем отличается дебетовая карта от кредитной?',
                        'type': 'single',
                        'options': [
                            {'text': 'Дебетовая использует собственные деньги, кредитная - заемные', 'correct': True},
                            {'text': 'Разницы нет', 'correct': False},
                            {'text': 'Разный цвет', 'correct': False},
                            {'text': 'Кредитная дороже', 'correct': False}
                        ],
                        'hint': 'Дебетовая - ваши деньги, кредитная - деньги банка'
                    },
                    {
                        'question': 'Что такое овердрафт?',
                        'type': 'single',
                        'options': [
                            {'text': 'Допустимое превышение баланса счета', 'correct': True},
                            {'text': 'Процент по вкладу', 'correct': False},
                            {'text': 'Банковская комиссия', 'correct': False},
                            {'text': 'Ипотечный кредит', 'correct': False}
                        ],
                        'hint': 'Позволяет тратить больше, чем есть на счете'
                    },
                    {
                        'question': 'Какие услуги банков наиболее востребованы?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Онлайн-банкинг', 'correct': True},
                            {'text': 'Мобильное приложение', 'correct': True},
                            {'text': 'Банковские переводы', 'correct': True},
                            {'text': 'Снятие наличных в другом городе', 'correct': False},
                            {'text': 'Пластиковые карты', 'correct': True}
                        ],
                        'hint': 'Современные услуги удобны и доступны'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое депозит?',
                        'type': 'single',
                        'options': [
                            {'text': 'Вклад денег в банк под процент', 'correct': True},
                            {'text': 'Кредит в банке', 'correct': False},
                            {'text': 'Банковский счет', 'correct': False},
                            {'text': 'Страховка', 'correct': False}
                        ],
                        'hint': 'Вклад с начислением процентов'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое процентная ставка "до востребования"?',
                        'type': 'single',
                        'options': [
                            {'text': 'Минимальная ставка для счета с возможностью снятия', 'correct': True},
                            {'text': 'Максимальная ставка', 'correct': False},
                            {'text': 'Ставка для кредита', 'correct': False},
                            {'text': 'Ставка по ипотеке', 'correct': False}
                        ],
                        'hint': 'Счет, с которого можно снимать в любое время'
                    }
                ]
            },
            # Категория: Безопасность
            'Финансовое мошенничество': {
                'easy': [
                    {
                        'question': 'Как защититься от телефонных мошенников?',
                        'type': 'single',
                        'options': [
                            {'text': 'Не сообщать банковские данные по телефону', 'correct': True},
                            {'text': 'Сообщать все данные для подтверждения', 'correct': False},
                            {'text': 'Выполнять все требования по телефону', 'correct': False},
                            {'text': 'Сообщать пароли', 'correct': False}
                        ],
                        'hint': 'Банки никогда не просят пароли и CVV по телефону'
                    },
                    {
                        'question': 'Что такое фишинг?',
                        'type': 'single',
                        'options': [
                            {'text': 'Мошенничество с целью получить личные данные', 'correct': True},
                            {'text': 'Надежный банк', 'correct': False},
                            {'text': 'Вид кредита', 'correct': False},
                            {'text': 'Технология безопасности', 'correct': False}
                        ],
                        'hint': 'Используются поддельные сайты и письма'
                    }
                ],
                'medium': [
                    {
                        'question': 'Как распознать мошенничество с SMS?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Неизвестный номер отправителя', 'correct': True},
                            {'text': 'Просьба прислать код', 'correct': True},
                            {'text': 'Сообщение от банка', 'correct': False},
                            {'text': 'Ссылка на подозрительный сайт', 'correct': True},
                            {'text': 'Грамматические ошибки', 'correct': True}
                        ],
                        'hint': 'Официальные сообщения банков грамотны'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое социальная инженерия?',
                        'type': 'single',
                        'options': [
                            {'text': 'Манипулирование людьми для получения информации', 'correct': True},
                            {'text': 'Социальная сеть', 'correct': False},
                            {'text': 'Метод обучения', 'correct': False},
                            {'text': 'Банковская услуга', 'correct': False}
                        ],
                        'hint': 'Использование психологических приемов'
                    }
                ]
            },
            'Страхование': {
                'easy': [
                    {
                        'question': 'Что такое страхование?',
                        'type': 'single',
                        'options': [
                            {'text': 'Защита от финансовых рисков', 'correct': True},
                            {'text': 'Способ инвестирования', 'correct': False},
                            {'text': 'Вид кредита', 'correct': False},
                            {'text': 'Банковский вклад', 'correct': False}
                        ],
                        'hint': 'Страхование защищает от убытков'
                    },
                    {
                        'question': 'Какие виды страхования существуют?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Жизнь и здоровье', 'correct': True},
                            {'text': 'Имущество', 'correct': True},
                            {'text': 'Автомобильное', 'correct': True},
                            {'text': 'Продуктовое', 'correct': False},
                            {'text': 'Туристическое', 'correct': True}
                        ],
                        'hint': 'Страхуется то, что может принести ущерб'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое франшиза в страховании?',
                        'type': 'single',
                        'options': [
                            {'text': 'Сумма, не покрываемая страховкой', 'correct': True},
                            {'text': 'Сумма страхования', 'correct': False},
                            {'text': 'Процент выплаты', 'correct': False},
                            {'text': 'Срок страхования', 'correct': False}
                        ],
                        'hint': 'Часть ущерба, которую платит клиент'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое сострахование?',
                        'type': 'single',
                        'options': [
                            {'text': 'Разделение риска между несколькими страховщиками', 'correct': True},
                            {'text': 'Совместное страхование', 'correct': False},
                            {'text': 'Групповое страхование', 'correct': False},
                            {'text': 'Отказ от страхования', 'correct': False}
                        ],
                        'hint': 'Большие риски делятся между компаниями'
                    }
                ]
            },
            'Финансовая грамотность': {
                'easy': [
                    {
                        'question': 'Что такое потребительские права?',
                        'type': 'single',
                        'options': [
                            {'text': 'Защита интересов потребителей', 'correct': True},
                            {'text': 'Права банков', 'correct': False},
                            {'text': 'Правила торговли', 'correct': False},
                            {'text': 'Налоговое право', 'correct': False}
                        ],
                        'hint': 'Защищают граждан при покупках и услугах'
                }
            ],
            'medium': [
                {
                        'question': 'Куда обращаться при нарушении финансовых прав?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Роспотребнадзор', 'correct': True},
                            {'text': 'Центробанк', 'correct': True},
                            {'text': 'В банк-нарушитель', 'correct': False},
                            {'text': 'Суд', 'correct': True},
                            {'text': 'К друзьям', 'correct': False}
                        ],
                        'hint': 'Есть государственные органы защиты'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое коллекторская деятельность?',
                        'type': 'single',
                        'options': [
                            {'text': 'Взыскание долгов законными методами', 'correct': True},
                            {'text': 'Кредитование', 'correct': False},
                            {'text': 'Страхование', 'correct': False},
                            {'text': 'Инвестирование', 'correct': False}
                        ],
                        'hint': 'Деятельность по взысканию задолженности'
                    }
                ]
            },
            'Цифровая безопасность': {
                'easy': [
                    {
                        'question': 'Какой пароль самый надежный?',
                    'type': 'single',
                    'options': [
                            {'text': 'Длинный с буквами, цифрами и символами', 'correct': True},
                            {'text': '123456', 'correct': False},
                            {'text': 'Пароль', 'correct': False},
                            {'text': 'Дата рождения', 'correct': False}
                        ],
                        'hint': 'Чем сложнее, тем безопаснее'
                    },
                    {
                        'question': 'Что такое двухфакторная аутентификация?',
                        'type': 'single',
                        'options': [
                            {'text': 'Двойная проверка личности', 'correct': True},
                            {'text': 'Два пароля', 'correct': False},
                            {'text': 'Два аккаунта', 'correct': False},
                            {'text': 'Два банка', 'correct': False}
                        ],
                        'hint': 'Пароль + код подтверждения'
                    }
                ],
                'medium': [
                    {
                        'question': 'Как защитить банковскую карту?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Не сообщать CVV посторонним', 'correct': True},
                            {'text': 'Включить SMS-уведомления', 'correct': True},
                            {'text': 'Сообщать CVV всем', 'correct': False},
                            {'text': 'Использовать официальные приложения', 'correct': True},
                            {'text': 'Хранить пин-код вместе с картой', 'correct': False}
                        ],
                        'hint': 'Основное правило - конфиденциальность данных'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое безопасное соединение HTTPS?',
                        'type': 'single',
                        'options': [
                            {'text': 'Зашифрованное соединение в интернете', 'correct': True},
                            {'text': 'Wi-Fi', 'correct': False},
                            {'text': 'Мобильная сеть', 'correct': False},
                            {'text': 'Банковский сайт', 'correct': False}
                        ],
                        'hint': 'Вся информация шифруется'
                    }
                ]
            },
            # Категория: Инвестиции
            'Основы инвестирования': {
                'easy': [
                    {
                        'question': 'Что такое инвестиции?',
                        'type': 'single',
                        'options': [
                            {'text': 'Вложение денег с целью получения дохода', 'correct': True},
                            {'text': 'Кредит', 'correct': False},
                            {'text': 'Расход', 'correct': False},
                            {'text': 'Зарплата', 'correct': False}
                        ],
                        'hint': 'Инвестиции приносят прибыль в будущем'
                    },
                    {
                        'question': 'Что такое диверсификация?',
                        'type': 'single',
                        'options': [
                            {'text': 'Распределение инвестиций между разными активами', 'correct': True},
                            {'text': 'Покупка одного вида акций', 'correct': False},
                            {'text': 'Хранение денег в банке', 'correct': False},
                            {'text': 'Получение кредита', 'correct': False}
                        ],
                        'hint': 'Не кладите все яйца в одну корзину'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое риск в инвестициях?',
                        'type': 'single',
                        'options': [
                            {'text': 'Возможность потери капитала', 'correct': True},
                            {'text': 'Гарантированная прибыль', 'correct': False},
                            {'text': 'Размер дивидендов', 'correct': False},
                            {'text': 'Процент по вкладу', 'correct': False}
                        ],
                        'hint': 'Чем выше риск, тем выше потенциальная доходность'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое временная стоимость денег?',
                        'type': 'single',
                        'options': [
                            {'text': 'Деньги сегодня стоят больше, чем завтра', 'correct': True},
                            {'text': 'Цена денег на валютном рынке', 'correct': False},
                            {'text': 'Зарплата', 'correct': False},
                            {'text': 'Курс валют', 'correct': False}
                        ],
                        'hint': 'Из-за инфляции и возможности инвестирования'
                    }
                ]
            },
            'Фондовый рынок': {
                'easy': [
                    {
                        'question': 'Что такое акция?',
                        'type': 'single',
                        'options': [
                            {'text': 'Доля в собственности компании', 'correct': True},
                            {'text': 'Кредит', 'correct': False},
                            {'text': 'Вклад', 'correct': False},
                            {'text': 'Обязательство', 'correct': False}
                        ],
                        'hint': 'Покупка акции делает вас совладельцем'
                    },
                    {
                        'question': 'Чем акция отличается от облигации?',
                        'type': 'single',
                        'options': [
                            {'text': 'Акция - доля, облигация - долг', 'correct': True},
                            {'text': 'Акция дешевле', 'correct': False},
                            {'text': 'Облигация дает право голоса', 'correct': False},
                            {'text': 'Нет отличий', 'correct': False}
                        ],
                        'hint': 'Акция - собственность, облигация - долговая расписка'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое дивиденды?',
                        'type': 'single',
                        'options': [
                            {'text': 'Выплаты акционерам от прибыли компании', 'correct': True},
                            {'text': 'Проценты по кредиту', 'correct': False},
                            {'text': 'Цена акции', 'correct': False},
                            {'text': 'Налог', 'correct': False}
                        ],
                        'hint': 'Часть прибыли компании выплачивается владельцам акций'
                }
            ],
            'hard': [
                {
                        'question': 'Что такое коэффициент P/E?',
                    'type': 'single',
                    'options': [
                            {'text': 'Соотношение цены акции к прибыли', 'correct': True},
                        {'text': 'Размер дивидендов', 'correct': False},
                            {'text': 'Курс валют', 'correct': False},
                            {'text': 'Процент инфляции', 'correct': False}
                        ],
                        'hint': 'Показывает, сколько стоит акция относительно прибыли'
                    }
                ]
            },
            'Пассивные инвестиции': {
                'easy': [
                    {
                        'question': 'Что такое ETF?',
                        'type': 'single',
                        'options': [
                            {'text': 'Биржевой инвестиционный фонд', 'correct': True},
                            {'text': 'Банковский вклад', 'correct': False},
                            {'text': 'Кредит', 'correct': False},
                            {'text': 'Страховка', 'correct': False}
                        ],
                        'hint': 'Индексный фонд, торгуемый на бирже'
                    },
                    {
                        'question': 'Что такое ПИФ?',
                        'type': 'single',
                        'options': [
                            {'text': 'Паевый инвестиционный фонд', 'correct': True},
                            {'text': 'Банковский счет', 'correct': False},
                            {'text': 'Кредитный союз', 'correct': False},
                            {'text': 'Страховая компания', 'correct': False}
                        ],
                        'hint': 'Фонд для коллективного инвестирования'
                    }
                ],
                'medium': [
                    {
                        'question': 'В чем преимущество индексных фондов?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Низкие комиссии', 'correct': True},
                            {'text': 'Диверсификация', 'correct': True},
                            {'text': 'Простота управления', 'correct': True},
                            {'text': 'Высокая стоимость', 'correct': False},
                            {'text': 'Высокая активность трейдера', 'correct': False}
                        ],
                        'hint': 'Повторяют индекс рынка'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое ребалансировка портфеля?',
                        'type': 'single',
                        'options': [
                            {'text': 'Возврат к исходному распределению активов', 'correct': True},
                            {'text': 'Продажа всех активов', 'correct': False},
                            {'text': 'Покупка случайных акций', 'correct': False},
                            {'text': 'Закрытие счета', 'correct': False}
                        ],
                        'hint': 'Поддержание желаемого соотношения активов'
                    }
                ]
            },
            'Альтернативные инвестиции': {
                'easy': [
                    {
                        'question': 'Что относится к альтернативным инвестициям?',
                    'type': 'multiple',
                    'options': [
                            {'text': 'Недвижимость', 'correct': True},
                            {'text': 'Криптовалюты', 'correct': True},
                            {'text': 'Золото', 'correct': True},
                            {'text': 'Банковский вклад', 'correct': False},
                            {'text': 'Обычные акции', 'correct': False}
                        ],
                        'hint': 'Альтернатива традиционным инструментам'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое доходность недвижимости?',
                        'type': 'single',
                        'options': [
                            {'text': 'Арендная доходность плюс рост стоимости', 'correct': True},
                            {'text': 'Только аренда', 'correct': False},
                            {'text': 'Только рост стоимости', 'correct': False},
                            {'text': 'Налоги', 'correct': False}
                        ],
                        'hint': 'Два источника дохода'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое blockchain?',
                        'type': 'single',
                        'options': [
                            {'text': 'Цепочка блоков с данными', 'correct': True},
                            {'text': 'Банковская система', 'correct': False},
                            {'text': 'Торговая платформа', 'correct': False},
                            {'text': 'Инвестиционный фонд', 'correct': False}
                        ],
                        'hint': 'Технология распределенного учета'
                    }
                ]
            },
            # Категория: Планирование
            'Финансовые цели': {
                'easy': [
                    {
                        'question': 'Что такое SMART-цель?',
                        'type': 'single',
                        'options': [
                            {'text': 'Конкретная, измеримая, достижимая, релевантная, с ограничением по времени', 'correct': True},
                            {'text': 'Быстрая цель', 'correct': False},
                            {'text': 'Большая цель', 'correct': False},
                            {'text': 'Простая цель', 'correct': False}
                        ],
                        'hint': 'Аббревиатура расшифровывается по критериям'
                    },
                    {
                        'question': 'Какие цели считаются долгосрочными?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Пенсионное накопление', 'correct': True},
                            {'text': 'Покупка квартиры', 'correct': True},
                            {'text': 'Еженедельные расходы', 'correct': False},
                            {'text': 'Отпуск через 5 лет', 'correct': True},
                            {'text': 'Обед сегодня', 'correct': False}
                        ],
                        'hint': 'Рассчитаны на срок более года'
                    }
                ],
                'medium': [
                    {
                        'question': 'Как правильно ставить финансовую цель?',
                        'type': 'single',
                        'options': [
                            {'text': 'Определить сумму, срок и план', 'correct': True},
                            {'text': 'Просто "накопить деньги"', 'correct': False},
                            {'text': 'Не планировать', 'correct': False},
                            {'text': 'Копить без цели', 'correct': False}
                        ],
                        'hint': 'Конкретика - залог успеха'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое временной горизонт цели?',
                        'type': 'single',
                        'options': [
                            {'text': 'Период для достижения цели', 'correct': True},
                            {'text': 'Время работы', 'correct': False},
                            {'text': 'Срок вклада', 'correct': False},
                            {'text': 'Срок кредита', 'correct': False}
                        ],
                        'hint': 'Определяет стратегию инвестирования'
                    }
                ]
            },
            'Пенсионное планирование': {
                'easy': [
                    {
                        'question': 'Из чего состоит пенсия?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Страховая часть', 'correct': True},
                            {'text': 'Накопительная часть', 'correct': True},
                            {'text': 'Дополнительное финансирование', 'correct': True},
                            {'text': 'Зарплата', 'correct': False},
                            {'text': 'Кредит', 'correct': False}
                        ],
                        'hint': 'Несколько источников обеспечения'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое накопительная пенсия?',
                        'type': 'single',
                        'options': [
                            {'text': 'Часть пенсии из индивидуальных накоплений', 'correct': True},
                            {'text': 'Страховая пенсия', 'correct': False},
                            {'text': 'Социальная пенсия', 'correct': False},
                            {'text': 'Досрочная пенсия', 'correct': False}
                        ],
                        'hint': 'Формируется из отчислений и инвестиций'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое коэффициент замещения?',
                        'type': 'single',
                        'options': [
                            {'text': 'Соотношение пенсии к зарплате', 'correct': True},
                            {'text': 'Размер пенсии', 'correct': False},
                            {'text': 'Возраст выхода', 'correct': False},
                            {'text': 'Стаж работы', 'correct': False}
                        ],
                        'hint': 'Показывает, какой процент зарплаты составит пенсия'
                    }
                ]
            },
            'Налоговое планирование': {
                'easy': [
                    {
                        'question': 'Что такое налоговый вычет?',
                        'type': 'single',
                        'options': [
                            {'text': 'Возврат части уплаченного налога', 'correct': True},
                            {'text': 'Дополнительный налог', 'correct': False},
                            {'text': 'Кредит', 'correct': False},
                            {'text': 'Штраф', 'correct': False}
                        ],
                        'hint': 'Снижение налоговой базы'
                    },
                    {
                        'question': 'Что такое ИИС?',
                        'type': 'single',
                        'options': [
                            {'text': 'Индивидуальный инвестиционный счет с льготами', 'correct': True},
                            {'text': 'Банковский счет', 'correct': False},
                            {'text': 'Кредитная карта', 'correct': False},
                            {'text': 'Страховка', 'correct': False}
                        ],
                        'hint': 'Дает налоговые льготы для инвестиций'
                    }
                ],
                'medium': [
                    {
                        'question': 'Какие налоговые льготы дает ИИС?',
                        'type': 'multiple',
                        'options': [
                            {'text': 'Налоговый вычет 13%', 'correct': True},
                            {'text': 'Освобождение от налога на прибыль', 'correct': True},
                            {'text': 'Снижение НДС', 'correct': False},
                            {'text': 'Отмена налога', 'correct': False}
                        ],
                        'hint': 'Два типа льгот в зависимости от выбранного режима'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое ЛДВ?',
                        'type': 'single',
                        'options': [
                            {'text': 'Льготное длительное владение ценными бумагами', 'correct': True},
                            {'text': 'Налоговое льгота', 'correct': False},
                            {'text': 'Банковский вклад', 'correct': False},
                            {'text': 'Инвестиционный счет', 'correct': False}
                        ],
                        'hint': 'Льгота для долгосрочных инвесторов'
                    }
                ]
            },
            'Наследственное планирование': {
                'easy': [
                    {
                        'question': 'Что такое завещание?',
                        'type': 'single',
                        'options': [
                            {'text': 'Распоряжение имуществом на случай смерти', 'correct': True},
                            {'text': 'Дарение', 'correct': False},
                            {'text': 'Продажа', 'correct': False},
                            {'text': 'Кредит', 'correct': False}
                        ],
                        'hint': 'Вступает в силу после смерти'
                    }
                ],
                'medium': [
                    {
                        'question': 'Что такое обязательная доля наследства?',
                        'type': 'single',
                        'options': [
                            {'text': 'Минимальная доля для определенных категорий', 'correct': True},
                            {'text': 'Произвольная доля', 'correct': False},
                            {'text': 'Вся наследство', 'correct': False},
                            {'text': 'Дарение', 'correct': False}
                        ],
                        'hint': 'Защищает права близких родственников'
                    }
                ],
                'hard': [
                    {
                        'question': 'Что такое наследственный фонд?',
                        'type': 'single',
                        'options': [
                            {'text': 'Управление наследством после смерти наследодателя', 'correct': True},
                            {'text': 'Место хранения завещания', 'correct': False},
                            {'text': 'Банковский счет', 'correct': False},
                            {'text': 'Налоговый вычет', 'correct': False}
                        ],
                        'hint': 'Позволяет управлять наследством'
                    }
                ]
            }
        }
        
        questions = []
        
        # Получаем вопросы для данной подкатегории и сложности
        if subcategory_name in subcategory_questions:
            if difficulty in subcategory_questions[subcategory_name]:
                templates = subcategory_questions[subcategory_name][difficulty]
                
                # Берем только уникальные вопросы без повторения
                unique_count = min(count, len(templates))
                for i in range(unique_count):
                questions.append(templates[i])
            else:
            # Если подкатегория не найдена, используем базовые вопросы
            questions.append({
                'question': f'Вопрос по теме {subcategory_name}',
                'type': 'single',
                'options': [
                    {'text': 'Вариант 1', 'correct': True},
                    {'text': 'Вариант 2', 'correct': False},
                    {'text': 'Вариант 3', 'correct': False},
                    {'text': 'Вариант 4', 'correct': False}
                ],
                'hint': 'Изучите тему подробнее'
            })
        
        return {'questions': questions}
