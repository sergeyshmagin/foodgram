#!/bin/bash

echo "=== Проверка содержимого /usr/share/nginx/html/ ==="
docker exec foodgram-proxy ls -la /usr/share/nginx/html/

echo ""
echo "=== Проверка index.html ==="
docker exec foodgram-proxy test -f /usr/share/nginx/html/index.html && echo "index.html EXISTS" || echo "index.html NOT FOUND"

echo ""
echo "=== Права на файлы ==="
docker exec foodgram-proxy ls -la /usr/share/nginx/html/index.html 2>/dev/null || echo "Файл не найден"

echo ""  
echo "=== Содержимое index.html (первые 5 строк) ==="
docker exec foodgram-proxy head -5 /usr/share/nginx/html/index.html 2>/dev/null || echo "Не удается прочитать файл" 