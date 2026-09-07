# -*- coding: utf-8 -*-
import os
import sys
import io
import time
import random
from django.core.management.base import BaseCommand
from news.models import NewsPost
from google import genai


# Curated high-quality cinema-related Unsplash images
CINEMA_IMAGES = [
    "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&q=80",
    "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800&q=80",
    "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=800&q=80",
    "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800&q=80",
    "https://images.unsplash.com/photo-1585951237318-9ea5e68b9b0b?w=800&q=80",
    "https://images.unsplash.com/photo-1524712245354-2c4e5e7121c0?w=800&q=80",
    "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=800&q=80",
    "https://images.unsplash.com/photo-1595769816263-9b910be24d5f?w=800&q=80",
    "https://images.unsplash.com/photo-1460881680858-30d872d5b530?w=800&q=80",
    "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?w=800&q=80",
    "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=800&q=80",
    "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=800&q=80",
]

# 5 unique topics to ensure diverse articles (Armenian)
TOPICS = [
    "\u0540\u0578\u056c\u056b\u057e\u0578\u0582\u0564\u0575\u0561\u0576 \u0576\u0578\u0580\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580",                          # Holliywood news
    "\u0531\u0580\u0570\u0565\u057d\u057f\u0561\u056f\u0561\u0576 \u0562\u0561\u0576\u0561\u056f\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0568 \u056f\u056b\u0576\u0578\u0575\u0578\u0582\u0574",       # AI in cinema
    "\u054d\u057a\u0561\u057d\u057e\u0578\u0572 \u0562\u056c\u0578\u056f\u0562\u0561\u057d\u057f\u0565\u0580\u0576\u0565\u0580",                               # Upcoming blockbusters
    "\u053f\u056b\u0576\u0578\u0583\u0561\u057c\u0561\u057f\u0578\u0576\u0576\u0565\u0580 \u0587 \u0574\u0580\u0581\u0561\u0576\u0561\u056f\u0576\u0565\u0580",                   # Film festivals & awards
    "\u0534\u0561\u057d\u0561\u056f\u0561\u0576 \u056f\u056b\u0576\u0578\u0575\u056b \u057e\u0565\u0580\u0561\u056e\u0576\u0578\u0582\u0576\u0564\u0568",                     # Revival of classic cinema
]


class Command(BaseCommand):
    help = "Generates 5 unique news articles using Google Gemini AI."

    def handle(self, *args, **options):
        # Fix Windows console encoding for Armenian text
        if sys.platform == 'win32':
            try:
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding='utf-8', errors='replace'
                )
            except Exception:
                pass

        api_key = os.environ.get('GEMINI_API_KEY_NEWS')
        if not api_key:
            self.stderr.write(self.style.ERROR(
                "GEMINI_API_KEY_NEWS is not set in environment."
            ))
            return

        client = genai.Client(api_key=api_key)

        # Shuffle images so each article gets a unique one
        images = random.sample(CINEMA_IMAGES, min(5, len(CINEMA_IMAGES)))

        success_count = 0

        for i in range(5):
            topic = TOPICS[i]
            image_url = images[i]

            # Build a unique prompt for each topic
            prompt = (
                f"Write an interesting, modern, and readable article "
                f"(about 200 words) specifically about: {topic}. "
                f"Write ONLY in Armenian (Eastern Armenian). "
                f"Return only the text. Make the first line the title. "
                f"Do NOT repeat content from previous articles."
            )

            self.stdout.write(f"[{i+1}/5] Generating article about: {topic}...")

            # Retry up to 3 times on rate limit errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt
                    )
                    text = response.text.strip()

                    lines = text.split('\n')

                    # The first non-empty line is the title
                    title = ""
                    content_lines = []

                    for line in lines:
                        clean_line = line.strip().strip('#').strip('*').strip()
                        if not clean_line:
                            continue
                        if not title:
                            title = clean_line
                        else:
                            content_lines.append(line)

                    content = '\n'.join(content_lines).strip()

                    if not title or not content:
                        self.stderr.write(self.style.ERROR(
                            f"  Could not parse article {i+1}. Skipping."
                        ))
                    else:
                        post = NewsPost.objects.create(
                            title=title[:500],
                            content=content,
                            image_url=image_url,
                            generated_by_ai=True
                        )
                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f"  Successfully generated article {i+1}/5 (ID: {post.id})"
                        ))
                    break  # Success or parse error, move to next article

                except Exception as e:
                    error_str = str(e)
                    if '429' in error_str and attempt < max_retries - 1:
                        # Parse retry delay from error if available
                        import re
                        match = re.search(r'retry in (\d+)', error_str, re.IGNORECASE)
                        wait_time = int(match.group(1)) + 5 if match else 60
                        self.stdout.write(self.style.WARNING(
                            f"  Rate limited. Waiting {wait_time}s before retry {attempt+2}/{max_retries}..."
                        ))
                        time.sleep(wait_time)
                    else:
                        self.stderr.write(self.style.ERROR(
                            f"  Error on article {i+1}: {e}"
                        ))
                        self.stdout.write(f"  Skipping article {i+1}, continuing...")
                        break

            # Delay between articles
            if i < 4:
                self.stdout.write("  Waiting 10 seconds...")
                time.sleep(10)

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Successfully generated {success_count}/5 articles."
        ))

