"""
Testes de upload de arquivos
"""
import pytest
import io
import csv
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

def create_test_csv():
    """Criar arquivo CSV de teste em memória"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(["nome", "idade", "salario", "ativo"])
    
    # Dados de teste
    writer.writerow(["João Silva", 30, 5000.50, True])
    writer.writerow(["Maria Santos", 25, 4500.00, True])
    writer.writerow(["Pedro Costa", 35, 6000.75, False])
    
    return io.BytesIO(output.getvalue().encode('utf-8'))

def test_upload_csv_success(client, authenticated_user, db_session):
    """Teste de upload de CSV bem-sucedido"""
    # Criar arquivo CSV de teste
    csv_content = create_test_csv()
    
    # Fazer upload
    response = client.post("/upload-csv", 
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"csrf_token": "test_token"}
    )
    
    # Deve redirecionar para dashboard
    assert response.status_code == 302
    assert response.headers["location"] == "/dashboard"
    
    # Verificar se upload foi salvo no banco
    upload = db_session.query(Upload).first()
    assert upload is not None
    assert upload.original_name == "test.csv"
    assert upload.user_id == authenticated_user.id
    assert upload.rows_total == 3  # 3 linhas de dados
    assert upload.cols_total == 4  # 4 colunas

def test_upload_non_csv_file(client, authenticated_user):
    """Teste de upload de arquivo não-CSV"""
    # Criar arquivo de texto simples
    text_content = io.BytesIO(b"Este não é um arquivo CSV")
    
    # Tentar fazer upload
    response = client.post("/upload-csv",
        files={"file": ("test.txt", text_content, "text/plain")},
        data={"csrf_token": "test_token"}
    )
    
    # Deve redirecionar com erro
    assert response.status_code == 302
    assert "error=Arquivo deve ser CSV" in response.headers["location"]

def test_upload_without_authentication(client):
    """Teste de upload sem autenticação"""
    csv_content = create_test_csv()
    
    # Tentar fazer upload sem estar logado
    response = client.post("/upload-csv",
        files={"file": ("test.csv", csv_content, "text/csv")},
        data={"csrf_token": "test_token"}
    )
    
    # Deve retornar erro 401
    assert response.status_code == 401

def test_dashboard_requires_authentication(client):
    """Teste de que dashboard requer autenticação"""
    response = client.get("/dashboard")
    assert response.status_code == 401

def test_dashboard_with_authentication(client, authenticated_user, db_session):
    """Teste de acesso ao dashboard autenticado"""
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
    
    db_session.add(upload1)
    db_session.commit()
    
    # Acessar dashboard
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard" in response.text
    assert "1" in response.text  # Total de uploads

def test_database_list_requires_authentication(client):
    """Teste de que lista de banco de dados requer autenticação"""
    response = client.get("/database")
    assert response.status_code == 401

def test_database_list_with_authentication(client, authenticated_user, db_session):
    """Teste de acesso à lista de banco de dados autenticado"""
    # Criar upload de teste
    upload = Upload(
        user_id=authenticated_user.id,
        original_name="test.csv",
        stored_path="test.csv",
        size_bytes=1000,
        rows_total=5,
        cols_total=3
    )
    
    db_session.add(upload)
    db_session.commit()
    
    # Acessar lista
    response = client.get("/database")
    assert response.status_code == 200
    assert "Banco de Dados" in response.text
    assert "test.csv" in response.text

def test_database_detail_requires_authentication(client):
    """Teste de que detalhes do banco de dados requerem autenticação"""
    response = client.get("/database/1")
    assert response.status_code == 401

def test_database_detail_with_authentication(client, authenticated_user, db_session):
    """Teste de acesso aos detalhes do banco de dados autenticado"""
    # Criar upload de teste
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
    
    # Acessar detalhes
    response = client.get(f"/database/{upload.id}")
    assert response.status_code == 200
    assert "test.csv" in response.text
    assert "col1" in response.text
