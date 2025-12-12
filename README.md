
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
	 python app/seed.py
	 ```
5. **Inicie o servidor:**
	 ```bash
	 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
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

```
app/
	main.py           # FastAPI app e rotas de páginas
	routes.py         # Endpoints API (auth, users, companies, invoices)
	models.py         # SQLAlchemy models
	schemas.py        # Pydantic schemas
	auth.py           # JWT, hash de senha
	database.py       # Engine e sessão
	config.py         # Configurações
	seed.py           # Popula o banco com dados de exemplo
	static/
		css/            # main.css, calendar.css
		uploads/        # PDFs enviados
	templates/
		base.html       # Template base (Vue.js, CSS, Lucide)
		...             # dashboard, calendar, invoices, companies, users
```

## Upload de Boleto (PDF)
- Admins podem anexar PDF ao criar/editar fatura
- Usuários e admins podem visualizar o PDF no calendário e na lista

## Observações
- O sistema usa SQLite por padrão. Para PostgreSQL, configure a variável `DATABASE_URL` no `.env`.
- O seed só roda se o banco estiver vazio.
- O frontend usa Vue.js 3 via CDN (não precisa buildar nada).

## Licença
MIT
