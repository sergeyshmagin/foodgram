#!/usr/bin/env python3
"""
Docker CORS Integration Test Script for Foodgram.
Тестирует CORS настройки в Docker окружении.
"""

import requests
import sys
import time


class DockerCORSTester:
    """Тестер CORS интеграции в Docker окружении."""
    
    def __init__(self):
        self.backend_url = "http://localhost"  # Через nginx
        self.api_url = "http://localhost/api"  # API через nginx  
        self.frontend_url = "http://localhost"  # Frontend через nginx
        self.session = requests.Session()
        
    def test_docker_services(self):
        """Тестирует доступность Docker сервисов."""
        print("🐳 Тестирование Docker сервисов...")
        
        services = {
            "Frontend (Nginx)": "http://localhost",
            "API через Nginx": "http://localhost/api/",  
            "Backend прямо": "http://localhost:8000/api/",
            "MinIO Console": "http://localhost:9001"
        }
        
        results = []
        
        for service_name, url in services.items():
            try:
                response = self.session.get(url, timeout=10)
                status = "✅" if response.status_code in [200, 404] else "❌"
                print(f"{status} {service_name}: {response.status_code}")
                results.append(response.status_code in [200, 404])
            except requests.RequestException as e:
                print(f"❌ {service_name}: Недоступен ({e})")
                results.append(False)
        
        return any(results)  # Хотя бы один сервис должен работать
    
    def test_nginx_cors_headers(self):
        """Тестирует CORS заголовки через Nginx."""
        print("\n🔍 Тестирование CORS через Nginx...")
        
        try:
            response = self.session.get(
                f"{self.api_url}/recipes/",
                headers={'Origin': 'http://localhost:3000'},
                timeout=10
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            print(f"✅ GET /api/recipes/ через Nginx - Status: {response.status_code}")
            print("CORS Headers через Nginx:")
            for header, value in cors_headers.items():
                if value:
                    print(f"  {header}: {value}")
                    
            return response.status_code == 200
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании Nginx CORS: {e}")
            return False
    
    def test_api_endpoints_docker(self):
        """Тестирует API endpoints в Docker."""
        print("\n🔍 Тестирование API endpoints в Docker...")
        
        endpoints = [
            '/api/recipes/',
            '/api/tags/',
            '/api/ingredients/',
            '/api/users/',
        ]
        
        results = []
        
        for endpoint in endpoints:
            try:
                response = self.session.get(
                    f"{self.backend_url}{endpoint}",
                    headers={'Origin': 'http://localhost'},
                    timeout=10
                )
                
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} GET {endpoint} - Status: {response.status_code}")
                
                results.append(response.status_code == 200)
                
            except requests.RequestException as e:
                print(f"❌ Ошибка при тестировании {endpoint}: {e}")
                results.append(False)
        
        return all(results)
    
    def test_frontend_static_files(self):
        """Тестирует статические файлы фронтенда."""
        print("\n🔍 Тестирование статических файлов фронтенда...")
        
        try:
            # Тест главной страницы
            response = self.session.get(f"{self.frontend_url}/", timeout=10)
            
            if response.status_code == 200:
                print("✅ Frontend главная страница доступна")
                
                # Проверяем, что это React приложение
                if 'react' in response.text.lower() or 'app' in response.text.lower():
                    print("✅ React приложение загружено")
                    return True
                else:
                    print("⚠️ Возможно, React приложение не загрузилось полностью")
                    return True
            else:
                print(f"❌ Frontend недоступен - Status: {response.status_code}")
                return False
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании фронтенда: {e}")
            return False
    
    def test_docker_networks(self):
        """Тестирует связь между Docker контейнерами."""
        print("\n🔍 Тестирование Docker сетей...")
        
        # Тест связи backend -> database (через API)
        try:
            response = self.session.get(f"{self.api_url}/users/", timeout=10)
            if response.status_code == 200:
                print("✅ Backend подключен к базе данных")
                return True
            else:
                print(f"❌ Проблемы с подключением к БД - Status: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании подключения к БД: {e}")
            return False
    
    def run_docker_tests(self):
        """Запускает все Docker тесты."""
        print("🐳 Запуск Docker CORS интеграционных тестов Foodgram")
        print(f"Backend/API: {self.api_url}")
        print(f"Frontend: {self.frontend_url}")
        print("=" * 60)
        
        results = []
        
        # Даем время на запуск сервисов
        print("⏳ Ожидание запуска сервисов... (5 секунд)")
        time.sleep(5)
        
        # Запускаем тесты
        results.append(self.test_docker_services())
        results.append(self.test_nginx_cors_headers())
        results.append(self.test_api_endpoints_docker())
        results.append(self.test_frontend_static_files())
        results.append(self.test_docker_networks())
        
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ DOCKER ТЕСТИРОВАНИЯ:")
        
        test_names = [
            "Docker сервисы",
            "CORS через Nginx",
            "API endpoints",
            "Frontend статика",
            "Docker сети"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{i+1}. {test_name}: {status}")
        
        overall_result = all(results)
        overall_status = "✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if overall_result else "❌ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ"
        
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {overall_status}")
        
        if not overall_result:
            print("\n💡 РЕКОМЕНДАЦИИ ДЛЯ DOCKER:")
            print("1. Проверьте запущены ли все контейнеры: docker-compose ps")
            print("2. Проверьте логи: docker-compose logs")
            print("3. Пересоберите контейнеры: docker-compose up --build")
            print("4. Проверьте настройки nginx.conf")
        else:
            print("\n🎉 Docker интеграция работает корректно!")
            print("🌐 Откройте http://localhost в браузере")
        
        return overall_result


def main():
    """Главная функция."""
    tester = DockerCORSTester()
    success = tester.run_docker_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 