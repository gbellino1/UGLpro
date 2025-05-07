from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def ejecutar_script():
    try:
        resultado = subprocess.run(['python3', 'uglpro.py'], capture_output=True, text=True)
        return f"<h3>Resultado de la ejecución:</h3><pre>{resultado.stdout}</pre>"
    except Exception as e:
        return f"<h3>Error al ejecutar:</h3><pre>{str(e)}</pre>"

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)