import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .services.ai_service import AIService

@require_POST
def chat_message(request):
    """
    Asynchronous POST view to handle chatbot messages.
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        product_context = data.get('product_context', None)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'response': 'Sorry, I received an invalid request format.'}, status=400)

    if not user_message:
        return JsonResponse({'response': 'Please enter a message.'}, status=400)

    # Initialize chatbot states in user session if missing
    if 'chatbot_state' not in request.session:
        request.session['chatbot_state'] = {}

    # Extract state sub-dict to pass by reference
    chatbot_session = request.session['chatbot_state']

    # Generate response
    response_text = AIService.generate_response(
        user_message=user_message,
        session_state=chatbot_session,
        product_context=product_context
    )

    # Re-assign and save session
    request.session['chatbot_state'] = chatbot_session
    request.session.modified = True

    return JsonResponse({'response': response_text})
