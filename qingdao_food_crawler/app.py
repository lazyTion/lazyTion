#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory
from crawler import QingdaoFoodCrawler

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    """Run the crawler with specified parameters."""
    try:
        # Get parameters from request
        sources = request.form.getlist('sources')
        pages = int(request.form.get('pages', 3))
        
        # Validate parameters
        if not sources:
            sources = ['dianping', 'meituan']
        
        if pages < 1 or pages > 10:
            pages = 3
        
        # Create and run the crawler
        crawler = QingdaoFoodCrawler(output_dir=DATA_DIR)
        csv_path, json_path = crawler.run(sources=sources, pages_per_source=pages)
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully crawled {len(crawler.restaurants)} restaurants',
            'count': len(crawler.restaurants),
            'csv_path': os.path.basename(csv_path) if csv_path else None,
            'json_path': os.path.basename(json_path) if json_path else None
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error during crawling: {str(e)}'
        }), 500

@app.route('/data')
def get_data():
    """Get the latest crawled data."""
    try:
        # Find the latest JSON file
        json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
        
        if not json_files:
            return jsonify({
                'status': 'error',
                'message': 'No data available. Please run the crawler first.'
            }), 404
        
        # Sort by modification time (newest first)
        latest_file = sorted(
            json_files,
            key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)),
            reverse=True
        )[0]
        
        # Read the JSON file
        with open(os.path.join(DATA_DIR, latest_file), 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return jsonify({
            'status': 'success',
            'data': data,
            'count': len(data),
            'file': latest_file
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error retrieving data: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download a data file."""
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

@app.route('/stats')
def get_stats():
    """Get statistics about the crawled data."""
    try:
        # Find the latest CSV file
        csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
        
        if not csv_files:
            return jsonify({
                'status': 'error',
                'message': 'No data available. Please run the crawler first.'
            }), 404
        
        # Sort by modification time (newest first)
        latest_file = sorted(
            csv_files,
            key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)),
            reverse=True
        )[0]
        
        # Read the CSV file
        df = pd.read_csv(os.path.join(DATA_DIR, latest_file), encoding='utf-8-sig')
        
        # Calculate statistics
        stats = {
            'total_restaurants': len(df),
            'sources': df['source'].value_counts().to_dict(),
            'top_categories': df['categories'].str.split(', ').explode().value_counts().head(10).to_dict(),
            'rating_distribution': df['rating'].value_counts().to_dict(),
            'average_rating': df['rating'].replace('No rating', None).astype(float, errors='ignore').mean()
        }
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'file': latest_file
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error calculating statistics: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=12000, debug=True)