import textwrap


class AIService:
    def __init__(self):
        # Texto en ASCII simple para evitar problemas de encoding en contenedores
        self.faq = {
            "que sensores usa": (
                "El ESP32-S3 usa DHT11 (temperatura/humedad), PIR SR501 "
                "(movimiento), 2 LEDs y un servo para la puerta."
            ),
            "como se envia telemetria": (
                "El firmware hace POST cada 5s a /api con JSON temp, hum, "
                "motion, led1, led2, door_open, door_angle y device."
            ),
            "como controlo el dispositivo": (
                "Desde el dashboard o POST /api/control con JSON "
                "{device, led1, led2, door_open, door_angle}. "
                "El ESP32 hace GET /api/control para aplicar el estado."
            ),
            "que stack usa": (
                "Backend Flask + MySQL; frontend Jinja+JS; IoT ESP32-S3; "
                "despliegue sugerido en EC2 con nginx+gunicorn y RDS MySQL."
            ),
            "como desplegar en aws": (
                "1) EC2 con Docker para app+nginx+mosquitto, 2) RDS MySQL, "
                "3) S3 para estaticos/backups, 4) CloudWatch para logs."
            ),
        }

    def answer(self, question: str) -> str:
        if not question:
            return "Pregunta algo sobre la plataforma o el dispositivo."
        q = question.lower()
        for key, value in self.faq.items():
            if key in q:
                return value
        return textwrap.dedent(
            """
            No tengo una respuesta exacta en la base de FAQs.
            - Controla el IoT con POST /api/control y revisa metricas en /api/metrics/summary.
            - Consulta el README o la documentacion para detalles.
            """
        ).strip()
