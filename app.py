from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'todo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                hora TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semana (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia TEXT NOT NULL,            
                hora TEXT NOT NULL,
                descricao TEXT NOT NULL
            );
            ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semana_detalhada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                semana INTEGER NOT NULL,
                dia TEXT NOT NULL,              
                hora TEXT NOT NULL,            
                descricao TEXT NOT NULL
            );
            ''')


        conn.commit()
        conn.close()

# Rotas para TAREFAS (tasks)

@app.route('/')
def index():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall() 
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    description = request.form['description']
    if description:
        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (description) VALUES (?)', (description,))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/toggle_task/<int:task_id>')
def toggle_task(task_id):
    conn = get_db_connection()
    task = conn.execute('SELECT done FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if task:
        new_status = 0 if task['done'] else 1
        conn.execute('UPDATE tasks SET done = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# Rotas para AGENDA (agendas)

@app.route('/agenda')
def agenda():
    conn = get_db_connection()
    agendas = conn.execute('SELECT * FROM agendas').fetchall()
    conn.close()
    return render_template('agenda.html', agendas=agendas)

@app.route('/add_agenda', methods=['POST'])
def add_agenda():
    description = request.form['description']
    horas = request.form.getlist('horas')

    if description and horas:
        horas_str = ",".join(horas)  # Junta em uma única string
        conn = get_db_connection()
        conn.execute('INSERT INTO agendas (description, hora) VALUES (?, ?)', (description, horas_str))
        conn.commit()
        conn.close()
    return redirect(url_for('agenda'))



from flask import request

@app.route('/toggle_agenda/<int:agenda_id>', methods=['POST'])
def toggle_agenda(agenda_id):
    conn = get_db_connection()
    agenda = conn.execute('SELECT done FROM agendas WHERE id = ?', (agenda_id,)).fetchone()
    if agenda:
        new_status = 0 if agenda['done'] else 1
        conn.execute('UPDATE agendas SET done = ? WHERE id = ?', (new_status, agenda_id))
        conn.commit()
    conn.close()
    return ('', 204)

@app.route('/delete_agenda/<int:agenda_id>', methods=['POST'])
def delete_agenda(agenda_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM agendas WHERE id = ?', (agenda_id,))
    conn.commit()
    conn.close()
    return ('', 204)


@app.route('/tarefas')
def tarefas():
    conn = get_db_connection()
    tarefas = conn.execute('SELECT id, description, hora, done FROM agendas').fetchall()
    conn.close()
    return jsonify([dict(t) for t in tarefas])



# rot5as para semanal

@app.route('/semanal')
def semanal():
    conn = get_db_connection()
    atividades = conn.execute('SELECT * FROM semana ORDER BY dia, hora').fetchall()
    conn.close()
    return render_template('semanal.html', atividades=atividades)

@app.route('/add_semanal', methods=['POST'])
def add_semanal():
    dia = request.form['dia']
    hora = request.form['hora']
    descricao = request.form['descricao']
    if dia and hora and descricao:
        conn = get_db_connection()
        conn.execute('INSERT INTO semana (dia, hora, descricao) VALUES (?, ?, ?)', (dia, hora, descricao))
        conn.commit()
        conn.close()
    return redirect(url_for('semanal'))


#rota planejamento

@app.route('/planejamento', methods=['GET', 'POST'])
def planejamento():
    semana = int(request.args.get('semana', 1))

    conn = get_db_connection()
    dados = conn.execute('SELECT * FROM semana_detalhada WHERE semana = ?', (semana,)).fetchall()
    conn.close()

    # Organizar dados por [hora][dia] para montar tabela
    grid = {}
    for item in dados:
        grid.setdefault(item['hora'], {})[item['dia']] = item['descricao']

    return render_template('planejamento.html', grid=grid, semana=semana)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
