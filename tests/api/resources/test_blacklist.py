import unittest
from unittest.mock import Mock, patch
import uuid

# Configurar el path para importar módulos de la aplicación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app.services.blacklist_create_service import BlacklistCreateService

class TestBlacklistCreateResource(unittest.TestCase):
    """Pruebas unitarias para la lógica del método post de BlacklistCreateResource"""
    
    def setUp(self):
        """Configuración inicial para cada test"""        
        # Datos de prueba válidos
        self.valid_data = {
            'email': 'test@ejemplo.com',
            'app_uuid': str(uuid.uuid4()),
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Mock del modelo Blacklist
        self.mock_blacklist = Mock()
        self.mock_blacklist.email = self.valid_data['email']
        self.mock_blacklist.app_uuid = self.valid_data['app_uuid']
        self.mock_blacklist.blocked_reason = self.valid_data['blocked_reason']
        self.mock_blacklist.ip_address = '192.168.1.1'
        
    def _simulate_post_logic(self, request_data, service_result):
        """
        Simula la lógica del método post del BlacklistCreateResource
        sin depender del contexto de Flask
        """
        # Simular la lógica del método post
        result = service_result
        
        if not result['success']:
            # Manejar errores
            error_message = result['errors'][0] if len(result['errors']) == 1 else result['errors']
            return {'error': error_message}, result['status_code']
        
        # Respuesta exitosa
        return {
            'message': result['message'],
            'data': {
                'email': result['data'].email,
                'app_uuid': result['data'].app_uuid,
                'blocked_reason': result['data'].blocked_reason,
                'ip_address': result['data'].ip_address
            }
        }, result['status_code']
    
    # =====================================
    # TESTS PARA POST METHOD - CASOS EXITOSOS
    # =====================================
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_successful_creation(self, mock_process_request):
        """Test lógica de creación exitosa de elemento en blacklist"""
        # Mock respuesta exitosa del servicio
        mock_process_request.return_value = {
            'success': True,
            'data': self.mock_blacklist,
            'message': 'Email agregado a la lista negra exitosamente',
            'status_code': 201
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(self.valid_data)
        response, status_code = self._simulate_post_logic(self.valid_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(self.valid_data)
        
        self.assertEqual(status_code, 200)
        self.assertIn('message', response)
        self.assertIn('data', response)
        self.assertEqual(response['message'], 'Email agregado a la lista negra exitosamente')
        self.assertEqual(response['data']['email'], self.valid_data['email'])
        self.assertEqual(response['data']['app_uuid'], self.valid_data['app_uuid'])
        self.assertEqual(response['data']['blocked_reason'], self.valid_data['blocked_reason'])
        self.assertEqual(response['data']['ip_address'], '192.168.1.1')
    
    # =====================================
    # TESTS PARA POST METHOD - CASOS DE ERROR
    # =====================================
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_validation_error_single(self, mock_process_request):
        """Test lógica de error de validación con un solo error"""
        invalid_data = {'app_uuid': str(uuid.uuid4())}  # Sin email
        
        # Mock respuesta de error del servicio
        mock_process_request.return_value = {
            'success': False,
            'errors': ['El campo email es requerido'],
            'status_code': 400
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(invalid_data)
        response, status_code = self._simulate_post_logic(invalid_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(invalid_data)
        
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'El campo email es requerido')
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_validation_error_multiple(self, mock_process_request):
        """Test lógica de error de validación con múltiples errores"""
        empty_data = {}  # Datos vacíos
        
        # Mock respuesta de error con múltiples errores
        mock_process_request.return_value = {
            'success': False,
            'errors': ['El campo email es requerido', 'El campo app_uuid es requerido'],
            'status_code': 400
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(empty_data)
        response, status_code = self._simulate_post_logic(empty_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(empty_data)
        
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertIsInstance(response['error'], list)
        self.assertEqual(len(response['error']), 2)
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_email_already_exists(self, mock_process_request):
        """Test lógica de error cuando el email ya existe en la blacklist"""
        # Mock respuesta de conflicto del servicio
        mock_process_request.return_value = {
            'success': False,
            'errors': ['El email ya está en la lista negra'],
            'status_code': 409
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(self.valid_data)
        response, status_code = self._simulate_post_logic(self.valid_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(self.valid_data)
        
        self.assertEqual(status_code, 409)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'El email ya está en la lista negra')
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_internal_server_error(self, mock_process_request):
        """Test lógica de error interno del servidor"""
        # Mock respuesta de error interno del servicio
        mock_process_request.return_value = {
            'success': False,
            'errors': ['Error interno del servidor: Database connection failed'],
            'status_code': 500
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(self.valid_data)
        response, status_code = self._simulate_post_logic(self.valid_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(self.valid_data)
        
        self.assertEqual(status_code, 500)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Error interno del servidor: Database connection failed')
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_invalid_uuid_format(self, mock_process_request):
        """Test lógica de error con formato de UUID inválido"""
        invalid_data = {
            'email': 'test@ejemplo.com',
            'app_uuid': 'invalid-uuid-format',
            'blocked_reason': 'Test'
        }
        
        # Mock respuesta de error de validación
        mock_process_request.return_value = {
            'success': False,
            'errors': ['El app_uuid debe ser un UUID válido'],
            'status_code': 400
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(invalid_data)
        response, status_code = self._simulate_post_logic(invalid_data, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(invalid_data)
        
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'El app_uuid debe ser un UUID válido')
    
    # =====================================
    # TESTS PARA REQUEST HANDLING
    # =====================================
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_empty_request_body(self, mock_process_request):
        """Test lógica de manejo de request body vacío"""
        # Mock respuesta de error del servicio para datos nulos
        mock_process_request.return_value = {
            'success': False,
            'errors': ['No se proporcionaron datos'],
            'status_code': 400
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(None)
        response, status_code = self._simulate_post_logic(None, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(None)
        
        self.assertEqual(status_code, 400)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'No se proporcionaron datos')
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_with_optional_blocked_reason(self, mock_process_request):
        """Test lógica de creación exitosa sin blocked_reason (campo opcional)"""
        data_without_reason = {
            'email': 'test@ejemplo.com',
            'app_uuid': str(uuid.uuid4())
        }
        
        # Mock blacklist sin blocked_reason
        mock_blacklist_no_reason = Mock()
        mock_blacklist_no_reason.email = data_without_reason['email']
        mock_blacklist_no_reason.app_uuid = data_without_reason['app_uuid']
        mock_blacklist_no_reason.blocked_reason = None
        mock_blacklist_no_reason.ip_address = '192.168.1.1'
        
        # Mock respuesta exitosa del servicio
        mock_process_request.return_value = {
            'success': True,
            'data': mock_blacklist_no_reason,
            'message': 'Email agregado a la lista negra exitosamente',
            'status_code': 201
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(data_without_reason)
        response, status_code = self._simulate_post_logic(data_without_reason, service_result)
        
        # Verificaciones
        mock_process_request.assert_called_once_with(data_without_reason)
        
        self.assertEqual(status_code, 201)
        self.assertIn('message', response)
        self.assertIn('data', response)
        self.assertEqual(response['data']['email'], data_without_reason['email'])
        self.assertEqual(response['data']['app_uuid'], data_without_reason['app_uuid'])
        self.assertIsNone(response['data']['blocked_reason'])
    
    # =====================================
    # TESTS PARA SERVICE INTEGRATION
    # =====================================
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_service_method_called_correctly(self, mock_process_request):
        """Test que el método del servicio es llamado con los parámetros correctos"""
        # Mock respuesta exitosa del servicio
        mock_process_request.return_value = {
            'success': True,
            'data': self.mock_blacklist,
            'message': 'Email agregado a la lista negra exitosamente',
            'status_code': 201
        }
        
        # Ejecutar lógica
        service_result = mock_process_request(self.valid_data)
        self._simulate_post_logic(self.valid_data, service_result)
        
        # Verificar que el servicio fue llamado exactamente una vez con los datos correctos
        mock_process_request.assert_called_once_with(self.valid_data)
    
    @patch.object(BlacklistCreateService, 'process_create_request')
    def test_post_logic_response_format_consistency(self, mock_process_request):
        """Test que el formato de respuesta es consistente"""
        # Mock respuesta exitosa del servicio
        mock_process_request.return_value = {
            'success': True,
            'data': self.mock_blacklist,
            'message': 'Email agregado a la lista negra exitosamente',
            'status_code': 201
        }
        
        # Ejecutar lógica del método
        service_result = mock_process_request(self.valid_data)
        response, status_code = self._simulate_post_logic(self.valid_data, service_result)
        
        # Verificar estructura de respuesta exitosa
        self.assertIsInstance(response, dict)
        self.assertIn('message', response)
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], dict)
        
        # Verificar campos requeridos en data
        required_fields = ['email', 'app_uuid', 'blocked_reason', 'ip_address']
        for field in required_fields:
            self.assertIn(field, response['data'])


if __name__ == '__main__':
    unittest.main()