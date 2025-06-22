#!/usr/bin/env python3
"""
CORS Integration Test Script for Foodgram
Тестирует CORS настройки между фронтендом и бэкендом
"""

import requests
import json
import sys
from urllib.parse import urljoin


class CORSTester:
    """Тестер CORS интеграции"""
    
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:3000"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.session = requests.Session()
        
    def test_cors_headers(self):
        """Тестирует CORS заголовки"""
        print("🔍 Тестирование CORS заголовков...")
        
        # Тест простого GET запроса
        try:
            response = self.session.get(
                f"{self.backend_url}/api/recipes/",
                headers={'Origin': self.frontend_url}
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials'),
            }
            
            print(f"✅ GET /api/recipes/ - Status: {response.status_code}")
            print("CORS Headers:")
            for header, value in cors_headers.items():
                if value:
                    print(f"  {header}: {value}")
                    
            return response.status_code == 200
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании GET запроса: {e}")
            return False
    
    def test_preflight_request(self):
        """Тестирует preflight OPTIONS запрос"""
        print("\n🔍 Тестирование preflight запроса...")
        
        try:
            response = self.session.options(
                f"{self.backend_url}/api/recipes/",
                headers={
                    'Origin': self.frontend_url,
                    'Access-Control-Request-Method': 'POST',
                    'Access-Control-Request-Headers': 'Content-Type, Authorization'
                }
            )
            
            print(f"✅ OPTIONS /api/recipes/ - Status: {response.status_code}")
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            print("Preflight CORS Headers:")
            for header, value in cors_headers.items():
                if value:
                    print(f"  {header}: {value}")
                    
            return response.status_code in [200, 204]
            
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании preflight запроса: {e}")
            return False
    
    def test_api_endpoints(self):
        """Тестирует основные API endpoints"""
        print("\n🔍 Тестирование основных API endpoints...")
        
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
                    headers={'Origin': self.frontend_url}
                )
                
                status = "✅" if response.status_code == 200 else "❌"
                print(f"{status} GET {endpoint} - Status: {response.status_code}")
                
                results.append(response.status_code == 200)
                
            except requests.RequestException as e:
                print(f"❌ Ошибка при тестировании {endpoint}: {e}")
                results.append(False)
        
        return all(results)
    
    def test_authentication_flow(self):
        """Тестирует аутентификацию с CORS"""
        print("\n🔍 Тестирование аутентификации...")
        
        # Создаем тестового пользователя
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        }
        
        try:
            # Регистрация
            response = self.session.post(
                f"{self.backend_url}/api/users/",
                headers={
                    'Origin': self.frontend_url,
                    'Content-Type': 'application/json'
                },
                json=user_data
            )
            
            if response.status_code in [201, 400]:  # 400 если пользователь уже существует
                print(f"✅ POST /api/users/ - Status: {response.status_code}")
            else:
                print(f"❌ POST /api/users/ - Status: {response.status_code}")
                return False
            
            # Авторизация
            login_data = {
                "email": user_data["email"],
                "password": user_data["password"]
            }
            
            response = self.session.post(
                f"{self.backend_url}/api/auth/token/login/",
                headers={
                    'Origin': self.frontend_url,
                    'Content-Type': 'application/json'
                },
                json=login_data
            )
            
            if response.status_code == 200:
                print(f"✅ POST /api/auth/token/login/ - Status: {response.status_code}")
                token_data = response.json()
                token = token_data.get('auth_token')
                
                if token:
                    print(f"✅ Получен токен аутентификации")
                    return True
                else:
                    print(f"❌ Токен не получен")
                    return False
            else:
                print(f"❌ POST /api/auth/token/login/ - Status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Ошибка при тестировании аутентификации: {e}")
            return False
    
    def run_all_tests(self):
        """Запускает все тесты"""
        print("🚀 Запуск CORS интеграционных тестов Foodgram")
        print(f"Backend: {self.backend_url}")
        print(f"Frontend: {self.frontend_url}")
        print("=" * 50)
        
        results = []
        
        # Проверяем доступность бэкенда
        try:
            response = self.session.get(f"{self.backend_url}/api/")
            if response.status_code != 200:
                print(f"❌ Бэкенд недоступен: {self.backend_url}")
                return False
            print(f"✅ Бэкенд доступен: {self.backend_url}")
        except requests.RequestException:
            print(f"❌ Бэкенд недоступен: {self.backend_url}")
            return False
        
        # Запускаем тесты
        results.append(self.test_cors_headers())
        results.append(self.test_preflight_request())
        results.append(self.test_api_endpoints())
        results.append(self.test_authentication_flow())
        
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        
        test_names = [
            "CORS заголовки",
            "Preflight запросы",
            "API endpoints",
            "Аутентификация"
        ]
        
        for i, (test_name, result) in enumerate(zip(test_names, results)):
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{i+1}. {test_name}: {status}")
        
        overall_result = all(results)
        overall_status = "✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if overall_result else "❌ ЕСТЬ ПРОВАЛЕННЫЕ ТЕСТЫ"
        
        print(f"\n🎯 ОБЩИЙ РЕЗУЛЬТАТ: {overall_status}")
        
        if not overall_result:
            print("\n💡 РЕКОМЕНДАЦИИ:")
            print("1. Проверьте настройки CORS в backend/foodgram/settings/")
            print("2. Убедитесь, что corsheaders установлен и настроен")
            print("3. Проверьте, что фронтенд запущен на localhost:3000")
            print("4. Проверьте, что бэкенд запущен на localhost:8000")
        
        return overall_result


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CORS Integration Tester for Foodgram')
    parser.add_argument('--backend', default='http://localhost:8000', help='Backend URL')
    parser.add_argument('--frontend', default='http://localhost:3000', help='Frontend URL')
    
    args = parser.parse_args()
    
    tester = CORSTester(args.backend, args.frontend)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 