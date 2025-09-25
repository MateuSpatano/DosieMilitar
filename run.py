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
        print("❌ Python 3.8+ é necessário")
        print(f"Versão atual: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detectado")

def check_virtual_env():
    """Verificar se está em ambiente virtual"""
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Ambiente virtual não detectado")
        print("Recomendado: python -m venv venv && venv\\Scripts\\activate (Windows) ou source venv/bin/activate (Linux/Mac)")
    else:
        print("✅ Ambiente virtual ativo")

def check_env_file():
    """Verificar arquivo .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado")
        if Path("env.example").exists():
            print("Copiando env.example para .env...")
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ Arquivo .env criado. Edite com suas configurações.")
        else:
            print("❌ Arquivo env.example não encontrado")
            return False
    else:
        print("✅ Arquivo .env encontrado")
    return True

def check_requirements():
    """Verificar se dependências estão instaladas"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ Dependências principais encontradas")
        return True
    except ImportError:
        print("❌ Dependências não encontradas")
        print("Execute: pip install -r requirements.txt")
        return False

def create_directories():
    """Criar diretórios necessários"""
    dirs = ["uploads", "app/static/css", "app/static/js", "app/templates"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Diretórios criados/verificados")

def main():
    """Função principal"""
    print("🚀 Inicializando Sistema de Upload CSV...")
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
    print("✅ Todas as verificações passaram!")
    print("🚀 Iniciando servidor...")
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
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    main()
