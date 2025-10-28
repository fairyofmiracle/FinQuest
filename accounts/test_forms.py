from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import CustomUserCreationForm

User = get_user_model()

class CustomUserCreationFormTest(TestCase):
    def test_form_valid_data(self):
        """Тестирует форму с валидными данными"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_email(self):
        """Тестирует форму с невалидным email"""
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_password_mismatch(self):
        """Тестирует форму с несовпадающими паролями"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_weak_password(self):
        """Тестирует форму со слабым паролем"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': '123',
            'password2': '123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_duplicate_username(self):
        """Тестирует форму с дублирующимся именем пользователя"""
        # Создаем существующего пользователя
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_form_duplicate_email(self):
        """Тестирует форму с дублирующимся email"""
        # Создаем существующего пользователя
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_empty_fields(self):
        """Тестирует форму с пустыми полями"""
        form_data = {}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
    
    def test_form_save(self):
        """Тестирует сохранение формы"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('newpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_form_save_commit_false(self):
        """Тестирует сохранение формы с commit=False"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save(commit=False)
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertFalse(user.pk)  # Пользователь не сохранен в БД
    
    def test_form_clean_username(self):
        """Тестирует валидацию имени пользователя"""
        form_data = {
            'username': 'a',  # Слишком короткое имя
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_form_clean_email(self):
        """Тестирует валидацию email"""
        form_data = {
            'username': 'newuser',
            'email': 'not-an-email',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_form_clean_password2(self):
        """Тестирует валидацию подтверждения пароля"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_meta_fields(self):
        """Тестирует поля формы"""
        form = CustomUserCreationForm()
        expected_fields = ['username', 'email', 'password1', 'password2']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_form_widgets(self):
        """Тестирует виджеты формы"""
        form = CustomUserCreationForm()
        
        # Проверяем, что email имеет правильный тип поля
        self.assertEqual(form.fields['email'].widget.input_type, 'email')
        
        # Проверяем, что пароли имеют правильный тип поля
        self.assertEqual(form.fields['password1'].widget.input_type, 'password')
        self.assertEqual(form.fields['password2'].widget.input_type, 'password')
    
    def test_form_help_text(self):
        """Тестирует справочный текст формы"""
        form = CustomUserCreationForm()
        
        # Проверяем наличие справочного текста для паролей
        self.assertIsNotNone(form.fields['password1'].help_text)
        self.assertIsNotNone(form.fields['password2'].help_text)
    
    def test_form_error_messages(self):
        """Тестирует сообщения об ошибках"""
        form_data = {
            'username': 'a',
            'email': 'invalid-email',
            'password1': '123',
            'password2': 'different'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Проверяем, что есть сообщения об ошибках
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
    
    def test_form_case_sensitivity(self):
        """Тестирует чувствительность к регистру"""
        # Создаем пользователя с именем в нижнем регистре
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Пытаемся создать пользователя с тем же именем в верхнем регистре
        form_data = {
            'username': 'TESTUSER',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        # Django по умолчанию не чувствителен к регистру для username
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_form_email_case_insensitivity(self):
        """Тестирует нечувствительность email к регистру"""
        # Создаем пользователя с email в нижнем регистре
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Пытаемся создать пользователя с тем же email в верхнем регистре
        form_data = {
            'username': 'newuser',
            'email': 'TEST@EXAMPLE.COM',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        form = CustomUserCreationForm(data=form_data)
        # Django по умолчанию не чувствителен к регистру для email
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
