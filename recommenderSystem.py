from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd
import numpy as np
import logging
from flask_caching import Cache
from geopy.distance import geodesic  # For accurate distance calculations

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Setup logging
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load datasets safely
try:
    location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
    cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
    cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
    cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))
    apartments_df = pd.read_csv('appartments.csv')  # Ensure this file exists
except Exception as e:
    logging.error(f"Error loading datasets: {e}")
    location_df, cosine_sim1, cosine_sim2, cosine_sim3, apartments_df = None, None, None, None, None

def recommend_properties_with_scores(property_name, top_n=5):
    """Recommend similar properties based on similarity matrices."""
    if location_df is None:
        return []

    # Combined similarity matrix
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    if property_name not in location_df.index:
        return []

    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]
    top_properties = location_df.index[top_indices].tolist()

    return [{'PropertyName': prop, 'SimilarityScore': round(score, 3)} for prop, score in zip(top_properties, top_scores)]

@app.route('/')
def index():
    try:
        # Ensure the datasets are loaded properly
        if location_df is None or location_df.empty:
            logging.error("Error: location_df is empty or not loaded")
            return "Error: Location data is not available", 500

        # Extract locations and apartments
        locations = location_df.columns.tolist()
        apartments = location_df.index.tolist()


        return render_template('aa.html', locations=locations, apartments=apartments)

    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return "Error: Something went wrong while loading the page", 500

@app.route('/search', methods=['POST'])
@cache.cached(timeout=60, query_string=True)
def search():
    """Find properties within a given radius with filtering."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400

        selected_location = data.get('location')
        radius = data.get('radius')

        if not selected_location or radius is None:
            return jsonify({'error': "Both 'location' and 'radius' are required."}), 400

        try:
            radius = float(radius)
        except ValueError:
            return jsonify({'error': "'radius' must be a valid number."}), 400

        if location_df is None or selected_location not in location_df.columns:
            return jsonify({'error': f"Location '{selected_location}' not found."}), 404

        result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()
        results = [{"name": key, "distance_km": round(value / 1000, 2)} for key, value in result_ser.items()]

        return jsonify(results)
    except Exception as e:
        logging.error(f"Error in search: {e}")
        return jsonify({'error': 'Something went wrong'}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Recommend properties based on a selected apartment."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Missing JSON body'}), 400

        selected_apartment = data.get('apartment')

        if not selected_apartment:
            return jsonify({'error': "Missing 'apartment' parameter."}), 400

        recommendations = recommend_properties_with_scores(selected_apartment)

        if not recommendations:
            return jsonify({'error': f"No recommendations found for '{selected_apartment}'."}), 404

        return jsonify(recommendations)
    except Exception as e:
        logging.error(f"Error in recommend: {e}")
        return jsonify({'error': 'Something went wrong'}), 500

if __name__ == '__main__':
    app.run(debug=True)
