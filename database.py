import sqlite3
from flask import g

DATABASE = 'produtos.db'

def conectar_bd():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def criar_tabelas():
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS administradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                quantidade INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                quantidade_vendida INTEGER NOT NULL,
                data_venda TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        ''')
        conn.commit()

def adicionar_admin(username, password):
    with conectar_bd() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO administradores (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

def inicializar_bd():
    criar_tabelas()
    adicionar_admin('admin', '$2b$12$abcdefghijklmnopqrstuv')  # Senha: "admin123"
