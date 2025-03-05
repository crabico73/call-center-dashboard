from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from typing import Optional
from flask_login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(120), nullable=False)
    role = Column(String(20), nullable=False, default='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AuthService:
    def __init__(self):
        """Initialize the auth service with database connection"""
        app_data_dir = os.path.join(os.environ['LOCALAPPDATA'], 'CallCenterDashboard')
        os.makedirs(app_data_dir, exist_ok=True)
        db_path = os.path.join(app_data_dir, 'users.db')
        self.engine = create_engine(f'sqlite:///{db_path}')
        
        # Create tables
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Create default admin user if not exists
        self.create_default_admin()
    
    def create_default_admin(self):
        """Create default admin user if no users exist"""
        if not self.session.query(User).first():
            admin = User(
                username='admin',
                role='admin'
            )
            admin.set_password('admin123')  # Default password
            self.session.add(admin)
            self.session.commit()
            print("Created default admin user (username: admin, password: admin123)")
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter_by(id=user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter_by(username=username).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None
    
    def create_user(self, username: str, password: str, role: str = 'user') -> Optional[User]:
        """Create a new user"""
        if self.get_user_by_username(username):
            return None
        
        user = User(username=username, role=role)
        user.set_password(password)
        self.session.add(user)
        self.session.commit()
        return user
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user's password"""
        user = self.get_user(user_id)
        if user:
            user.set_password(new_password)
            self.session.commit()
            return True
        return False 