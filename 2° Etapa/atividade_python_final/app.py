import sqlite3
import os
import json
import urllib.request
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ---------- Configuração / Segurança ----------
# Em produção, defina a variável de ambiente SECRET_KEY com um valor forte
# e aleatório, e nunca deixe DEBUG=True.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'troque-esta-chave-em-producao')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False') == 'True'

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

STATUS_VALIDOS = ['pendente', 'em_andamento', 'concluida']
STATUS_LABELS = {
    'pendente': 'Pendente',
    'em_andamento': 'Em andamento',
    'concluida': 'Concluída',
}


# ---------- Banco de dados ----------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()


# ---------- Autenticação (proteção de rotas) ----------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Faça login para continuar.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')

        if not nome or not email or not senha:
            flash('Preencha todos os campos.', 'danger')
            return render_template('register.html')

        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'danger')
            return render_template('register.html')

        if senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
            return render_template('register.html')

        conn = get_db()
        existente = conn.execute('SELECT id FROM usuarios WHERE email = ?', (email,)).fetchone()
        if existente:
            conn.close()
            flash('Este e-mail já está cadastrado.', 'danger')
            return render_template('register.html')

        senha_hash = generate_password_hash(senha)
        conn.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)',
            (nome, email, senha_hash)
        )
        conn.commit()
        conn.close()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        conn = get_db()
        usuario = conn.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        conn.close()

        # check_password_hash lida com a comparação segura do hash,
        # nunca comparamos senhas em texto puro.
        if usuario and check_password_hash(usuario['senha'], senha):
            session.clear()
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            flash(f'Bem-vindo(a), {usuario["nome"]}!', 'success')
            return redirect(url_for('dashboard'))

        flash('E-mail ou senha inválidos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))


# ---------- Integração com API externa ----------

def get_frase_motivacional():
    try:
        req = urllib.request.Request(
            'https://api.adviceslip.com/advice',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
            return data.get('slip', {}).get('advice')
    except Exception:
        return None


# ---------- Dashboard / CRUD de tarefas ----------

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    tarefas = conn.execute(
        'SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC',
        (session['usuario_id'],)
    ).fetchall()
    conn.close()

    frase = get_frase_motivacional()

    return render_template(
        'dashboard.html',
        tarefas=tarefas,
        frase=frase,
        status_labels=STATUS_LABELS
    )


@app.route('/api/tarefas')
@login_required
def api_tarefas():
    """Retorna as tarefas do usuário logado em JSON, com filtro opcional de status.
    Usada pelo dropdown de filtro do dashboard (item 8), sem recarregar a página."""
    status = request.args.get('status', 'todas')

    conn = get_db()
    if status in STATUS_VALIDOS:
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE usuario_id = ? AND status = ? ORDER BY id DESC',
            (session['usuario_id'], status)
        ).fetchall()
    else:
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC',
            (session['usuario_id'],)
        ).fetchall()
    conn.close()

    resultado = []
    for t in tarefas:
        item = dict(t)
        item['status_label'] = STATUS_LABELS.get(item['status'], item['status'])
        resultado.append(item)

    return jsonify(resultado)


@app.route('/nova_tarefa', methods=['GET', 'POST'])
@login_required
def nova_tarefa():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status', 'pendente')

        if not titulo:
            flash('O título é obrigatório.', 'danger')
            return render_template('nova_tarefa.html', status_validos=STATUS_VALIDOS, status_labels=STATUS_LABELS)

        if status not in STATUS_VALIDOS:
            status = 'pendente'

        conn = get_db()
        conn.execute(
            'INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)',
            (titulo, descricao, status, session['usuario_id'])
        )
        conn.commit()
        conn.close()

        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('nova_tarefa.html', status_validos=STATUS_VALIDOS, status_labels=STATUS_LABELS)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    conn = get_db()
    tarefa = conn.execute(
        'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
        (id, session['usuario_id'])
    ).fetchone()

    if tarefa is None:
        conn.close()
        flash('Tarefa não encontrada.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status', tarefa['status'])

        if not titulo:
            flash('O título é obrigatório.', 'danger')
            conn.close()
            return render_template(
                'editar_tarefa.html', tarefa=tarefa,
                status_validos=STATUS_VALIDOS, status_labels=STATUS_LABELS
            )

        if status not in STATUS_VALIDOS:
            status = tarefa['status']

        conn.execute(
            'UPDATE tarefas SET titulo = ?, descricao = ?, status = ? WHERE id = ? AND usuario_id = ?',
            (titulo, descricao, status, id, session['usuario_id'])
        )
        conn.commit()
        conn.close()

        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template(
        'editar_tarefa.html', tarefa=tarefa,
        status_validos=STATUS_VALIDOS, status_labels=STATUS_LABELS
    )


@app.route('/excluir/<int:id>', methods=['POST'])
@login_required
def excluir(id):
    conn = get_db()
    conn.execute('DELETE FROM tarefas WHERE id = ? AND usuario_id = ?', (id, session['usuario_id']))
    conn.commit()
    conn.close()
    flash('Tarefa excluída.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/concluir/<int:id>', methods=['POST'])
@login_required
def concluir(id):
    conn = get_db()
    conn.execute(
        "UPDATE tarefas SET status = 'concluida' WHERE id = ? AND usuario_id = ?",
        (id, session['usuario_id'])
    )
    conn.commit()
    conn.close()
    flash('Tarefa marcada como concluída!', 'success')
    return redirect(url_for('dashboard'))


# ---------- Dashboard de progresso (item 10) ----------

@app.route('/progresso')
@login_required
def progresso():
    return render_template('progresso.html')


@app.route('/api/progresso')
@login_required
def api_progresso():
    conn = get_db()
    linhas = conn.execute(
        'SELECT status, COUNT(*) as total FROM tarefas WHERE usuario_id = ? GROUP BY status',
        (session['usuario_id'],)
    ).fetchall()
    conn.close()

    contagem = {s: 0 for s in STATUS_VALIDOS}
    for linha in linhas:
        contagem[linha['status']] = linha['total']

    return jsonify({
        'labels': [STATUS_LABELS[s] for s in STATUS_VALIDOS],
        'valores': [contagem[s] for s in STATUS_VALIDOS]
    })


# ---------- Desafio avançado: versão REST em JSON ----------

@app.route('/api/rest/tarefas', methods=['GET', 'POST'])
@login_required
def rest_tarefas():
    conn = get_db()

    if request.method == 'GET':
        tarefas = conn.execute(
            'SELECT * FROM tarefas WHERE usuario_id = ? ORDER BY id DESC',
            (session['usuario_id'],)
        ).fetchall()
        conn.close()
        return jsonify([dict(t) for t in tarefas])

    dados = request.get_json(silent=True) or {}
    titulo = (dados.get('titulo') or '').strip()
    descricao = (dados.get('descricao') or '').strip()
    status = dados.get('status', 'pendente')

    if not titulo:
        conn.close()
        return jsonify({'erro': 'O campo titulo é obrigatório.'}), 400

    if status not in STATUS_VALIDOS:
        status = 'pendente'

    cursor = conn.execute(
        'INSERT INTO tarefas (titulo, descricao, status, usuario_id) VALUES (?, ?, ?, ?)',
        (titulo, descricao, status, session['usuario_id'])
    )
    conn.commit()
    nova_id = cursor.lastrowid
    tarefa = conn.execute('SELECT * FROM tarefas WHERE id = ?', (nova_id,)).fetchone()
    conn.close()

    return jsonify(dict(tarefa)), 201


@app.route('/api/rest/tarefas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def rest_tarefa_detalhe(id):
    conn = get_db()
    tarefa = conn.execute(
        'SELECT * FROM tarefas WHERE id = ? AND usuario_id = ?',
        (id, session['usuario_id'])
    ).fetchone()

    if tarefa is None:
        conn.close()
        return jsonify({'erro': 'Tarefa não encontrada.'}), 404

    if request.method == 'GET':
        conn.close()
        return jsonify(dict(tarefa))

    if request.method == 'DELETE':
        conn.execute('DELETE FROM tarefas WHERE id = ? AND usuario_id = ?', (id, session['usuario_id']))
        conn.commit()
        conn.close()
        return jsonify({'mensagem': 'Tarefa excluída com sucesso.'})

    # PUT: atualização parcial/total
    dados = request.get_json(silent=True) or {}
    titulo = (dados.get('titulo') or tarefa['titulo']).strip()
    descricao = dados.get('descricao', tarefa['descricao'])
    status = dados.get('status', tarefa['status'])

    if status not in STATUS_VALIDOS:
        status = tarefa['status']

    conn.execute(
        'UPDATE tarefas SET titulo = ?, descricao = ?, status = ? WHERE id = ? AND usuario_id = ?',
        (titulo, descricao, status, id, session['usuario_id'])
    )
    conn.commit()
    tarefa_atualizada = conn.execute('SELECT * FROM tarefas WHERE id = ?', (id,)).fetchone()
    conn.close()

    return jsonify(dict(tarefa_atualizada))


if __name__ == '__main__':
    init_db()
    app.run(debug=app.config['DEBUG'])
