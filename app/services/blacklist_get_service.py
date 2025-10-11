from http import HTTPStatus
from ..models.blacklist import Blacklist
from ..api.extensions import db
from sqlalchemy.exc import SQLAlchemyError


class BlacklistGetService:
    """Servicio para obtener información de un email en la blacklist"""
    
    @staticmethod
    def get_blacklist_by_email(email: str | None) -> dict:
        """
        Busca un email en la blacklist y retorna si está bloqueado y el motivo
        
        Args:
            email (str): Email a buscar en la blacklist
            
        Returns:
            dict: Solo is_blocked (boolean) y blocked_reason (si está bloqueado)
        """
        # Validar que el email no esté vacío
        if not email or not email.strip():
            raise ValueError('El email no puede estar vacío')
        
        # Normalizar email (lowercase y trim)
        email = email.strip().lower()
        
        # Buscar el email en la blacklist
        blacklist_entry = db.session.query(Blacklist).filter_by(email=email).first()
        
        if blacklist_entry:
            # Email encontrado en blacklist
            return {
                'is_blocked': True,
                'blocked_reason': blacklist_entry.blocked_reason
            }
        else:
            # Email no encontrado en blacklist
            return {
                'is_blocked': False
            }
