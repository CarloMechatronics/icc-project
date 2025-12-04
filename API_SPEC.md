# API Specification - ESP32 ↔ Backend

## Base URL
```
http://44.222.106.109:8000
```

## Endpoints

### 1. **POST /api** - Ingest Telemetry (ESP32 → Backend)
**Frequency:** Every 5 seconds

**Request:**
```json
{
  "temp": 25.5,
  "hum": 60.2,
  "motion": true,
  "led1": false,
  "led2": false,
  "door_open": false,
  "door_angle": 0,
  "device": "esp32-1"
}
```

**Response (201):**
```json
{
  "status": "ingested",
  "device": "esp32-1",
  "metrics": {
    "temp": 25.5,
    "hum": 60.2
  }
}
```

---

### 2. **GET /api/control?device=esp32-1** - Poll Control State (ESP32 polls)
**Frequency:** Every 3 seconds

**Response (200):**
```json
{
  "controls": [
    {"control": "led1", "value": false},
    {"control": "led2", "value": false},
    {"control": "door_open", "value": false},
    {"control": "door_angle", "value": 0}
  ],
  "updated_at": "2025-12-02T10:30:45.123456"
}
```

**ESP32 Parser expects:** `"control":"led1"` with `"value":` pair

---

### 3. **POST /api/control** - Set Control State (Dashboard → Backend)
**Triggered:** User interactions (toggle switches, angle input)

**Request:**
```json
{
  "device": "esp32-1",
  "led1": true,
  "led2": false,
  "door_open": true,
  "door_angle": 90
}
```

**Response (200):**
```json
{
  "status": "queued",
  "controls": {
    "controls": [
      {"control": "led1", "value": true},
      {"control": "led2", "value": false},
      {"control": "door_open", "value": true},
      {"control": "door_angle", "value": 90}
    ],
    "updated_at": "2025-12-02T10:31:20.654321"
  }
}
```

---

### 4. **GET /api/temp?device=esp32-1** - Get Latest Temperature
**Consumer:** Dashboard.js

**Response (200):**
```json
{
  "device": "esp32-1",
  "temp": 25.5,
  "timestamp": "2025-12-02T10:30:45.123456",
  "message": null
}
```

If no data: `"message": "sin datos"`

---

### 5. **GET /api/hum?device=esp32-1** - Get Latest Humidity
**Consumer:** Dashboard.js

**Response (200):**
```json
{
  "device": "esp32-1",
  "hum": 60.2,
  "timestamp": "2025-12-02T10:30:45.123456",
  "message": null
}
```

---

### 6. **GET /api/motion?device=esp32-1** - Get Latest Motion
**Consumer:** Dashboard.js

**Response (200):**
```json
{
  "device": "esp32-1",
  "motion": true,
  "timestamp": "2025-12-02T10:30:45.123456",
  "message": null
}
```

---

### 7. **GET /api/metrics/summary** - Get Metrics Summary
**Consumer:** Dashboard.js

**Response (200):**
```json
{
  "devices": 1,
  "readings": 150,
  "latest_reading": "2025-12-02T10:30:45.123456"
}
```

---

## Flow Diagram

```
ESP32 (loop every 5s)
  └─→ POST /api (send sensor + state data)
      └─→ Backend stores in DB + cache
      
ESP32 (loop every 3s)
  └─→ GET /api/control?device=esp32-1
      └─→ Backend returns latest controls
      └─→ ESP32 parses "control":"led1", "value":bool
      └─→ ESP32 applies to GPIO

Dashboard (on load + every 4s)
  └─→ GET /api/temp, /api/hum, /api/motion
      └─→ Backend returns latest cached metrics

Dashboard (on user action)
  └─→ POST /api/control {led1, led2, door_open, door_angle}
      └─→ Backend updates in-memory state
      └─→ Next ESP32 poll gets new controls
```

## Troubleshooting

### ESP32 not receiving telemetry?
1. Check `POST /api` is hitting (verify WiFi connected)
2. Check database INSERT permissions
3. Verify `device: "esp32-1"` matches in all requests

### ESP32 not receiving controls?
1. Verify `GET /api/control?device=esp32-1` HTTP 200
2. Ensure ESP32 parser finds `"control":"led1"` in JSON
3. Check WiFi connection timing

### Dashboard showing "sin datos"?
1. Verify `POST /api` was called at least once
2. Check database has readings for device
3. Ensure timestamps are valid ISO format
