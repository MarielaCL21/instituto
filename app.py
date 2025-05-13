from flask import Flask, request, redirect, render_template, url_for, flash
import sqlite3
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'ClavesuperSecreta'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Obtener conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Inicializar base de datos
def init_db():
    conn = get_db_connection()
    conn.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """
    )
    conn.commit()
    conn.close()

# Clase Usuario para flask-Login
class User(UserMixin):
    def __init__(self, id, username, password, name=None, email=None):
        self.id = id
        self.username = username
        self.password = password
        self.name = name
        self.email = email

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['password'], user['name'], user['email'])
        return None

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user:
            return User(user['id'], user['username'], user['password'], user['name'], user['email'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hash_pass = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (name, email, username, password) VALUES (?, ?, ?, ?)',
                (name, email, username, hash_pass)
            )
            conn.commit()
            flash('Usuario registrado correctamente. Inicia sesión.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username, name=current_user.name)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

#conectar base de datos
def get_db_connection():
    conn = sqlite3.connect("bd_instituto.db")
    conn.row_factory = sqlite3.Row
    return conn



#listado de estudiantes
@app.route("/estudiantes")
def estudiantes():
    conn = get_db_connection()
    estudiantes = conn.execute("SELECT * FROM estudiantes").fetchall()
    conn.close()
    return render_template("estudiantes.html",estudiantes = estudiantes)
 
#nuevo  estudiante 
@app.route("/estudiante/nuevo", methods=['GET', 'POST'])
def nuevo_estudiante():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        fecha_nacimiento = request.form['fecha_nacimiento']

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO estudiantes (nombre, apellidos, fecha_nacimiento) VALUES (?, ?, ?)",
            (nombre, apellidos, fecha_nacimiento)
        )
        conn.commit()
        conn.close()
        flash("Estudiante agregado correctamente", "success")
        return redirect(url_for("estudiantes"))

    return render_template("form_estudiante.html")

#editar estudiante

@app.route("/estudiante/editar/<int:id>", methods=['GET', 'POST'])
def editar_estudiante(id):
    conn = get_db_connection()
    estudiante = conn.execute("SELECT * FROM estudiantes WHERE id = ?", (id,)).fetchone()

    if request.method == 'POST':
        nombre = request.form['nombre']
        apellidos = request.form['apellidos']
        fecha_nacimiento = request.form['fecha_nacimiento']

        conn.execute(
            "UPDATE estudiantes SET nombre = ?, apellidos = ?, fecha_nacimiento = ? WHERE id = ?",
            (nombre, apellidos, fecha_nacimiento, id)
        )
        conn.commit()
        conn.close()
        flash("Estudiante actualizado correctamente", "success")
        return redirect(url_for("estudiantes"))

    conn.close()
    return render_template("form_estudiante.html", estudiante=estudiante)

#eliminar estudiante
@app.route("/estudiante/eliminar/<int:id>")
def eliminar_estudiante(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM estudiantes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Estudiante eliminado correctamente", "success")
    return redirect(url_for("estudiantes"))
#listado de curso
@app.route("/cursos")
def cursos():
    conn = get_db_connection()
    cursos = conn.execute("SELECT * FROM cursos").fetchall()
    conn.close()
    return render_template("cursos.html",cursos = cursos)

#nuevo curso
@app.route("/curso/nuevo",methods=['GET','POST'])
def nuevo_curso():
    if request.method == 'POST':
        #leer formulario
        descripcion=  request.form['descripcion']
        horas = request.form['horas']
    
        conn = get_db_connection()
        conn.execute("INSERT INTO cursos (descripcion,horas) VALUES (?,?)", (descripcion,horas))
   
        conn.commit()
        conn.close()
        flash('Curso agregado correctamente','success')
        return redirect(url_for('cursos'))
    return render_template('form_curso.html')

#editar curso
@app.route("/curso/editar/<int:id>",methods =['GET','POST'])
def editar_curso(id):
    conn = get_db_connection()
    curso = conn.execute("SELECT * FROM cursos WHERE id = ?", (id,)).fetchone()
    if request.method == 'POST':
        descripcion=  request.form['descripcion']
        horas = request.form['horas']
    
        conn.execute("UPDATE cursos SET descripcion = ?, horas = ? WHERE id = ?", (descripcion,horas,id))
        conn.commit()
        conn.close()
        flash('Curso actualizado','success')
        return redirect(url_for('cursos'))
    return render_template("form_curso.html",curso = curso)

#eliminar curso
@app.route('/curso/eliminar/<int:id>')
def eliminar_curso(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM cursos WHERE id=?",(id,))
    conn.commit()
    conn.close()
    flash('Curso eliminado','success')
    return redirect(url_for('cursos'))

#listado de inscripciones
@app.route("/inscripciones")
def inscripciones():
    conn = get_db_connection()
    inscripciones = conn.execute(
        """
        SELECT i.id,
        i.fecha,
        e.nombre || ' ' || e.apellidos as estudiante,
        c.descripcion as curso
        FROM inscripciones i
        JOIN estudiantes e ON i.estudiante_id = e.id
        JOIN cursos c ON i.curso_id = c.id
        """).fetchall()
    conn.close()
    return render_template("inscripciones.html",inscripciones=inscripciones)

#nuevo  inscripcion
@app.route("/inscripcion/nuevo", methods=['GET', 'POST'])
def nueva_inscripcion():
    conn = get_db_connection()
    if request.method == 'POST':
        fecha = request.form['fecha']
        estudiante_id = request.form['estudiante_id']
        curso_id = request.form['curso_id']

        conn.execute(
            """
            INSERT INTO inscripciones (fecha, estudiante_id, curso_id)
            VALUES (?, ?, ?)
            """,
            (fecha, estudiante_id, curso_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("inscripciones"))

    # En caso de GET
    estudiantes = conn.execute(
    """
    SELECT id, nombre || ' ' || apellidos as nombre
    FROM estudiantes
    """
).fetchall()
    cursos = conn.execute(
        """
        SELECT id, descripcion FROM cursos
        """
    ).fetchall()
    conn.close()
    return render_template('form_inscripcion.html', estudiantes=estudiantes, cursos=cursos)

#editar inscripción 
@app.route("/inscripcion/editar/<int:id>", methods=['GET', 'POST'])
def editar_inscripcion(id):
    conn = get_db_connection()
    if request.method == 'POST':
        fecha = request.form['fecha']
        estudiante_id = request.form['estudiante_id']
        curso_id = request.form['curso_id']

        conn.execute(
            """
            UPDATE inscripciones 
            SET fecha = ?, estudiante_id = ?, curso_id = ?
            WHERE id = ?
            """,
            (fecha, estudiante_id, curso_id, id)
        )
        conn.commit()
        conn.close()
        flash("Inscripción actualizada correctamente", "success")
        return redirect(url_for("inscripciones"))

    # Cargar datos existentes
    inscripcion = conn.execute(
        "SELECT * FROM inscripciones WHERE id = ?", (id,)
    ).fetchone()

    estudiantes = conn.execute(
        "SELECT id, nombre || ' ' || apellidos as nombre FROM estudiantes"
    ).fetchall()

    cursos = conn.execute(
        "SELECT id, descripcion FROM cursos"
    ).fetchall()
    
    conn.close()
    return render_template(
        'form_inscripcion.html',
        estudiantes=estudiantes,
        cursos=cursos,
        inscripcion=inscripcion
    )

#eliminar inscripcion
@app.route('/inscripcion/eliminar/<int:id>')
def eliminar_inscripcion(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM inscripciones WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inscripciones'))  

if __name__== '__main__':
    init_db()
    app.run(debug=True)