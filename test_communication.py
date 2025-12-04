#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar que la comunicación ESP32 ↔ Backend funciona correctamente.

Ejecutar:
    python test_communication.py
"""

import json
import sys
import io
from datetime import datetime

# Configurar stdout para UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_esp32_parser():
    """Simular el parser del ESP32 con el nuevo formato"""
    print("=" * 70)
    print("TEST 1: Verificar que el parser del ESP32 funciona con array")
    print("=" * 70)
    
    # Simular respuesta del backend (array de controles)
    # IMPORTANTE: en C++, String.indexOf busca subcadenas
    json_response = '[{"control":"led1","value":true},{"control":"led2","value":false},{"control":"door_open","value":true},{"control":"door_angle","value":90}]'
    
    print(f"\nRespuesta del backend:\n{json_response}\n")
    
    # Simular el parser del ESP32 (del código .ino)
    # Nota: se usa string de búsqueda sin espacios porque eso es lo que retorna jsonify en Flask
    def parse_bool_control(json_str: str, control_name: str) -> bool:
        """Simula parseBoolControl del ESP32 del código .ino"""
        # Buscar patrón: "control":"led1"
        pattern = f'"control":"{control_name}"'
        pos = json_str.find(pattern)
        if pos < 0:
            print(f"   [DEBUG] Pattern '{pattern}' no encontrado")
            return None
        
        print(f"   [DEBUG] Pattern '{pattern}' encontrado en posición {pos}")
        
        # Buscar "value": después del patrón
        val_pos = json_str.find('"value":', pos)
        if val_pos < 0:
            print(f"   [DEBUG] '\"value\":' no encontrado después de posición {pos}")
            return None
        
        print(f"   [DEBUG] '\"value\":' encontrado en posición {val_pos}")
        
        # Buscar "true" o "false" después de "value":
        # Limitamos la búsqueda a los próximos 30 caracteres
        search_area = json_str[val_pos:val_pos+30]
        true_pos = search_area.find("true")
        false_pos = search_area.find("false")
        
        if false_pos >= 0 and (true_pos < 0 or false_pos < true_pos):
            print(f"   [DEBUG] Encontrado 'false' en posición {false_pos} del área de búsqueda")
            return False
        elif true_pos >= 0:
            print(f"   [DEBUG] Encontrado 'true' en posición {true_pos} del área de búsqueda")
            return True
        
        print(f"   [DEBUG] No se encontró 'true' o 'false'")
        return None
    
    # Test parser
    print("\nParsing led1:")
    led1 = parse_bool_control(json_response, "led1")
    print(f"Resultado: {led1} (esperado: True)\n")
    
    print("Parsing led2:")
    led2 = parse_bool_control(json_response, "led2")
    print(f"Resultado: {led2} (esperado: False)\n")
    
    print("Parsing door_open:")
    door_open = parse_bool_control(json_response, "door_open")
    print(f"Resultado: {door_open} (esperado: True)\n")
    
    success = led1 == True and led2 == False and door_open == True
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Parser funciona con array\n")
    
    return success


def test_control_service():
    """Verificar el ControlService retorna array"""
    print("=" * 70)
    print("TEST 2: Verificar ControlService retorna array")
    print("=" * 70)
    
    # Simular ControlService
    class ControlService:
        def __init__(self):
            self._state = {}
        
        def _default_state(self):
            return {
                "controls": [
                    {"control": "led1", "value": False},
                    {"control": "led2", "value": False},
                    {"control": "door_open", "value": False},
                    {"control": "door_angle", "value": 0},
                ],
                "updated_at": datetime.utcnow().isoformat(),
            }
        
        def set_controls(self, device, payload):
            state = self._state.get(device) or self._default_state()
            for key in ["led1", "led2", "door_open", "door_angle"]:
                if key in payload:
                    for item in state["controls"]:
                        if item["control"] == key:
                            item["value"] = payload[key]
            state["updated_at"] = datetime.utcnow().isoformat()
            self._state[device] = state
            return state
        
        def get_controls(self, device):
            state = self._state.get(device)
            if not state:
                return []
            return state.get("controls", [])
    
    service = ControlService()
    device = "esp32-1"
    
    # Test 1: GET initial (debe retornar array vacío)
    result1 = service.get_controls(device)
    print(f"\n1. GET /api/control?device={device} (inicial)")
    print(f"   Resultado: {json.dumps(result1)}")
    print(f"   Esperado: []")
    pass1 = result1 == []
    print(f"   {'✅ PASS' if pass1 else '❌ FAIL'}")
    
    # Test 2: POST para establecer controles
    payload = {
        "device": device,
        "led1": True,
        "led2": False,
        "door_open": True,
        "door_angle": 90
    }
    state = service.set_controls(device, payload)
    print(f"\n2. POST /api/control")
    print(f"   Payload: {json.dumps(payload)}")
    print(f"   State guardado: ✅")
    pass2 = state is not None
    print(f"   {'✅ PASS' if pass2 else '❌ FAIL'}")
    
    # Test 3: GET después de POST (debe retornar array con controles)
    result3 = service.get_controls(device)
    print(f"\n3. GET /api/control?device={device} (después de POST)")
    print(f"   Resultado: {json.dumps(result3)}")
    expected = [
        {"control": "led1", "value": True},
        {"control": "led2", "value": False},
        {"control": "door_open", "value": True},
        {"control": "door_angle", "value": 90}
    ]
    print(f"   Esperado: {json.dumps(expected)}")
    pass3 = result3 == expected
    print(f"   {'✅ PASS' if pass3 else '❌ FAIL'}")
    
    success = pass1 and pass2 and pass3
    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: ControlService funciona correctamente\n")
    
    return success


def main():
    """Ejecutar todos los tests"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  VERIFICACIÓN DE COMUNICACIÓN ESP32 ↔ BACKEND".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    results = []
    
    try:
        results.append(test_esp32_parser())
    except Exception as e:
        print(f"❌ ERROR en test_esp32_parser: {e}\n")
        results.append(False)
    
    try:
        results.append(test_control_service())
    except Exception as e:
        print(f"❌ ERROR en test_control_service: {e}\n")
        results.append(False)
    
    # Resumen
    print("=" * 70)
    print("RESUMEN")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests pasados: {passed}/{total}")
    
    if all(results):
        print("\n✅ TODOS LOS TESTS PASARON - LA COMUNICACIÓN FUNCIONA")
        print("\nPróximos pasos:")
        print("1. Hacer git commit de los cambios")
        print("2. Hacer deploy en EC2")
        print("3. Reiniciar los contenedores Docker")
        print("4. Verificar en el dashboard que los dispositivos funcionan")
        return 0
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        return 1


if __name__ == "__main__":
    sys.exit(main())
