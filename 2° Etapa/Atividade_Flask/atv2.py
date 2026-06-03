from flask import Flask

app = Flask(__name__)

@app.route("/curriculo")
def curriculo():
    return '''
        <html>

        <h1 style="font-size: 30px; text-align: center">Fábio Lima Rodrigues

        <h4 style="font-weight: normal; text-align: right">Telefone: +55 (31) 98258-2835
        <h4 style="font-weight: normal; text-align: right">Email: fabiolimarodrigues2021@gmail.com
        <h4 style="font-weight: normal; text-align: right">Localização: Belo Horizonte, MG
        <hr>

        <h2 style="font-size: 30px;">Habilidades:
        <h3>Idiomas:
        <h4 style="font-weight: normal;">• Fluência em inglês
        <h3>Aplicativos:
        <h4 style="font-weight: normal;">• Pacote Office
        <h4 style="font-weight: normal;">• Canva
        <h4 style="font-weight: normal;">• Figma
        <h3>Linguagens de Programação:
        <h4 style="font-weight: normal;">• MySQL
        <h4 style="font-weight: normal;">• C#
        <h4 style="font-weight: normal;">• Python
        <h3>Desenvolvimento Web:
        <h4 style="font-weight: normal;">• HTML
        <h4 style="font-weight: normal;">• CSS
        <h4 style="font-weight: normal;">• JavaScript
        <h4 style="font-weight: normal;">• PHP

        </html>
'''

if __name__ == "__main__":
    app.run(debug=True)