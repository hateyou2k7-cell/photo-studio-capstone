from business.models.iauth_repository import IAuthRepository
from business.models.auth import Auth
from typing import Optional
from database.databases.factory_database import FactoryDatabase as db_factory
from sqlalchemy.orm import Session
from database.models.auth.auth_user_model import AuthUserModel
from database.models.film_user_model import User, ProviderProfile
from werkzeug.security import check_password_hash


class AuthRepository(IAuthRepository):
    def __init__(self, session: Session = None):
        self.session = session or db_factory.get_database('POSTGREE').session
    
    def login(self, auth: Auth) -> Auth:
        user = self.session.query(AuthUserModel).filter_by(username=auth.username).first()
        if not user:
            return None
        if not check_password_hash(user.password_hash, auth.password):
            return None
        auth_user = self.session.query(User).filter_by(email=user.email).first()
        if auth_user:
            auth.id = auth_user.id
            auth.role = auth_user.role
        else:
            auth.id = user.id
            auth.role = 'user'
        return auth
   
    def register(self, auth: Auth, role: str = 'user') -> Optional[Auth]:
        try:
            new_auth_user = AuthUserModel(
                username=auth.username,
                password_hash=auth.password,
                email=auth.email
            )
            self.session.add(new_auth_user)
            self.session.flush()

            new_user = User(
                email=auth.email,
                password_hash=auth.password,
                full_name=auth.username,
                role=role,
                is_active=True,
            )
            self.session.add(new_user)
            self.session.flush()

            if role == 'provider':
                provider_profile = ProviderProfile(
                    user_id=new_user.id,
                    business_name=auth.username + "'s Studio",
                    description='',
                    status='approved'
                )
                self.session.add(provider_profile)

            self.session.commit()
            self.session.refresh(new_auth_user)
            auth.id = new_auth_user.id
            return auth
        except Exception as e:
            self.session.rollback()
            print(f"Register error: {e}")
            return None
        finally:
            self.session.close()

    def check_exist(self, username: str) -> bool:
        existing_user = self.session.query(AuthUserModel).filter_by(username=username).first()
        if existing_user:
            return True
        return False

    def remember_password(self) -> Optional[Auth]:
        return None

    def look_account(self, Id: int) -> bool:
        return True

    def un_look_account(self, course_id: int) -> None:
        pass
    

    

