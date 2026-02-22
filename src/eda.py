import pandas as pd

# Load data
train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")

# Basic shapes
print("Train shape:", train.shape)
print("Test shape:", test.shape)

# Columns and types
print("\nColumns and types:")
print(train.dtypes)

# First rows
print("\nFirst 5 rows:")
print(train.head())

# Missing values
print("\nMissing values per column:")
print(train.isnull().sum())

# Target distribution
TARGET = "Purchased_Coverage_Bundle"
print(f"\nTarget distribution ({TARGET}):")
print(train[TARGET].value_counts())
print("\nTarget percentage:")
print(train[TARGET].value_counts(normalize=True) * 100)

# Quick feature insights
print("\nNumber of features:", train.shape[1] - 1)  # excluding target
print("Number of rows:", train.shape[0])

# ID or weird columns
ID_COL = "User_ID"
if ID_COL in train.columns:
    print(f"\nColumn '{ID_COL}' exists and should not be used as feature.")

# Optional: check for text/date columns
for col in train.columns:
    if train[col].dtype == 'object':
        print(f"Column '{col}' looks like text/categorical.")

print("\nMissing values:")
print(train.isnull().sum())

print("\nData types:")
print(train.dtypes)

TARGET = "Purchased_Coverage_Bundle"
ID_COL = "User_ID"

X = train.drop(columns=[TARGET])
y = train[TARGET]