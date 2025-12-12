
# DK Invoice Calendar

Sistema completo de gestão de faturas com calendário, upload de boletos (PDF), controle de empresas, usuários e dashboard, feito com **FastAPI**, **SQLAlchemy**, **Vue.js 3** (CDN), **Jinja2** e tema escuro moderno.

## Funcionalidades

- **Login com JWT** (admin, superadmin, usuário)
- **Dashboard** com estatísticas (faturas, pendentes, pagas, vencidas)
- **Calendário interativo**: visualize faturas por dia, marque como paga/não paga, veja boletos
- **Upload de PDF** (boleto) para cada fatura
- **CRUD de Faturas** (admin/superadmin)
- **CRUD de Empresas** (admin/superadmin)
- **CRUD de Usuários** (superadmin)
- **Tema escuro** e design responsivo
- **Notificações toast** para feedback instantâneo
- **Seed automático** para ambiente de desenvolvimento

## Tecnologias
- **Backend:** FastAPI, SQLAlchemy, Pydantic, JWT, bcrypt
- **Frontend:** Vue.js 3 (CDN), Jinja2, Lucide Icons
- **Banco:** SQLite (dev) ou PostgreSQL (produção)
- **Estilo:** CSS customizado, dark theme

## Como rodar

1. **Clone o repositório:**
	 ```bash
	 git clone <repo-url>
	 cd dk-api
	 ```
2. **Crie o ambiente virtual:**
	 ```bash
	 python -m venv .venv
	 .venv\Scripts\activate  # Windows
	 # source .venv/bin/activate  # Linux/Mac
	 ```
3. **Instale as dependências:**
	 ```bash
	 pip install -r requirements.txt
	 ```
4. **Rode o seed (opcional):**
	 ```bash
	 cd backend
	 python -m app.seed
	 ```
5. **Inicie o servidor:**
	 ```bash
	 cd backend
	 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
	 ```
	 Ou execute do diretório raiz:
	 ```bash
	 cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
	 ```
6. **Acesse:**
	 - Login: http://localhost:8000/login
	 - Dashboard: http://localhost:8000/dashboard

## Usuários de teste

- **Super Admin:**
	- Email: `super@example.com`
	- Senha: `super123`
- **Admin:**
	- Email: `admin@example.com`
	- Senha: `admin123`
- **Usuário (ACME):**
	- Email: `user@acme.com`
	- Senha: `user123`
- **Usuário (TechStart):**
	- Email: `user@techstart.com`
	- Senha: `user123`

## Estrutura do Projeto

O projeto está organizado em duas pastas principais para separar claramente o frontend e o backend:

```
backend/                  # Código do servidor/API
  app/
    main.py              # FastAPI app e rotas de páginas
    routes.py            # Endpoints API (auth, users, companies, invoices)
    models.py            # SQLAlchemy models
    schemas.py           # Pydantic schemas
    auth.py              # JWT, hash de senha
    database.py          # Engine e sessão
    config.py            # Configurações
    seed.py              # Popula o banco com dados de exemplo
    __init__.py          # Inicialização do módulo

frontend/                # Recursos do cliente/interface
  static/
    css/                 # main.css, calendar.css
    uploads/             # PDFs enviados (boletos)
  templates/             # Templates Jinja2/HTML
    base.html            # Template base (Vue.js, CSS, Lucide)
    login.html           # Página de login
    dashboard.html       # Dashboard principal
    calendar.html        # Calendário de faturas
    invoices.html        # Gerenciamento de faturas
    companies.html       # Gerenciamento de empresas
    users.html           # Gerenciamento de usuários
    components/          # Componentes reutilizáveis
      sidebar.html       # Barra lateral de navegação

dev.db                   # Banco de dados SQLite (desenvolvimento)
```

### Separação Frontend/Backend

- **Backend (`backend/`)**: Contém toda a lógica de negócio, API REST, autenticação, modelos de dados e configuração do banco de dados. É executado com FastAPI/Uvicorn.

- **Frontend (`frontend/`)**: Contém templates HTML com Vue.js 3 (via CDN), arquivos CSS estáticos e uploads. O backend serve esses arquivos através do FastAPI StaticFiles e Jinja2Templates.

## Upload de Boleto (PDF)
- Admins podem anexar PDF ao criar/editar fatura
- Usuários e admins podem visualizar o PDF no calendário e na lista

## Workflow de Desenvolvimento

### Trabalhando com Backend

Para fazer alterações no backend (API, modelos, autenticação):

1. Navegue para o diretório `backend/`
2. Edite os arquivos Python em `backend/app/`
3. Os principais arquivos são:
   - `main.py` - Aplicação FastAPI e rotas de páginas
   - `routes.py` - Endpoints da API REST
   - `models.py` - Modelos do banco de dados
   - `auth.py` - Autenticação e JWT
   - `schemas.py` - Validação de dados com Pydantic

### Trabalhando com Frontend

Para fazer alterações no frontend (HTML, CSS, JavaScript):

1. Navegue para o diretório `frontend/`
2. Templates HTML estão em `frontend/templates/`
3. CSS e assets estão em `frontend/static/`
4. O frontend usa Vue.js 3 via CDN (não requer build)

### Importante

- O servidor sempre deve ser executado a partir do diretório `backend/`
- Os caminhos para templates e static files são relativos ao diretório raiz do projeto
- O banco de dados (`dev.db`) fica na raiz do projeto
- Uploads de PDFs são salvos em `frontend/static/uploads/`

## Observações
- O sistema usa SQLite por padrão (`dev.db` na raiz do projeto). Para PostgreSQL, configure a variável `DATABASE_URL` no `.env`.
- O seed só roda se o banco estiver vazio.
- O frontend usa Vue.js 3 via CDN (não precisa buildar nada).
- **Importante:** O servidor deve ser iniciado a partir do diretório `backend/` para que os caminhos relativos funcionem corretamente.

## Licença
MIT
