# DK Invoice Calendar

Sistema completo de gestão de faturas com calendário, separado em **Backend API REST** e **Frontend Vue.js**.

## 🏗️ Arquitetura

O projeto foi refatorado seguindo princípios de **Clean Architecture** e separação de responsabilidades:

```
dk-api/
├── backend/          # API REST com FastAPI
│   ├── app/          # Código da aplicação
│   ├── tests/        # Testes (97% coverage)
│   └── README.md     # Documentação do backend
├── frontend/         # SPA Vue.js 3 (em desenvolvimento)
└── app/              # Código legado (será removido)
```

## 🚀 Backend API

### Tecnologias
- FastAPI
- SQLAlchemy
- Pydantic
- JWT Authentication
- pytest (97% coverage)

### Quick Start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python -m app.db.seed
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

📖 [Ver documentação completa do backend](./backend/README.md)

## 🎨 Frontend (Em Desenvolvimento)

### Tecnologias Planejadas
- Vue.js 3
- Vite
- Pinia (State Management)
- Vue Router
- Axios
- Vitest

## 📡 API Endpoints

### Autenticação
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Usuário atual

### Dashboard
- `GET /api/v1/dashboard/stats` - Estatísticas

### Faturas
- `GET /api/v1/invoices/` - Listar
- `POST /api/v1/invoices/` - Criar (Admin)
- `PUT /api/v1/invoices/{id}` - Atualizar (Admin)
- `PATCH /api/v1/invoices/{id}/toggle-paid` - Toggle status
- `DELETE /api/v1/invoices/{id}` - Deletar (Admin)
- `POST /api/v1/invoices/{id}/upload` - Upload PDF (Admin)

### Empresas
- `GET /api/v1/companies/` - Listar
- `POST /api/v1/companies/` - Criar (Admin)
- `PUT /api/v1/companies/{id}` - Atualizar (Admin)
- `DELETE /api/v1/companies/{id}` - Deletar (Admin)

### Usuários
- `GET /api/v1/users/` - Listar (SuperAdmin)
- `POST /api/v1/users/` - Criar (SuperAdmin)
- `PUT /api/v1/users/{id}` - Atualizar (SuperAdmin)
- `DELETE /api/v1/users/{id}` - Deletar (SuperAdmin)

## 🔐 Permissões

### SuperAdmin
- Gerenciar usuários, empresas e faturas
- Acesso total ao sistema

### Admin
- Gerenciar empresas e faturas
- Não pode gerenciar usuários

### User
- Visualizar dados da própria empresa
- Marcar faturas como pagas/não pagas

## 👥 Usuários de Teste

Após executar o seed (`python -m app.db.seed`):

| Email | Senha | Role | Empresa |
|-------|-------|------|---------|
| super@example.com | super123 | SuperAdmin | - |
| admin@example.com | admin123 | Admin | - |
| user@acme.com | user123 | User | ACME Corporation |
| user@techstart.com | user123 | User | TechStart Ltda |

## 🧪 Testes

### Backend
```bash
cd backend
pytest --cov=app --cov-report=html
```

**Cobertura atual: 97.32%** ✅

## 📦 Estrutura Detalhada

### Backend
```
backend/app/
├── api/v1/endpoints/    # Endpoints da API
├── core/                # Configurações e segurança
├── models/              # Modelos do banco
├── schemas/             # Validação de dados
├── repositories/        # Camada de dados
├── services/            # Lógica de negócio
├── db/                  # Database e seed
└── utils/               # Utilitários
```

## 🔧 Desenvolvimento

### Adicionar novo endpoint

1. Criar schema em `backend/app/schemas/`
2. Criar service em `backend/app/services/`
3. Criar endpoint em `backend/app/api/v1/endpoints/`
4. Escrever testes em `backend/tests/`
5. Verificar coverage: `pytest --cov=app`

## 🚀 Deploy

### Backend

**Opção 1: Docker**
```bash
cd backend
docker build -t dk-api .
docker run -p 8000:8000 dk-api
```

**Opção 2: Render/Railway/Heroku**
- Configure `DATABASE_URL` nas variáveis de ambiente
- Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend

Em desenvolvimento...

## 📝 Changelog

### v2.0.0 - Refatoração Completa
- ✅ Separação Backend/Frontend
- ✅ Clean Architecture no backend
- ✅ 97% de cobertura de testes
- ✅ API REST com FastAPI
- ✅ Documentação completa
- 🚧 Frontend Vue.js (em desenvolvimento)

### v1.0.0 - Versão Original
- Sistema monolítico com Jinja2 templates
- Vue.js via CDN

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

MIT

## 👨‍💻 Autor

Tiago Lemos - [GitHub](https://github.com/lemosss)
