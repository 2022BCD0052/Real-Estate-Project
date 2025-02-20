from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

# Load location and similarity data
location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))
cosine_sim1 = pickle.load(open('datasets/cosine_sim1.pkl', 'rb'))
cosine_sim2 = pickle.load(open('datasets/cosine_sim2.pkl', 'rb'))
cosine_sim3 = pickle.load(open('datasets/cosine_sim3.pkl', 'rb'))

def recommend_properties_with_scores(property_name, top_n=5):
    cosine_sim_matrix = 0.5 * cosine_sim1 + 0.8 * cosine_sim2 + 1 * cosine_sim3

    try:
        property_index = location_df.index.get_loc(property_name)
        sim_scores = list(enumerate(cosine_sim_matrix[property_index]))
        sorted_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        top_indices = [i[0] for i in sorted_scores[1:top_n + 1]]
        top_scores = [i[1] if i[1] is not None else 0 for i in sorted_scores[1:top_n + 1]]  # Ensure valid numbers
        top_properties = location_df.index[top_indices].tolist()

        recommendations_df = pd.DataFrame({
            'PropertyName': top_properties,
            'SimilarityScore': top_scores
        })
        return recommendations_df.to_dict(orient='records')

    except KeyError:
        return []  # Return empty list if property name not found

@app.route('/', methods=['GET', 'POST'])

def home():
    locations = sorted(location_df.columns.to_list())
    apartments = sorted(location_df.index.to_list())
    recommendations = []
    search_results = []

    if request.method == 'POST':
        if 'search' in request.form:
            selected_location = request.form['location']
            radius = float(request.form['radius'])

            # Filter locations based on radius
            result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()
            search_results = [f"{key} - {round(value / 1000)} kms" for key, value in result_ser.items()]

        if 'recommend' in request.form:
            selected_apartment = request.form['apartment']
            recommendation_df = recommend_properties_with_scores(selected_apartment)
            recommendations = recommendation_df.to_dict(orient='records')
    print("Recommendations:", recommendations)  # Debugging line

    return render_template('recommenderSystem.html', locations=locations, apartments=apartments, recommendations=recommendations, search_results=search_results)

if __name__ == '__main__':
    app.run(debug=True)
