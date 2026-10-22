
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "Dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "risk_model.pkl")


def main():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    df = df.rename(columns={
        "Humid (%)": "Humid",
        "Light (Fux)": "Light",
        "CO2 (pmm)": "CO2"
    })

    required = ["Fruit", "Temp", "Humid", "Light", "CO2", "Class"]
    df = df[required].copy()

    df["Class"] = df["Class"].astype(str).str.strip().str.title()

    for col in ["Temp", "Humid", "Light", "CO2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Fruit"] = df["Fruit"].astype(str).str.strip()
    df = df[df["Class"].isin(["Good", "Bad"])]
    df = df.dropna(subset=["Fruit", "Class"])

    X = df[["Fruit", "Temp", "Humid", "Light", "CO2"]]
    y = df["Class"]

    numeric = ["Temp", "Humid", "Light", "CO2"]

    preprocessor = ColumnTransformer([
        ("numbers", Pipeline([
            ("fill", SimpleImputer(strategy="median")),
            ("scale", StandardScaler())
        ]), numeric),

        ("fruit", Pipeline([
            ("fill", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore"))
        ]), ["Fruit"])
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    print("Training model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    print("Accuracy:", round(accuracy_score(y_test, predictions) * 100, 2), "%")
    print(classification_report(y_test, predictions))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Model saved successfully:", MODEL_PATH)


if __name__ == "__main__":
    main()
