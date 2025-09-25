# 🚀 Guia de Início Rápido

## Instalação e Execução

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Ambiente
```bash
# Copiar arquivo de configuração
copy env.example .env

# Editar .env (opcional - pode usar valores padrão)
notepad .env
```

### 3. Executar Aplicação
```bash
# Opção 1: Script automático
python run.py

# Opção 2: Comando direto
uvicorn app.main:app --reload
```

### 4. Acessar Sistema
- URL: http://localhost:8000
- Primeiro usuário registrado vira operador automaticamente

## 🎯 Teste Rápido

### 1. Registrar Usuário
- Acesse http://localhost:8000
- Clique em "Cadastrar"
- Preencha os dados (primeiro usuário vira operador)

### 2. Fazer Upload
- Use o arquivo `exemplo_dados.csv` incluído
- Vá para Dashboard
- Selecione o arquivo e clique "Enviar"

### 3. Visualizar Dados
- Acesse "Banco de Dados"
- Veja a lista de uploads
- Clique em "Ver detalhes" para preview

## 🧪 Executar Testes
```bash
pytest -v
```

## 📁 Estrutura Principal
```
app/
├── main.py          # Aplicação principal
├── models.py        # Modelos do banco
├── routers/         # Rotas da API
├── services/        # Lógica de negócio
├── templates/       # Páginas HTML
└── static/          # CSS/JS
```

## ⚙️ Configurações Importantes

### .env
```env
SECRET_KEY=sua_chave_secreta
DATABASE_URL=sqlite:///./app.db
MAX_UPLOAD_MB=20
```

### Operador
- Configure `OPERATOR_EMAIL` e `OPERATOR_PASSWORD` no .env
- Ou registre o primeiro usuário (vira operador automaticamente)

## 🔧 Solução de Problemas

### Erro de Importação
```bash
pip install -r requirements.txt
```

### Erro de Banco
```bash
rm app.db
uvicorn app.main:app --reload
```

### Porta Ocupada
```bash
uvicorn app.main:app --reload --port 8001
```

## 📚 Documentação Completa
Veja `README.md` para documentação detalhada.

---
**Sistema pronto para uso! 🎉**
