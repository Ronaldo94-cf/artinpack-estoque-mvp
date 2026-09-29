from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'artinpack_secret_key'

DB_NAME = 'database.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                minimo INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                data TEXT NOT NULL,
                responsavel TEXT NOT NULL
            )
        ''')
        # Inserir dados iniciais de exemplo
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Caixa de Papelão Reforçada', 15, 5)")
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Fita Adhesiva Padrão', 2, 10)")
        cursor.execute("INSERT INTO produtos (nome, quantidade, minimo) VALUES ('Plástico Bolha (Metro)', 48, 10)")
        conn.commit()
        conn.close()

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= minimo")
    estoque_baixo = cursor.fetchone()[0]
    
    cursor.execute("SELECT item, cetxliação FROM (SELECT nome as item, quantidade as cetxliação FROM produtos WHERE quantidade <= minimo)")
    criticos = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', total_produtos=total_produtos, estoque_baixo=estoque_baixo, criticos=criticos)

@app.route('/movimentacao', methods=['GET', 'POST'])
def movimentacao():
    if request.method == 'POST':
        tipo = request.form['tipo']
        produto = request.form['produto']
        quantidade = int(request.form['quantidade'])
        data = request.form['data']
        responsavel = request.form['responsavel']
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movimentacoes (tipo, produto, quantidade, data, responsavel) VALUES (?, ?, ?, ?, ?)",
                       (tipo, produto, quantidade, data, responsavel))
        
        if tipo == 'Entrada':
            cursor.execute("UPDATE produtos SET quantidade = quantidade + ? WHERE nome = ?", (quantidade, produto))
        else:
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE nome = ?", (quantidade, produto))
            
        conn.commit()
        conn.close()
        flash('Movimentação registrada com sucesso!')
        return redirect(url_for('movimentacao'))
        
    return render_template('movimentacao.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)