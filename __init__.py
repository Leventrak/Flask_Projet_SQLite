from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
import hashlib

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Fonctions utilitaires
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Décorateurs pour la protection des routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Accès réservé aux administrateurs', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes principales
@app.route('/')
def index():
    # Récupérer les statistiques
    conn = get_db()
    
    # Total des livres disponibles
    total_books = conn.execute('SELECT SUM(available) FROM books').fetchone()[0]
    
    # Total des emprunts actifs
    active_loans = conn.execute('SELECT COUNT(*) FROM loans WHERE return_date IS NULL').fetchone()[0]
    
    # Total des utilisateurs
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    
    # Récupérer les 3 derniers livres ajoutés
    recent_books = conn.execute('''
        SELECT title, author, quantity, available 
        FROM books 
        ORDER BY id DESC 
        LIMIT 3
    ''').fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         total_books=total_books,
                         active_loans=active_loans,
                         total_users=total_users,
                         recent_books=recent_books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                         (username, password)).fetchone()
        db.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        
        flash('Identifiants incorrects', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Routes pour la gestion des livres
@app.route('/books')
def list_books():
    db = get_db()
    books = db.execute('SELECT * FROM books ORDER BY title').fetchall()
    db.close()
    return render_template('books/list.html', books=books)

@app.route('/books/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        db = get_db()
        db.execute('INSERT INTO books (title, author, isbn, quantity) VALUES (?, ?, ?, ?)',
                  (request.form['title'], request.form['author'], 
                   request.form['isbn'], request.form['quantity']))
        db.commit()
        db.close()
        flash('Livre ajouté avec succès', 'success')
        return redirect(url_for('list_books'))
    return render_template('books/add.html')

@app.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_book(id):
    db = get_db()
    if request.method == 'POST':
        db.execute('UPDATE books SET title = ?, author = ?, isbn = ?, quantity = ? WHERE id = ?',
                  (request.form['title'], request.form['author'], 
                   request.form['isbn'], request.form['quantity'], id))
        db.commit()
        flash('Livre modifié avec succès', 'success')
        return redirect(url_for('list_books'))
    
    book = db.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('books/edit.html', book=book)

@app.route('/books/<int:id>/delete', methods=['POST'])
@admin_required
def delete_book(id):
    db = get_db()
    db.execute('DELETE FROM books WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Livre supprimé avec succès', 'success')
    return redirect(url_for('list_books'))

# Routes pour les emprunts
@app.route('/loans')
@login_required
def list_loans():
    db = get_db()
    try:
        if session['role'] == 'admin':
            loans = db.execute('''
                SELECT l.id, l.loan_date, l.due_date, l.return_date, l.status,
                       b.title, u.username,
                       CASE 
                           WHEN l.return_date IS NULL AND l.due_date < datetime('now', 'localtime')
                           THEN 1 
                           ELSE 0 
                       END as is_overdue
                FROM loans l
                JOIN books b ON l.book_id = b.id 
                JOIN users u ON l.user_id = u.id 
                ORDER BY l.loan_date DESC
            ''').fetchall()
        else:
            loans = db.execute('''
                SELECT l.id, l.loan_date, l.due_date, l.return_date, l.status,
                       b.title,
                       CASE 
                           WHEN l.return_date IS NULL AND l.due_date < datetime('now', 'localtime')
                           THEN 1 
                           ELSE 0 
                       END as is_overdue
                FROM loans l
                JOIN books b ON l.book_id = b.id 
                WHERE l.user_id = ? 
                ORDER BY l.loan_date DESC
            ''', (session['user_id'],)).fetchall()
        
        # Convertir les résultats en liste de dictionnaires
        loans_list = []
        for loan in loans:
            loan_dict = dict(loan)
            # Convertir les dates en objets datetime
            for date_field in ['loan_date', 'due_date', 'return_date']:
                if loan_dict.get(date_field):
                    try:
                        loan_dict[date_field] = datetime.strptime(loan_dict[date_field], '%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        loan_dict[date_field] = None
            loans_list.append(loan_dict)
        
        return render_template('loans/list.html', loans=loans_list)
        
    except Exception as e:
        flash(f'Une erreur est survenue : {str(e)}', 'error')
        return redirect(url_for('index'))
    finally:
        db.close()

@app.route('/loans/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    db = get_db()
    book = db.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
    
    if not book or book['available'] < 1:
        flash('Ce livre n\'est pas disponible', 'error')
        return redirect(url_for('list_books'))
    
    due_date = datetime.now() + timedelta(days=14)
    db.execute('''
        INSERT INTO loans (book_id, user_id, due_date) 
        VALUES (?, ?, ?)
    ''', (book_id, session['user_id'], due_date))
    
    db.execute('UPDATE books SET available = available - 1 WHERE id = ?', (book_id,))
    db.commit()
    db.close()
    
    flash('Livre emprunté avec succès', 'success')
    return redirect(url_for('list_loans'))

@app.route('/loans/<int:id>/return', methods=['POST'])
@login_required
def return_book(id):
    db = get_db()
    loan = db.execute('SELECT * FROM loans WHERE id = ?', (id,)).fetchone()
    
    if loan and (session['role'] == 'admin' or loan['user_id'] == session['user_id']):
        db.execute('''
            UPDATE loans 
            SET status = 'returned', return_date = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (id,))
        db.execute('UPDATE books SET available = available + 1 WHERE id = ?', 
                  (loan['book_id'],))
        db.commit()
        flash('Livre retourné avec succès', 'success')
    else:
        flash('Opération non autorisée', 'error')
    
    db.close()
    return redirect(url_for('list_loans'))

if __name__ == '__main__':
    app.run(debug=True)

application = app  # Pour uWSGI
