import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
import nltk
import time
from urllib.robotparser import RobotFileParser
import logging
from typing import List, Dict, Any, Optional

# Download VADER lexicon for sentiment analysis
nltk.download('vader_lexicon', quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Set up Flask app and CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to check if scraping is allowed
def is_scraping_allowed(url: str) -> bool:
    try:
        rp = RobotFileParser()
        rp.set_url(url + "/robots.txt")
        rp.read()
        return rp.can_fetch("*", url)
    except Exception as e:
        logging.error(f"Error checking robots.txt for URL: {url}")
        logging.error(e)
        return False

# Function to get soup object from URL
def get_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL: {url}")
        logging.error(e)
        return None

# Function to extract reviews from a page
def extract_reviews(soup: BeautifulSoup) -> List[str]:
    reviews_section = soup.find_all('div', class_='text show-more__control')
    reviews = [review.text.strip() for review in reviews_section]
    return reviews

# Function to get all reviews by handling pagination
def get_all_reviews(base_url: str, num_pages: int = 5) -> List[str]:
    all_reviews = []
    for page in range(num_pages):
        url = f"{base_url}reviews?start={page * 10}"
        logging.info(f"Fetching URL: {url}")
        soup = get_soup(url)
        if soup:
            reviews = extract_reviews(soup)
            if reviews:
                all_reviews.extend(reviews)
            else:
                logging.warning(f"No reviews found on page {page + 1}")
        else:
            logging.warning(f"No soup object returned for URL: {url}")
        time.sleep(1)  # Respectful crawling delay
    return all_reviews

# Function to categorize sentiment based on compound score
def categorize_sentiment(compound_score: float) -> str:
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

# Function to analyze sentiment of reviews
def analyze_sentiment(reviews: List[str]) -> List[Dict[str, Any]]:
    sia = SentimentIntensityAnalyzer()
    sentiment_analysis = []
    
    for review in reviews:
        sentiment_scores = sia.polarity_scores(review)
        sentiment_category = categorize_sentiment(sentiment_scores['compound'])
        sentiment_analysis.append({
            'review': review,
            'scores': sentiment_scores,
            'category': sentiment_category
        })
    
    return sentiment_analysis

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        base_url = data.get('base_url')
        num_pages = data.get('num_pages', 5)

        # Ensure num_pages is an integer
        try:
            num_pages = int(num_pages)
        except ValueError:
            return jsonify({"error": "num_pages must be an integer"}), 400

        if not base_url:
            return jsonify({"error": "Base URL is required"}), 400

        if not is_scraping_allowed(base_url):
            return jsonify({"error": "Scraping not allowed by robots.txt"}), 403

        reviews = get_all_reviews(base_url, num_pages)
        if not reviews:
            return jsonify({"error": "No reviews found"}), 404

        sentiments = analyze_sentiment(reviews)

        response = {
            'sentiments': sentiments
        }
        return jsonify(response)
    except Exception as e:
        logging.error("Error during sentiment analysis", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
