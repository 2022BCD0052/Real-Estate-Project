from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import base64
from io import BytesIO

app = Flask(__name__)

# ✅ Load dataset
file_path = "datasets/data_viz1.csv"
df = pd.read_csv(file_path)

# ✅ Aggregate numerical data for visualization
num_cols = df.select_dtypes(include=['number']).columns  # Selecting only numerical columns
group_df = df.groupby('sector')[num_cols].mean().reset_index()

# ✅ Create map function
def create_map(highlight_sectors=None, zoom=10):
    fig = px.scatter_mapbox(
        group_df,
        lat="latitude",
        lon="longitude",
        color="price_per_sqft",
        size="built_up_area",
        hover_name="sector",
        color_continuous_scale="Turbo",
        zoom=zoom,
        mapbox_style="carto-positron"
    )

    if highlight_sectors and isinstance(highlight_sectors, list):
        filtered_df = group_df[group_df["sector"].isin(highlight_sectors)]
        
        if not filtered_df.empty:
            highlight_trace = px.scatter_mapbox(
                filtered_df,
                lat="latitude",
                lon="longitude",
                size="built_up_area",
                hover_name="sector",
                color_discrete_sequence=["red"],  # \u2705 Highlight in Red
            ).data[0]

            fig.add_trace(highlight_trace)

            # \u2705 Improved Dynamic Zoom Calculation
            min_lat, max_lat = filtered_df["latitude"].min(), filtered_df["latitude"].max()
            min_lon, max_lon = filtered_df["longitude"].min(), filtered_df["longitude"].max()
            center_lat = (min_lat + max_lat) / 2
            center_lon = (min_lon + max_lon) / 2

            # \u2705 Better Dynamic Zoom Calculation
            lat_diff = max_lat - min_lat
            lon_diff = max_lon - min_lon
            zoom = max(3, 12 - max(lat_diff, lon_diff) * 50)  # More stable zoom adjustment

            fig.update_layout(mapbox=dict(center={"lat": center_lat, "lon": center_lon}, zoom=zoom))

    return pio.to_json(fig)

# ✅ Initial Map JSON
plot_json = create_map()


@app.route('/')
def home():
    return render_template('analysis.html', plot_json=plot_json, sectors=group_df["sector"].tolist())


@app.route('/get_updated_map', methods=['POST'])
def get_updated_map():
    """Update the map when a sector is selected."""
    data = request.json
    selected_sectors = data.get("sector")

    if not selected_sectors:
        return jsonify({"error": "No sector selected"}), 400

    # ✅ Ensure selected_sectors is a list
    if isinstance(selected_sectors, str):  
        selected_sectors = [selected_sectors]  # Convert single string to list

    updated_plot_json = create_map(highlight_sectors=selected_sectors, zoom=13)
    return jsonify({"plot_json": updated_plot_json})



@app.route('/get_wordcloud', methods=['POST'])
def get_wordcloud():
    """Generate a word cloud for the selected sector."""
    data = request.json
    selected_sector = data.get("sector")

    if not selected_sector:
        return jsonify({"error": "No sector selected"}), 400

    # ✅ Generate word cloud based on the sector name
    text_data = f"{selected_sector} real estate investment opportunity affordability luxury"
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

    # ✅ Convert word cloud to image
    img_buffer = BytesIO()
    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()

    return jsonify({"wordcloud": f"data:image/png;base64,{img_base64}"})


@app.route('/reset_map', methods=['POST'])
def reset_map():
    """Reset the map to default view."""
    reset_plot_json = create_map()
    return jsonify({"plot_json": reset_plot_json})




# plot scatter plot for the selected sector

@app.route('/get_default_data', methods=['GET'])
def get_default_data():
    """Provide default word cloud and scatter plot for initial page load."""
    default_sector = df["sector"].mode()[0]  # Choose the most common sector as default

    # ✅ Generate default word cloud
    text_data = f"{default_sector} real estate investment opportunity affordability luxury"
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

    img_buffer = BytesIO()
    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()

    # ✅ Generate default scatter plot
    new_df = df[df["sector"] == default_sector]
    fig = px.scatter(
        new_df,
        x='built_up_area',
        y='price_per_sqft',
        color='bedrooms',
        size='price',
        hover_name='project_name',
        title=f"Real Estate Investment Opportunities in {default_sector}",
        labels={'built_up_area': 'Built-up Area (sqft)', 'price_per_sqft': 'Price per Sqft (INR)'}
    )
    scatter_plot_json = pio.to_json(fig)

    return jsonify({
        "default_sector": default_sector,
        "wordcloud": f"data:image/png;base64,{img_base64}",
        "scatter_plot_json": scatter_plot_json
    })

@app.route('/get_scatter_plot', methods=['POST'])
def get_scatter_plot():
    data = request.json
    selected_sector = data.get("sector")

    if not selected_sector:
        return jsonify({"error": "No sector selected"}), 400

    # \u2705 Ensure filtering happens correctly
    new_df = df[df["sector"] == selected_sector]

    if new_df.empty:
        return jsonify({"error": f"No data available for sector: {selected_sector}"}), 400

    # \u2705 Create Scatter Plot with Correct Columns
    fig = px.scatter(
        new_df,  # \U0001f539 Use the filtered dataframe!
        x="built_up_area",  
        y="price",  
        color="bedRoom",  # \U0001f539 Correct column name
        size="price",  
        hover_name="society",
        title=f"Built-up Area vs Price for {selected_sector}",
        labels={"built_up_area": "Built-up Area (sqft)", "price": "Price (INR)"},
    )

    plot_json = pio.to_json(fig)

    return jsonify({"plot_json": plot_json})
print("Server is running...")
print(df.columns)



#  more plots were there in the original code, but I have removed them to keep the code simple and easy to understand
# get average price per sqft for the selected sector
@app.route('/get_avg_price', methods=['GET'])
def get_avg_price():
    avg_price = df.groupby("sector")["price"].mean().reset_index()

    fig = px.bar(
        avg_price, 
        x="sector", 
        y="price", 
        title="Average Price Per Sector", 
        labels={"price": "Average Price (INR)", "sector": "Sector"}, 
        color="sector"
    )
    return jsonify({"plot_json": pio.to_json(fig)})

# build a pie chart for the selected sector
@app.route('/get_builtup_distribution', methods=['GET'])
def get_builtup_distribution():
    fig = px.histogram(
        df, 
        x="built_up_area", 
        nbins=50, 
        title="Distribution of Built-up Area",
        labels={"built_up_area": "Built-up Area (sqft)"},
        color_discrete_sequence=["#FF5733"]
    )
    return jsonify({"plot_json": pio.to_json(fig)})

# Luxury Score Analysis (Box Plot)

@app.route('/get_luxury_analysis', methods=['GET'])
def get_luxury_analysis():
    fig = px.box(
        df, 
        x="sector", 
        y="luxury_score", 
        title="Luxury Score Across Sectors",
        labels={"luxury_score": "Luxury Score", "sector": "Sector"},
        color="sector"
    )
    return jsonify({"plot_json": pio.to_json(fig)})

#  Property Count by Type (Pie Chart)
@app.route('/get_property_distribution', methods=['GET'])
def get_property_distribution():
    property_counts = df["property_type"].value_counts().reset_index()
    property_counts.columns = ["property_type", "count"]

    fig = px.pie(
        property_counts, 
        names="property_type", 
        values="count", 
        title="Property Type Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    return jsonify({"plot_json": pio.to_json(fig)})




if __name__ == '__main__':
    app.run(debug=True)
