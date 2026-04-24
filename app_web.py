from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>ERP Principal - Funciona</h1>"

@app.route('/erp/1')
def erp_uno():
    return "<h1>Bienvenido al ERP 1 de Pablo</h1><p>Servidor activo en puerto 5000</p>"

if __name__ == '__main__':
    app.run(port=5000, debug=True)