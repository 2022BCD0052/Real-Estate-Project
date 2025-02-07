from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load DataFrame and Model
with open('df.pkl', 'rb') as file:
    df = pickle.load(file)
with open('pipeline.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

@app.route('/')
def home():
    return render_template('index.html', sectors=sorted(df['sector'].unique().tolist()),
                           bedrooms=sorted(df['bedRoom'].unique().tolist()),
                           bathrooms=sorted(df['bathroom'].unique().tolist()),
                           balconies=sorted(df['balcony'].unique().tolist()),
                           ages=sorted(df['agePossession'].unique().tolist()),
                           furnishing_types=sorted(df['furnishing_type'].unique().tolist()),
                           luxury_categories=sorted(df['luxury_category'].unique().tolist()),
                           floor_categories=sorted(df['floor_category'].unique().tolist()))

@app.route('/predict', methods=['POST'])
def predict():
    property_type = request.form['property_type']
    sector = request.form['sector']
    bedrooms = float(request.form['bedrooms'])
    bathroom = float(request.form['bathroom'])
    balcony = request.form['balcony']
    property_age = request.form['property_age']
    built_up_area = float(request.form['built_up_area'])
    servant_room = float(request.form['servant_room'])
    store_room = float(request.form['store_room'])
    furnishing_type = request.form['furnishing_type']
    luxury_category = request.form['luxury_category']
    floor_category = request.form['floor_category']

    data = [[property_type, sector, bedrooms, bathroom, balcony, property_age, built_up_area,
             servant_room, store_room, furnishing_type, luxury_category, floor_category]]
    columns = ['property_type', 'sector', 'bedRoom', 'bathroom', 'balcony', 'agePossession',
               'built_up_area', 'servant room', 'store room', 'furnishing_type', 'luxury_category', 'floor_category']
    user_input = pd.DataFrame(data, columns=columns)

    price = np.expm1(model.predict(user_input))[0]
    low = price - 0.2 * price
    high = price + 0.2 * price
    return render_template('result.html',
                       price=round(float(price), 2),
                       low=round(float(low), 2),
                       high=round(float(high), 2))



if __name__ == '__main__':
    app.run(debug=True)
