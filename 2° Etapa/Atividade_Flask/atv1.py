from flask import Flask

app = Flask(__name__)

@app.route("/decorator")
def decorator():
    return "Um decorator é uma função que recebe uma função e a retorna como uma função nova com algum comportamento específico"

if __name__ == "__main__":
    app.run(debug=True)