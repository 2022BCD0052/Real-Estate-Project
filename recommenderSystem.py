from flask import Flask, request, jsonify, render_template
import pickle
import pandas as pd

app = Flask(__name__)

# Load datasets
try:
    location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
    cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
    cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
    cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))
except Exception as e:
    print("Error loading datasets:", e)

def recommend_properties_with_scores(property_name, top_n=5):
    """Recommend similar properties based on the similarity matrices."""
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    if property_name not in location_df.index:
        return []

    sim_scores = list(enumerate(cosine_sim_matrix[location_df.index.get_loc(property_name)]))
    sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
    top_scores = [i[1] for i in sorted_scores[1:top_n + 1]]
    top_properties = location_df.index[top_indices].tolist()

    return [{'PropertyName': prop, 'SimilarityScore': score} for prop, score in zip(top_properties, top_scores)]

@app.route('/')
def index():
    """Render the main HTML page with dropdowns pre-filled."""
    locations = location_df.columns.tolist()
    apartments = location_df.index.tolist()
    return render_template('aa.html', locations=locations, apartments=apartments)

@app.route('/search', methods=['POST'])
def search():
    """Find properties within a given radius."""
    data = request.json
    selected_location = data.get('location')
    radius = float(data.get('radius', 0))

    if selected_location not in location_df.columns:
        return jsonify({'error': 'Invalid location'}), 400

    result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()
    results = [{"name": key, "distance_km": round(value / 1000, 2)} for key, value in result_ser.items()]

    return jsonify(results)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Recommend properties based on a selected apartment."""
    data = request.json
    selected_apartment = data.get('apartment')

    recommendations = recommend_properties_with_scores(selected_apartment)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
