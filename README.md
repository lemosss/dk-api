# DK Invoice Calendar - Backend API

Sistema de gestão de faturas com calendário - API REST com arquitetura limpa.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados e settings
- **JWT** - Autenticação com tokens
- **bcrypt** - Hash de senhas
- **pytest** - Framework de testes (97% de cobertura)

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/       # Endpoints da API
│   │       └── router.py        # Router principal v1
│   ├── core/
│   │   ├── config.py           # Configurações
│   │   ├── security.py         # JWT e hashing
│   │   └── dependencies.py     # Dependências injetáveis
│   ├── models/                 # Modelos SQLAlchemy
│   ├── schemas/                # Schemas Pydantic
│   ├── repositories/           # Camada de dados
│   ├── services/               # Lógica de negócio
│   ├── db/                     # Database e seed
│   └── utils/                  # Utilitários
├── tests/                      # Testes (97% coverage)
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── uploads/                    # PDFs enviados
└── requirements.txt            # Dependências
```

## 🛠️ Instalação e Configuração

### 1. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Para desenvolvimento
```

### 3. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e ajuste conforme necessário:

```bash
cp .env.example .env
```

Variáveis disponíveis:
- `SECRET_KEY` - Chave secreta para JWT (mude em produção!)
- `DATABASE_URL` - URL do banco de dados
- `BACKEND_CORS_ORIGINS` - Origens permitidas para CORS
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Tempo de expiração do token

### 4. Popular o banco de dados (opcional)

```bash
python -m app.db.seed
```

Isso criará usuários de teste:
- **Super Admin:** super@example.com / super123
- **Admin:** admin@example.com / admin123
- **Usuário ACME:** user@acme.com / user123
- **Usuário TechStart:** user@techstart.com / user123

## 🚀 Executar a Aplicação

### Modo desenvolvimento

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Modo produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa: 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Executar Testes

### Todos os testes com coverage

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Apenas testes unitários

```bash
pytest tests/unit/
```

### Apenas testes de integração

```bash
pytest tests/integration/
```

### Apenas testes E2E

```bash
pytest tests/e2e/
```

### Relatório de cobertura

Após executar os testes, abra `htmlcov/index.html` no navegador para ver o relatório detalhado.

**Cobertura atual: 97.32%** ✅

## 📡 Endpoints da API

### Autenticação
- `POST /api/v1/auth/login` - Login (retorna JWT)
- `GET /api/v1/auth/me` - Dados do usuário atual

### Dashboard
- `GET /api/v1/dashboard/stats` - Estatísticas do dashboard

### Faturas (Invoices)
- `GET /api/v1/invoices/` - Listar faturas
- `GET /api/v1/invoices/{id}` - Obter fatura
- `POST /api/v1/invoices/` - Criar fatura (Admin)
- `PUT /api/v1/invoices/{id}` - Atualizar fatura (Admin)
- `PATCH /api/v1/invoices/{id}/toggle-paid` - Alternar status de pagamento
- `DELETE /api/v1/invoices/{id}` - Deletar fatura (Admin)
- `POST /api/v1/invoices/{id}/upload` - Upload de PDF (Admin)
- `GET /api/v1/invoices/calendar` - Dados do calendário
- `GET /api/v1/invoices/by-date` - Faturas por data

### Empresas (Companies)
- `GET /api/v1/companies/` - Listar empresas
- `GET /api/v1/companies/{id}` - Obter empresa
- `POST /api/v1/companies/` - Criar empresa (Admin)
- `PUT /api/v1/companies/{id}` - Atualizar empresa (Admin)
- `DELETE /api/v1/companies/{id}` - Deletar empresa (Admin)

### Usuários (Users)
- `GET /api/v1/users/` - Listar usuários (SuperAdmin)
- `GET /api/v1/users/{id}` - Obter usuário (SuperAdmin)
- `POST /api/v1/users/` - Criar usuário (SuperAdmin)
- `PUT /api/v1/users/{id}` - Atualizar usuário (SuperAdmin)
- `DELETE /api/v1/users/{id}` - Deletar usuário (SuperAdmin)

## 🔐 Autenticação e Autorização

O sistema usa JWT (JSON Web Tokens) para autenticação. Existem três níveis de permissão:

1. **SuperAdmin** - Acesso total (gerenciar usuários, empresas e faturas)
2. **Admin** - Gerenciar empresas e faturas
3. **User** - Visualizar apenas dados da própria empresa

### Como usar:

1. Faça login em `/api/v1/auth/login` com email e senha
2. Copie o `access_token` retornado
3. Use o token no header `Authorization: Bearer {token}` nas requisições

## 🏗️ Arquitetura

O projeto segue os princípios de **Clean Architecture** com camadas bem definidas:

### Camadas

1. **API (Endpoints)** - Recebe requisições HTTP e retorna respostas
2. **Services** - Lógica de negócio
3. **Repositories** - Acesso aos dados
4. **Models** - Entidades do banco de dados
5. **Schemas** - Validação de dados de entrada/saída

### Fluxo de dados

```
Request → Endpoint → Service → Repository → Database
Response ← Endpoint ← Service ← Repository ← Database
```

## 🔧 Desenvolvimento

### Adicionar novo endpoint

1. Criar schema em `app/schemas/`
2. Criar service em `app/services/`
3. Criar endpoint em `app/api/v1/endpoints/`
4. Adicionar rota em `app/api/v1/router.py`
5. Escrever testes em `tests/`

### Padrões de código

- Use type hints em todas as funções
- Docstrings em classes e funções públicas
- Siga PEP 8
- Mantenha coverage acima de 96%

## 📝 Licença

MIT
