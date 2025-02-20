from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load location distance dataset
location_df = pickle.load(open('datasets/location_distance.pkl', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def home():
    locations = sorted(location_df.columns.to_list())
    recommendations = []

    if request.method == 'POST':
        selected_location = request.form['location']
        radius = float(request.form['radius'])

        # Filtering locations within the given radius
        result_ser = location_df[location_df[selected_location] < radius * 1000][selected_location].sort_values()

        # Format recommendations
        recommendations = [f"{key} - {round(value / 1000)} kms" for key, value in result_ser.items()]

    return render_template('recommenderSystem.html', locations=locations, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
