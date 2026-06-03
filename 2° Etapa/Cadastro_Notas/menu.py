import pandas as pd
from datetime import datetime
import os

Arquivo = "notas.csv"

if not os.path.exists(Arquivo):
    df = pd.DataFrame(columns=["Aluno", "Nota", "DataHora"])
    df.to_csv(Arquivo, index=False)

def cadastrar_nota():
    aluno = input("Nome do aluno: ")
    nota = float(input("Nota: "))
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M")

    nova_linha = pd.DataFrame([[aluno, nota, data_hora]] , columns = ["Aluno", "Nota", "DataHora"])

    df = pd.read_csv(Arquivo)
    df = pd.concat([df, nova_linha], ignore_index = True)
    df.to_csv(Arquivo, index=False)

    print("Nota cadastrada com sucesso!\n")

def listar_notas():
    df = pd.read_csv(Arquivo)
    print(df)

while True:
    print("1 - Cadastrar nota")
    print("2 - Listar notas")
    print("0 - Sair")

    opcao = input("Escolha: ")

    if opcao == "1":
        cadastrar_nota()
    elif opcao == "2":
        listar_notas()
    elif opcao == "0":
        break