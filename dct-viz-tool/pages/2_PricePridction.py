import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Set Page Configuration
st.set_page_config(page_title="Viz Demo")

# Load DataFrame
with open('df.pkl', 'rb') as file:
    df = pickle.load(file)

st.write("Available columns in DataFrame:", df.columns.tolist())

# Page Header
st.header('Enter your inputs')

# Property Type Selection
property_type = st.selectbox('Property Type', ['flat', 'house'])

# Sector Selection
sector = st.selectbox('Sector', sorted(df['sector'].unique().tolist()))

# Number of Bedrooms
bedrooms = float(st.selectbox('Number of Bedrooms', sorted(df['bedRoom'].unique().tolist())))

# Number of Bathrooms
bathroom = float(st.selectbox('Number of Bathrooms', sorted(df['bathroom'].unique().tolist())))

# Number of Balconies
balcony = st.selectbox('Balconies', sorted(df['balcony'].unique().tolist()))

# Property Age
property_age = st.selectbox('Property Age', sorted(df['agePossession'].unique().tolist()))

# Built-up Area Input
built_up_area = float(st.number_input('Built Up Area'))

# Servant Room Availability
servant_room = float(st.selectbox('Servant Room', [0.0, 1.0]))

# Store Room Availability
store_room = float(st.selectbox('Store Room', [0.0, 1.0]))

# Furnishing Type (Fixing incorrect column name)
furnishing_type = st.selectbox('Furnishing Type', sorted(df['furnishing_type'].unique().tolist()))

# Floor Category & Luxury Category (Fixing incorrect column names)
luxury_category = st.selectbox('Luxury Category', sorted(df['luxury_category'].unique().tolist()))
floor_category = st.selectbox('Floor Category', sorted(df['floor_category'].unique().tolist()))

if st.button('Predict Price'):

    data = [[
        property_type, sector, bedrooms, bathroom, balcony, property_age, built_up_area,
        servant_room, store_room, furnishing_type, luxury_category, floor_category
    ]]
    
    # Corrected column names
    columns = [
        'property_type', 'sector', 'bedRoom', 'bathroom', 'balcony', 'agePossession',
        'built_up_area', 'servant room', 'store room', 'furnishing_type', 'luxury_category', 'floor_category'
    ]
    
    # Create DataFrame
    user_input = pd.DataFrame(data, columns=columns)

    # Load Model
    with open("pipeline.pkl", "rb") as model_file:
        model = pickle.load(model_file)
    
    # Predict Price
    price = np.expm1(model.predict(user_input))[0]
    low = price - 0.2 * price
    high = price + 0.2 * price
    
    # Display Price

    st.write(f"The price of flat or house between \u20b9{price:.2f} cr and \u20b9{high:.2f} cr")
