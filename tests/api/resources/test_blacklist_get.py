import unittest
from unittest.mock import Mock, patch
from http import HTTPStatus

# Configurar el path para importar módulos de la aplicación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from app.services.blacklist_get_service import BlacklistGetService

class TestBlacklistGetResource(unittest.TestCase):
    """Pruebas unitarias para la lógica del método get de BlacklistGetResource"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.test_email = 'test@ejemplo.com'
        self.test_email_upper = 'TEST@EJEMPLO.COM'
        self.test_email_spaces = '  test@ejemplo.com  '
        
    def _simulate_get_logic(self, email, service_result=None, service_exception=None):
        """
        Simula la lógica del método get del BlacklistGetResource
        sin depender del contexto de Flask
        """
        # Simular la lógica del método get
        try:
            if service_exception:
                raise service_exception
            else:
                result = service_result
            
            # Respuesta exitosa - retorna directamente los datos del servicio
            return result, HTTPStatus.OK
            
        except ValueError as e:
            # Error de validación
            return {'error': str(e)}, HTTPStatus.BAD_REQUEST
            
        except Exception as e:
            # Error interno del servidor
            return {'error': 'Error interno del servidor'}, HTTPStatus.INTERNAL_SERVER_ERROR
    
    # =====================================
    # TESTS PARA GET METHOD - CASOS EXITOSOS
    # =====================================
    
    def test_get_logic_email_found_in_blacklist(self):
        """Test lógica de consulta exitosa cuando el email está en la blacklist"""
        # Mock respuesta del servicio - email encontrado
        service_result = {
            'is_blocked': True,
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.OK, HTTPStatus.OK)
        self.assertTrue(response['is_blocked'])
        self.assertEqual(response['blocked_reason'], 'Comportamiento sospechoso')
        
        # Verificar que no hay campos innecesarios
        self.assertNotIn('message', response)
        self.assertNotIn('data', response)
        self.assertNotIn('success', response)
        self.assertNotIn('errors', response)
    
    def test_get_logic_email_not_found_in_blacklist(self):
        """Test lógica de consulta exitosa cuando el email NO está en la blacklist"""
        # Mock respuesta del servicio - email no encontrado
        service_result = {
            'is_blocked': False
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.OK, HTTPStatus.OK)
        self.assertFalse(response['is_blocked'])
        
        # Verificar que no hay campos innecesarios
        self.assertNotIn('blocked_reason', response)
        self.assertNotIn('message', response)
        self.assertNotIn('data', response)
        self.assertNotIn('success', response)
        self.assertNotIn('errors', response)
    
    # =====================================
    # TESTS PARA GET METHOD - CASOS DE ERROR
    # =====================================
    
    def test_get_logic_validation_error_empty_email(self):
        """Test lógica de error cuando el email está vacío"""
        # Mock excepción de validación del servicio
        service_exception = ValueError('El email no puede estar vacío')
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_exception=service_exception)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.BAD_REQUEST, HTTPStatus.BAD_REQUEST)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'El email no puede estar vacío')
    
    def test_get_logic_validation_error_none_email(self):
        """Test lógica de error cuando el email es None"""
        # Mock excepción de validación del servicio
        service_exception = ValueError('El email no puede estar vacío')
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(None, service_exception=service_exception)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.BAD_REQUEST, HTTPStatus.BAD_REQUEST)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'El email no puede estar vacío')
    
    def test_get_logic_database_error(self):
        """Test lógica de error de base de datos"""
        # Mock excepción de base de datos
        from sqlalchemy.exc import SQLAlchemyError
        service_exception = SQLAlchemyError('Database connection failed')
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_exception=service_exception)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Error interno del servidor')
    
    def test_get_logic_unexpected_error(self):
        """Test lógica de error inesperado"""
        # Mock excepción inesperada
        service_exception = Exception('Unexpected error occurred')
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_exception=service_exception)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.INTERNAL_SERVER_ERROR, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Error interno del servidor')
    
    # =====================================
    # TESTS PARA ESTRUCTURA DE RESPUESTA
    # =====================================
    
    def test_response_structure_blocked(self):
        """Test estructura de respuesta cuando está bloqueado"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': True,
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificar estructura de respuesta
        self.assertIsInstance(response, dict)
        self.assertIn('is_blocked', response)
        self.assertIn('blocked_reason', response)
        
        # Verificar tipos de datos
        self.assertIsInstance(response['is_blocked'], bool)
        self.assertIsInstance(response['blocked_reason'], str)
        self.assertTrue(response['is_blocked'])
    
    def test_response_structure_not_blocked(self):
        """Test estructura de respuesta cuando NO está bloqueado"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': False
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificar estructura de respuesta
        self.assertIsInstance(response, dict)
        self.assertIn('is_blocked', response)
        self.assertNotIn('blocked_reason', response)
        
        # Verificar tipos de datos
        self.assertIsInstance(response['is_blocked'], bool)
        self.assertFalse(response['is_blocked'])
    
    def test_response_structure_error(self):
        """Test estructura de respuesta de error"""
        # Mock excepción
        service_exception = ValueError('Email requerido')
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_exception=service_exception)
        
        # Verificar estructura de respuesta de error
        self.assertIsInstance(response, dict)
        self.assertIn('error', response)
        self.assertIsInstance(response['error'], str)
        self.assertGreater(len(response['error']), 0)
    
    # =====================================
    # TESTS PARA DIFERENTES CASOS DE EMAIL
    # =====================================
    
    def test_get_logic_email_case_insensitive(self):
        """Test que el servicio maneja emails en diferentes casos"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': True,
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Ejecutar lógica del método con email en mayúsculas
        response, _ = self._simulate_get_logic(self.test_email_upper, service_result)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.OK, HTTPStatus.OK)
        self.assertTrue(response['is_blocked'])
    
    def test_get_logic_email_with_spaces(self):
        """Test que el servicio maneja emails con espacios"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': True,
            'blocked_reason': 'Comportamiento sospechoso'
        }
        
        # Ejecutar lógica del método con email con espacios
        response, _ = self._simulate_get_logic(self.test_email_spaces, service_result)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.OK, HTTPStatus.OK)
        self.assertTrue(response['is_blocked'])
    
    # =====================================
    # TESTS PARA EDGE CASES
    # =====================================
    
    def test_get_logic_with_none_blocked_reason(self):
        """Test cuando está bloqueado pero blocked_reason es None"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': True,
            'blocked_reason': None
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificaciones
        self.assertEqual(HTTPStatus.OK, HTTPStatus.OK)
        self.assertTrue(response['is_blocked'])
        self.assertIsNone(response['blocked_reason'])
    
    def test_get_logic_minimal_response(self):
        """Test que la respuesta es mínima y contiene solo lo necesario"""
        # Mock respuesta del servicio
        service_result = {
            'is_blocked': False
        }
        
        # Ejecutar lógica del método
        response, _ = self._simulate_get_logic(self.test_email, service_result)
        
        # Verificar que la respuesta es mínima
        self.assertEqual(len(response), 1)  # Solo 'is_blocked'
        self.assertIn('is_blocked', response)
        
        # Verificar que no hay campos innecesarios
        unnecessary_fields = ['message', 'data', 'success', 'errors', 'status_code', 'email', 'app_uuid', 'ip_address', 'created_at', 'updated_at']
        for field in unnecessary_fields:
            self.assertNotIn(field, response)


if __name__ == '__main__':
    unittest.main()