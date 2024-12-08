import logging
from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = '!%/#A7/¡'

usuarios = {}
intentos_fallidos = {}
bloqueo_duracion = timedelta(minutes=5)

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

with open('app.log', 'w'):
    pass

@app.route('/')
def index():
    app.logger.info('Página de inicio cargada')
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        clave_cifrada = generate_password_hash(clave, method='pbkdf2:sha256', salt_length=8)
        usuarios[usuario] = clave_cifrada
        app.logger.info(f'Usuario registrado: {usuario}')
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']

        if usuario in intentos_fallidos:
            if datetime.now() < intentos_fallidos[usuario]['bloqueado_hasta']:
                error = 'Demasiados intentos fallidos. Inténtelo más tarde.'
                app.logger.warning(f'Usuario {usuario} está bloqueado hasta {intentos_fallidos[usuario]["bloqueado_hasta"]}')
                return render_template('login.html', error=error)

        usuario_clave = usuarios.get(usuario)
        app.logger.info(f'Clave almacenada para {usuario}: {usuario_clave}')
        if usuario_clave is not None and check_password_hash(usuario_clave, clave):
            session['usuario'] = usuario
            intentos_fallidos.pop(usuario, None)
            app.logger.info(f'Login exitoso para el usuario: {usuario}')
            return redirect(url_for('dashboard'))
        else:
            if usuario not in intentos_fallidos:
                intentos_fallidos[usuario] = {'intentos': 0, 'bloqueado_hasta': datetime.now()}

            intentos_fallidos[usuario]['intentos'] += 1
            if intentos_fallidos[usuario]['intentos'] >= 3:
                intentos_fallidos[usuario]['bloqueado_hasta'] = datetime.now() + bloqueo_duracion
                error = 'Demasiados intentos fallidos. Inténtelo más tarde.'
                app.logger.warning(f'Usuario {usuario} bloqueado temporalmente.')
            else:
                error = 'Credenciales inválidas. Intente de nuevo.'
                app.logger.warning(f'Intento fallido para {usuario}. Intentos fallidos: {intentos_fallidos[usuario]["intentos"]}')

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'usuario' in session:
        app.logger.info('Dashboard cargado')
        return render_template('dashboard.html', usuario=session["usuario"])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    app.logger.info(f'Usuario {session.get("usuario")} ha cerrado sesión')
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)