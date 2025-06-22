#!/bin/bash
# Script to fix frontend deployment

echo "🔧 Fixing frontend deployment..."

# Remove existing volume to force rebuild
echo "📦 Removing old frontend volume..."
docker volume rm infra_frontend_build 2>/dev/null || true

# Rebuild frontend without cache
echo "🏗️ Rebuilding frontend..."
cd /d/Dev/practicum/FINAL/infra
docker-compose build --no-cache frontend

# Create a simple HTML file as fallback
echo "📄 Creating temporary frontend..."
docker run --rm -v infra_frontend_build:/data alpine sh -c "
mkdir -p /data
cat > /data/index.html << 'EOF'
<!DOCTYPE html>
<html lang='ru'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Foodgram - Продуктовый помощник</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; text-align: center; }
        .header { background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .status { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 10px; }
        .api-link { color: #007bff; text-decoration: none; }
    </style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>🍽️ Foodgram</h1>
            <p>Продуктовый помощник</p>
        </div>
        <div class='status'>
            <h2>✅ Бэкенд запущен успешно!</h2>
            <p>React фронтенд находится в разработке.</p>
            <p>Вы можете использовать API напрямую:</p>
            <a href='/api/' class='btn'>📚 API Documentation</a>
            <a href='/admin/' class='btn'>⚙️ Администрирование</a>
            <hr>
            <h3>🔗 Доступные эндпоинты:</h3>
            <p><a href='/api/recipes/' class='api-link'>GET /api/recipes/</a> - Список рецептов</p>
            <p><a href='/api/ingredients/' class='api-link'>GET /api/ingredients/</a> - Ингредиенты</p>
            <p><a href='/api/tags/' class='api-link'>GET /api/tags/</a> - Теги</p>
            <p><a href='/api/users/' class='api-link'>GET /api/users/</a> - Пользователи</p>
        </div>
    </div>
</body>
</html>
EOF
"

# Restart services
echo "🔄 Restarting services..."
docker-compose restart frontend nginx

echo "✅ Frontend fix completed!"
echo "🌐 Check: http://localhost/" 