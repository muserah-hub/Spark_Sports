import os
import json
import urllib.request
from django.conf import settings
from products.models import Product, Category

class AIService:
    """
    Abstracted AI Service layer for Spark AI.
    Handles communication with external LLMs (Gemini) or falls back
    to a rule-based local expert system if no API key is available.
    """
    @staticmethod
    def generate_response(user_message, session_state, product_context=None):
        """
        Main entry point for generating responses.
        Detects if Gemini API Key is set and routes appropriately.
        """
        # Retrieve API Key from Django settings
        api_key = getattr(settings, 'GEMINI_API_KEY', '')

        # Build context prompt
        system_instruction = (
            "You are Spark AI, a premium virtual assistant, cricket coach, and sports nutrition expert "
            "for 'Spark Sports' (a cricket commerce brand in Pakistan). You are helpful, energetic, "
            "and professional. You sell cricket bats, clothing, pads, and other items. "
            "IMPORTANT: When recommending products, ONLY refer to actual products in the Spark Sports database. "
            "When offering dietary or sports nutrition advice, state that this is for general educational "
            "purposes and you are not a doctor or registered dietitian. Suggest users with medical needs consult professional doctors."
        )

        # If product context is provided, append it to context
        if product_context:
            system_instruction += (
                f"\nCURRENT PRODUCT CONTEXT: The user is looking at a product called '{product_context.get('name')}' "
                f"in the category '{product_context.get('category')}' priced at Rs. {product_context.get('price')}. "
                f"Stock status: {'In Stock' if product_context.get('in_stock') else 'Out of Stock'}. "
                f"Description: {product_context.get('description')}. Answer questions directly relating to this."
            )

        if api_key:
            return AIService._call_gemini_api(api_key, system_instruction, user_message)
        else:
            return AIService._generate_local_fallback(user_message, session_state, product_context)

    @staticmethod
    def _call_gemini_api(api_key, system_instruction, user_message):
        """
        Performs raw HTTP POST request to the Google Gemini API (gemini-1.5-flash)
        to avoid pip dependency resolution errors.
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        prompt = f"{system_instruction}\n\nUser Question: {user_message}\nSpark AI Response:"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 800,
                "temperature": 0.7
            }
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                response_text = res_data['candidates'][0]['content']['parts'][0]['text']
                return response_text
        except Exception as e:
            # Fall back to simulated warning if request fails
            return (
                "⚠️ [Spark AI] Connected to API, but encountered a connection error. "
                "Here is my offline fallback assistance: " + 
                AIService._generate_local_fallback(user_message, {}, None)
            )

    @staticmethod
    def _generate_local_fallback(user_message, session_state, product_context):
        """
        Offline Expert Rule-based responder when Gemini API key is missing.
        Suppports database query lookups, onboarding questionnaire, and disclaimers.
        """
        msg = user_message.lower().strip()

        # 1. DIET ONBOARDING FLOW STATES
        # Check if we are currently mid-questionnaire
        onboarding_state = session_state.get('diet_flow_state')
        
        if onboarding_state == 'awaiting_age':
            session_state['diet_age'] = user_message
            session_state['diet_flow_state'] = 'awaiting_goal'
            return (
                "Got it! Next, what is your primary goal? "
                "(e.g., Increase match stamina, build power/muscle, weight management, general fitness)"
            )
        
        elif onboarding_state == 'awaiting_goal':
            session_state['diet_goal'] = user_message
            session_state['diet_flow_state'] = 'awaiting_schedule'
            return (
                "Understood! How many days a week do you train or play cricket? (e.g., 2 days, 5 days, daily)"
            )
            
        elif onboarding_state == 'awaiting_schedule':
            session_state['diet_schedule'] = user_message
            session_state['diet_flow_state'] = 'awaiting_allergies'
            return (
                "Almost done! Do you have any food allergies, dietary restrictions, or preferences? "
                "(e.g., Vegetarian, lactose intolerant, none)"
            )
            
        elif onboarding_state == 'awaiting_allergies':
            session_state['diet_allergies'] = user_message
            # Compile results and generate meal plan
            age = session_state.get('diet_age')
            goal = session_state.get('diet_goal')
            schedule = session_state.get('diet_schedule')
            allergies = session_state.get('diet_allergies')
            
            # Reset flow state
            session_state['diet_flow_state'] = None
            
            # Nutrition template response
            meal_plan = (
                f"### 📋 Your Customized 7-Day Cricket Training Diet Plan\n"
                f"*Compiled for age '{age}' | Goal: {goal} | Training: {schedule} | Notes: {allergies}*\n\n"
                f"**Medical Disclaimer:** *This meal plan is for general educational guidance only. "
                f"Spark Sports is not a registered healthcare provider. Please consult a dietitian for medical needs.*\n\n"
                f"**Daily Meal Structure:**\n"
                f"- **Breakfast (08:00 AM):** Oatmeal with bananas, almonds, and 2 boiled egg whites (protein & slow carbs).\n"
                f"- **Lunch (01:30 PM):** Grilled chicken breast or lentils (Daal) with brown rice, mixed green salad, and curd/yogurt.\n"
                f"- **Pre-Training Snack (2 hours before):** Sweet potato or fruit bowl with a glass of fresh pomegranate juice.\n"
                f"- **Dinner (08:30 PM):** Whole wheat chapati/roti with mutton/beef mince (Keema) or fish, served with stir-fried vegetables.\n"
                f"- **Hydration Reminder:** Keep sipping water throughout training (aim for 3-4 liters daily).\n\n"
                f"Would you like advice on pre-match meal ideas or hydration strategies instead?"
            )
            return meal_plan

        # 2. TRIGGER MEAL PLAN ONBOARDING
        if any(kw in msg for kw in ['diet plan', 'meal plan', 'nutrition plan', '7-day plan', 'create a plan']):
            session_state['diet_flow_state'] = 'awaiting_age'
            return (
                "🏏 Let's customize your cricket training meal plan!\n"
                "I will ask you 4 quick questions. First, what is your age range? (e.g., Under 15, 15-19, 20-30, 30+)"
            )

        # 3. GENERAL SPORTS NUTRITION TRIGGERS
        if any(kw in msg for kw in ['nutrition', 'protein', 'carbohydrate', 'pre-match', 'hydration', 'diet', 'food']):
            return (
                "🏏 **Spark Sports General Nutrition Guide:**\n\n"
                "1. **Pre-Match Meals:** Eat complex carbohydrates 2-3 hours before a match (e.g., oatmeal, pasta, whole grains) to maintain steady glucose levels. Avoid heavy fats.\n"
                "2. **Hydration:** Drink 500ml water 2 hours before play, and sip electrolyte mixes during breaks to prevent cramping.\n"
                "3. **Post-Training Recovery:** Consume high-quality protein (chicken, eggs, lentils) combined with carbohydrates within 45 minutes of training to rebuild muscle fibers.\n\n"
                "*Disclaimer: This is general educational information. Consult a registered dietitian for personalized clinical programs.*"
            )

        # 4. PRODUCT RECOMMENDATION BY BUDGET
        if 'budget' in msg or 'rs' in msg or 'rupees' in msg or 'recommend a bat' in msg or 'buy a bat' in msg:
            # Try to extract numbers representing budget
            words = msg.split()
            budget = None
            for word in words:
                clean_word = ''.join(c for c in word if c.isdigit())
                if clean_word:
                    budget = float(clean_word)
                    break
            
            bats = Product.objects.filter(category__name__icontains='Bat', available=True)
            if budget:
                suitable_bats = bats.filter(price__lte=budget)[:3]
                if suitable_bats.exists():
                    res = f"🏏 Based on your budget of Rs. {budget:,.0f}, I recommend these bats:\n\n"
                    for bat in suitable_bats:
                        res += f"- **{bat.name}** - Rs. {bat.price:,.0f} ({'In Stock' if bat.is_in_stock else 'Out of Stock'})\n"
                    return res
                else:
                    lowest_bat = Product.objects.filter(category__name__icontains='Bat', available=True).order_by('price').first()
                    if lowest_bat:
                        return f"Our entry-level bat is **{lowest_bat.name}** at Rs. {lowest_bat.price:,.0f}. That might fit your requirements!"
            
            # General bat recommendation
            featured_bats = Product.objects.filter(category__name__icontains='Bat', featured=True, available=True)[:2]
            if featured_bats.exists():
                res = "We have premium cricket bats in stock. Check out:\n"
                for bat in featured_bats:
                    res += f"- **{bat.name}** - Rs. {bat.price:,.0f}\n"
                return res
            return "Please visit our Shop page to see our full collection of English Willow and Kashmir Willow cricket bats."

        # 5. SHOES RECOMMENDATION FOR FAST BOWLER
        if 'fast bowler' in msg or 'bowler shoes' in msg or 'spikes' in msg or 'shoes' in msg:
            shoes = Product.objects.filter(category__name__icontains='Shoes', available=True)[:2]
            if shoes.exists():
                res = "👟 Fast Bowlers require shoes with reinforced ankle support and custom spike configurations for their delivery stride. Recommended gear:\n\n"
                for shoe in shoes:
                    res += f"- **{shoe.name}** - Rs. {shoe.price:,.0f}\n"
                return res
            return "Check out our footwear selection on the Shop page for high-grip cricket spikes designed for bowling impact."

        # 6. PRODUCT DETAIL CONTEXT ANSWERS
        if product_context:
            name = product_context.get('name')
            price = product_context.get('price')
            category = product_context.get('category')
            in_stock = product_context.get('in_stock')

            if 'price' in msg or 'cost' in msg or 'how much' in msg:
                return f"The **{name}** is currently priced at Rs. {price}. " + (
                    "It is in stock and ready to ship!" if in_stock else "It is currently out of stock."
                )
            if 'stock' in msg or 'available' in msg or 'buy' in msg:
                return f"Yes, the **{name}** is {'in stock' if in_stock else 'currently out of stock'}. You can add it to your cart directly from this page!"
            
            return (
                f"You are asking about the **{name}** (Category: {category}). It is a premium product "
                f"crafted for top performance. Priced at Rs. {price}. Let me know if you need to know about its specifications!"
            )

        # 7. GENERAL WELCOME/FALLBACK
        return (
            "I'm here to help you get geared up! 🏏 You can ask me:\n"
            "- 'Recommend a bat under Rs. 15,000'\n"
            "- 'Create a 7-day cricket training meal plan'\n"
            "- 'Tell me about pre-match meals and hydration'\n"
            "What can I assist you with?"
        )
