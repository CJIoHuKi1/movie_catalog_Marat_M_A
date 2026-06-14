import pytest
import tempfile
import os
from app import app
import models

@pytest.fixture
def client():
    """Фикстура для тестирования Flask-клиента с временной БД"""
    db_fd, temp_db = tempfile.mkstemp()
    models.DATABASE = temp_db
    models.init_db()
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client
    
    os.close(db_fd)
    os.unlink(temp_db)

def test_index_status(client):
    """Тест 1: Главная страница — код ответа 200"""
    response = client.get('/')
    assert response.status_code == 200

def test_add_movie(client):
    """Тест 2: Добавление объекта — проверка, что объект появляется в БД"""
    response = client.post('/add', data={
        'title': 'Тестовый фильм',
        'director': 'Тест Режиссёр',
        'year': 2023,
        'genre': 'Комедия',
        'rating': 5,
        'description': 'Тестовое описание',
        'poster_url': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Проверяем, что фильм появился в БД
    movies = models.get_all_movies()
    titles = [m['title'] for m in movies]
    assert 'Тестовый фильм' in titles

def test_search_filter(client):
    """Тест 3: Поиск/фильтрация — возвращаются только нужные записи"""
    # Добавляем два фильма
    client.post('/add', data={'title': 'Матрица', 'director': 'Вачи', 'year': 1999, 'genre': 'Фантастика', 'rating': 5, 'description': '', 'poster_url': ''})
    client.post('/add', data={'title': 'Такси', 'director': 'Пирес', 'year': 1998, 'genre': 'Боевик', 'rating': 4, 'description': '', 'poster_url': ''})
    
    # Поиск по названию
    response = client.get('/?search=Матрица')
    content = response.data.decode()
    assert 'Матрица' in content
    assert 'Такси' not in content

def test_404_error(client):
    """Тест 4: Обработка ошибки — 404 при обращении к несуществующему ID"""
    response = client.get('/movie/99999')
    assert response.status_code == 404

def test_validation_empty_title(client):
    """Тест 5: Валидация — отклонение пустого поля названия"""
    response = client.post('/add', data={
        'title': '',
        'director': 'Режиссёр',
        'year': 2023,
        'genre': 'Комедия',
        'rating': 5,
        'description': '',
        'poster_url': ''
    })
    
    content = response.data.decode()
    assert 'Название фильма обязательно' in content