from sqlalchemy import Column, String, DateTime
from datetime import datetime
from ..api.extensions import db


class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    
    email = Column(String(255), primary_key=True, nullable=False)
    app_uuid = Column(String(36), nullable=False)
    blocked_reason = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # 45 caracteres para IPv6
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, email, app_uuid, blocked_reason, ip_address=None):
        self.email = email
        self.app_uuid = app_uuid
        self.blocked_reason = blocked_reason
        self.ip_address = ip_address
    
    def __repr__(self):
        return f'<Blacklist(email="{self.email}", app_uuid="{self.app_uuid}", blocked_reason="{self.blocked_reason}")>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización JSON"""
        return {
            'email': self.email,
            'app_uuid': self.app_uuid,
            'blocked_reason': self.blocked_reason,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
