# InsureAI — Insurance Coverage Bundle Recommender

A multiclass classification system that predicts the most suitable insurance coverage bundle for a customer, built for an academic hackathon competition.

The system consists of three parts:
- **ML pipeline** — offline training with LightGBM and a self-contained inference module (`solution.py`) following the judge's submission specification
- **REST API** — a FastAPI backend that serves predictions over HTTP
- **Frontend** — a React + Vite interface that collects customer information and displays the model's recommendation

---

## Project Structure

```
DataQuest7/
│
├── solution.py               # Judge submission entry point (self-contained)
├── model.joblib              # Serialized trained LightGBM model (~4.9 MB)
├── requirements.txt          # Minimal inference dependencies (judge-required)
│
├── src/
│   ├── features.py           # Data cleaning and feature engineering (training)
│   ├── train.py              # Full training pipeline with cross-validation
│   └── utils.py              # Utility helpers
│
├── API/
│   ├── __init__.py
│   └── main.py               # FastAPI application, CORS, /predict endpoint
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── main.tsx
│       └── app/
│           ├── App.tsx
│           └── components/
│               ├── assessment-form.tsx   # Multi-step intake form
│               ├── result-panel.tsx      # Recommendation modal
│               ├── hero-section.tsx
│               └── background-effects.tsx
│
├── data/
│   ├── train.csv             # Training dataset (not committed to public repo)
│   └── test.csv              # Evaluation dataset
│
├── notebooks/                # Reserved for exploratory work
├── eda.py                    # Exploratory data analysis script
└── venv/                     # Python virtual environment (not committed)
```

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### 1. Clone the repository

```bash
git clone <repository-url>
cd DataQuest7
```

### 2. Python virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Python dependencies

Install inference dependencies (required by judge):

```bash
pip install pandas numpy joblib lightgbm
```

Install API server dependencies:

```bash
pip install fastapi "uvicorn[standard]"
```

To retrain the model, also install:

```bash
pip install scikit-learn
```

### 4. Frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the Backend (API Server)

From the project root (`DataQuest7/`), with the virtual environment active:

```bash
uvicorn API.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: **`http://localhost:8000`**

The `--reload` flag enables hot-reload during development. Remove it for stable runs.

---

## Swagger / API Documentation

FastAPI generates interactive documentation automatically.

Once the server is running, open: **`http://localhost:8000/docs`**

This provides a full interactive UI to explore and test all endpoints.

---

## Running the Frontend

```bash
cd frontend
npm run dev
```

The application will be available at: **`http://localhost:5173`**

The frontend sends POST requests to `http://localhost:8000/predict`. Both the API server and the Vite dev server must be running simultaneously.

---

## API Endpoints

### `GET /health`

Simple liveness check.

**Response:**
```json
{ "status": "ok" }
```

---

### `POST /predict`

Submits a customer profile and returns the recommended coverage bundle class.

**Request body (JSON):**

| Field | Type | Description |
|---|---|---|
| `age` | int | Customer age |
| `occupation` | string | `professional`, `business`, `employee`, `retired`, `self-employed` |
| `income` | float | Estimated annual income |
| `maritalStatus` | string | `single`, `married`, `divorced`, `widowed` |
| `dependents` | int | Number of total dependents |
| `hasChildren` | bool | Whether any dependents are children under 18 |
| `homeOwner` | bool | Whether the customer owns their home |
| `vehicles` | int | Number of vehicles |
| `propertyValue` | float | Estimated property value |
| `currentInsurance` | string | Existing provider or `"none"` |
| `claimsHistory` | int | Number of claims filed in the last 5 years |
| `riskTolerance` | string | `low`, `medium`, `high` |

**Response:**
```json
{ "bundle_id": 3 }
```

`bundle_id` is an integer in the range `[0, 7]` corresponding to the model's predicted coverage bundle class.

---

## How the AI Model Works

### Dataset

The training data (`train.csv`) contains approximately 60,000 insurance policy records with 29 columns. The target variable is `Purchased_Coverage_Bundle`, an integer class label (0–9) representing which coverage bundle a customer historically purchased.

### Feature Engineering

Three high-cardinality or low-information columns are dropped: `Employer_ID` (94% missing), `Broker_ID` (14% missing), and `Region_Code`.

The `Policy_Start_Month` string column is replaced with two cyclical features using trigonometric encoding:

$$\text{month\_sin} = \sin\!\left(\frac{2\pi \cdot m}{12}\right), \quad \text{month\_cos} = \cos\!\left(\frac{2\pi \cdot m}{12}\right)$$

This preserves the circular nature of months — December is numerically adjacent to January.

Five columns are encoded as the `category` dtype, which LightGBM handles natively without one-hot encoding:
`Broker_Agency_Type`, `Deductible_Tier`, `Acquisition_Channel`, `Payment_Schedule`, `Employment_Status`.

Missing values are imputed with domain-appropriate defaults: `Child_Dependents` → `0`, `Deductible_Tier` → `"Unknown"`, `Acquisition_Channel` → `"Unknown"`.

The final feature set contains **25 columns**.

### Class Imbalance Handling

Two strategies are applied:

1. **Rare class merging** — classes 8 and 9 each contain fewer than 10 training samples. These are remapped to class 7 during training only. The inference output still uses the original class space.

2. **Inverse-sqrt sample weights** — each sample is weighted by $1/\sqrt{\text{class\_count}}$, normalized so the maximum weight is 1. This prevents the majority class from dominating gradient updates.

### Model

A **LightGBM** gradient-boosted tree classifier (`multiclass` objective) is used.

Key hyperparameters:

| Parameter | Value | Rationale |
|---|---|---|
| `num_leaves` | 31 | Limits tree complexity |
| `max_depth` | 6 | Prevents overfitting |
| `learning_rate` | 0.05 | Slow learning for better generalization |
| `n_estimators` | ~210 | Set by CV early stopping |
| `reg_alpha / reg_lambda` | 1.0 | L1 + L2 regularization |
| `subsample` | 0.8 | Row subsampling per tree |
| `colsample_bytree` | 0.8 | Feature subsampling per tree |

### Training Strategy

A **5-fold StratifiedKFold** cross-validation is used to find the stable best iteration. Each fold uses early stopping (50 rounds patience). The final model is trained on the full dataset at `avg(best_iteration) + 10` to account for the additional data.

**Cross-validation result:** Macro-F1 = **0.5817 ± 0.0102**

### Inference Flow

```
Raw customer row (JSON)
  → API maps frontend fields → 25 model features
  → solution.preprocess(df)
      - drop unused columns
      - fill missing values
      - cyclical month encoding
      - category dtype casting
  → solution.predict(model, df)
      - select FEATURE_COLUMNS in training order
      - model.predict(X) → class label [0-7]
  → {"bundle_id": N}
```

---

## Judge Submission

The judge evaluates the solution using exactly three functions from `solution.py`:

```python
preprocess(df)   # Cleans and encodes a raw input DataFrame
load_model()     # Loads model.joblib from the working directory
predict(df, model)  # Returns predictions given preprocessed df and model
```

### Constraints honored

- `solution.py` is fully **self-contained** — it imports nothing from `src/`
- All preprocessing constants (`FEATURE_COLUMNS`, `CATEGORICAL_COLUMNS`, `MONTH_MAP`) are hardcoded inline
- `load_model()` loads from `model.joblib` in the working directory
- `predict()` returns a dictionary with `User_ID` and `recommended_bundle` lists
- `requirements.txt` lists only inference-time dependencies: `pandas`, `numpy`, `joblib`, `lightgbm`

To retrain and regenerate `model.joblib`:

```bash
python -c "from src.train import train_model; train_model('data/train.csv')"
```

---

## Technologies Used

| Layer | Technology |
|---|---|
| ML model | LightGBM 4.x |
| ML utilities | scikit-learn (StratifiedKFold, f1_score) |
| Data processing | pandas, numpy |
| Model serialization | joblib |
| API server | FastAPI + uvicorn |
| Frontend framework | React 18 + TypeScript |
| Frontend build tool | Vite 6 |
| Styling | Tailwind CSS v4 |
| UI components | Radix UI, MUI, lucide-react |
| Animations | Motion (motion/react) |
| Python version | 3.10 |

---

## Known Limitations

- **Class imbalance is severe.** Classes 8 and 9 have fewer than 10 samples each and are merged into class 7 during training. The model cannot reliably distinguish all 10 original bundle types.
- **Macro-F1 of ~0.58** reflects the inherent difficulty of the task with the given dataset size and class distribution. Minority classes remain harder to predict.
- **Feature mapping is approximate.** The frontend collects user-friendly fields (e.g., `income`, `vehicles`) that are mapped to model features by the API. This mapping involves assumptions (e.g., payment schedule defaults to "Monthly") that may not reflect real policy data.
- **No authentication.** The API has no access control and is intended for local/demo use only.
- **CORS is open to localhost only.** Deploying to a remote server would require updating the allowed origins.

---

## Future Improvements

- Collect more samples for rare bundles to make full 10-class prediction viable
- Expose confidence scores from `model.predict_proba()` rather than just the top-1 class
- Add a `/explain` endpoint using SHAP values to provide per-prediction feature attribution
- Extend the frontend form with fields that better align with actual model features (`Policy_Start_Month`, `Acquisition_Channel`, etc.)
- Add input validation and error handling to the frontend when the API is unreachable
- Persist user sessions and prediction history

---

## Authors

Developed for the **DataQuest Hackathon — Session 7**

| Name | Role |
|---|---|
| Team member(s) | ML pipeline, API, frontend |

*GL3 S2 — Academic year 2025/2026*
