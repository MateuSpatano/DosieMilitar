"""
Testes do dashboard
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db, Base
from app.models import User, Upload, UserRole
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

@pytest.fixture(scope="function")
def authenticated_user(client, db_session):
    """Usuário autenticado para testes"""
    # Criar usuário
    auth_service = AuthService(db_session)
    user = auth_service.create_user("João", "joao@test.com", "123456")
    
    # Fazer login
    login_response = client.post("/login", data={
        "email": "joao@test.com",
        "password": "123456",
        "csrf_token": "test_token"
    })
    
    assert login_response.status_code == 302
    return user

def test_dashboard_redirects_unauthenticated(client):
    """Teste de redirecionamento para usuários não autenticados"""
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 401

def test_dashboard_loads_with_authentication(client, authenticated_user):
    """Teste de carregamento do dashboard autenticado"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text
    assert "Upload de CSV" in response.text

def test_dashboard_shows_stats(client, authenticated_user, db_session):
    """Teste de exibição de estatísticas no dashboard"""
    # Criar alguns uploads de teste
    upload1 = Upload(
        user_id=authenticated_user.id,
        original_name="test1.csv",
        stored_path="test1.csv",
        size_bytes=1000,
        rows_total=10,
        cols_total=5,
        columns_json='["col1", "col2", "col3", "col4", "col5"]',
        dtypes_json='{"col1": "string", "col2": "int", "col3": "float", "col4": "bool", "col5": "string"}',
        sample_rows_json='[{"col1": "test", "col2": 1, "col3": 1.5, "col4": true, "col5": "test"}]'
    )
    
    upload2 = Upload(
        user_id=authenticated_user.id,
        original_name="test2.csv",
        stored_path="test2.csv",
        size_bytes=2000,
        rows_total=20,
        cols_total=3,
        columns_json='["a", "b", "c"]',
        dtypes_json='{"a": "int", "b": "float", "c": "string"}',
        sample_rows_json='[{"a": 1, "b": 2.5, "c": "test"}]'
    )
    
    db_session.add(upload1)
    db_session.add(upload2)
    db_session.commit()
    
    # Acessar dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se estatísticas são exibidas
    assert "2" in response.text  # Total de uploads
    assert "30" in response.text  # Total de linhas (10 + 20)
    assert "test2.csv" in response.text  # Último upload

def test_dashboard_empty_state(client, authenticated_user):
    """Teste de estado vazio do dashboard"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se mostra estado vazio
    assert "0" in response.text  # Total de uploads
    assert "Nenhum" in response.text or "0" in response.text  # Estado vazio

def test_dashboard_upload_form_present(client, authenticated_user):
    """Teste de presença do formulário de upload"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se formulário de upload está presente
    assert 'name="file"' in response.text
    assert 'accept=".csv"' in response.text
    assert 'type="submit"' in response.text

def test_dashboard_chart_data_structure(client, authenticated_user, db_session):
    """Teste de estrutura dos dados do gráfico"""
    # Criar upload com dados de tipos
    upload = Upload(
        user_id=authenticated_user.id,
        original_name="test.csv",
        stored_path="test.csv",
        size_bytes=1000,
        rows_total=5,
        cols_total=3,
        columns_json='["col1", "col2", "col3"]',
        dtypes_json='{"col1": "string", "col2": "int", "col3": "float"}',
        sample_rows_json='[{"col1": "test", "col2": 1, "col3": 1.5}]'
    )
    
    db_session.add(upload)
    db_session.commit()
    
    # Acessar dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se dados do gráfico estão presentes
    assert "string" in response.text
    assert "int" in response.text
    assert "float" in response.text

def test_dashboard_last_upload_info(client, authenticated_user, db_session):
    """Teste de informações do último upload"""
    # Criar upload de teste
    upload = Upload(
        user_id=authenticated_user.id,
        original_name="ultimo_arquivo.csv",
        stored_path="ultimo_arquivo.csv",
        size_bytes=1500,
        rows_total=15,
        cols_total=4,
        columns_json='["a", "b", "c", "d"]',
        dtypes_json='{"a": "string", "b": "int", "c": "float", "d": "bool"}',
        sample_rows_json='[{"a": "test", "b": 1, "c": 1.5, "d": true}]'
    )
    
    db_session.add(upload)
    db_session.commit()
    
    # Acessar dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se informações do último upload são exibidas
    assert "ultimo_arquivo.csv" in response.text
    assert "15" in response.text  # Número de linhas
    assert "4" in response.text   # Número de colunas

def test_dashboard_csrf_token_present(client, authenticated_user):
    """Teste de presença do token CSRF no formulário"""
    response = client.get("/dashboard")
    assert response.status_code == 200
    
    # Verificar se token CSRF está presente
    assert 'name="csrf_token"' in response.text
    assert 'type="hidden"' in response.text
