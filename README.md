# Sistema de Upload CSV

Um sistema web completo para upload, processamento e análise de arquivos CSV, desenvolvido com FastAPI e Bootstrap 5.

## 🚀 Características

- **Autenticação completa** com sistema de usuários e operador
- **Upload de arquivos CSV** com validação e processamento automático
- **Dashboard interativo** com estatísticas e gráficos
- **Banco de dados** para gerenciar todos os uploads
- **Interface responsiva** para desktop e mobile
- **Segurança robusta** com CSRF, validações e hash de senhas
- **Testes automatizados** para garantir qualidade

## 📋 Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd ProjetoAPI.DOCIEMILITAR
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
copy env.example .env

# Edite o arquivo .env com suas configurações
```

### 5. Execute a aplicação
```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em: http://localhost:8000

## ⚙️ Configuração

### Arquivo .env
```env
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///./app.db
OPERATOR_EMAIL=admin@exemplo.com
OPERATOR_PASSWORD=senha_do_operador
MAX_UPLOAD_MB=20
```

### Variáveis de Ambiente

- `SECRET_KEY`: Chave secreta para assinatura de cookies (obrigatória)
- `DATABASE_URL`: URL do banco de dados (SQLite por padrão)
- `OPERATOR_EMAIL`: Email do operador (opcional)
- `OPERATOR_PASSWORD`: Senha do operador (opcional)
- `MAX_UPLOAD_MB`: Tamanho máximo de upload em MB (padrão: 500)

## 👥 Usuários e Papéis

### Sistema de Usuários
- **Operador**: Apenas 1 por sistema, com privilégios administrativos
- **Usuários comuns**: Podem fazer upload e gerenciar própria conta

### Criação do Operador
1. **Via variáveis de ambiente**: Configure `OPERATOR_EMAIL` e `OPERATOR_PASSWORD`
2. **Primeiro registro**: Se não houver operador, o primeiro usuário registrado vira operador

## 🎯 Funcionalidades

### Dashboard
- Estatísticas gerais do sistema
- Gráfico de distribuição por tipo de dados
- Formulário de upload de CSV
- Informações do último upload

### Banco de Dados
- Lista todos os uploads com filtros
- Paginação e busca
- Detalhes de cada upload
- Download de arquivos originais
- Preview dos dados (primeiras 100 linhas)

### Gerenciar Conta
- Visualizar perfil
- Alterar senha
- Excluir conta (exceto operador)

### Upload de CSV
- Validação de extensão (.csv apenas)
- Detecção automática de encoding
- Detecção de separadores (vírgula, ponto e vírgula, tab, pipe)
- Análise de tipos de dados
- Preview das primeiras linhas

## 🔒 Segurança

- **Hash de senhas** com bcrypt
- **Cookies HttpOnly** para sessões
- **Proteção CSRF** em formulários
- **Validação de arquivos** (extensão e tamanho)
- **Headers de segurança** (X-Content-Type-Options, X-Frame-Options, etc.)
- **Escape de dados** em templates

## 🧪 Testes

Execute os testes com:
```bash
pytest -v
```

### Cobertura de Testes
- Autenticação (registro, login, logout)
- Upload de arquivos
- Dashboard e estatísticas
- Proteção de rotas
- Validações de segurança

## 📁 Estrutura do Projeto

```
project/
├── app/
│   ├── main.py              # Aplicação principal
│   ├── config.py            # Configurações
│   ├── db.py                # Configuração do banco
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── security.py          # Utilitários de segurança
│   ├── services/            # Serviços de negócio
│   │   ├── auth_service.py
│   │   ├── csv_service.py
│   │   ├── file_service.py
│   │   └── stats_service.py
│   ├── routers/             # Rotas da API
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── database.py
│   │   └── account.py
│   ├── templates/           # Templates HTML
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── database/
│   │   └── account/
│   └── static/              # Arquivos estáticos
│       ├── css/
│       └── js/
├── tests/                   # Testes automatizados
├── uploads/                 # Diretório de uploads
├── requirements.txt         # Dependências
├── env.example             # Exemplo de configuração
└── README.md               # Este arquivo
```

## 🚀 Uso do Sistema

### 1. Primeiro Acesso
1. Acesse http://localhost:8000
2. Registre-se como primeiro usuário (vira operador automaticamente)
3. Ou configure operador via variáveis de ambiente

### 2. Upload de CSV
1. Acesse o Dashboard
2. Selecione um arquivo .csv
3. Clique em "Enviar Arquivo"
4. Visualize as estatísticas atualizadas

### 3. Gerenciar Uploads
1. Acesse "Banco de Dados"
2. Use filtros para encontrar uploads
3. Clique em "Ver detalhes" para preview
4. Baixe arquivos originais

### 4. Gerenciar Conta
1. Acesse "Gerenciar Conta"
2. Altere senha se necessário
3. Exclua conta (exceto operador)

## 🔧 Desenvolvimento

### Adicionando Novas Funcionalidades
1. Crie novos serviços em `app/services/`
2. Adicione rotas em `app/routers/`
3. Crie templates em `app/templates/`
4. Adicione testes em `tests/`

### Banco de Dados
- SQLite por padrão (desenvolvimento)
- PostgreSQL suportado via variável `DATABASE_URL`
- Migrações automáticas no startup

### Deploy
1. Configure variáveis de ambiente de produção
2. Use HTTPS em produção
3. Configure `SECRET_KEY` segura
4. Use banco PostgreSQL para produção

## 🐛 Solução de Problemas

### Erro de Importação
```bash
# Verifique se está no ambiente virtual
pip list

# Reinstale dependências
pip install -r requirements.txt
```

### Erro de Banco de Dados
```bash
# Delete o arquivo de banco e reinicie
rm app.db
uvicorn app.main:app --reload
```

### Erro de Upload
- Verifique se o arquivo é .csv
- Confirme se não excede o limite de tamanho
- Verifique permissões do diretório uploads/

## 📝 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Execute os testes
3. Consulte os logs da aplicação
4. Abra uma issue no repositório

---

**Desenvolvido com ❤️ usando FastAPI, Bootstrap 5 e Python**
