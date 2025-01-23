import sqlite3
import hashlib
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connexion à la base de données
connection = sqlite3.connect('database.db')

# Lecture et exécution du schéma SQL
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Ajout des utilisateurs de test
cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
           ('admin', hash_password('admin123'), 'admin'))
cur.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
           ('user', hash_password('user123'), 'user'))

# Ajout de quelques livres de test
books = [
    ('Le Petit Prince', 'Antoine de Saint-Exupéry', '978-2-07-040850-4', 2),
    ('1984', 'George Orwell', '978-2-07-036822-8', 3),
    ('L\'Étranger', 'Albert Camus', '978-2-07-036002-4', 1),
    ('Notre-Dame de Paris', 'Victor Hugo', '978-2-253-00637-6', 2),
    ('Les Misérables', 'Victor Hugo', '978-2-253-09634-7', 2)
]

for book in books:
    cur.execute('''
        INSERT INTO books (title, author, isbn, quantity, available) 
        VALUES (?, ?, ?, ?, ?)
    ''', (book[0], book[1], book[2], book[3], book[3]))

# Ajout de quelques emprunts de test
cur.execute("SELECT id FROM users WHERE username = 'user' LIMIT 1")
user_id = cur.fetchone()[0]

cur.execute("SELECT id FROM books WHERE title = 'Le Petit Prince' LIMIT 1")
book_id = cur.fetchone()[0]

# Créer un emprunt actif
due_date = datetime.now() + timedelta(days=14)
cur.execute('''
    INSERT INTO loans (book_id, user_id, due_date) 
    VALUES (?, ?, ?)
''', (book_id, user_id, due_date))

# Mettre à jour la disponibilité du livre
cur.execute('UPDATE books SET available = available - 1 WHERE id = ?', (book_id,))

connection.commit()
connection.close()

print("Base de données créée avec succès avec les données de test !")
