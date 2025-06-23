#!/bin/bash

# =============================================================================
# Скрипт настройки SSL сертификатов через Certbot для Foodgram
# =============================================================================

set -e

DOMAIN="foodgram.freedynamicdns.net"
EMAIL="admin@${DOMAIN}"

echo "🔐 Настройка SSL сертификатов для домена: $DOMAIN"

# Обновляем систему
echo "📦 Обновление системы..."
sudo apt update && sudo apt upgrade -y

# Устанавливаем Certbot
echo "🛠 Установка Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# Останавливаем nginx если запущен
echo "⏹ Остановка nginx..."
sudo systemctl stop nginx 2>/dev/null || true
docker stop foodgram-nginx 2>/dev/null || true

# Получаем сертификат
echo "🔑 Получение SSL сертификата..."
sudo certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN

# Проверяем, что сертификат получен
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "✅ SSL сертификат успешно получен!"
    
    # Показываем информацию о сертификате
    echo "📋 Информация о сертификате:"
    sudo certbot certificates
    
    # Настраиваем автообновление
    echo "🔄 Настройка автообновления сертификата..."
    
    # Создаем скрипт для обновления с перезапуском Docker контейнера
    sudo tee /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh > /dev/null << 'EOF'
#!/bin/bash
# Перезапуск nginx контейнера после обновления сертификата
cd /home/foodgram/app
docker-compose restart nginx
EOF
    
    sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/restart-nginx.sh
    
    # Тестируем автообновление
    echo "🧪 Тестирование автообновления..."
    sudo certbot renew --dry-run
    
    echo "✅ SSL настроен успешно!"
    echo "🔗 Сертификаты находятся в: /etc/letsencrypt/live/$DOMAIN/"
    echo "📅 Автообновление настроено через systemd timer"
    
else
    echo "❌ Ошибка получения SSL сертификата!"
    exit 1
fi

# Создаем символические ссылки для Docker
echo "🔗 Создание символических ссылок для Docker..."
sudo mkdir -p /home/foodgram/app/infra/ssl
sudo ln -sf /etc/letsencrypt/live/$DOMAIN/fullchain.pem /home/foodgram/app/infra/ssl/
sudo ln -sf /etc/letsencrypt/live/$DOMAIN/privkey.pem /home/foodgram/app/infra/ssl/

echo "🎉 SSL настройка завершена!"
echo "🚀 Теперь можно запускать Docker контейнеры с HTTPS" 