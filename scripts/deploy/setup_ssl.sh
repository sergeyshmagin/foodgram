#!/bin/bash

# 🔒 SSL Setup Script for Foodgram Production
# Автоматическая настройка SSL сертификатов через Let's Encrypt

set -e

DOMAIN="foodgram.freedynamicdns.net"
EMAIL="admin@foodgram.ru"
NGINX_CONF="/etc/nginx/sites-available/foodgram"
NGINX_LINK="/etc/nginx/sites-enabled/foodgram"

echo "🔒 Настройка SSL для домена: $DOMAIN"

# Проверяем права root
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт должен запускаться от root"
   exit 1
fi

# Обновляем систему
echo "📦 Обновление системы..."
apt update
apt upgrade -y

# Устанавливаем необходимые пакеты
echo "📦 Установка пакетов..."
apt install -y nginx certbot python3-certbot-nginx curl

# Проверяем что Nginx не запущен (будет запущен через Docker)
echo "🔧 Останавливаем системный Nginx..."
systemctl stop nginx || true
systemctl disable nginx || true

# Создаем директорию для webroot challenge
echo "📁 Создание директорий..."
mkdir -p /var/www/certbot
mkdir -p /etc/letsencrypt/live/$DOMAIN

# Создаем временную конфигурацию Nginx для получения сертификата
echo "⚙️ Создание временной конфигурации Nginx..."
cat > /tmp/nginx_temp.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 200 "SSL setup in progress...";
        add_header Content-Type text/plain;
    }
}
EOF

# Запускаем временный Nginx для получения сертификата
echo "🚀 Запуск временного Nginx..."
docker run --rm -d \
    --name nginx-ssl-temp \
    -p 80:80 \
    -v /tmp/nginx_temp.conf:/etc/nginx/conf.d/default.conf \
    -v /var/www/certbot:/var/www/certbot \
    nginx:alpine

# Ждем запуска Nginx
sleep 5

# Получаем SSL сертификат
echo "🔐 Получение SSL сертификата..."
certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --force-renewal \
    -d $DOMAIN

# Останавливаем временный Nginx
echo "🛑 Остановка временного Nginx..."
docker stop nginx-ssl-temp || true

# Проверяем что сертификат получен
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "❌ Ошибка: Сертификат не получен!"
    exit 1
fi

echo "✅ SSL сертификат успешно получен!"

# Настраиваем автообновление сертификата
echo "🔄 Настройка автообновления..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'docker exec foodgram-prod-nginx nginx -s reload'") | crontab -

# Создаем скрипт для обновления сертификата
cat > /usr/local/bin/renew-ssl.sh << 'EOF'
#!/bin/bash
# Обновление SSL сертификата для Foodgram

echo "🔄 Проверка обновления SSL сертификата..."
certbot renew --quiet

# Перезагружаем Nginx в Docker контейнере
if docker ps | grep -q foodgram-prod-nginx; then
    echo "🔄 Перезагрузка Nginx..."
    docker exec foodgram-prod-nginx nginx -s reload
    echo "✅ Nginx перезагружен"
else
    echo "⚠️ Контейнер foodgram-prod-nginx не найден"
fi
EOF

chmod +x /usr/local/bin/renew-ssl.sh

# Создаем systemd timer для автообновления
cat > /etc/systemd/system/ssl-renew.service << EOF
[Unit]
Description=Renew SSL certificates for Foodgram
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/renew-ssl.sh
User=root
EOF

cat > /etc/systemd/system/ssl-renew.timer << EOF
[Unit]
Description=Run SSL renewal twice daily
Requires=ssl-renew.service

[Timer]
OnCalendar=*-*-* 12:00:00
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Активируем timer
systemctl daemon-reload
systemctl enable ssl-renew.timer
systemctl start ssl-renew.timer

# Показываем информацию о сертификате
echo "📋 Информация о сертификате:"
certbot certificates

echo ""
echo "✅ SSL настройка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Запустите Docker Compose с обновленной конфигурацией Nginx"
echo "2. Проверьте доступность сайта по HTTPS: https://$DOMAIN"
echo "3. Проверьте автообновление: systemctl status ssl-renew.timer"
echo ""
echo "🔧 Полезные команды:"
echo "- Проверка сертификата: certbot certificates"
echo "- Тест обновления: certbot renew --dry-run"
echo "- Просмотр логов: journalctl -u ssl-renew.service"
echo "- Статус timer: systemctl status ssl-renew.timer"
echo ""
echo "🔒 SSL сертификат будет автоматически обновляться каждые 12 часов" 