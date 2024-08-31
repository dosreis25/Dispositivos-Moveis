from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from database import conectar_bd, inicializar_bd

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.before_request
def antes_requisicao():
    g.db = conectar_bd()

@app.teardown_request
def depois_requisicao(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = g.db.execute('SELECT * FROM administradores WHERE username = ?', (username,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin[2], password):
            session['admin'] = username
            return redirect(url_for('ver_registros'))

        return 'Login inválido, tente novamente.'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])
        quantidade = int(request.form['quantidade'])

        g.db.execute('INSERT INTO produtos (nome, descricao, preco, quantidade) VALUES (?, ?, ?, ?)',
                     (nome, descricao, preco, quantidade))
        g.db.commit()
        return redirect(url_for('listar_produtos'))

    return render_template('cadastrar_produto.html')

@app.route('/produtos')
def listar_produtos():
    cursor = g.db.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    return render_template('listar_produtos.html', produtos=produtos)

@app.route('/vender', methods=['GET', 'POST'])
def realizar_venda():
    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        quantidade_vendida = int(request.form['quantidade_vendida'])

        cursor = g.db.execute('SELECT quantidade FROM produtos WHERE id = ?', (produto_id,))
        produto = cursor.fetchone()

        if produto and produto[0] >= quantidade_vendida:
            g.db.execute('UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?',
                         (quantidade_vendida, produto_id))
            g.db.execute('INSERT INTO vendas (produto_id, quantidade_vendida, data_venda) VALUES (?, ?, ?)',
                         (produto_id, quantidade_vendida, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            g.db.commit()
            return redirect(url_for('listar_produtos'))
        else:
            return 'Quantidade insuficiente em estoque.'

    cursor = g.db.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    return render_template('realizar_venda.html', produtos=produtos)

@app.route('/registros')
def ver_registros():
    if 'admin' not in session:
        return redirect(url_for('login'))

    cursor = g.db.execute('''
        SELECT v.id, p.nome, v.quantidade_vendida, v.data_venda 
        FROM vendas v JOIN produtos p ON v.produto_id = p.id
    ''')
    vendas = cursor.fetchall()
    return render_template('ver_registros.html', vendas=vendas)

if __name__ == '__main__':
    inicializar_bd()
    app.run(debug=True)
