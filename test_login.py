import requests

usuario = 'usuario_de_prueba_1'
#claves = ['clave_de_prueba_1', 'clave_de_prueba_2', 'clave_de_prueba_3']
claves = ['clave_de_prueba_1', 'clave_de_prueba_2', 'clave_de_prueba_4']
url = 'http://127.0.0.1:5000/login'

def intento_login(usuario, clave):
    datos = {'usuario': usuario, 'clave': clave}
    respuesta = requests.post(url, data=datos)
    if 'Credenciales inválidas' in respuesta.text: 
        print(f'Contraseña incorrecta: {clave}') 
    elif 'Demasiados intentos fallidos' in respuesta.text: 
        print('Demasiados intentos fallidos. Inténtelo más tarde.') 
    else: 
        print(f'Contraseña correcta: {clave}')

for clave in claves:
    intento_login(usuario, clave)