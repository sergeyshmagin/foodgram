# 🔒 Безопасный деплой Foodgram

## 📋 Обзор

Данное руководство описывает лучшие практики для безопасного развертывания проекта Foodgram в продакшн окружении.

## ⚠️ Критически важно!

**НИКОГДА НЕ ИСПОЛЬЗУЙТЕ ХАРДКОД ПАРОЛЕЙ В DOCKERFILE ИЛИ ИСХОДНОМ КОДЕ!**

## 🔐 Создание администратора

### Безопасный способ (рекомендуется)

#### 1. Через переменные окружения

```bash
# Установите переменные окружения
export ADMIN_EMAIL=admin@yourdomain.com
export ADMIN_PASSWORD=YourSuperStrongPassword123!
export ADMIN_USERNAME=admin

# Запустите контейнер с этими переменными
docker run -d \
  -e ADMIN_EMAIL=$ADMIN_EMAIL \
  -e ADMIN_PASSWORD=$ADMIN_PASSWORD \
  -e ADMIN_USERNAME=$ADMIN_USERNAME \
  your-foodgram-image
```

#### 2. Через management команду после запуска

```bash
# Войдите в контейнер
docker exec -it foodgram-backend bash

# Создайте админа безопасно
python manage.py create_admin_safe \
  --email admin@yourdomain.com \
  --password "YourStrongPassword123!" \
  --username admin
```

#### 3. Через docker-compose с env файлом

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - ADMIN_EMAIL=${ADMIN_EMAIL}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - ADMIN_USERNAME=${ADMIN_USERNAME}
    env_file:
      - .env
```

```bash
# .env файл (НЕ КОММИТЬТЕ В GIT!)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourSuperStrongPassword123!
ADMIN_USERNAME=admin
```

## 🚫 Небезопасные способы (НЕ ИСПОЛЬЗУЙТЕ!)

### ❌ Хардкод в Dockerfile
```dockerfile
# ПЛОХО! НЕ ДЕЛАЙТЕ ТАК!
RUN python manage.py shell -c "User.objects.create_superuser('admin', 'admin123')"
```

### ❌ Простые пароли
```bash
# ПЛОХО! Слишком простые пароли
ADMIN_PASSWORD=admin
ADMIN_PASSWORD=123456
ADMIN_PASSWORD=password
```

### ❌ Пароли в открытом виде
```bash
# ПЛОХО! Пароль виден в истории команд
docker run -e ADMIN_PASSWORD=mypassword image
```

## 🔑 Требования к паролям

### Минимальные требования:
- ✅ Минимум 8 символов (рекомендуется 12+)
- ✅ Содержит заглавные буквы (A-Z)
- ✅ Содержит строчные буквы (a-z)
- ✅ Содержит цифры (0-9)
- ✅ Содержит специальные символы (!@#$%^&*)

### Примеры хороших паролей:
```
MyS3cur3P@ssw0rd!
Admin2024#Secure$
FoodGr@m$tR0ng2024!
```

## 🛠️ Управление админом через команды

### Создание нового админа
```bash
python manage.py create_admin_safe \
  --email admin@example.com \
  --password "StrongPassword123!" \
  --username admin
```

### Обновление существующего админа
```bash
python manage.py create_admin_safe \
  --email admin@example.com \
  --password "NewStrongPassword123!" \
  --force
```

### Проверка созданного админа
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
admin = User.objects.filter(email='admin@example.com').first();
print(f'Admin exists: {admin is not None}');
print(f'Is superuser: {admin.is_superuser if admin else False}')
"
```

## 🔧 Настройка в CI/CD

### GitHub Actions
```yaml
env:
  ADMIN_EMAIL: ${{ secrets.ADMIN_EMAIL }}
  ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
  ADMIN_USERNAME: ${{ secrets.ADMIN_USERNAME }}
```

### GitLab CI
```yaml
variables:
  ADMIN_EMAIL: $ADMIN_EMAIL
  ADMIN_PASSWORD: $ADMIN_PASSWORD
  ADMIN_USERNAME: $ADMIN_USERNAME
```

## 📝 Чеклист безопасности

### Перед деплоем:
- [ ] Пароль админа соответствует требованиям безопасности
- [ ] Переменные окружения настроены правильно
- [ ] Секреты не попали в git репозиторий
- [ ] .env файлы добавлены в .gitignore
- [ ] SECRET_KEY уникален для продакшена
- [ ] DEBUG=False в продакшене

### После деплоя:
- [ ] Админ создан успешно
- [ ] Можно войти в админ-панель
- [ ] Смените пароль при первом входе
- [ ] Удалите тестовые аккаунты
- [ ] Проверьте логи на ошибки

## 🚨 Что делать при компрометации

### Если пароль админа скомпрометирован:

1. **Немедленно смените пароль:**
```bash
python manage.py create_admin_safe \
  --email admin@example.com \
  --password "NewSecurePassword123!" \
  --force
```

2. **Проверьте логи на подозрительную активность:**
```bash
grep "admin" /app/logs/*.log
docker logs foodgram-backend | grep -i "login\|auth"
```

3. **Обновите все секреты:**
```bash
# Смените SECRET_KEY
# Смените пароли базы данных
# Смените ключи MinIO
```

## 📖 Дополнительные ресурсы

- [Django Security Guide](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Password Guidelines](https://owasp.org/www-project-cheat-sheets/cheatsheets/Authentication_Cheat_Sheet.html)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/) 