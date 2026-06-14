from flask import Flask, render_template, request, redirect, url_for, abort
import models

app = Flask(__name__)

# Инициализация БД при первом запуске
models.init_db()

@app.route('/')
def index():
    """Главная страница — список фильмов с поиском и фильтром"""
    search = request.args.get('search', '')
    genre = request.args.get('genre', 'все')
    movies = models.get_all_movies(search=search, genre=genre if genre != 'все' else None)
    genres = models.get_all_genres()
    return render_template('index.html', movies=movies, search=search, genre=genre, genres=genres)

@app.route('/movie/<int:movie_id>')
def detail(movie_id):
    """Детальная страница фильма"""
    movie = models.get_movie_by_id(movie_id)
    if movie is None:
        abort(404)
    return render_template('detail.html', movie=movie)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Добавление нового фильма"""
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form.get('year', type=int)
        genre = request.form['genre']
        rating = request.form.get('rating', type=int)
        description = request.form['description']
        poster_url = request.form['poster_url']
        
        # Валидация
        errors = models.validate_movie_data(title, director, year, genre, rating)
        if errors:
            return render_template('add.html', errors=errors, form_data=request.form)
        
        models.add_movie(title, director, year, genre, rating, description, poster_url)
        return redirect(url_for('index'))
    
    return render_template('add.html', errors=None, form_data={})

@app.route('/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    """Редактирование фильма"""
    movie = models.get_movie_by_id(movie_id)
    if movie is None:
        abort(404)
    
    if request.method == 'POST':
        title = request.form['title']
        director = request.form['director']
        year = request.form.get('year', type=int)
        genre = request.form['genre']
        rating = request.form.get('rating', type=float)
        description = request.form['description']
        poster_url = request.form['poster_url']
        
        errors = models.validate_movie_data(title, director, year, genre, rating)
        if errors:
            return render_template('edit.html', movie=movie, errors=errors, form_data=request.form)
        
        models.update_movie(movie_id, title, director, year, genre, rating, description, poster_url)
        return redirect(url_for('detail', movie_id=movie_id))
    
    return render_template('edit.html', movie=movie, errors=None, form_data=movie)

@app.route('/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    """Удаление фильма"""
    movie = models.get_movie_by_id(movie_id)
    if movie is None:
        abort(404)
    models.delete_movie(movie_id)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки"""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)# Главный файл приложения
