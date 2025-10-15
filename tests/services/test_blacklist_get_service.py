import unittest
from unittest.mock import Mock, patch
from http import HTTPStatus

# Configurar el path para importar módulos de la aplicación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app.services.blacklist_get_service import BlacklistGetService
from app.models.blacklist import Blacklist

class TestBlacklistGetService(unittest.TestCase):
    """Pruebas unitarias para BlacklistGetService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.test_email = 'test@ejemplo.com'
        self.test_email_upper = 'TEST@EJEMPLO.COM'
        self.test_email_spaces = '  test@ejemplo.com  '
        self.test_email_normalized = 'test@ejemplo.com'
        
        # Mock del modelo Blacklist
        self.mock_blacklist = Mock()
        self.mock_blacklist.email = self.test_email_normalized
        self.mock_blacklist.app_uuid = '550e8400-e29b-41d4-a716-446655440000'
        self.mock_blacklist.blocked_reason = 'Comportamiento sospechoso'
        self.mock_blacklist.ip_address = '192.168.1.1'
        self.mock_blacklist.created_at = Mock()
        self.mock_blacklist.created_at.isoformat.return_value = '2023-01-01T10:00:00'
        self.mock_blacklist.updated_at = Mock()
        self.mock_blacklist.updated_at.isoformat.return_value = '2023-01-01T10:00:00'
    
    # =====================================
    # TESTS PARA CASOS EXITOSOS
    # =====================================
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_found(self, mock_db):
        """Test obtener email que está en la blacklist"""
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = self.mock_blacklist
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        # Verificaciones
        mock_db.session.query.assert_called_once_with(Blacklist)
        mock_query.filter_by.assert_called_once_with(email=self.test_email_normalized)
        mock_filter.first.assert_called_once()
        
        # Verificar resultado - solo los campos necesarios
        self.assertIsInstance(result, dict)
        self.assertTrue(result['is_blocked'])
        self.assertEqual(result['blocked_reason'], 'Comportamiento sospechoso')
        
        # Verificar que no hay campos innecesarios
        self.assertNotIn('success', result)
        self.assertNotIn('message', result)
        self.assertNotIn('errors', result)
        self.assertNotIn('status_code', result)
        self.assertNotIn('email', result)
        self.assertNotIn('app_uuid', result)
        self.assertNotIn('ip_address', result)
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_not_found(self, mock_db):
        """Test obtener email que NO está en la blacklist"""
        # Mock de la consulta de base de datos - no encontrado
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None  # No encontrado
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        # Verificaciones
        mock_db.session.query.assert_called_once_with(Blacklist)
        mock_query.filter_by.assert_called_once_with(email=self.test_email_normalized)
        mock_filter.first.assert_called_once()
        
        # Verificar resultado - solo los campos necesarios
        self.assertIsInstance(result, dict)
        self.assertFalse(result['is_blocked'])
        
        # Verificar que no hay campos innecesarios
        self.assertNotIn('blocked_reason', result)
        self.assertNotIn('success', result)
        self.assertNotIn('message', result)
        self.assertNotIn('errors', result)
        self.assertNotIn('status_code', result)
        self.assertNotIn('email', result)
        self.assertNotIn('app_uuid', result)
        self.assertNotIn('ip_address', result)
    
    # =====================================
    # TESTS PARA NORMALIZACIÓN DE EMAIL
    # =====================================
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_case_insensitive(self, mock_db):
        """Test que el servicio normaliza emails a lowercase"""
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = self.mock_blacklist
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método con email en mayúsculas
        result = BlacklistGetService.get_blacklist_by_email(self.test_email_upper)
        
        # Verificar que se normalizó a lowercase
        mock_query.filter_by.assert_called_once_with(email=self.test_email_normalized)
        self.assertTrue(result['is_blocked'])
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_trim_spaces(self, mock_db):
        """Test que el servicio elimina espacios del email"""
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = self.mock_blacklist
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método con email con espacios
        result = BlacklistGetService.get_blacklist_by_email(self.test_email_spaces)
        
        # Verificar que se eliminaron los espacios
        mock_query.filter_by.assert_called_once_with(email=self.test_email_normalized)
        self.assertTrue(result['is_blocked'])
    
    # =====================================
    # TESTS PARA VALIDACIÓN DE ENTRADA
    # =====================================
    
    def test_get_blacklist_by_email_empty_string(self):
        """Test validación de email vacío"""
        with self.assertRaises(ValueError) as context:
            BlacklistGetService.get_blacklist_by_email("")
        
        self.assertEqual(str(context.exception), 'El email no puede estar vacío')
    
    def test_get_blacklist_by_email_none(self):
        """Test validación de email None"""
        with self.assertRaises(ValueError) as context:
            BlacklistGetService.get_blacklist_by_email(None)
        
        self.assertEqual(str(context.exception), 'El email no puede estar vacío')
    
    def test_get_blacklist_by_email_whitespace_only(self):
        """Test validación de email solo con espacios"""
        with self.assertRaises(ValueError) as context:
            BlacklistGetService.get_blacklist_by_email("   ")
        
        self.assertEqual(str(context.exception), 'El email no puede estar vacío')
    
    # =====================================
    # TESTS PARA ERRORES DE BASE DE DATOS
    # =====================================
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_sqlalchemy_error(self, mock_db):
        """Test manejo de errores de SQLAlchemy"""
        # Mock error de SQLAlchemy
        from sqlalchemy.exc import SQLAlchemyError
        mock_db.session.query.side_effect = SQLAlchemyError("Database connection failed")
        
        # Ejecutar método y verificar que se propaga el error
        with self.assertRaises(SQLAlchemyError) as context:
            BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        self.assertEqual(str(context.exception), "Database connection failed")
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_unexpected_error(self, mock_db):
        """Test manejo de errores inesperados"""
        # Mock error inesperado
        mock_db.session.query.side_effect = Exception("Unexpected error")
        
        # Ejecutar método y verificar que se propaga el error
        with self.assertRaises(Exception) as context:
            BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        self.assertEqual(str(context.exception), "Unexpected error")
    
    # =====================================
    # TESTS PARA DIFERENTES TIPOS DE EMAIL
    # =====================================
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_with_special_characters(self, mock_db):
        """Test con email que contiene caracteres especiales"""
        special_email = 'test+tag@ejemplo.com'
        
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(special_email)
        
        # Verificar que se procesó correctamente
        mock_query.filter_by.assert_called_once_with(email=special_email)
        self.assertFalse(result['is_blocked'])
    
    @patch('app.services.blacklist_get_service.db')
    def test_get_blacklist_by_email_long_email(self, mock_db):
        """Test con email muy largo"""
        long_email = 'a' * 200 + '@ejemplo.com'
        
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(long_email)
        
        # Verificar que se procesó correctamente
        mock_query.filter_by.assert_called_once_with(email=long_email)
        self.assertFalse(result['is_blocked'])
    
    # =====================================
    # TESTS PARA ESTRUCTURA DE RESPUESTA
    # =====================================
    
    @patch('app.services.blacklist_get_service.db')
    def test_response_structure_success_blocked(self, mock_db):
        """Test estructura de respuesta cuando está bloqueado"""
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = self.mock_blacklist
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        # Verificar estructura de respuesta
        self.assertIsInstance(result, dict)
        self.assertIn('is_blocked', result)
        self.assertIn('blocked_reason', result)
        
        # Verificar tipos de datos
        self.assertIsInstance(result['is_blocked'], bool)
        self.assertIsInstance(result['blocked_reason'], str)
        self.assertTrue(result['is_blocked'])
    
    @patch('app.services.blacklist_get_service.db')
    def test_response_structure_success_not_blocked(self, mock_db):
        """Test estructura de respuesta cuando NO está bloqueado"""
        # Mock de la consulta de base de datos
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter_by.return_value = mock_filter
        mock_db.session.query.return_value = mock_query
        
        # Ejecutar método
        result = BlacklistGetService.get_blacklist_by_email(self.test_email)
        
        # Verificar estructura de respuesta
        self.assertIsInstance(result, dict)
        self.assertIn('is_blocked', result)
        self.assertNotIn('blocked_reason', result)
        
        # Verificar tipos de datos
        self.assertIsInstance(result['is_blocked'], bool)
        self.assertFalse(result['is_blocked'])


if __name__ == '__main__':
    unittest.main()