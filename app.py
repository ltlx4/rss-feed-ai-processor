
import os
import feedparser
from openai import OpenAI
from flask import Flask, render_template
from dotenv import load_dotenv
import datetime
import json
from collections import defaultdict


# Load environment variables
load_dotenv()
# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Flask app
app = Flask(__name__)


# RSS feeds to monitor (tech news sources)
RSS_FEEDS = {
    'TechCrunch': 'https://techcrunch.com/feed/',
    'Wired': 'https://www.wired.com/feed/rss',
    'The Verge': 'https://www.theverge.com/rss/index.xml',
    'Ars Technica': 'https://arstechnica.com/feed/',
    'Mashable': 'https://mashable.com/feeds/rss/all'
}

# Cache file to store processed articles
CACHE_FILE = 'news_cache.json'

def load_cache():
    """Load cached news articles"""
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'articles': {}, 'last_updated': None}

def save_cache(cache):
    """Save news articles to cache"""
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def fetch_news_feeds():
    """Fetch all RSS feeds and return parsed entries"""
    all_entries = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            # Standardize entry format
            entry_data = {
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', '#'),
                'summary': entry.get('summary', entry.get('description', 'No summary')),
                'published': entry.get('published', ''),
                'source': source
            }
            all_entries.append(entry_data)
    return all_entries


def analyze_article(article):
    """Use OpenAI to analyze and score a news article"""
    prompt = f"""
    Analyze this tech news article and provide a score from 1-10 based on:
    - Importance in the tech industry
    - Potential impact
    - Novelty/innovation
    - Relevance to developers/tech professionals

    Title: {article['title']}
    Summary: {article['summary']}

    Return your response as JSON with these fields:
    - score (1-10)
    - reasons (array of strings explaining the score)
    - tags (array of relevant tech tags)
    - is_highlight (boolean, true if score >= 7)

    Only respond with a valid JSON object and nothing else.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tech news analyst. Always respond with valid JSON and nothing else. Provide concise, accurate analysis in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        analysis = json.loads(response.choices[0].message.content)
        # Validate score
        score = analysis.get('score', 5)
        try:
            score = int(score)
        except Exception:
            score = 5
        score = max(1, min(10, score))
        return {
            'score': score,
            'reasons': analysis.get('reasons', []),
            'tags': analysis.get('tags', []),
            'is_highlight': bool(analysis.get('is_highlight', False))
        }
    except Exception as e:
        print(f"Error analyzing article: {e}")
        return {
            'score': 5,
            'reasons': ['Analysis failed'],
            'tags': [],
            'is_highlight': False
        }

def process_news():
    """Fetch and analyze news articles"""
    cache = load_cache()
    new_articles = fetch_news_feeds()
    
    processed_articles = cache.get('articles', {})
    updated = False
    
    for article in new_articles:
        # Use title+source as unique key
        article_key = f"{article['title']}-{article['source']}"
        
        if article_key not in processed_articles:
            print(f"Processing new article: {article['title']}")
            analysis = analyze_article(article)
            processed_articles[article_key] = {
                **article,
                **analysis,
                'processed_at': datetime.datetime.now().isoformat()
            }
            updated = True
    
    if updated:
        cache['articles'] = processed_articles
        cache['last_updated'] = datetime.datetime.now().isoformat()
        save_cache(cache)
    
    return cache

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    """Format a datetime string or timestamp"""
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

@app.route('/')
def home():
    """Main page showing all news and highlights"""
    cache = process_news()
    articles = list(cache.get('articles', {}).values())
    
    # Sort by score (highest first)
    articles.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # Get highlights (score >= 7)
    highlights = [a for a in articles if a.get('is_highlight', False)]
    
    # Group by tags for exploration
    tag_groups = defaultdict(list)
    for article in articles:
        for tag in article.get('tags', []):
            tag_groups[tag].append(article)
    
    return render_template('index.html', 
                         articles=articles,
                         highlights=highlights,
                         tag_groups=tag_groups,
                         last_updated=cache.get('last_updated'))

if __name__ == '__main__':
    app.run(debug=True)