from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("inicio/pagina_inicio.html")

@app.route("/main")
def main():
    return render_template("pagina_principal/info_lab.html")

@app.route("/login")
def login():
    return render_template("login/index.html")

@app.route("/exp")
def exper():
    return render_template("pagina_exp/exp.html")

@app.route("/reg")
def reg():
    return render_template("registro/main.html")

@app.route("/res")
def res():
    return render_template("reserva_horas/reserva.html")

@app.route("/sim")
def sim():
    return render_template("Simulacion/simulacion_base_movil.html")

@app.route("/cuenta")
def perfil():
    return render_template("perfil/datos_personales.html")