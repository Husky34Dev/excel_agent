"""
Script para probar las validaciones de seguridad del sandbox
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.executor.sandbox_executor import SandboxExecutor, SecurityError

def test_security_validation():
    """Probar las validaciones de seguridad"""
    
    print("🛡️ PROBANDO VALIDACIONES DE SEGURIDAD")
    print("=" * 60)
    
    # Crear ejecutor
    executor = SandboxExecutor()
    
    # Casos de prueba
    test_cases = [
        # ✅ CÓDIGO SEGURO
        {
            "name": "✅ Código pandas válido",
            "code": """
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3]})
print(df.shape)
""",
            "should_pass": True
        },
        
        # ❌ IMPORTS PROHIBIDOS
        {
            "name": "❌ Import os prohibido",
            "code": """
import os
os.system('ls')
""",
            "should_pass": False
        },
        
        {
            "name": "❌ Import requests prohibido",
            "code": """
import requests
requests.get('http://evil.com')
""",
            "should_pass": False
        },
        
        # ❌ FUNCIONES PELIGROSAS
        {
            "name": "❌ Función exec() prohibida",
            "code": """
import pandas as pd
exec("print('hacked')")
""",
            "should_pass": False
        },
        
        {
            "name": "❌ Función open() prohibida",
            "code": """
import pandas as pd
open('/etc/passwd', 'r')
""",
            "should_pass": False
        },
        
        # ✅ CÓDIGO COMPLEJO PERO SEGURO
        {
            "name": "✅ Análisis pandas complejo",
            "code": """
import pandas as pd
import numpy as np
from datetime import datetime

df = pd.DataFrame({
    'fecha': pd.date_range('2024-01-01', periods=100),
    'valores': np.random.randn(100)
})

resultado = df.groupby(df['fecha'].dt.month)['valores'].mean()
print(resultado.head())
""",
            "should_pass": True
        },
        
        # ❌ ACCESO A ATRIBUTOS PRIVADOS
        {
            "name": "❌ Acceso a __dict__ prohibido",
            "code": """
import pandas as pd
df = pd.DataFrame({'a': [1, 2]})
print(df.__dict__)
""",
            "should_pass": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 50)
        
        try:
            # Probar validación
            executor.validate_code(test['code'])
            
            if test['should_pass']:
                print("✅ CORRECTO: Código válido pasó la validación")
                passed += 1
            else:
                print("❌ ERROR: Código malicioso NO fue detectado")
                failed += 1
                
        except SecurityError as e:
            if not test['should_pass']:
                print(f"✅ CORRECTO: Código malicioso detectado - {e}")
                passed += 1
            else:
                print(f"❌ ERROR: Código válido fue rechazado - {e}")
                failed += 1
        except Exception as e:
            print(f"💥 ERROR INESPERADO: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN DE PRUEBAS:")
    print(f"✅ Pasaron: {passed}")
    print(f"❌ Fallaron: {failed}")
    print(f"📈 Éxito: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 ¡TODAS LAS VALIDACIONES FUNCIONAN CORRECTAMENTE!")
    else:
        print("⚠️ Algunas validaciones fallaron - revisar implementación")

if __name__ == "__main__":
    test_security_validation()
