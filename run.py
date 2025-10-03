#!/usr/bin/env python3
"""
Script de inicialização da aplicação
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verificar versão do Python"""
    if sys.version_info < (3, 8):
        print("ERRO: Python 3.8+ é necessário")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)
    print(f"OK: Python {sys.version.split()[0]} detectado")

def check_virtual_env():
    """Verificar se está em ambiente virtual"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("AVISO: Ambiente virtual não detectado")
        print("Recomendado: python -m venv venv && venv\\Scripts\\activate (Windows) ou source venv/bin/activate (Linux/Mac)")
    else:
        print("OK: Ambiente virtual ativo")

def check_env_file():
    """Verificar arquivo .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("AVISO: Arquivo .env não encontrado")
        if Path("env.example").exists():
            print("Copiando env.example para .env...")
            import shutil
            shutil.copy("env.example", ".env")
            print("OK: Arquivo .env criado. Edite com suas configurações.")
        else:
            print("ERRO: Arquivo env.example não encontrado")
            return False
    else:
        print("OK: Arquivo .env encontrado")
    return True

def check_requirements():
    """Verificar se dependências estão instaladas"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("OK: Dependências principais encontradas")
        return True
    except ImportError:
        print("ERRO: Dependências não encontradas")
        print("Execute: pip install -r requirements.txt")
        return False

def create_directories():
    """Criar diretórios necessários"""
    dirs = ["uploads", "app/static/css", "app/static/js", "app/templates"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("OK: Diretórios criados/verificados")

def main():
    """Função principal"""
    print("INICIANDO: Sistema de Upload CSV...")
    print("=" * 50)
    
    # Verificações
    check_python_version()
    check_virtual_env()
    
    if not check_env_file():
        return
    
    if not check_requirements():
        return
    
    create_directories()
    
    print("=" * 50)
    print("OK: Todas as verificações passaram!")
    print("INICIANDO: Servidor...")
    print("=" * 50)
    print("Acesse: http://localhost:8000")
    print("Para parar: Ctrl+C")
    print("=" * 50)
    
    # Iniciar servidor
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nSERVIDOR: Parado pelo usuário")
    except Exception as e:
        print(f"ERRO: Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()
