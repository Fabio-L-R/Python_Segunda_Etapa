# No app.py da Aula 11 — BLUEPRINT: importe e REGISTRE o pacote de rotas da locadora
from controllers.locadora_controller import locadora_bp

# Sem esta linha o Flask não conhece as URLs /locadora/ — dá 404
app.register_blueprint(locadora_bp)

# No layout.html — 'locadora' é o apelido do Blueprint, 'index' é a função
# <a href="{{ url_for('locadora.index') }}">Locadora</a>
