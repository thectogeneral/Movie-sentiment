// src/App.js

import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [numPages, setNumPages] = useState(1);
  const [reviews, setReviews] = useState([]);
  const [sentiments, setSentiments] = useState([]);
  const [error, setError] = useState('');

  const analyzeSentiment = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/analyze', {
        base_url: url,
        num_pages: numPages,
      });
      //setReviews(response.data.reviews);
      setSentiments(response.data.sentiments);
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred');
      setReviews([]);
      setSentiments([]);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Sentiment Analysis</h1>
        <input
          type="text"
          placeholder="Enter IMDb URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <input
          type="number"
          placeholder="Number of pages"
          value={numPages}
          onChange={(e) => setNumPages(e.target.value)}
        />
        <button onClick={analyzeSentiment}>Analyze</button>
        {error && <p className="error">{error}</p>}
        <div className="results">
  {sentiments.length > 0 && (
    <>
      <h2>Sentiments</h2>
      {sentiments.map((sentiment, index) => (
        <ul key={index} className="card">
          <li>
            <strong>Category:</strong> {sentiment.category}
          </li>
          <li>
            <strong>Review:</strong> {sentiment.review}
          </li>
          <li>
            <strong>Positive:</strong> {sentiment.scores.pos}
          </li>
          <li>
            <strong>Neutral:</strong> {sentiment.scores.neu}
          </li>
          <li>
            <strong>Negative:</strong> {sentiment.scores.neg}
          </li>
          <li>
            <strong>Compound:</strong> {sentiment.scores.compound}
          </li>
        </ul>
      ))}
    </>
  )}
</div>

      </header>
    </div>
  );
}

export default App;
