# Painel de Controle de Tarefas (Flask)

Projeto completo desenvolvido conforme o roteiro "Praticando" (Flask + SQLite +
autenticação + CRUD + API externa + Bootstrap 5 + Chart.js).

## Como rodar

1. Crie e ative um ambiente virtual (recomendado):
   ```
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (Linux/Mac)
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. (Opcional, mas recomendado) defina sua própria chave secreta antes de rodar:
   ```
   set SECRET_KEY=uma-chave-bem-aleatoria      (Windows)
   export SECRET_KEY=uma-chave-bem-aleatoria   (Linux/Mac)
   ```

4. Rode a aplicação:
   ```
   python app.py
   ```

5. Acesse http://127.0.0.1:5000 no navegador. O banco `database.db` (SQLite)
   é criado automaticamente na primeira execução.

## Estrutura

```
tarefas_app/
├── app.py                  # rotas, banco de dados, autenticação, API
├── requirements.txt
├── database.db              # criado automaticamente na 1ª execução
├── templates/
│   ├── base.html            # layout base, navbar, modo escuro
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html       # lista de tarefas + filtro por status (AJAX)
│   ├── nova_tarefa.html
│   ├── editar_tarefa.html
│   └── progresso.html       # gráficos com Chart.js
└── static/
    ├── css/style.css        # cores por status + tema escuro
    └── js/main.js           # toggle de modo escuro (localStorage)
```

## Funcionalidades implementadas

- **Autenticação**: cadastro, login e logout, senhas com hash
  (`werkzeug.security`), rotas internas protegidas por sessão.
- **CRUD de tarefas**: `/dashboard`, `/nova_tarefa`, `/editar/<id>`,
  `/excluir/<id>` (mais `/concluir/<id>` como atalho de conveniência).
- **Banco SQLite**: tabelas `usuarios` e `tarefas`, criadas automaticamente
  com `FOREIGN KEY` e `ON DELETE CASCADE`.
- **API externa**: frase motivacional do dia exibida no `/dashboard`,
  consumida de `https://api.adviceslip.com/advice`.
- **Interface**: Bootstrap 5 + Bootstrap Icons, cards responsivos.
- **Filtro de status via AJAX**: dropdown no dashboard chama `/api/tarefas`
  e re-renderiza a lista sem recarregar a página.
- **Cores por status**: pendente = amarelo, em andamento = azul,
  concluída = verde.
- **Modo escuro**: alternável pela navbar, persistido em `localStorage`.
- **Dashboard de progresso** (`/progresso`): gráficos de barras e pizza
  (Chart.js) alimentados por `/api/progresso` (JSON).
- **Desafio avançado**: API REST completa em
  `/api/rest/tarefas` (GET, POST) e `/api/rest/tarefas/<id>`
  (GET, PUT, DELETE), retornando JSON.

## Segurança e boas práticas aplicadas

- `SECRET_KEY` configurável via variável de ambiente.
- `DEBUG` controlado por variável de ambiente (`FLASK_DEBUG`), `False` por
  padrão.
- Senhas nunca armazenadas em texto puro (hash + verificação segura).
- Validação básica de campos obrigatórios e tamanho mínimo de senha.
- Consultas SQL sempre parametrizadas (proteção contra SQL Injection).
- Todas as rotas de tarefas filtram por `usuario_id`, então um usuário nunca
  acessa/edita tarefas de outro.
