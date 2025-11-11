import unittest
from unittest.mock import Mock, patch, MagicMock
import uuid
from flask import Flask
from sqlalchemy.exc import IntegrityError

# Configurar el path para importar módulos de la aplicación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.services.blacklist_create_service import BlacklistCreateService


class TestBlacklistCreateService(unittest.TestCase):
    """Pruebas unitarias para BlacklistCreateService"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Datos de prueba válidos
        self.valid_data = {
            'email': 'test@ejemplo.com',
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Datos inválidos para testing
        self.invalid_data_no_email = {
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Test'
        }
        
        self.invalid_data_bad_uuid = {
            'email': 'test@ejemplo.com',
            'app_uuid': 'invalid-uuid',
            'blocked_reason': 'Test'
        }

    # =====================================
    # TESTS PARA validate_data
    # =====================================
    
    def test_validate_data_with_valid_data(self):
        """Test validación exitosa con datos válidos"""
        errors = BlacklistCreateService.validate_data(self.valid_data)
        self.assertEqual(errors, [])
    
    def test_validate_data_with_none(self):
        """Test validación cuando data es None"""
        errors = BlacklistCreateService.validate_data(None)
        self.assertEqual(errors, ['No se proporcionaron datos'])
    
    def test_validate_data_with_empty_dict(self):
        """Test validación con diccionario vacío - también es falsy en Python"""
        errors = BlacklistCreateService.validate_data({})
        self.assertEqual(errors, ['No se proporcionaron datos'])
    
    def test_validate_data_missing_email(self):
        """Test validación cuando falta el email"""
        errors = BlacklistCreateService.validate_data(self.invalid_data_no_email)
        self.assertIn('El campo email es requerido', errors)
    
    def test_validate_data_empty_email(self):
        """Test validación cuando el email está vacío"""
        data = self.valid_data.copy()
        data['email'] = ''
        errors = BlacklistCreateService.validate_data(data)
        self.assertIn('El campo email es requerido', errors)
    
    def test_validate_data_missing_app_uuid(self):
        """Test validación cuando falta app_uuid"""
        data = self.valid_data.copy()
        del data['app_uuid']
        errors = BlacklistCreateService.validate_data(data)
        self.assertIn('El campo app_uuid es requerido', errors)
    
    def test_validate_data_missing_blocked_reason(self):
        """Test validación cuando falta blocked_reason - no se valida en el servicio actual"""
        data = self.valid_data.copy()
        del data['blocked_reason']
        errors = BlacklistCreateService.validate_data(data)
        # El servicio actual no valida blocked_reason, por lo que no debe haber errores adicionales
        self.assertEqual(errors, [])
    
    def test_validate_data_invalid_uuid(self):
        """Test validación con UUID inválido"""
        errors = BlacklistCreateService.validate_data(self.invalid_data_bad_uuid)
        self.assertIn('El app_uuid debe ser un UUID válido', errors)
    
    def test_validate_data_multiple_errors(self):
        """Test validación con múltiples errores"""
        invalid_data = {
            'email': '',
            'app_uuid': 'invalid-uuid',
            'blocked_reason': ''  # Este campo no se valida en el servicio actual
        }
        errors = BlacklistCreateService.validate_data(invalid_data)
        self.assertGreater(len(errors), 1)
        self.assertIn('El campo email es requerido', errors)
        self.assertIn('El app_uuid debe ser un UUID válido', errors)
        # No validamos blocked_reason en la implementación actual

    # =====================================
    # TESTS PARA email_exists
    # =====================================
    
    @patch('app.services.blacklist_create_service.Blacklist')
    def test_email_exists_true(self, mock_blacklist):
        """Test cuando el email ya existe"""
        # Mock de la consulta que retorna un objeto (email existe)
        mock_blacklist.query.filter_by.return_value.first.return_value = Mock()
        
        result = BlacklistCreateService.email_exists('test@ejemplo.com')
        self.assertTrue(result)
        mock_blacklist.query.filter_by.assert_called_once_with(email='test@ejemplo.com')
    
    @patch('app.services.blacklist_create_service.Blacklist')
    def test_email_exists_false(self, mock_blacklist):
        """Test cuando el email no existe"""
        # Mock de la consulta que retorna None (email no existe)
        mock_blacklist.query.filter_by.return_value.first.return_value = None
        
        result = BlacklistCreateService.email_exists('nuevo@ejemplo.com')
        self.assertFalse(result)
        mock_blacklist.query.filter_by.assert_called_once_with(email='nuevo@ejemplo.com')

    # =====================================
    # TESTS PARA get_client_ip
    # =====================================
    
    def test_get_client_ip_with_x_forwarded_for(self):
        """Test obtención de IP desde X-Forwarded-For"""
        with self.app.test_request_context(headers={'X-Forwarded-For': '192.168.1.100, 10.0.0.1'}):
            ip = BlacklistCreateService.get_client_ip()
            self.assertEqual(ip, '192.168.1.100')
    
    def test_get_client_ip_with_x_real_ip(self):
        """Test obtención de IP desde X-Real-IP"""
        with self.app.test_request_context(headers={'X-Real-IP': '203.0.113.50'}):
            ip = BlacklistCreateService.get_client_ip()
            self.assertEqual(ip, '203.0.113.50')
    
    def test_get_client_ip_with_cloudflare(self):
        """Test obtención de IP desde Cloudflare"""
        with self.app.test_request_context(headers={'CF-Connecting-IP': '198.51.100.25'}):
            ip = BlacklistCreateService.get_client_ip()
            self.assertEqual(ip, '198.51.100.25')
    
    def test_get_client_ip_fallback_to_remote_addr(self):
        """Test fallback a REMOTE_ADDR cuando no hay headers"""
        with self.app.test_request_context(environ_base={'REMOTE_ADDR': '127.0.0.1'}):
            ip = BlacklistCreateService.get_client_ip()
            self.assertEqual(ip, '127.0.0.1')
    
    def test_get_client_ip_unknown_fallback(self):
        """Test fallback a 'unknown' cuando no hay IP disponible"""
        with self.app.test_request_context():
            ip = BlacklistCreateService.get_client_ip()
            self.assertEqual(ip, 'unknown')

    # =====================================
    # TESTS PARA create_blacklist_item
    # =====================================
    
    @patch('app.services.blacklist_create_service.db')
    @patch('app.services.blacklist_create_service.BlacklistCreateService.get_client_ip')
    @patch('app.services.blacklist_create_service.Blacklist')
    def test_create_blacklist_item_success(self, mock_blacklist_class, mock_get_ip, mock_db):
        """Test creación exitosa de elemento en blacklist"""
        # Configurar mocks
        mock_get_ip.return_value = '192.168.1.100'
        mock_blacklist_instance = Mock()
        mock_blacklist_class.return_value = mock_blacklist_instance
        
        # Ejecutar el método
        result, error = BlacklistCreateService.create_blacklist_item(
            'test@ejemplo.com',
            str(uuid.uuid4()),
            'Test reason'
        )
        
        # Verificaciones
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        mock_db.session.add.assert_called_once_with(mock_blacklist_instance)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.blacklist_create_service.db')
    @patch('app.services.blacklist_create_service.BlacklistCreateService.get_client_ip')
    @patch('app.services.blacklist_create_service.Blacklist')
    def test_create_blacklist_item_integrity_error(self, mock_blacklist_class, mock_get_ip, mock_db):
        """Test manejo de IntegrityError"""
        # Configurar mocks
        mock_get_ip.return_value = '192.168.1.100'
        mock_blacklist_instance = Mock()
        mock_blacklist_class.return_value = mock_blacklist_instance
        mock_db.session.commit.side_effect = IntegrityError("test", "test", "test")
        
        # Ejecutar el método
        result, error = BlacklistCreateService.create_blacklist_item(
            'test@ejemplo.com',
            str(uuid.uuid4()),
            'Test reason'
        )
        
        # Verificaciones
        self.assertIsNone(result)
        self.assertEqual(error, 'Error de integridad en la base de datos')
        mock_db.session.rollback.assert_called_once()
    
    @patch('app.services.blacklist_create_service.db')
    @patch('app.services.blacklist_create_service.BlacklistCreateService.get_client_ip')
    @patch('app.services.blacklist_create_service.Blacklist')
    def test_create_blacklist_item_general_exception(self, mock_blacklist_class, mock_get_ip, mock_db):
        """Test manejo de excepciones generales"""
        # Configurar mocks
        mock_get_ip.return_value = '192.168.1.100'
        mock_blacklist_instance = Mock()
        mock_blacklist_class.return_value = mock_blacklist_instance
        mock_db.session.commit.side_effect = Exception("Error de prueba")
        
        # Ejecutar el método
        result, error = BlacklistCreateService.create_blacklist_item(
            'test@ejemplo.com',
            str(uuid.uuid4()),
            'Test reason'
        )
        
        # Verificaciones
        self.assertIsNone(result)
        self.assertIn('Error interno del servidor', error)
        mock_db.session.rollback.assert_called_once()

    # =====================================
    # TESTS PARA process_create_request (MÉTODO PRINCIPAL)
    # =====================================
    
    def test_process_create_request_success(self):
        """Test procesamiento exitoso de petición"""
        with patch.object(BlacklistCreateService, 'validate_data', return_value=[]), \
             patch.object(BlacklistCreateService, 'email_exists', return_value=False), \
             patch.object(BlacklistCreateService, 'create_blacklist_item') as mock_create:
            
            # Configurar mock
            mock_blacklist = Mock()
            mock_create.return_value = (mock_blacklist, None)
            
            # Ejecutar
            result = BlacklistCreateService.process_create_request(self.valid_data)
            
            # Verificaciones
            self.assertTrue(result['success'])
            self.assertEqual(result['status_code'], 200)
            self.assertEqual(result['message'], 'Email agregado a la lista negra exitosamente')
            self.assertEqual(result['data'], mock_blacklist)
    
    def test_process_create_request_validation_errors(self):
        """Test procesamiento con errores de validación"""
        with patch.object(BlacklistCreateService, 'validate_data', 
                         return_value=['El campo email es requerido']):
            
            result = BlacklistCreateService.process_create_request({})
            
            self.assertFalse(result['success'])
            self.assertEqual(result['status_code'], 400)
            self.assertEqual(result['errors'], ['El campo email es requerido'])
    
    def test_process_create_request_email_exists(self):
        """Test procesamiento cuando el email ya existe"""
        with patch.object(BlacklistCreateService, 'validate_data', return_value=[]), \
             patch.object(BlacklistCreateService, 'email_exists', return_value=True):
            
            result = BlacklistCreateService.process_create_request(self.valid_data)
            
            self.assertFalse(result['success'])
            self.assertEqual(result['status_code'], 409)
            self.assertEqual(result['errors'], ['El email ya está en la lista negra'])
    
    def test_process_create_request_creation_error(self):
        """Test procesamiento con error en la creación"""
        with patch.object(BlacklistCreateService, 'validate_data', return_value=[]), \
             patch.object(BlacklistCreateService, 'email_exists', return_value=False), \
             patch.object(BlacklistCreateService, 'create_blacklist_item', 
                         return_value=(None, 'Error de base de datos')):
            
            result = BlacklistCreateService.process_create_request(self.valid_data)
            
            self.assertFalse(result['success'])
            self.assertEqual(result['status_code'], 500)
            self.assertEqual(result['errors'], ['Error de base de datos'])

    # =====================================
    # TESTS DE INTEGRACIÓN
    # =====================================
    
    def test_integration_full_flow_success(self):
        """Test de integración: flujo completo exitoso"""
        with patch('app.services.blacklist_create_service.db'), \
             patch('app.services.blacklist_create_service.Blacklist') as mock_blacklist_class:
            
            # Configurar mocks
            mock_blacklist_class.query.filter_by.return_value.first.return_value = None
            mock_instance = Mock()
            mock_instance.email = self.valid_data['email']
            mock_instance.app_uuid = self.valid_data['app_uuid']
            mock_instance.blocked_reason = self.valid_data['blocked_reason']
            mock_instance.ip_address = '127.0.0.1'
            mock_blacklist_class.return_value = mock_instance
            
            with self.app.test_request_context():
                result = BlacklistCreateService.process_create_request(self.valid_data)
            
            # Verificaciones
            self.assertTrue(result['success'])
            self.assertEqual(result['status_code'], 201)
            self.assertIsNotNone(result['data'])


if __name__ == '__main__':
    unittest.main()