from flask import Flask, render_template, request
import pickle
import pandas as pd
import os

app = Flask(__name__)

model_path = os.path.join('model', 'model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        form = request.form

        data = {
            'Delivery_person_Age': float(form['Delivery_person_Age']),
            'Delivery_person_Ratings': float(form['Delivery_person_Ratings']),
            'Restaurant_latitude': float(form['Restaurant_latitude']),
            'Restaurant_longitude': float(form['Restaurant_longitude']),
            'Delivery_location_latitude': float(form['Delivery_location_latitude']),
            'Delivery_location_longitude': float(form['Delivery_location_longitude']),
            'Vehicle_condition': int(form['Vehicle_condition']),
            'multiple_deliveries': int(form['multiple_deliveries']),
            'Weatherconditions': form['Weatherconditions'],
            'Road_traffic_density': form['Road_traffic_density'],
            'Type_of_order': form['Type_of_order'],
            'Type_of_vehicle': form['Type_of_vehicle'],
            'Festival': form['Festival'],
            'City': form['City']
        }

        df = pd.DataFrame([data])
        df_encoded = pd.get_dummies(df)

        model_columns = model.feature_names_in_
        for col in model_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[model_columns]

        prediction = model.predict(df_encoded)[0]
        return render_template('result.html', prediction=round(prediction, 2))

    except Exception as e:
        return render_template('result.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
