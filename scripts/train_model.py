import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Paths
labeled_dir = "data/labeled"
model_dir = "model"
os.makedirs(model_dir, exist_ok=True)

# Load all labeled CSVs (p1_labeled.csv to p5_labeled.csv)
dataframes = []
for i in range(1, 6):
    path = os.path.join(labeled_dir, f"p{i}_labeled.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        dataframes.append(df)
    else:
        print(f"[!] Skipping p{i}_labeled.csv — not found.")

# Combine all into one DataFrame
df_all = pd.concat(dataframes, ignore_index=True)

# Drop rows with missing text/font_size
df_all.dropna(subset=["text", "font_size"], inplace=True)

# Encode font_name with 'unknown' added for unseen fonts during inference
unique_fonts = list(df_all["font_name"].astype(str).unique())
if "unknown" not in unique_fonts:
    unique_fonts.append("unknown")

font_encoder = LabelEncoder()
font_encoder.fit(unique_fonts)
df_all["font_name_encoded"] = font_encoder.transform(df_all["font_name"].astype(str))

# Save font_name encoder
joblib.dump(font_encoder, os.path.join(model_dir, "font_encoder.pkl"))

# Features used for training
features = ["font_size", "is_bold", "is_title_case", "is_uppercase", "line_len", "font_name_encoded"]
X = df_all[features]

# 1️⃣ Train is_heading model (binary classifier)
y_heading = df_all["is_heading"]
X_train, X_val, y_train, y_val = train_test_split(X, y_heading, test_size=0.2, random_state=42)

heading_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
heading_model.fit(X_train, y_train)
joblib.dump(heading_model, os.path.join(model_dir, "heading_model.pkl"))
print("[✓] Trained and saved heading_model.pkl")

# 2️⃣ Train heading_level model (multi-class classifier for H1/H2/H3)
df_headings = df_all[df_all["is_heading"] == 1].copy()
df_headings = df_headings[df_headings["heading_level"].isin(["H1", "H2", "H3"])]

if not df_headings.empty:
    level_encoder = LabelEncoder()
    df_headings["heading_level_encoded"] = level_encoder.fit_transform(df_headings["heading_level"])

    y_level = df_headings["heading_level_encoded"]
    X_level = df_headings[features]

    level_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    level_model.fit(X_level, y_level)

    joblib.dump(level_model, os.path.join(model_dir, "level_model.pkl"))
    joblib.dump(level_encoder, os.path.join(model_dir, "level_encoder.pkl"))
    print("[✓] Trained and saved level_model.pkl")
else:
    print("[!] Skipping level_model training — no H1/H2/H3 samples found.")
