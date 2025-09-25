"""
Testes de autenticação
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db, Base
from app.models import User, UserRole
from app.services.auth_service import AuthService

# Configurar banco de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    """Cliente de teste"""
    # Criar tabelas
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Limpar tabelas após cada teste
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Sessão do banco para testes"""
    db = TestingSessionLocal()
    yield db
    db.close()

def test_register_user(client, db_session):
    """Teste de registro de usuário"""
    response = client.post("/register", data={
        "name": "João Silva",
        "email": "joao@test.com",
        "password": "123456",
        "confirm_password": "123456",
        "csrf_token": "test_token"
    })
    
    # Deve redirecionar para dashboard
    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"
    
    # Verificar se usuário foi criado
    auth_service = AuthService(db_session)
    user = auth_service.get_user_by_id(1)
    assert user is not None
    assert user.name == "João Silva"
    assert user.email == "joao@test.com"
    assert user.role == UserRole.OPERATOR  # Primeiro usuário vira operador

def test_register_duplicate_email(client, db_session):
    """Teste de registro com email duplicado"""
    # Criar primeiro usuário
    auth_service = AuthService(db_session)
    auth_service.create_user("João", "joao@test.com", "123456")
    
    # Tentar criar segundo usuário com mesmo email
    response = client.post("/register", data={
        "name": "João Silva",
        "email": "joao@test.com",
        "password": "123456",
        "confirm_password": "123456",
        "csrf_token": "test_token"
    })
    
    # Deve retornar erro
    assert response.status_code == 200
    assert "Email já está em uso" in response.text

def test_login_success(client, db_session):
    """Teste de login bem-sucedido"""
    # Criar usuário
    auth_service = AuthService(db_session)
    auth_service.create_user("João", "joao@test.com", "123456")
    
    # Fazer login
    response = client.post("/login", data={
        "email": "joao@test.com",
        "password": "123456",
        "csrf_token": "test_token"
    })
    
    # Deve redirecionar para dashboard
    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"

def test_login_invalid_credentials(client, db_session):
    """Teste de login com credenciais inválidas"""
    # Criar usuário
    auth_service = AuthService(db_session)
    auth_service.create_user("João", "joao@test.com", "123456")
    
    # Tentar login com senha errada
    response = client.post("/login", data={
        "email": "joao@test.com",
        "password": "wrong_password",
        "csrf_token": "test_token"
    })
    
    # Deve retornar erro
    assert response.status_code == 200
    assert "Email ou senha incorretos" in response.text

def test_logout(client, db_session):
    """Teste de logout"""
    # Criar usuário e fazer login
    auth_service = AuthService(db_session)
    auth_service.create_user("João", "joao@test.com", "123456")
    
    # Fazer login primeiro
    login_response = client.post("/login", data={
        "email": "joao@test.com",
        "password": "123456",
        "csrf_token": "test_token"
    })
    assert login_response.status_code == 302
    
    # Fazer logout
    logout_response = client.post("/logout")
    assert logout_response.status_code == 302
    assert logout_response.headers["location"] == "/login"

def test_first_user_becomes_operator(db_session):
    """Teste de que o primeiro usuário vira operador"""
    auth_service = AuthService(db_session)
    
    # Criar primeiro usuário
    user = auth_service.create_user("João", "joao@test.com", "123456")
    assert user.role == UserRole.OPERATOR
    
    # Criar segundo usuário
    user2 = auth_service.create_user("Maria", "maria@test.com", "123456")
    assert user2.role == UserRole.USER

def test_operator_cannot_be_deleted(db_session):
    """Teste de que operador não pode ser deletado"""
    auth_service = AuthService(db_session)
    
    # Criar operador
    operator = auth_service.create_user("Operador", "op@test.com", "123456", UserRole.OPERATOR)
    
    # Tentar deletar operador
    with pytest.raises(ValueError, match="Operador não pode ser excluído"):
        auth_service.delete_user(operator.id)
