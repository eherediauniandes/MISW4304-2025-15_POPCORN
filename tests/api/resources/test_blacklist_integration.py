import unittest
from unittest.mock import Mock, patch
import json

# Configurar el path para importar módulos de la aplicación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app import create_app
from app.api.extensions import db
from app.models.blacklist import Blacklist


class TestBlacklistIntegration(unittest.TestCase):
    """Tests de integración para los endpoints de blacklist"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Crear tablas de prueba
        db.create_all()
        
        # Crear cliente de prueba
        self.client = self.app.test_client()
        
        # Token válido para autenticación
        self.valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoic3RhdGljLXVzZXIiLCJyb2xlIjoiYWRtaW4ifQ.6bUHdYJk1cRnn-SVZEXAMPLEpR0fZ2mJb_YWbl8pW1lM"
        
        # Headers con autenticación
        self.auth_headers = {
            'Authorization': f'Bearer {self.valid_token}',
            'Content-Type': 'application/json'
        }
        
        # Datos de prueba
        self.test_email = 'test@ejemplo.com'
        self.test_data = {
            'email': self.test_email,
            'app_uuid': '550e8400-e29b-41d4-a716-446655440000',
            'blocked_reason': 'Comportamiento sospechoso'
        }
    
    def tearDown(self):
        """Limpieza después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    # =====================================
    # TESTS PARA ENDPOINT POST (CREATE)
    # =====================================
    
    def test_post_create_blacklist_success(self):
        """Test POST /blacklists - creación exitosa"""
        response = self.client.post(
            '/blacklists',
            data=json.dumps(self.test_data),
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertIn('data', data)
        self.assertEqual(data['data']['email'], self.test_email)
    
    def test_post_create_blacklist_missing_auth(self):
        """Test POST /blacklists - sin autenticación"""
        response = self.client.post(
            '/blacklists',
            data=json.dumps(self.test_data),
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_post_create_blacklist_invalid_data(self):
        """Test POST /blacklists - datos inválidos"""
        invalid_data = {'app_uuid': 'invalid-uuid'}
        
        response = self.client.post(
            '/blacklists',
            data=json.dumps(invalid_data),
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_post_create_blacklist_empty_data(self):
        """Test POST /blacklists - datos vacíos"""
        response = self.client.post(
            '/blacklists',
            data=json.dumps({}),
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    # =====================================
    # TESTS PARA ENDPOINT GET
    # =====================================
    
    def test_get_blacklist_email_found(self):
        """Test GET /blacklists/<email> - email encontrado en blacklist"""
        # Primero crear una entrada en la blacklist
        blacklist_entry = Blacklist(
            email=self.test_email,
            app_uuid=self.test_data['app_uuid'],
            blocked_reason=self.test_data['blocked_reason']
        )
        db.session.add(blacklist_entry)
        db.session.commit()
        
        # Consultar el email
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_blocked'])
        self.assertEqual(data['blocked_reason'], self.test_data['blocked_reason'])
    
    def test_get_blacklist_email_not_found(self):
        """Test GET /blacklists/<email> - email no encontrado"""
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['is_blocked'])
        self.assertNotIn('blocked_reason', data)
    
    def test_get_blacklist_email_empty(self):
        """Test GET /blacklists/<email> - email vacío"""
        response = self.client.get(
            '/blacklists/',
            headers=self.auth_headers
        )
        
        # Debería devolver 404 porque la ruta no existe
        self.assertEqual(response.status_code, 404)
    
    def test_get_blacklist_missing_auth(self):
        """Test GET /blacklists/<email> - sin autenticación"""
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers={'Content-Type': 'application/json'}
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_blacklist_email_with_spaces(self):
        """Test GET /blacklists/<email> - email con espacios"""
        email_with_spaces = '  test@ejemplo.com  '
        
        # Primero crear una entrada en la blacklist
        blacklist_entry = Blacklist(
            email=self.test_email,  # Sin espacios
            app_uuid=self.test_data['app_uuid'],
            blocked_reason=self.test_data['blocked_reason']
        )
        db.session.add(blacklist_entry)
        db.session.commit()
        
        # Consultar con espacios
        response = self.client.get(
            f'/blacklists/{email_with_spaces}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_blocked'])
    
    def test_get_blacklist_email_case_insensitive(self):
        """Test GET /blacklists/<email> - email case insensitive"""
        email_upper = 'TEST@EJEMPLO.COM'
        
        # Primero crear una entrada en la blacklist
        blacklist_entry = Blacklist(
            email=self.test_email,  # lowercase
            app_uuid=self.test_data['app_uuid'],
            blocked_reason=self.test_data['blocked_reason']
        )
        db.session.add(blacklist_entry)
        db.session.commit()
        
        # Consultar con mayúsculas
        response = self.client.get(
            f'/blacklists/{email_upper}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_blocked'])
    
    @patch('app.services.blacklist_get_service.db.session.query')
    def test_get_blacklist_database_error(self, mock_query):
        """Test GET /blacklists/<email> - error de base de datos"""
        # Mock error de base de datos
        from sqlalchemy.exc import SQLAlchemyError
        mock_query.side_effect = SQLAlchemyError('Database error')
        
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Error interno del servidor')
    
    @patch('app.services.blacklist_get_service.db.session.query')
    def test_get_blacklist_unexpected_error(self, mock_query):
        """Test GET /blacklists/<email> - error inesperado"""
        # Mock error inesperado
        mock_query.side_effect = Exception('Unexpected error')
        
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Error interno del servidor')
    
    def test_get_blacklist_with_none_blocked_reason(self):
        """Test GET /blacklists/<email> - blocked_reason es None"""
        # Crear entrada sin blocked_reason
        blacklist_entry = Blacklist(
            email=self.test_email,
            app_uuid=self.test_data['app_uuid'],
            blocked_reason=None
        )
        db.session.add(blacklist_entry)
        db.session.commit()
        
        # Consultar el email
        response = self.client.get(
            f'/blacklists/{self.test_email}',
            headers=self.auth_headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['is_blocked'])
        self.assertIsNone(data['blocked_reason'])
    
    # =====================================
    # TESTS PARA COBERTURA COMPLETA
    # =====================================
    
    def test_post_create_blacklist_multiple_errors(self):
        """Test POST /blacklists - múltiples errores de validación"""
        with patch('app.services.blacklist_create_service.BlacklistCreateService.process_create_request') as mock_process:
            mock_process.return_value = {
                'success': False,
                'errors': ['Error 1', 'Error 2'],
                'status_code': 400
            }
            
            response = self.client.post(
                '/blacklists',
                data=json.dumps(self.test_data),
                headers=self.auth_headers
            )
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertIsInstance(data['error'], list)
            self.assertEqual(len(data['error']), 2)
    
    def test_post_create_blacklist_single_error(self):
        """Test POST /blacklists - un solo error de validación"""
        with patch('app.services.blacklist_create_service.BlacklistCreateService.process_create_request') as mock_process:
            mock_process.return_value = {
                'success': False,
                'errors': ['Solo un error'],
                'status_code': 400
            }
            
            response = self.client.post(
                '/blacklists',
                data=json.dumps(self.test_data),
                headers=self.auth_headers
            )
            
            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
            self.assertEqual(data['error'], 'Solo un error')


if __name__ == '__main__':
    unittest.main()
