"""
Валидаторы для проверки пользовательских данных
"""
import re
from django.core.exceptions import ValidationError
from django.utils.html import escape


def validate_quiz_answer(answer_data, question):
    """
    Валидирует ответ на вопрос викторины
    
    Args:
        answer_data: данные ответа из POST
        question: объект вопроса
    
    Returns:
        Валидированные данные или raises ValidationError
    """
    question_type = question.get('type', 'single')
    
    if question_type == 'matching':
        return validate_matching_answer(answer_data, question)
    elif question_type == 'sorting':
        return validate_sorting_answer(answer_data, question)
    elif question_type == 'multiple':
        return validate_multiple_answer(answer_data, question)
    else:
        return validate_single_answer(answer_data, question)


def validate_matching_answer(answer_data, question):
    """Валидирует ответ на matching вопрос"""
    selected_matches = []
    
    for key, value in answer_data.items():
        if key.startswith('match_'):
            try:
                right_idx = int(key.split('_')[1])
                left_idx = int(value)
                
                # Проверяем индексы
                if left_idx < 0 or right_idx < 0:
                    raise ValidationError("Недопустимые индексы")
                
                if left_idx >= len(question.get('left_items', [])):
                    raise ValidationError("Недопустимый левый индекс")
                
                if right_idx >= len(question.get('right_items', [])):
                    raise ValidationError("Недопустимый правый индекс")
                
                selected_matches.append([left_idx, right_idx])
            except (ValueError, IndexError) as e:
                raise ValidationError(f"Ошибка парсинга: {e}")
    
    return selected_matches


def validate_sorting_answer(answer_data, question):
    """Валидирует ответ на sorting вопрос"""
    selected_order = []
    items = question.get('items', [])
    
    # Собираем в правильном порядке (sort_0, sort_1, sort_2, ...)
    sort_keys = sorted([key for key in answer_data.keys() if key.startswith('sort_')])
    
    for key in sort_keys:
        try:
            item_id = int(answer_data[key])
            
            # Проверяем, что такой ID существует
            if not any(item.get('id') == item_id for item in items):
                raise ValidationError(f"Недопустимый ID элемента: {item_id}")
            
            selected_order.append(item_id)
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Ошибка парсинга сортировки: {e}")
    
    return selected_order


def validate_multiple_answer(answer_data, question):
    """Валидирует ответ на множественный выбор"""
    if 'answers' not in answer_data:
        raise ValidationError("Не указаны ответы")
    
    selected_indices = answer_data.getlist('answers') if hasattr(answer_data, 'getlist') else answer_data.get('answers', [])
    
    if not selected_indices:
        raise ValidationError("Выберите хотя бы один вариант")
    
    try:
        selected_indices = [int(i) for i in selected_indices]
    except (ValueError, TypeError):
        raise ValidationError("Недопустимые индексы ответов")
    
    # Проверяем, что индексы в допустимом диапазоне
    max_index = len(question.get('options', [])) - 1
    if any(idx < 0 or idx > max_index for idx in selected_indices):
        raise ValidationError("Недопустимые индексы ответов")
    
    return selected_indices


def validate_single_answer(answer_data, question):
    """Валидирует ответ на одиночный выбор"""
    if 'answer' not in answer_data:
        raise ValidationError("Не указан ответ")
    
    try:
        selected_index = int(answer_data['answer'])
    except (ValueError, TypeError):
        raise ValidationError("Недопустимый индекс ответа")
    
    # Проверяем, что индекс в допустимом диапазоне
    max_index = len(question.get('options', [])) - 1
    if selected_index < 0 or selected_index > max_index:
        raise ValidationError("Недопустимый индекс ответа")
    
    return selected_index


def sanitize_user_input(text):
    """
    Очищает пользовательский ввод от потенциально опасных символов
    
    Args:
        text: текст для очистки
    
    Returns:
        Очищенный текст
    """
    if not text:
        return ""
    
    # Экранируем HTML
    text = escape(text)
    
    # Удаляем потенциально опасные паттерны
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def validate_question_index(index, total_questions):
    """
    Валидирует индекс вопроса
    
    Args:
        index: индекс вопроса
        total_questions: общее количество вопросов
    
    Returns:
        Валидированный индекс или raises ValidationError
    """
    try:
        index = int(index)
    except (ValueError, TypeError):
        raise ValidationError("Недопустимый индекс вопроса")
    
    if index < 0 or index >= total_questions:
        raise ValidationError(f"Индекс вопроса вне диапазона (0-{total_questions-1})")
    
    return index


def validate_completion_time(time_value):
    """
    Валидирует время прохождения
    
    Args:
        time_value: значение времени в секундах
    
    Returns:
        Валидированное время или raises ValidationError
    """
    try:
        time_value = int(time_value)
    except (ValueError, TypeError):
        return 0  # По умолчанию 0
    
    # Проверяем разумные пределы (максимум 1 час)
    if time_value < 0 or time_value > 3600:
        raise ValidationError("Недопустимое время прохождения")
    
    return time_value

