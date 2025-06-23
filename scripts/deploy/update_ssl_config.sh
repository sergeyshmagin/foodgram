#!/bin/bash

# =============================================================================
# Скрипт обновления SSL конфигурации для Foodgram на продакшн сервере
# Создает символические ссылки Let's Encrypt сертификатов в стандартной директории
# =============================================================================

set -e

DOMAIN="foodgram.freedynamicdns.net"
APP_DIR="/home/foodgram/app"
SSL_DIR="/etc/ssl/certs"

echo "🔐 Обновление SSL конфигурации для домена: $DOMAIN"

# Проверяем наличие сертификатов Let's Encrypt
echo "🔍 Проверка наличия SSL сертификатов..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ SSL сертификаты не найдены в /etc/letsencrypt/live/$DOMAIN/"
    echo "💡 Сначала запустите скрипт setup_ssl.sh для получения сертификатов"
    exit 1
fi

echo "✅ SSL сертификаты Let's Encrypt найдены!"

# Показываем информацию о сертификате
echo "📋 Информация о текущем сертификате:"
sudo certbot certificates | grep -A 10 "$DOMAIN" || true

# Создаем символические ссылки в стандартной директории
echo "🔗 Создание символических ссылок в $SSL_DIR..."

# Создаем директорию если не существует
sudo mkdir -p $SSL_DIR

# Удаляем старые ссылки если они есть
sudo rm -f $SSL_DIR/fullchain.pem
sudo rm -f $SSL_DIR/privkey.pem

# Создаем новые символические ссылки
sudo ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem $SSL_DIR/fullchain.pem
sudo ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem $SSL_DIR/privkey.pem

# Проверяем созданные ссылки
echo "🔍 Проверка созданных символических ссылок:"
sudo ls -la $SSL_DIR/fullchain.pem
sudo ls -la $SSL_DIR/privkey.pem

# Проверяем что ссылки работают
if [ -f "$SSL_DIR/fullchain.pem" ] && [ -f "$SSL_DIR/privkey.pem" ]; then
    echo "✅ Символические ссылки созданы успешно!"
else
    echo "❌ Ошибка создания символических ссылок!"
    exit 1
fi

# Переходим в директорию приложения
cd $APP_DIR

# Проверяем наличие docker-compose файла
if [ ! -f "infra/docker-compose.yml" ]; then
    echo "❌ Файл docker-compose.yml не найден в $APP_DIR/infra/"
    exit 1
fi

# Останавливаем nginx контейнер если запущен
echo "⏹ Остановка nginx контейнера..."
docker-compose -f infra/docker-compose.yml stop nginx 2>/dev/null || true

# Проверяем синтаксис nginx конфигурации
echo "🧪 Проверка синтаксиса nginx конфигурации..."
docker run --rm \
    -v "$(pwd)/infra/nginx.conf:/etc/nginx/conf.d/default.conf:ro" \
    -v "$SSL_DIR:/etc/ssl/certs:ro" \
    nginx:1.25.4-alpine nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Синтаксис nginx конфигурации корректен!"
else
    echo "❌ Ошибка в конфигурации nginx!"
    exit 1
fi

# Запускаем nginx контейнер с новой конфигурацией
echo "🚀 Запуск nginx контейнера с SSL..."
docker-compose -f infra/docker-compose.yml up -d nginx

# Ждем запуска
sleep 5

# Проверяем статус контейнера
echo "📊 Проверка статуса контейнера nginx..."
if docker ps | grep -q "foodgram-nginx"; then
    echo "✅ Nginx контейнер запущен успешно!"
    
    # Проверяем SSL соединение
    echo "🔐 Проверка SSL соединения..."
    timeout 10 openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | grep -q "Verify return code: 0" && \
        echo "✅ SSL соединение работает корректно!" || \
        echo "⚠️ Проблемы с SSL соединением (возможно, DNS еще не обновился)"
    
    # Показываем логи nginx
    echo "📋 Последние логи nginx:"
    docker logs --tail 10 foodgram-nginx
    
else
    echo "❌ Ошибка запуска nginx контейнера!"
    echo "📋 Логи nginx:"
    docker logs foodgram-nginx
    exit 1
fi

# Настраиваем автообновление сертификатов
echo "🔄 Настройка автообновления сертификатов..."

# Создаем скрипт для обновления символических ссылок и перезапуска контейнера
sudo tee /etc/letsencrypt/renewal-hooks/deploy/update-symlinks-and-restart.sh > /dev/null << EOF
#!/bin/bash
# Обновление символических ссылок и перезапуск nginx после обновления сертификата

DOMAIN="$DOMAIN"
SSL_DIR="$SSL_DIR"
APP_DIR="$APP_DIR"

# Обновляем символические ссылки
rm -f \$SSL_DIR/fullchain.pem
rm -f \$SSL_DIR/privkey.pem
ln -sf /etc/letsencrypt/live/\$DOMAIN/fullchain.pem \$SSL_DIR/fullchain.pem
ln -sf /etc/letsencrypt/live/\$DOMAIN/privkey.pem \$SSL_DIR/privkey.pem

# Перезапускаем nginx контейнер
cd \$APP_DIR
docker-compose -f infra/docker-compose.yml restart nginx

echo "\$(date): SSL сертификат обновлен, символические ссылки пересозданы, nginx перезапущен" >> /var/log/certbot-renewal.log
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/update-symlinks-and-restart.sh

# Создаем логи для отслеживания обновлений
sudo touch /var/log/certbot-renewal.log
sudo chmod 644 /var/log/certbot-renewal.log

echo "✅ Автообновление сертификатов настроено!"

# Показываем итоговую информацию
echo ""
echo "🎉 SSL конфигурация успешно обновлена!"
echo "🔗 Домен: https://$DOMAIN"
echo "📁 Оригинальные сертификаты: /etc/letsencrypt/live/$DOMAIN/"
echo "🔗 Символические ссылки: $SSL_DIR/"
echo "🔄 Автообновление: настроено через systemd timer"
echo "📋 Логи обновлений: /var/log/certbot-renewal.log"
echo ""
echo "🧪 Команды для проверки:"
echo "  - Статус контейнеров: docker ps"
echo "  - Логи nginx: docker logs foodgram-nginx"
echo "  - Проверка SSL: curl -I https://$DOMAIN"
echo "  - Проверка ссылок: sudo ls -la $SSL_DIR/"
echo "  - Тест обновления: sudo certbot renew --dry-run" 