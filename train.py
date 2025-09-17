import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle
import os

# Load the dataset
df = pd.read_csv("train.csv")

# Clean the target column
df['Time_taken(min)'] = df['Time_taken(min)'].str.extract('(\d+)').astype(int)

# Drop irrelevant columns
df.drop(['ID', 'Delivery_person_ID', 'Order_Date'], axis=1, inplace=True)

# Fill missing values (if any)
df.fillna({
    'Weatherconditions': 'Sunny',
    'Road_traffic_density': 'Medium',
    'Festival': 'No',
    'City': 'Urban',
    'Time_Orderd': df['Time_Orderd'].mode()[0],
    'Time_Order_picked': df['Time_Order_picked'].mode()[0]
}, inplace=True)

# Convert time columns to datetime
df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], format='%H:%M:%S', errors='coerce')
df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'], format='%H:%M:%S', errors='coerce')

# Calculate time difference in minutes
df['prep_time_mins'] = (df['Time_Order_picked'] - df['Time_Orderd']).dt.total_seconds() / 60.0
df['prep_time_mins'] = df['prep_time_mins'].fillna(0)

# Drop original time columns
df.drop(['Time_Orderd', 'Time_Order_picked'], axis=1, inplace=True)

# Separate features and target
X = df.drop('Time_taken(min)', axis=1)
y = df['Time_taken(min)']

# One-hot encode categorical columns
X_encoded = pd.get_dummies(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the trained model
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

# Save the columns used in training (for consistent prediction later)
with open("columns.pkl", "wb") as f:
    pickle.dump(X_encoded.columns.tolist(), f)

print("Training complete. model.pkl and columns.pkl saved.")
