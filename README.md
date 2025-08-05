# rss-feed-ai-processor

A Flask-based RSS feed fetcher that retrieves RSS feeds, processes each feed item using OpenAI's API to generate a score, summary, and other insights, then caches the processed data in JSON format for efficient retrieval.

## Features

- Fetches RSS feeds from user-specified URLs.
- Processes each feed item using OpenAI API:
  - Generates a summary.
  - Provides a relevance or quality score.
  - Extracts other useful insights (customizable).
- Caches processed feed data as JSON files to minimize redundant API calls and speed up response times.
- Built with Flask for easy integration and deployment.
- Simple API endpoints for fetching and viewing processed feeds.

## Tech Stack

- Python 3.x
- Flask
- feedparser (for RSS parsing)
- OpenAI API
- JSON for caching

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/rss-feed-ai-processor.git
   cd rss-feed-ai-processor
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your OpenAI API key in a `.env` file:
   ```bash
   OPENAI_API_KEY=your-api-key-here
5. Run the app:
   ```bash
   python app.py
   ```
6. Access the app at `http://localhost:5000`.

