# Solución: Sincronizar Comunicación ESP32 ↔ Backend

## Diagnóstico
El servidor en `44.222.106.109:8000` tiene un código **diferente** al del repositorio. 

**El código en el repositorio retorna:**
```json
{
  "controls": [{"control": "led1", "value": false}, ...],
  "updated_at": "..."
}
```

**El servidor real retorna:**
```json
[{"control":"led1","device":"esp32-1","time":"...","value":true}]
```

---

## Opción 1: Actualizar el repositorio para retornar ARRAY (Rápido)

**Cambiar en `app/services/control_service.py`:**

```python
def get_controls(self, device: str):
    state = self._state.get(device)
    if not state:
        return []  # Retornar array vacío (compatible con servidor real)
    
    # Convertir a formato array compatible con ESP32
    controls = state.get("controls", [])
    return controls  # Retornar solo el array
```

Esto hace que el ESP32 reciba:
```json
[
  {"control": "led1", "value": false},
  {"control": "led2", "value": false},
  ...
]
```

El parser del ESP32 busca `"control":"led1"` en el JSON, así que funcionará con un array.

---

## Opción 2: Actualizar el servidor para usar el código del repositorio (Correcto)

1. **Conectar a la EC2:**
   ```bash
   ssh ec2-user@44.222.106.109
   ```

2. **Acceder al código:**
   ```bash
   cd /ruta/a/icc-project
   ```

3. **Verificar si está en git:**
   ```bash
   git status
   ```

4. **Si tiene cambios sin commit:**
   ```bash
   git diff app/services/control_service.py
   git diff app/controllers/devices.py
   ```

5. **Actualizar con el código del repositorio:**
   ```bash
   git pull origin main
   docker-compose -f docker-compose.mysql.yml down
   docker build -t icc-app .
   docker-compose -f docker-compose.mysql.yml up -d
   ```

---

## Opción 3: Implementación Robusta con Persistencia en BD

**RECOMENDADO para producción**

Cambiar `app/services/control_service.py` para usar una tabla de BD:

```python
from app.repositories import ControlRepository

class ControlService:
    """Control de dispositivos con persistencia en BD"""

    def __init__(self, control_repo: ControlRepository | None = None):
        self.control_repo = control_repo or ControlRepository()

    def _default_state(self) -> Dict[str, Any]:
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
        # Guardar en BD
        state = self.control_repo.get_or_create(device)
        for key in ["led1", "led2", "door_open", "door_angle"]:
            if key in payload:
                state[key] = payload[key]
        state["updated_at"] = datetime.utcnow().isoformat()
        self.control_repo.save(device, state)
        return state

    def get_controls(self, device: str):
        # Leer de BD
        state = self.control_repo.get(device)
        if not state:
            return self._default_state()
        return state
```

Crear `app/repositories/control_repository.py`:

```python
from datetime import datetime
from typing import Dict, Any
from app import db

class DeviceControl(db.Model):
    __tablename__ = "device_controls"
    
    id = db.Column(db.BigInteger, primary_key=True)
    device_id = db.Column(db.String(255), nullable=False, unique=True)
    led1 = db.Column(db.Boolean, default=False)
    led2 = db.Column(db.Boolean, default=False)
    door_open = db.Column(db.Boolean, default=False)
    door_angle = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ControlRepository:
    def get(self, device_id: str):
        control = DeviceControl.query.filter_by(device_id=device_id).first()
        if not control:
            return None
        return {
            "controls": [
                {"control": "led1", "value": control.led1},
                {"control": "led2", "value": control.led2},
                {"control": "door_open", "value": control.door_open},
                {"control": "door_angle", "value": control.door_angle},
            ],
            "updated_at": control.updated_at.isoformat(),
        }
    
    def save(self, device_id: str, state: Dict[str, Any]):
        control = DeviceControl.query.filter_by(device_id=device_id).first()
        if not control:
            control = DeviceControl(device_id=device_id)
            db.session.add(control)
        
        # Actualizar valores
        for item in state.get("controls", []):
            control_name = item.get("control")
            value = item.get("value")
            if control_name == "led1":
                control.led1 = value
            elif control_name == "led2":
                control.led2 = value
            elif control_name == "door_open":
                control.door_open = value
            elif control_name == "door_angle":
                control.door_angle = value
        
        control.updated_at = datetime.utcnow()
        db.session.commit()
        return control
```

---

## Opción Elegida para Este Proyecto: **Opción 1**

Es la más rápida y no requiere cambios en la BD ni migraciones.

**Pasos:**

1. **Actualizar `app/services/control_service.py`:**

```python
from datetime import datetime
from typing import Dict, Any, List


class ControlService:
    """In-memory control queue for IoT devices.

    Keeps the latest desired state; devices poll and apply.
    """

    def __init__(self):
        self._state: Dict[str, Dict[str, Any]] = {}

    def _default_state(self) -> Dict[str, Any]:
        """Estado por defecto (para primera vez)"""
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
        """Retorna ARRAY de controles (compatible con servidor real)"""
        state = self._state.get(device)
        if not state:
            # Retornar array vacío para primera vez
            return []
        # Retornar solo el array de controles (sin "updated_at" en la respuesta)
        return state.get("controls", [])
    
    def get_controls_with_metadata(self, device: str) -> Dict[str, Any]:
        """Retorna controles con metadata (para otras apis)"""
        state = self._state.get(device) or self._default_state()
        return state
```

2. **Actualizar `app/controllers/devices.py` para retornar el array correctamente:**

```python
@devices_bp.get("/control")
def get_control():
    device_id = request.args.get("device", "esp32-1")
    state = control_service.get_controls(device_id)
    # Retornar como JSON array
    return jsonify(state)
```

Con esto:
- Primera consulta: `curl http://..../api/control?device=esp32-1` → `[]`
- Después de POST: `curl http://..../api/control?device=esp32-1` → `[{"control":"led1","value":true}...]`

---

## Verificación Final

Después de los cambios, probar:

```bash
# 1. GET inicial (debe retornar array vacío)
curl http://44.222.106.109:8000/api/control?device=esp32-1
# Resultado esperado: []

# 2. POST para establecer controles
curl -X POST http://44.222.106.109:8000/api/control \
  -H "Content-Type: application/json" \
  -d '{"device":"esp32-1","led1":true,"led2":false}'
# Resultado esperado: {"status":"queued","controls":{...}}

# 3. GET después de POST (debe retornar array con controles)
curl http://44.222.106.109:8000/api/control?device=esp32-1
# Resultado esperado: [{"control":"led1","value":true},...]

# 4. Verificar que el ESP32 puede parsear (revisar logs del ESP32)
# El parser busca: "control":"led1" y "value":true
# Que está presente en el array
```

---

## Resumen

- ✅ **Rápido**: 5 minutos para implementar
- ✅ **Compatible**: Funciona con el ESP32 actual
- ✅ **Mínimo cambio**: Solo 2 archivos modificados
- ⚠️ **Limitación**: Sin persistencia (pierde datos si se reinicia)

Para producción, implementar Opción 3 con BD.
