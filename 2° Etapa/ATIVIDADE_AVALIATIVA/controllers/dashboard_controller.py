from flask import Blueprint, render_template

from models import Locacao, Veiculo

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def index():
    return render_template(
        "index.html",
        total_locacao=Locacao.query.count(),
        total_veiculos=Veiculo.query.count(),
        locacoes_recentes=Locacao.listar_com_detalhes()[:5],
    )