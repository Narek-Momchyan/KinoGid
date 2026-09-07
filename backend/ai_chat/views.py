import os
import json
from google import genai
from google.genai import types
from rest_framework.decorators import api_view
from rest_framework.response import Response
from film.models import Movie

# Configure Gemini API
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY_CHAT'))

@api_view(['POST'])
def ai_advisor_view(request):
    user_message = request.data.get('user_message', '').strip()
    if not user_message:
        return Response({'error': 'No user_message provided.'}, status=400)

    try:
        movies = Movie.objects.filter(is_series=False).prefetch_related('categories')
        
        catalog_lines = []
        for m in movies:
            title = m.title_am or m.title_en or m.title_ru or f"Movie {m.id}"
            genres = ", ".join([c.name for c in m.categories.all() if c.name])
            year = m.release_year or "Unknown"
            catalog_lines.append(f"ID: {m.id} | Title: {title} | Genres: {genres} | Year: {year}")
            
        movie_catalog_string = "\n".join(catalog_lines)
        if not movie_catalog_string:
            movie_catalog_string = "No movies currently available."

        # 2. Build Prompt
        history = request.data.get('history', [])
        lang = request.data.get('lang', 'am')
        
        # Map lang to language name
        lang_name = "Armenian"
        if lang == 'en':
            lang_name = "English"
        elif lang == 'ru':
            lang_name = "Russian"
            
        history_str = ""
        if history:
            history_str = "\n--- CHAT HISTORY ---\n"
            for msg in history:
                role = "User" if msg.get("role") == "user" else "AI"
                history_str += f"{role}: {msg.get('text')}\n"
            history_str += "--------------------\n"

        prompt = f"""You are a helpful, enthusiastic movie advisor for our streaming site. 
You must reply exclusively in {lang_name}. Speak naturally, enthusiastically, and casually like a friend in {lang_name}.
You are in an ongoing, continuous conversation. DO NOT greet the user on every single message. ONLY greet them if the history is completely empty. If the user asks for 'another one' or similar, look at the chat history, see what you just recommended, and suggest a different movie from the catalog.

ANTI-HALLUCINATION RULE: DO NOT invent, guess, or fabricate information about the movies. You must ONLY rely on the data provided in the catalog.
LANGUAGE RULE: Most movies in our streaming database are dubbed in Russian (Ռուսերեն) unless explicitly marked as Armenian. If the user asks 'Is this movie in Armenian?', you MUST truthfully tell them: 'No, this movie is currently available in Russian.' DO NOT lie just to please the user.
Never promise a specific translation, audio quality, or release date unless it is explicitly confirmed in the provided catalog context.

Here is the catalog of available movies in our database:
{movie_catalog_string}
{history_str}
The user asks: '{user_message}'

Recommend 1 to 6 movies strictly from the provided catalog that best match the query. 
You MUST return your response in strict JSON format like this:
{{
   "reply": "Your conversational response in Armenian explaining why you recommend this.",
   "recommended_movies": [
      {{"id": 123, "title": "Movie Title"}}
   ]
}}"""
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                response_mime_type='application/json'
            )
        )
        text = response.text.strip()
        
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        result_json = json.loads(text)
        
        if 'recommended_movies' in result_json:
            hydrated_movies = []
            for rec in result_json['recommended_movies']:
                try:
                    movie_obj = Movie.objects.get(id=rec.get('id'))
                    hydrated_movies.append({
                        'id': movie_obj.id,
                        'title': rec.get('title') or movie_obj.title_am or movie_obj.title_en,
                        'slug': movie_obj.slug,
                        'poster': movie_obj.poster.name if movie_obj.poster else None,
                        'release_year': movie_obj.release_year
                    })
                except Movie.DoesNotExist:
                    continue
            result_json['recommended_movies'] = hydrated_movies
            
    except json.JSONDecodeError:
        # Fallback if Gemini fails to return strict JSON
        result_json = {
            "reply": "Կներեք, ես չկարողացա ճիշտ մշակել Ձեր հարցումը։ Խնդրում եմ փորձել կրկին։",
            "recommended_movies": []
        }
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response(result_json)

