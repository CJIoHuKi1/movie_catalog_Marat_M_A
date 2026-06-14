import sqlite3
import os

DATABASE = 'movies.db'

def get_db():
    """Возвращает соединение с БД"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создаёт таблицу фильмов, если её нет"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            director TEXT NOT NULL,
            year INTEGER NOT NULL,
            genre TEXT NOT NULL,
            rating REAL CHECK(rating >= 1 AND rating <= 10),
            description TEXT,
            poster_url TEXT
        )
    ''')
    conn.commit()
    conn.close()

    # Заполняем тестовыми данными, если БД пустая
    from seed import seed
    seed()
    
def get_all_movies(search=None, genre=None):
    """Возвращает список фильмов с фильтрацией по поиску и жанру"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM movies WHERE 1=1"
    params = []
    
    if search:
        query += " AND title LIKE ?"
        params.append(f'%{search}%')
    
    if genre and genre != 'все':
        query += " AND genre = ?"
        params.append(genre)
    
    query += " ORDER BY title"
    cursor.execute(query, params)
    movies = cursor.fetchall()
    conn.close()
    return movies

def get_movie_by_id(movie_id):
    """Возвращает фильм по ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    conn.close()
    return movie

def add_movie(title, director, year, genre, rating, description, poster_url):
    """Добавляет новый фильм"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO movies (title, director, year, genre, rating, description, poster_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, director, year, genre, rating, description, poster_url))
    conn.commit()
    movie_id = cursor.lastrowid
    conn.close()
    return movie_id

def update_movie(movie_id, title, director, year, genre, rating, description, poster_url):
    """Обновляет информацию о фильме"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE movies
        SET title = ?, director = ?, year = ?, genre = ?, rating = ?, description = ?, poster_url = ?
        WHERE id = ?
    ''', (title, director, year, genre, rating, description, poster_url, movie_id))
    conn.commit()
    conn.close()

def delete_movie(movie_id):
    """Удаляет фильм"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

def get_all_genres():
    """Возвращает список всех жанров"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT genre FROM movies ORDER BY genre")
    genres = [row['genre'] for row in cursor.fetchall()]
    conn.close()
    return genres

def validate_movie_data(title, director, year, genre, rating):
    """Валидация данных формы"""
    errors = []
    if not title or title.strip() == '':
        errors.append('Название фильма обязательно')
    if not director or director.strip() == '':
        errors.append('Режиссёр обязателен')
    if not year:
        errors.append('Год выпуска обязателен')
    elif year < 1888 or year > 2026:
        errors.append('Год должен быть от 1888 до 2026')
    if not genre or genre.strip() == '':
        errors.append('Жанр обязателен')
    if not rating:
        errors.append('Оценка обязательна')
    elif rating < 1 or rating > 5:
        errors.append('Оценка должна быть от 1 до 5')
    return errors# Модели для работы с базой данных
