import os
import re
import json
import time
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

from deep_translator import GoogleTranslator
from google import genai
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify

from film.models import RawMovie, Movie
from header.models import Category, Navbar

class Command(BaseCommand):
    help = 'Processes RawMovie entries, uses Gemini to extract title/year, fetches TMDB data, and saves to Movie.'

    def handle(self, *args, **options):
        gemini_api_key = os.environ.get('GEMINI_API_KEY')
        tmdb_api_key = os.environ.get('TMDB_API_KEY')

        if not gemini_api_key or not tmdb_api_key:
            self.stdout.write(self.style.ERROR("Missing GEMINI_API_KEY or TMDB_API_KEY in environment variables."))
            return

        # Initialize the new genai client
        client = genai.Client(api_key=gemini_api_key)

        self.stdout.write(self.style.SUCCESS("Starting continuous movie processing..."))

        try:
            while True:
                raw_movies = RawMovie.objects.filter(is_processed=False)
                count = raw_movies.count()
                
                if count == 0:
                    self.stdout.write("Waiting for new movies...")
                    time.sleep(60)
                    continue

                self.stdout.write(self.style.SUCCESS(f"Found {count} unprocessed RawMovies."))

                for raw_movie in raw_movies:
                    self.stdout.write(self.style.WARNING(f"\nProcessing RawMovie {raw_movie.id} (Telegram ID: {raw_movie.telegram_message_id})"))
                    
                    caption = raw_movie.original_caption
                    if not caption:
                        self.stdout.write(self.style.ERROR("No caption found. Skipping and marking as processed."))
                        raw_movie.is_processed = True
                        raw_movie.save()
                        time.sleep(4)
                        continue

                    # ===== SNIPER OVERRIDE =====
                    # If manual_tmdb_id is set, skip ALL search logic and fetch directly
                    if raw_movie.manual_tmdb_id:
                        self.stdout.write(self.style.SUCCESS(f"SNIPER OVERRIDE: Using manual TMDB ID {raw_movie.manual_tmdb_id}"))
                        
                        # Extract episode info from caption even for manual overrides
                        episode_string = ""
                        force_tv = raw_movie.manual_is_tv
                        season_number = None
                        episode_number = None
                        
                        s_match = re.search(r'(?i)(?:\u0565\u0569\u0565\u0580\u0561\u0577\u0580\u057b\u0561\u0576|season)[\s:\u0589\-]*(\d+)', caption)
                        e_match = re.search(r'(?i)(?:\u0574\u0561\u057d|\u057d\u0565\u0580\u056b\u0561|episode|\u0574\u0561\u057d\u0568|\u057d\u0565\u0580\u056b\u0561\u0576)[\s:\u0589\-]*(\d+)', caption)
                        
                        if s_match and e_match:
                            season_number = int(s_match.group(1))
                            episode_number = int(e_match.group(1))
                            episode_string = f"(\u054d\u0565\u0566\u0578\u0576 {season_number}, \u054d\u0565\u0580\u056b\u0561 {episode_number})"
                        elif e_match:
                            season_number = 1
                            episode_number = int(e_match.group(1))
                            episode_string = f"(\u054d\u0565\u0580\u056b\u0561 {episode_number})"
                        
                        try:
                            tmdb_data = self.fetch_tmdb_by_id(raw_movie.manual_tmdb_id, tmdb_api_key, force_tv, episode_string)
                            if tmdb_data:
                                tmdb_data['season_number'] = season_number
                                tmdb_data['episode_number'] = episode_number
                                self.save_to_movie(tmdb_data, raw_movie.telegram_message_id)
                                raw_movie.is_processed = True
                                raw_movie.save()
                                self.stdout.write(self.style.SUCCESS(f"SNIPER saved: {tmdb_data['title_en']}!"))
                            else:
                                self.stdout.write(self.style.ERROR(f"SNIPER fetch failed for TMDB ID {raw_movie.manual_tmdb_id}"))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"SNIPER error: {e}"))
                        
                        time.sleep(6)
                        continue

                    # 1. Ask Gemini
                    prompt = (
                        f"Analyze this Armenian movie description. Extract the original English international "
                        f"movie name and release year. Return ONLY a valid JSON object with keys 'title' "
                        f"and 'year' (as integer). Do not include markdown formatting or any other text. Text: {caption}"
                    )

                    title = None
                    year = None
                    cleaned_hy_title = None
                    
                    try:
                        response = client.models.generate_content(
                            model='gemini-3.6-flash',
                            contents=prompt,
                        )
                        json_text = response.text.strip('`').replace('json\n', '').strip()
                        parsed_data = json.loads(json_text)
                        title = parsed_data.get('title')
                        year = parsed_data.get('year')
                        
                        if not title:
                            raise ValueError("Title is missing from JSON.")
                            
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Gemini limit reached or error ({e}). Using fallback translator..."))
                        try:
                            # Regex to capture the movie name in Armenian
                            title_match = re.search(r'(?:Անուն|Անվանում|Անվանումը)[։:\-]\s*([^\n\(]+)', caption, re.IGNORECASE)
                            if title_match:
                                raw_hy_title = title_match.group(1).strip()
                            else:
                                raw_hy_title = caption.split('\n')[0].strip()
                                
                            cleaned_hy_title = self.clean_movie_title(raw_hy_title)
                            
                            # Fallback if cleaning stripped everything
                            if not cleaned_hy_title and raw_hy_title:
                                cleaned_hy_title = raw_hy_title
                                
                            if cleaned_hy_title:
                                title = self.safe_translate(cleaned_hy_title, 'hy', 'en', cleaned_hy_title)
                                
                            if not title:
                                raise ValueError("Title is empty after fallback extraction and translation.")
                            
                            # Attempt to find a 4-digit year in the caption
                            year_match = re.search(r'\b(19\d{2}|20\d{2})\b', caption)
                            if year_match:
                                year = int(year_match.group(1))
                        except Exception as fallback_e:
                            self.stdout.write(self.style.ERROR(f"Fallback extraction failed: {fallback_e}. Skipping (leaving unprocessed)."))
                            time.sleep(4)
                            continue

                    self.stdout.write(self.style.SUCCESS(f"Extracted -> Title: {title}, Year: {year}"))

                    # Extract TV Episode info
                    episode_string = ""
                    force_tv = False
                    season_number = None
                    episode_number = None
                    
                    ep_match = re.search(r'(?i)(?:մաս|սերիա|եթերաշրջան|season|episode|մասը|սերիան)[\s:։\-]*(\d+)', caption)
                    season_match = re.search(r'(?i)(?:եթերաշրջան|season)[\s:։\-]*(\d+)', caption)
                    series_match = re.search(r'(?i)(?:մաս|սերիա|episode|մասը|սերիան)[\s:։\-]*(\d+)', caption)
                    
                    if season_match and series_match:
                        season_number = int(season_match.group(1))
                        episode_number = int(series_match.group(1))
                        episode_string = f"(Սեզոն {season_number}, Սերիա {episode_number})"
                        force_tv = True
                    elif series_match:
                        season_number = 1
                        episode_number = int(series_match.group(1))
                        episode_string = f"(Սերիա {episode_number})"
                        force_tv = True
                    elif ep_match:
                        season_number = 1
                        episode_number = int(ep_match.group(1))
                        episode_string = f"(Սերիա {episode_number})"
                        force_tv = True

                    # 2. Fetch TMDB
                    tmdb_data = self.fetch_tmdb_data(title, year, tmdb_api_key, cleaned_hy_title, episode_string, force_tv)
                    
                    if tmdb_data:
                        tmdb_data['season_number'] = season_number
                        tmdb_data['episode_number'] = episode_number
                    
                    if not tmdb_data:
                        # PLAN C: Hard Fallback
                        self.stdout.write(self.style.NOTICE("TMDB failed. Saved to DB using raw Telegram data and translations."))
                        
                        desc_am = re.sub(r'(?i)16\+', '', caption).strip()
                        
                        try:
                            hy_title = cleaned_hy_title or caption.split('\n')[0].strip()
                            
                            title_am = hy_title
                            if episode_string:
                                title_am = f"{title_am} {episode_string}"
                                
                            title_en = self.safe_translate(hy_title, 'hy', 'en', title or "Unknown Title") if hy_title else (title or "Unknown Title")
                            title_ru = self.safe_translate(hy_title, 'hy', 'ru', "Неизвестный") if hy_title else "Неизвестный"
                            
                            desc_to_translate = desc_am[:4500] if desc_am else ""
                            desc_en = self.safe_translate(desc_to_translate, 'hy', 'en', "") if desc_to_translate else ""
                            desc_ru = self.safe_translate(desc_to_translate, 'hy', 'ru', "") if desc_to_translate else ""
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f"Translation failed in Plan C: {e}"))
                            title_en = title or "Unknown Title"
                            title_ru, title_am = "Неизвестный", "Անհայտ"
                            desc_en, desc_ru = "", ""

                        # Attempt to extract genres
                        genre_match = re.search(r'(?:Ժանր|Ժանրը|Ժանրեր)[։:\-]\s*([^\n]+)', caption, re.IGNORECASE)
                        plan_c_genres = []
                        if genre_match:
                            genre_str = genre_match.group(1).strip()
                            # Split by commas or ampersands or "և"
                            genre_names = [g.strip() for g in re.split(r'[,և&]', genre_str) if g.strip()]
                            for g in genre_names:
                                try:
                                    g_en = self.safe_translate(g, 'hy', 'en', g)
                                    g_slug = slugify(g_en)
                                except:
                                    g_slug = slugify(g)
                                plan_c_genres.append({'name': g, 'slug': g_slug})

                        tmdb_data = {
                            'tmdb_id': -raw_movie.telegram_message_id,  # Dummy unique ID
                            'poster_url': "",
                            'release_year': year or 2026,
                            'duration': 0,
                            'title_en': title_en,
                            'description_en': desc_en,
                            'title_ru': title_ru,
                            'description_ru': desc_ru,
                            'title_am': title_am,
                            'description_am': desc_am,
                            'genres': plan_c_genres,
                            'is_tv': force_tv,
                            'season_number': season_number,
                            'episode_number': episode_number
                        }

                    # 3. Save to Movie
                    try:
                        self.save_to_movie(tmdb_data, raw_movie.telegram_message_id)
                        raw_movie.is_processed = True
                        raw_movie.save()
                        self.stdout.write(self.style.SUCCESS(f"Successfully saved Movie: {tmdb_data['title_en']}!"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Database error while saving movie: {e}"))

                    time.sleep(6)
                    
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nProcess stopped by user."))

    def has_armenian(self, text):
        if not text: return False
        return bool(re.search(r'[Ա-Ֆա-ֆ]', text))

    def has_russian(self, text):
        if not text: return False
        return bool(re.search(r'[А-Яа-я]', text))

    def safe_translate(self, text, src, dest, fallback_text):
        if not text: return fallback_text
        try:
            translated = GoogleTranslator(source=src, target=dest).translate(text)
            if not translated: return fallback_text
            
            # Sanitize against Error 500 injections
            if re.search(r'(?i)(Error 500|Server Error|That\'s an error|<html|<body)', translated):
                self.stdout.write(self.style.ERROR(f"Sanitized Translator Error 500 in: {translated[:30]}..."))
                return fallback_text
                
            return translated
        except Exception:
            return fallback_text

    def clean_movie_title(self, raw_title):
        if not raw_title:
            return ""
        # Remove everything inside parentheses or brackets
        cleaned = re.sub(r'\(.*?\)', ' ', raw_title)
        cleaned = re.sub(r'\[.*?\]', ' ', cleaned)
        # Remove age ratings & HD
        cleaned = re.sub(r'(?i)\b(?:12\+|16\+|18\+|12|16|18|hd)\b', ' ', cleaned)
        # Remove junk Armenian words
        for word in ['հայերեն', 'թարգմանությամբ', 'որակով', 'կինո', 'ֆիլմ']:
            cleaned = re.sub(f'(?i){word}', ' ', cleaned)
        # Clean extra spaces and trailing/leading punctuation
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[\-։:՝.,!]+|[\-։:՝.,!]+$', '', cleaned).strip()
        return cleaned

    def fetch_tmdb_data(self, title, year, api_key, original_title=None, episode_string=None, force_tv=False):
        def _search(q, endpoint="search/multi"):
            if not q:
                return None
            encoded_title = urllib.parse.quote(q)
            year_query = f"&primary_release_year={year}" if year else ""
            search_url = f"https://api.themoviedb.org/3/{endpoint}?api_key={api_key}&query={encoded_title}{year_query}&language=en-US"
            resp = requests.get(search_url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('results'):
                    return data
                if year:
                    search_url_no_year = f"https://api.themoviedb.org/3/{endpoint}?api_key={api_key}&query={encoded_title}&language=en-US"
                    resp = requests.get(search_url_no_year)
                    if resp.status_code == 200:
                        return resp.json()
            return None

        try:
            endpoint = "search/tv" if force_tv else "search/multi"
            data = _search(title, endpoint)
            
            if (not data or not data.get('results')) and original_title and original_title != title:
                data = _search(original_title, endpoint)
                
            # Search 3 (Fuzzy Search): First 2 words of the translated english title
            if (not data or not data.get('results')) and title:
                words = title.split()
                if len(words) > 2:
                    fuzzy_title = " ".join(words[:2])
                    data = _search(fuzzy_title, endpoint)
                
            if not data or not data.get('results'):
                return None
                
            result = data['results'][0]
            media_type = result.get('media_type', 'tv' if force_tv else 'movie')
            
            movie_id = result['id']
            
            is_tv = (media_type == 'tv')
            details_endpoint = "tv" if is_tv else "movie"
            
            # Fetch full details for languages
            details_url = f"https://api.themoviedb.org/3/{details_endpoint}/{movie_id}?api_key={api_key}"
            
            data_en = requests.get(f"{details_url}&language=en-US").json()
            data_ru = requests.get(f"{details_url}&language=ru-RU").json()
            data_hy = requests.get(f"{details_url}&language=hy-AM").json()

            poster_path = data_en.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else ""
            
            if is_tv:
                release_date = data_en.get('first_air_date', '')
                tmdb_title_en = data_en.get('name') or title
                duration = 0
                if data_en.get('episode_run_time'):
                    duration = data_en.get('episode_run_time')[0]
            else:
                release_date = data_en.get('release_date', '')
                tmdb_title_en = data_en.get('title') or title
                duration = data_en.get('runtime', 0) or 0
                
            release_year = int(release_date.split('-')[0]) if release_date else (year or 0)
            
            genres = data_en.get('genres', [])
            genres_hy = data_hy.get('genres', [])
            
            translated_genres = []
            for i, g in enumerate(genres):
                name_en = g.get('name')
                name_hy = genres_hy[i].get('name') if i < len(genres_hy) else name_en
                
                if not name_hy or name_hy == name_en:
                    name_am = self.safe_translate(name_en, 'en', 'hy', name_en)
                else:
                    name_am = name_hy
                    
                translated_genres.append({
                    'name': name_am,
                    'slug': slugify(name_en)
                })
            
            title_en = tmdb_title_en
            desc_en = data_en.get('overview', '')

            # Russian logic
            tmdb_title_ru = data_ru.get('name') if is_tv else data_ru.get('title')
            raw_title_ru = tmdb_title_ru or title_en
            raw_desc_ru = data_ru.get('overview') or desc_en
            
            if not self.has_russian(raw_title_ru):
                title_ru = self.safe_translate(title_en, 'auto', 'ru', raw_title_ru)
            else:
                title_ru = raw_title_ru
                
            if not self.has_russian(raw_desc_ru) and desc_en:
                desc_ru = self.safe_translate(desc_en, 'auto', 'ru', raw_desc_ru)
            else:
                desc_ru = raw_desc_ru

            # Armenian logic
            tmdb_title_am = data_hy.get('name') if is_tv else data_hy.get('title')
            raw_title_am = tmdb_title_am or title_en
            raw_desc_am = data_hy.get('overview') or desc_en
            
            if not self.has_armenian(raw_title_am):
                title_am = self.safe_translate(title_en, 'auto', 'hy', raw_title_am)
            else:
                title_am = raw_title_am
                
            if not self.has_armenian(raw_desc_am) and desc_en:
                desc_am = self.safe_translate(desc_en, 'auto', 'hy', raw_desc_am)
            else:
                desc_am = raw_desc_am
                
            if episode_string:
                title_am = f"{title_am} {episode_string}"
            
            return {
                'tmdb_id': movie_id,
                'poster_url': poster_url,
                'release_year': release_year,
                'duration': duration,
                'title_en': title_en,
                'description_en': desc_en,
                'title_ru': title_ru,
                'description_ru': desc_ru,
                'title_am': title_am,
                'description_am': desc_am,
                'genres': translated_genres,
                'is_tv': is_tv
            }
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"TMDB Fetch Exception: {e}"))
            return None

    def fetch_tmdb_by_id(self, tmdb_id, api_key, is_tv=False, episode_string=None):
        """Sniper Override: fetch TMDB data directly by exact ID, no search."""
        try:
            details_endpoint = "tv" if is_tv else "movie"
            details_url = f"https://api.themoviedb.org/3/{details_endpoint}/{tmdb_id}?api_key={api_key}"
            
            data_en = requests.get(f"{details_url}&language=en-US").json()
            data_ru = requests.get(f"{details_url}&language=ru-RU").json()
            data_hy = requests.get(f"{details_url}&language=hy-AM").json()

            poster_path = data_en.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}" if poster_path else ""
            
            if is_tv:
                release_date = data_en.get('first_air_date', '')
                tmdb_title_en = data_en.get('name') or f"TV-{tmdb_id}"
                duration = 0
                if data_en.get('episode_run_time'):
                    duration = data_en.get('episode_run_time')[0]
            else:
                release_date = data_en.get('release_date', '')
                tmdb_title_en = data_en.get('title') or f"Movie-{tmdb_id}"
                duration = data_en.get('runtime', 0) or 0
                
            release_year = int(release_date.split('-')[0]) if release_date else 0
            
            genres = data_en.get('genres', [])
            genres_hy = data_hy.get('genres', [])
            
            translated_genres = []
            for i, g in enumerate(genres):
                name_en = g.get('name')
                name_hy = genres_hy[i].get('name') if i < len(genres_hy) else name_en
                if not name_hy or name_hy == name_en:
                    name_am = self.safe_translate(name_en, 'en', 'hy', name_en)
                else:
                    name_am = name_hy
                translated_genres.append({'name': name_am, 'slug': slugify(name_en)})
            
            title_en = tmdb_title_en
            desc_en = data_en.get('overview', '')

            # Russian
            tmdb_title_ru = data_ru.get('name') if is_tv else data_ru.get('title')
            raw_title_ru = tmdb_title_ru or title_en
            raw_desc_ru = data_ru.get('overview') or desc_en
            title_ru = self.safe_translate(title_en, 'auto', 'ru', raw_title_ru) if not self.has_russian(raw_title_ru) else raw_title_ru
            desc_ru = self.safe_translate(desc_en, 'auto', 'ru', raw_desc_ru) if (not self.has_russian(raw_desc_ru) and desc_en) else raw_desc_ru

            # Armenian
            tmdb_title_am = data_hy.get('name') if is_tv else data_hy.get('title')
            raw_title_am = tmdb_title_am or title_en
            raw_desc_am = data_hy.get('overview') or desc_en
            title_am = self.safe_translate(title_en, 'auto', 'hy', raw_title_am) if not self.has_armenian(raw_title_am) else raw_title_am
            desc_am = self.safe_translate(desc_en, 'auto', 'hy', raw_desc_am) if (not self.has_armenian(raw_desc_am) and desc_en) else raw_desc_am
                
            if episode_string:
                title_am = f"{title_am} {episode_string}"
            
            return {
                'tmdb_id': tmdb_id,
                'poster_url': poster_url,
                'release_year': release_year,
                'duration': duration,
                'title_en': title_en,
                'description_en': desc_en,
                'title_ru': title_ru,
                'description_ru': desc_ru,
                'title_am': title_am,
                'description_am': desc_am,
                'genres': translated_genres,
                'is_tv': is_tv
            }
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"SNIPER Fetch Exception: {e}"))
            return None

    def save_to_movie(self, data, telegram_message_id):
        poster_file = None
        if data['poster_url']:
            try:
                resp = requests.get(data['poster_url'])
                if resp.status_code == 200:
                    poster_file = ContentFile(resp.content, name=f"{data['tmdb_id']}_poster.jpg")
            except:
                pass

        slug = slugify(data['title_en']) + f"-{telegram_message_id}"
        
        movie, created = Movie.objects.update_or_create(
            telegram_message_id=telegram_message_id,
            defaults={
                'tmdb_id': data['tmdb_id'],
                'title_en': data['title_en'],
                'title_ru': data['title_ru'],
                'title_am': data['title_am'],
                'description_en': data['description_en'],
                'description_ru': data['description_ru'],
                'description_am': data['description_am'],
                'slug': slug,
                'release_year': data['release_year'],
                'duration': data['duration'],
                'is_series': data.get('is_tv', False),
                'season_number': data.get('season_number'),
                'episode_number': data.get('episode_number')
            }
        )
        
        movie.save() # STRICT SAVE ORDER FIRST
        
        if created and poster_file:
            movie.poster.save(poster_file.name, poster_file, save=True)
            
        # Process Categories (Genres)
        try:
            movies_navbar = Navbar.objects.get(slug='movies', lang='am')
        except:
            movies_navbar = None
            
        for genre in data['genres']:
            try:
                genre_name = genre.get('name')
                if genre_name:
                    genre_slug = genre.get('slug') or slugify(genre_name)
                    cat, _ = Category.objects.get_or_create(
                        name=genre_name,
                        lang='am',
                        defaults={
                            'slug': genre_slug,
                            'navbar': movies_navbar
                        }
                    )
                    movie.categories.add(cat)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding genre {genre_name}: {e}"))

        # CATEGORY REQUIREMENT: Always add "Հայերեն թարգմանված" category
        try:
            dub_cat, _ = Category.objects.get_or_create(
                name="Հայերեն թարգմանված",
                lang='am',
                defaults={
                    'slug': "armenian dub",  # Keeping slug to match URL but updating name
                    'navbar': movies_navbar
                }
            )
            movie.categories.add(dub_cat)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error adding default category: {e}"))
            
        if data.get('is_tv'):
            try:
                tv_cat, _ = Category.objects.get_or_create(
                    name="Սերիալներ",
                    lang='am',
                    defaults={
                        'slug': "tv-series",
                        'navbar': movies_navbar
                    }
                )
                movie.categories.add(tv_cat)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error adding TV category: {e}"))
