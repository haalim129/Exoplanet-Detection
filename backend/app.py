import joblib
from flask import Flask, request, jsonify
import os
import pandas as pd
import numpy as np

app = Flask(__name__, static_folder='fronted', static_url_path='')

# Serve index.html at the root
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Load trained model and scaler
svm_model = joblib.load("svm.pkl")
scaler = joblib.load("scaler.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files.get('file')

    # Check if file is provided
    if not file:
        return jsonify({'error': 'No file uploaded. Please upload a CSV file with flux value.'})

    # Ensure file is a CSV
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Invalid file type. Please upload a CSV file with flux value.'})

    try:
        # Read CSV using 'python' engine with on_bad_lines option
        data = pd.read_csv(file, encoding='latin1', sep=',', engine='python', on_bad_lines='skip')
    except Exception as e:
        return jsonify({'error': f'Not able to read CSV file: {str(e)}'})

    # Drop 'LABEL' column if exists
    if 'LABEL' in data.columns:
        data = data.drop(columns=['LABEL'])

    # Standardize column names: strip extra spaces and convert to uppercase
    data.columns = data.columns.str.strip().str.upper()

    # Select numeric columns
    input_data = data.select_dtypes(include=['number'])

    # Ensure required FLUX column is present
    if 'FLUX' not in data.columns and not any(col.startswith('FLUX.') for col in data.columns):
        return jsonify({'error': 'Flux value should be 3197.'})

    # Ensure FLUX value is exactly 3197
    if len(input_data.columns) != 3197:
        return jsonify({'error': 'Flux value should be 3197.'})

    try:
        # Apply the saved scaler to the input data
        input_data_scaled = scaler.transform(input_data)
    except Exception as e:
        return jsonify({'error': 'Flux values should be 3197.'})

    try:
        # Predict using the loaded model
        prediction = svm_model.predict(input_data_scaled)
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'})

    # Decide result message based on prediction
    if 1 in prediction:
        result_message = "Congratulation! Exoplanet detected in your data. Check the detailed flux analysis below."
    else:
        result_message = "No exoplanet found. Review the flux graph for potential insights."

    # Extract flux data for chart:
    if 'FLUX' in data.columns:
        flux_data = data['FLUX'].tolist()
    elif any(col.startswith('FLUX.') for col in data.columns):
        flux_cols = [col for col in data.columns if col.startswith('FLUX.')]
        flux_data = data[flux_cols].iloc[0].tolist()
    else:
        flux_data = None

    return jsonify({
        'prediction': prediction.tolist(),
        'result_message': result_message,
        'flux_data': flux_data
    })

if __name__ == '__main__':
    app.run(debug=True)
