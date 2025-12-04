#!/usr/bin/env python3
"""
Script para verificar la comunicacion ESP32 <-> Backend.

Ejecutar:
    python test_communication.py
"""

from __future__ import annotations

import io
import json
import sys
from datetime import datetime

# Asegurar salida UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def parse_bool_control(json_str: str, control_name: str):
    """Simula parseBoolControl del firmware (busca substrings sin parsear JSON)."""

    pattern = f'"control":"{control_name}"'
    pos = json_str.find(pattern)
    if pos < 0:
        return None

    val_pos = json_str.find('"value":', pos)
    if val_pos < 0:
        return None

    search_area = json_str[val_pos : val_pos + 30]
    false_pos = search_area.find("false")
    true_pos = search_area.find("true")

    if false_pos >= 0 and (true_pos < 0 or false_pos < true_pos):
        return False
    if true_pos >= 0:
        return True
    return None


def test_esp32_parser():
    print("=" * 70)
    print("TEST 1: Parser del ESP32 con formato array")
    print("=" * 70)

    json_response = (
        '[{"control":"led1","value":true},'
        '{"control":"led2","value":false},'
        '{"control":"door_open","value":true},'
        '{"control":"door_angle","value":90}]'
    )

    print("\nRespuesta del backend:")
    print(json_response)

    led1 = parse_bool_control(json_response, "led1")
    led2 = parse_bool_control(json_response, "led2")
    door_open = parse_bool_control(json_response, "door_open")

    print(f"\nParsing led1 -> {led1} (esperado: True)")
    print(f"Parsing led2 -> {led2} (esperado: False)")
    print(f"Parsing door_open -> {door_open} (esperado: True)")

    success = led1 is True and led2 is False and door_open is True
    print("\nRESULTADO:", "PASS" if success else "FAIL")
    return success


def test_control_service():
    print("=" * 70)
    print("TEST 2: ControlService retorna array para el ESP32")
    print("=" * 70)

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

    result1 = service.get_controls(device)
    print(f"\nGET inicial -> {json.dumps(result1)} (esperado: [])")
    pass1 = result1 == []
    print("OK" if pass1 else "FAIL")

    payload = {"device": device, "led1": True, "led2": False, "door_open": True, "door_angle": 90}
    state = service.set_controls(device, payload)
    print(f"\nPOST set_controls -> {json.dumps(payload)}")
    pass2 = state is not None
    print("OK" if pass2 else "FAIL")

    result3 = service.get_controls(device)
    expected = [
        {"control": "led1", "value": True},
        {"control": "led2", "value": False},
        {"control": "door_open", "value": True},
        {"control": "door_angle", "value": 90},
    ]
    print(f"\nGET despues de POST -> {json.dumps(result3)}")
    print(f"Esperado            -> {json.dumps(expected)}")
    pass3 = result3 == expected
    print("OK" if pass3 else "FAIL")

    success = pass1 and pass2 and pass3
    print("\nRESULTADO:", "PASS" if success else "FAIL")
    return success


def main():
    print("\nVERIFICACION DE COMUNICACION ESP32 <-> BACKEND\n")
    results = []

    try:
        results.append(test_esp32_parser())
    except Exception as exc:  # pragma: no cover - helper script
        print(f"ERROR en test_esp32_parser: {exc}")
        results.append(False)

    try:
        results.append(test_control_service())
    except Exception as exc:  # pragma: no cover - helper script
        print(f"ERROR en test_control_service: {exc}")
        results.append(False)

    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Tests pasados: {passed}/{total}")

    if all(results):
        print("TODO OK - La comunicacion deberia funcionar.")
        return 0

    print("Algun test fallo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
