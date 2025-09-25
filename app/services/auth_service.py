"""
Serviço de autenticação
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import User, UserRole
from app.security import hash_password, verify_password
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Serviço de autenticação"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, name: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """Criar novo usuário"""
        # Verificar se já existe usuário com este email
        existing_user = self.db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError("Email já está em uso")
        
        # Verificar regra do operador único
        if role == UserRole.OPERATOR:
            existing_operator = self.db.query(User).filter(User.role == UserRole.OPERATOR).first()
            if existing_operator:
                raise ValueError("Já existe um operador no sistema")
        
        # Se não há operador e este é o primeiro usuário, promover a operador
        if role == UserRole.USER:
            existing_operator = self.db.query(User).filter(User.role == UserRole.OPERATOR).first()
            if not existing_operator:
                role = UserRole.OPERATOR
                logger.info(f"Primeiro usuário {email} promovido a operador")
        
        # Criar usuário
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str) -> User | None:
        """Autenticar usuário"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: int) -> User | None:
        """Obter usuário por ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_operator(self) -> User | None:
        """Obter operador do sistema"""
        return self.db.query(User).filter(User.role == UserRole.OPERATOR).first()
    
    def create_operator_from_env(self) -> bool:
        """Criar operador a partir das variáveis de ambiente"""
        if not settings.operator_email or not settings.operator_password:
            return False
        
        # Verificar se já existe operador
        if self.get_operator():
            return False
        
        try:
            self.create_user(
                name="Operador",
                email=settings.operator_email,
                password=settings.operator_password,
                role=UserRole.OPERATOR
            )
            logger.info(f"Operador criado: {settings.operator_email}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar operador: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Deletar usuário (apenas usuários comuns)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if user.role == UserRole.OPERATOR:
            raise ValueError("Operador não pode ser excluído")
        
        self.db.delete(user)
        self.db.commit()
        return True
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Alterar senha do usuário"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Senha atual incorreta")
        
        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True
