const deviceId = "esp32-1";

// El dashboard habla siempre con el mismo origen (localhost/EC2) en rutas /api/*.
// El backend Flask local se encarga de proxyar estas rutas al EC2 real.

function withBase(path) {
  const base = window.APP_API_BASE || "";
  if (!base) return path;
  // Evitar dobles slashes si el path ya empieza con /
  return `${base.replace(/\/$/, "")}${path}`;
}

async function fetchJSON(path, options = {}) {
  const res = await fetch(withBase(path), options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// ==== LECTURAS: /api/temp, /api/hum, /api/motion (proxy a EC2) ====
async function loadTelemetry() {
  try {
    const [tempData, humData, motionData] = await Promise.all([
      fetchJSON(`/api/temp?device=${deviceId}`),
      fetchJSON(`/api/hum?device=${deviceId}`),
      fetchJSON(`/api/motion?device=${deviceId}`),
    ]);

    if (tempData.temp !== undefined && tempData.temp !== null) {
      const v = typeof tempData.temp === "number" ? tempData.temp.toFixed(1) : tempData.temp;
      setText("temp-value", `${v} C`);
      setText("temp-updated", tempData.timestamp || "-");
    }
    if (humData.hum !== undefined && humData.hum !== null) {
      const v = typeof humData.hum === "number" ? humData.hum.toFixed(1) : humData.hum;
      setText("hum-value", `${v} %`);
      setText("hum-updated", humData.timestamp || "-");
    }
    if (motionData.motion !== undefined && motionData.motion !== null) {
      setText("motion-value", motionData.motion ? "Activo" : "Inactivo");
      setText("motion-updated", motionData.timestamp || "-");
    }
  } catch (err) {
    console.error("telemetry", err);
    setText("temp-updated", "sin datos");
    setText("hum-updated", "sin datos");
    setText("motion-updated", "sin datos");
  }
}

// ==== CONTROL: /api/control (proxy a EC2 /api/control) ====
async function applyControl() {
  const led1 = document.getElementById("led1-toggle").checked;
  const led2 = document.getElementById("led2-toggle").checked;
  const doorOpen = document.getElementById("door-toggle").checked;
  const doorAngle = parseInt(document.getElementById("door-angle").value, 10) || 0;
  try {
    const result = await fetchJSON("/api/control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        device: deviceId,
        led1,
        led2,
        door_open: doorOpen,
        door_angle: doorAngle,
      }),
    });
    const updatedAt = result.updated || (result.controls && result.controls.updated_at);
    setText("control-status", `Enviado (${updatedAt || "ahora"})`);
  } catch (err) {
    console.error("control", err);
    setText("control-status", "Error al enviar");
  }
}

async function loadMetrics() {
  try {
    // De momento mostramos el listado bruto que devuelve el backend remoto via /api (proxy local)
    const data = await fetchJSON("/api?limit=20");
    const pre = document.getElementById("metrics-json");
    if (pre) pre.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    console.error("metrics", err);
  }
}

function wireUI() {
  const btn = document.getElementById("apply-control");
  if (btn) btn.addEventListener("click", applyControl);

  const led1Toggle = document.getElementById("led1-toggle");
  if (led1Toggle) led1Toggle.addEventListener("change", applyControl);
}

window.addEventListener("DOMContentLoaded", () => {
  wireUI();
  loadTelemetry();
  loadMetrics();
  setInterval(loadTelemetry, 4000);
  setInterval(loadMetrics, 10000);
});
