from datetime import datetime
from typing import Dict, Any, List


class ControlService:
    """In-memory control queue for IoT devices.

    Keeps the latest desired state; devices poll and apply.
    ESP32 polls GET /api/control?device=esp32-1 and expects an array of controls.
    """

    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {}

    def _default_state(self) -> Dict[str, Any]:
        """Default state structure (internal representation)"""
        return {
            "controls": [
                {"control": "led1", "value": False},
                {"control": "led2", "value": False},
                {"control": "door_open", "value": False},
                {"control": "door_angle", "value": 0},
            ],
            "updated_at": datetime.utcnow().isoformat(),
        }

    def set_controls(self, device: str, payload: Dict[str, Any]):
        """Store controls from frontend and return full state for response"""
        state = self._state.get(device) or self._default_state()
        for key in ["led1", "led2", "door_open", "door_angle"]:
            if key in payload:
                for item in state["controls"]:
                    if item["control"] == key:
                        item["value"] = payload[key]
        state["updated_at"] = datetime.utcnow().isoformat()
        self._state[device] = state
        return state

    def get_controls(self, device: str) -> List[Dict[str, Any]]:
        """
        Return controls as ARRAY for ESP32 polling.
        
        ESP32 parser expects:
        [
          {"control": "led1", "value": false},
          {"control": "led2", "value": false},
          ...
        ]
        
        Returns:
            List: Empty list if device not yet initialized, array of controls otherwise.
        """
        state = self._state.get(device)
        if not state:
            # First time device polls - return empty array
            return []
        # Return only the controls array (ESP32 will iterate and parse)
        return state.get("controls", [])
