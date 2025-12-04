from flask import Blueprint, jsonify, request

from app.services.ai_service import AIService

ia_bp = Blueprint("ia", __name__, url_prefix="/api/ia")
ai_service = AIService()


@ia_bp.post("/faq")
def faq_chat():
    payload = request.get_json(silent=True) or {}
    question = payload.get("question", "")
    answer = ai_service.answer(question)
    return jsonify({"question": question, "answer": answer})
