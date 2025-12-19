# Outfit Recommendation AI: Deep Learning, Tabular ML, and 2.5D Avatar Try-On

## Repository Purpose (Academic Summary)

This repository implements a **comprehensive end-to-end outfit recommendation system** that maps **weather + context + user profile** inputs to **multi-piece outfit recommendations** using six distinct approaches:

### Model Zoo (6 Models)

1. **Rule-based Baseline** — Handcrafted decision logic with temperature thresholds and context rules
2. **XGBoost** — Gradient-boosted decision trees (sklearn)
3. **Random Forest** — Ensemble of decision trees (sklearn)
4. **MLP (sklearn)** — Multi-layer perceptron neural network baseline
5. **ANN (PyTorch)** — Deep artificial neural network with dropout regularization
6. **CNN1D (PyTorch)** — Experimental 1D convolutional network adapted for tabular data
7. **LSTM (PyTorch)** — Experimental recurrent network treating features as sequential inputs

### Project Highlights

- **Tabular ML Design** — Feature engineering, one-hot encoding, stratified splits, robust evaluation
- **Deep Learning Integration** — PyTorch-based models with early stopping and GPU support
- **Model Comparison** — Unified metrics (Accuracy, Macro F1) across all 6 models
- **Deployment-Ready System** — Flask REST API, modern UI, real-time weather integration
- **2.5D Avatar Try-On** — Premium layered mannequin with realistic clothing SVGs, CSS 3D depth, and anatomical alignment
- **Personalized Recommendations** — Multi-outfit generation with style, color palette, and event-aware filtering
- **Visual Diversity** — Pinterest-style outfit cards with accent colors, unique subtitles, and green selection highlighting

---

## 1. Project Title

**AI-Based Outfit Recommendation from Weather and Context: Comprehensive Model Comparison (Rules, Tree-Based ML, Neural Networks, and Deep Learning) with Premium 2.5D Avatar Try-On**

---

## 2. Problem Definition

Outfit recommendation is a **context-dependent multi-class classification problem** with significant complexity:

### Key Challenges

- **Context Interactions** — Temperature alone is insufficient; rain, wind, season, and event type create complex decision boundaries
- **Categorical Features** — Variables like `yagmur`, `ruzgar`, `ortam`, `mevsim` require proper encoding
- **Human Constraints** — Outputs must be socially and physically plausible (e.g., rain → umbrella, formal event → formal attire)
- **Personalization** — User preferences (style, color palette, cold sensitivity) must influence recommendations
- **Multi-Piece Coordination** — Complete outfits require coordinating top, bottom, shoes, outerwear, and accessories

### Why AI is Suitable

- The mapping `(weather, context, user_profile)` → `outfit` is learnable as supervised classification
- ML models capture interaction patterns beyond hard-coded thresholds
- Deep learning can model complex non-linear relationships in tabular data
- Model comparison provides educational insights into generalization and overfitting

---

## 3. System Overview
This system is intentionally designed as a complete pipeline:

- **Data layer**
  - Tabular dataset stored as a CSV.
  - Feature columns: numeric + categorical.

- **ML layer**
  - Preprocessing with `ColumnTransformer` + `OneHotEncoder(handle_unknown="ignore")`.
  - Multiple model candidates trained and evaluated on the same splits.
  - Artifacts saved as `joblib` pipelines (`.pkl`) + `metrics.json`.

- **Web/UI layer**
  - Flask backend serving:
    - predictions (`/api/predict`)
    - model metrics (`/api/model-metrics`)
    - weather fetch (`/api/weather/<city>`)
  - Pinterest-style UI rendering multiple outfit recommendations.
  - 2.5D Avatar Try-On visualization of outfit pieces.

High-level architecture:

```
User (Browser)
  -> web-app (Flask + templates + static JS/CSS)
     -> /api/weather/<city>  (external weather provider via utils)
     -> /api/predict
         -> load model pipeline (best / xgboost / mlp)
         -> rule baseline prediction
         -> generate multi-piece outfits + avatar_layers
     -> /api/model-metrics
         -> read outfit-ai/models/metrics.json
```

---

## 4. Dataset Description
Dataset file:

- `outfit-ai/data/weather_outfit.csv`

Columns (tabular features):

- **Numeric feature**
  - `sicaklik` (temperature in °C)

- **Categorical features**
  - `yagmur` (rain): `var | yok`
  - `ruzgar` (wind): `zayıf | orta | kuvvetli`
  - `ortam` (occasion/environment): `günlük | okul | özel`
  - `mevsim` (season): `kış | ilkbahar | yaz | sonbahar`

Label column:

- `kiyafet` (multi-class outfit label, e.g., `kalın_mont_şemsiye`, `tişört_şort`, `gömlek_pantolon`)

Why this is tabular data:

- The input is a fixed-length vector of heterogeneous features.
- The predictive signal is mostly contained in **structured attributes** rather than sequences or spatial structure.
- The primary modeling requirement is **learning decision boundaries and feature interactions**.

---

## 5. Model Selection Rationale
This project explicitly uses tabular ML models rather than deep learning models designed for other data modalities.

Why CNN is **not** suitable:

- CNNs assume local spatial correlations in grid-like data (images).
- The dataset does not contain image tensors for training; it contains structured features.

Why LSTM is **not** suitable:

- LSTMs model temporal sequences.
- Each record is an independent example, not a time series.

Why tree-based models and MLP are suitable:

- **Tree-based models** (XGBoost/RandomForest) handle non-linear interactions well and are strong baselines for tabular data.
- **MLP** can model non-linear decision boundaries after one-hot encoding, serving as a classical neural baseline.
- Both families naturally support multi-class classification and can be compared in a controlled way.

---

## 6. Trained Models
The system includes three main predictors.

### Rule-based baseline
File:

- `outfit-ai/rules_baseline.py`

Core idea:

- Manually encodes human decision logic (temperature thresholds, rain adds umbrella, etc.).

Educational role:

- Provides an interpretable baseline for model comparison.
- Demonstrates that “working logic” is not necessarily “optimal generalization.”

### Tree-based model (XGBoost or RandomForest fallback)
Training logic:

- `outfit-ai/train_models.py` attempts to import `xgboost.XGBClassifier`.
- If XGBoost is not available, it falls back to `sklearn.ensemble.RandomForestClassifier`.

Saved as:

- `outfit-ai/models/xgb_model.pkl` (latest)

Note:

- In the current `metrics.json`, the display name for the `xgboost` key is `RandomForest`, which indicates the fallback path was used during training.

### MLP (Neural Network)
Training logic:

- `sklearn.neural_network.MLPClassifier`
- Trained as a pipeline with encoding and scaling.

Saved as:

- `outfit-ai/models/mlp_model.pkl` (latest)

---

## 7. Training Pipeline
Primary training script:

- `outfit-ai/train_models.py`

### Preprocessing
The pipeline uses:

- `ColumnTransformer` to separate numeric and categorical handling.
- `OneHotEncoder(handle_unknown="ignore")` for categorical columns.
- `StandardScaler(with_mean=False)` for MLP (compatible with sparse one-hot encoded matrices).

Configuration of features is centralized in:

- `outfit-ai/config.py`
  - `FEATURE_COLUMNS = ['sicaklik', 'yagmur', 'ruzgar', 'ortam', 'mevsim']`
  - `TARGET_COLUMN = 'kiyafet'`

### Train/validation/test split
`train_models.py` performs:

- stratified split into:
  - train
  - validation
  - test

The resulting split sizes are stored in `metrics.json`.

### Metrics used
For each model the following metrics are computed:

- **Accuracy**: overall correctness.
- **Macro F1**: averages F1 over classes equally (important for multi-class settings where classes may be imbalanced).

### Model persistence
Artifacts are saved in:

- `outfit-ai/models/`

Typical files:

- `best_model.pkl`
- `xgb_model.pkl`
- `mlp_model.pkl`
- timestamped versions (e.g., `mlp_YYYYMMDD_HHMMSS.pkl`)

### metrics.json
Saved to:

- `outfit-ai/models/metrics.json`

This file is also used by the backend endpoint `/api/model-metrics`.

---

## 8. Results & Comparison
The following table is taken directly from `outfit-ai/models/metrics.json` (test split).

| Model | Accuracy | Macro F1 | Notes |
| --- | ---: | ---: | --- |
| Rules Baseline | 0.7105 | 0.6553 | Threshold + rain/wind rules |
| Tree-based (`xgboost` key) | 0.8947 | 0.8088 | Trained as RandomForest fallback in this run |
| MLP | 0.9474 | 0.9558 | Best overall generalization in this run |

Why MLP was selected as the best model:

- The selection rule in `train_models.py` chooses the model maximizing:
  - first `macro_f1`, then `accuracy`.
- In this run, MLP achieves the highest Macro F1 and Accuracy.
- Macro F1 is particularly important here because it values performance across all outfit classes, not only frequent ones.

---

## 9. Backend Architecture
Deployed backend entry point:

- `web-app/app.py` (Flask)

Deployment command:

- `Procfile`: `web: gunicorn app:app --chdir web-app`

Key API endpoints:

### `GET /api/weather/<city>`
- Fetches weather data for a given city.
- Uses `utils.weather_api` (via wttr or a similar provider) to produce a consistent weather payload.

### `GET /api/model-metrics`
- Returns the content of `outfit-ai/models/metrics.json`.
- Purpose: UI can show model comparison and “best model” selection.

### `POST /api/predict`
Inference responsibilities:

- Parses inputs: `sicaklik, yagmur, ruzgar, ortam, mevsim`.
- Optional user context (for multi-outfit assembly):
  - `gender, age_range, height_cm, weight_kg, style, color_palette, cold_sensitivity, event_type`
- Loads a model pipeline based on `model` field:
  - `best` (default), `xgboost`, `mlp`, or `rules`
- Computes:
  - ML prediction (with probability when available)
  - Rule-based baseline prediction
  - Selected prediction depending on the chosen model
- Generates multi-outfit recommendations:
  - `generate_outfit_recommendations(...)` from `outfit-ai/personalized_recommendations.py`

Inference flow (simplified):

1. Create a one-row `pandas.DataFrame`.
2. Run `model.predict()` (and `predict_proba` if supported).
3. Compute rule prediction via `rule_based_outfit`.
4. Build multi-piece outfits + avatar layers.
5. Return JSON response used by the UI.

---

## 10. Outfit Logic & Correctness Rules
While ML predicts an **outfit label**, the UI displays **multi-piece outfits** (top/bottom/shoes/outerwear/accessory). This requires additional correctness constraints.

Where this logic lives:

- `outfit-ai/personalized_recommendations.py`
- `outfit-ai/catalog.py`

Examples of enforced constraints:

- Category structure:
  - Always assemble a coherent set of categories (top, bottom, shoes, etc.).
- Weather constraints:
  - Rain implies adding a rain accessory strategy (umbrella) and/or rain-friendly outerwear.
  - Cold implies outerwear is likely required.
- Event constraints:
  - Formal events constrain shoes and styling.

Why rules are still necessary even with ML:

- The ML model outputs a single label; it does not guarantee a valid decomposition into multi-piece categories.
- The system must preserve **domain constraints** that are not explicitly optimized by the classification objective.
- This hybrid architecture (ML + constraints) reflects real-world recommender systems where correctness is not purely statistical.

---

## 11. Deep Learning Models (PyTorch)

In addition to traditional ML models, this project includes **experimental deep learning models** trained with PyTorch.

### Training Script

**File**: `outfit-ai/train_deep_models.py`

This script trains three PyTorch-based models:

1. **ANN (Artificial Neural Network)** — Multi-layer perceptron with dropout regularization
2. **CNN1D (1D Convolutional Network)** — Experimental adaptation treating tabular features as 1D signals
3. **LSTM (Long Short-Term Memory)** — Experimental adaptation treating features as sequential inputs

### Architecture Details

**ANN Model**:
```python
class ANNModel(nn.Module):
    def __init__(self, input_dim, num_classes, hidden_dims=[128, 64]):
        super(ANNModel, self).__init__()
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.3))
            prev_dim = hidden_dim
        layers.append(nn.Linear(prev_dim, num_classes))
        self.network = nn.Sequential(*layers)
```

**CNN1D Model** (Experimental):
- Treats feature vector as 1D signal with channel dimension
- Uses 1D convolutions with adaptive pooling
- **Note**: This is an experimental adaptation; CNNs are typically designed for spatial data

**LSTM Model** (Experimental):
- Treats each feature as a time step
- Uses 2-layer LSTM with dropout
- **Note**: This is an experimental adaptation; LSTMs are typically designed for sequential data

### Training Process

- **Early Stopping**: Monitors validation loss with patience=15 epochs
- **Optimizer**: Adam with learning rate 0.001
- **Loss Function**: CrossEntropyLoss
- **Batch Size**: 32
- **Device**: Automatically uses GPU if available, otherwise CPU

### Model Persistence

Models are saved in two formats:
- Timestamped: `outfit-ai/models/{model}_YYYYMMDD_HHMMSS.pt`
- Latest: `outfit-ai/models/{model}_model.pt`

Metrics are saved to:
- `outfit-ai/models/metrics_deep.json`

### Running Deep Learning Training

```bash
cd outfit-ai
python train_deep_models.py --dataset data/weather_outfit.csv --test-size 0.2 --val-size 0.1 --seed 42
```

**Requirements**:
```bash
pip install torch
```

---

## 12. Avatar Try-On (Premium 2.5D)

This project features a **premium 2.5D layered mannequin** that visualizes complete outfits with realistic clothing and strong depth illusion.

### Implementation

**Assets**: `web-app/static/images/avatar/*.svg`
- Realistic clothing silhouettes (t-shirts, jeans, sneakers, jackets, umbrellas)
- Anatomically aligned with human proportions
- Gradient fills, fabric details, and realistic shadows

**Backend**: `outfit-ai/personalized_recommendations.py`
- Generates `avatar_layers` field per outfit
- Maps outfit pieces to avatar layer categories
- Provides Boyner-only shop links

**Frontend**:
- **HTML**: `web-app/templates/index.html` — Layered `<img>` elements with fixed IDs
- **CSS**: `web-app/static/css/styles.css` — CSS 3D transforms, perspective, layered shadows
- **JavaScript**: `web-app/static/js/main.js` — State management, click-to-update, smooth transitions

### 3D Depth Illusion (CSS Only)

```css
.avatar-stage {
    perspective: 1200px;
    perspective-origin: 50% 45%;
    transform-style: preserve-3d;
}

.avatar-top {
    transform: translateZ(28px) translateY(-3px) scale(1.008);
    filter: drop-shadow(0 18px 38px rgba(0, 0, 0, 0.38))
            drop-shadow(0 8px 16px rgba(0, 0, 0, 0.28));
    z-index: 3;
}

.avatar-outerwear {
    transform: translateZ(38px) translateY(-1px) scale(1.012);
    filter: drop-shadow(0 22px 44px rgba(0, 0, 0, 0.42))
            drop-shadow(0 10px 20px rgba(0, 0, 0, 0.32));
    z-index: 4;
}
```

### Layer Stack (Front to Back)

1. **Highlight** (z-index: 6) — Screen blend mode overlay
2. **Accessory** (z-index: 5) — Umbrella, bag, etc.
3. **Outerwear** (z-index: 4) — Jacket, coat
4. **Top** (z-index: 3) — T-shirt, shirt
5. **Shoes** (z-index: 2) — Sneakers, boots
6. **Bottom** (z-index: 2) — Jeans, pants
7. **Body** (z-index: 1) — Mannequin base
8. **Shadow** (z-index: 0) — Ambient ground shadow

### Why 2.5D Instead of Full 3D

- **Lightweight**: No WebGL/Three.js dependencies
- **Deterministic**: Consistent rendering across all browsers
- **Educational Focus**: Emphasizes ML reasoning over graphics complexity
- **Performance**: Instant loading and smooth transitions

Weather-driven dressing logic (educational value):

- The avatar demonstrates how model outputs + constraints translate into UI behavior.
- The system exposes explainable “if rain then accessory” logic within an ML pipeline.

---

## 13. UI & UX Design

Key UI decisions are implemented in `web-app/`.

### Visual Features

**Pinterest-Style Outfit Grid**:
- Masonry layout with 3 columns
- Visual diversity with per-card accent colors
- Unique subtitles generated from outfit pieces
- Varied board images rotating across cards

**Green Selection Highlighting**:
```css
.pin-card.is-selected {
    border: 2px solid #22c55e;
    box-shadow: var(--shadow-lg), 
                0 0 0 4px rgba(34, 197, 94, 0.15),
                0 0 24px rgba(34, 197, 94, 0.3);
}

.pin-card.is-selected::after {
    content: 'Selected';
    background: #22c55e;
    /* ... badge styling ... */
}
```

**Active City Chip**:
- Displays selected city above outfit grid
- Updates on city selection or prediction
- Green gradient background with location pin emoji

**Model Zoo with Badges**:
- Type badges: Rule-based, ML, Deep Learning
- Experimental badges for CNN1D and LSTM
- Color-coded for visual distinction

### UX Enhancements

- **Drawer Navigation**: Mobile-friendly collapsible sidebar
- **Skeleton Loading**: Perceived performance during API calls
- **Deterministic Fallbacks**: Category SVGs and generated placeholders prevent broken UI
- **Smooth Transitions**: Cubic-bezier animations for avatar layer changes
- **Toast Notifications**: Non-intrusive feedback for user actions

---

## 14. Shopping Integration

Shopping integration is intentionally lightweight and safe:

- **Boyner-only** links are generated for outfit pieces
- Approach: search-query link generation (no scraping)
- Safe URL construction from piece metadata

**Implementation**: `outfit-ai/catalog.py`

```python
def _boyner_search_link(label: str, category: str) -> str:
    query = f"{label} {category}".strip()
    encoded = urllib.parse.quote_plus(query)
    return f"https://www.boyner.com.tr/search?q={encoded}"
```

**Design Rationale**:
- Avoids fragile web scraping pipelines
- Respects retailer terms of service
- Keeps project aligned with educational and ethical constraints

---

## 15. How to Run

The repository contains two main runnable components:

- `web-app/` for the deployed Flask UI
- `outfit-ai/` for training scripts and auxiliary tools

### 15.1 Train Traditional ML Models

From the repository root:

```bash
cd outfit-ai
python train_models.py
```

This will:
- Train XGBoost/RandomForest and MLP models
- Compute accuracy and macro F1 metrics
- Save models to `outfit-ai/models/`
- Generate `metrics.json`

### 15.2 Train Deep Learning Models (Optional)

**Requirements**:
```bash
pip install torch
```

**Training**:
```bash
cd outfit-ai
python train_deep_models.py --dataset data/weather_outfit.csv --test-size 0.2 --val-size 0.1 --seed 42
```

This will:
- Train ANN, CNN1D, and LSTM models with PyTorch
- Use GPU if available, otherwise CPU
- Apply early stopping with patience=15
- Save models as `.pt` files
- Generate `metrics_deep.json`

### 15.3 Run the Flask Web Application

**Install dependencies**:
```bash
pip install -r web-app/requirements.txt
```

**Run locally**:
```bash
python web-app/app.py
```

**Access**:
- Open `http://localhost:5000` in your browser

### 15.4 Optional: Run the Streamlit Demo

The repository also contains a Streamlit UI:

```bash
pip install -r outfit-ai/requirements.txt
streamlit run outfit-ai/app.py
```

### 15.5 Deployment

**Render/Heroku Deployment**:

The project is configured for platform deployment via:
- `Procfile`: `web: gunicorn app:app --chdir web-app`
- `requirements.txt` in `web-app/`

**Environment Variables** (if needed):
- `FLASK_ENV=production`
- Weather API keys (if using external providers)

**Build Steps**:
1. Push to Git repository
2. Connect to Render/Heroku
3. Set build command: `pip install -r web-app/requirements.txt`
4. Set start command: `gunicorn app:app --chdir web-app`
5. Deploy

---

## 16. Reproducibility Guide

### Complete Setup from Scratch

**1. Clone Repository**:
```bash
git clone <repository-url>
cd outfit-recommendation-ai
```

**2. Install Dependencies**:
```bash
# Traditional ML models
pip install -r outfit-ai/requirements.txt

# Web application
pip install -r web-app/requirements.txt

# Deep learning (optional)
pip install torch
```

**3. Train All Models**:
```bash
# Traditional ML
cd outfit-ai
python train_models.py

# Deep learning (optional)
python train_deep_models.py
```

**4. Verify Model Artifacts**:
```bash
ls outfit-ai/models/
# Expected: best_model.pkl, xgb_model.pkl, mlp_model.pkl, metrics.json
# Optional: ann_model.pt, cnn1d_model.pt, lstm_model.pt, metrics_deep.json
```

**5. Run Application**:
```bash
cd ../web-app
python app.py
```

**6. Test in Browser**:
- Navigate to `http://localhost:5000`
- Select a city (e.g., Istanbul)
- Adjust weather parameters
- Click "Kıyafet Öner" to generate recommendations
- Click outfit cards to update avatar
- View Model Zoo in comparison section

### Expected Results

**Traditional ML Models** (from `metrics.json`):
- Rules Baseline: ~71% accuracy, ~66% macro F1
- RandomForest/XGBoost: ~89% accuracy, ~81% macro F1
- MLP: ~95% accuracy, ~96% macro F1

**Deep Learning Models** (from `metrics_deep.json`, if trained):
- ANN: Comparable to MLP sklearn
- CNN1D: Experimental, may vary
- LSTM: Experimental, may vary

### Troubleshooting

**Issue**: Models not found
- **Solution**: Run training scripts first

**Issue**: PyTorch not available
- **Solution**: Deep learning models are optional; traditional ML models will work

**Issue**: Weather API fails
- **Solution**: Use manual weather input in UI

**Issue**: Avatar layers not displaying
- **Solution**: Check browser console; SVG assets should be in `web-app/static/images/avatar/`

---

## 17. Educational Outcomes

This project demonstrates core learning outcomes expected in an applied AI/ML course:

### Machine Learning Fundamentals
- Supervised learning formulation of a real-world decision problem
- Tabular preprocessing and categorical feature handling
- Model comparison with appropriate metrics (Accuracy vs Macro F1)
- Baseline design using explicit rules
- Understanding of model families: tree-based, neural networks, deep learning

### Production-Oriented Skills
- Model persistence and versioning
- Reproducible metrics logging
- API-based inference with Flask
- UI integration and robustness to missing assets
- Deployment configuration (Procfile, requirements.txt)

### Hybrid Reasoning
- ML provides the primary prediction
- Rules/constraints enforce validity and interpretability
- Multi-piece outfit assembly with domain constraints
- Personalization through user profile integration

### Advanced Topics
- Deep learning for tabular data (experimental)
- Early stopping and regularization
- GPU acceleration with PyTorch
- Model Zoo architecture for comparison
- 2.5D visualization with CSS 3D transforms

---

## 18. Future Work

Feasible extensions for a next iteration:

### Visualization Enhancements
- Replace 2.5D avatar with true 3D avatar (mesh + rigging + WebGL renderer)
- Add animation for outfit transitions
- Support for multiple body types and poses

### Personalization
- User embeddings for preference learning
- Collaborative filtering for similar user recommendations
- Gender/style-aware feature modeling
- Historical outfit tracking and favorites

### Feedback Loop
- Collect user accept/reject signals
- Train re-ranking model or contextual bandit
- A/B testing framework for model comparison
- Online learning with user feedback

### Dataset Improvements
- More diverse contexts (humidity, precipitation probability, UV index)
- Broader label taxonomy (business casual, athleisure, etc.)
- Real-world data collection from user interactions
- Bias analysis and fairness metrics

### Model Enhancements
- Transformer-based models for tabular data (FT-Transformer, TabNet)
- Ensemble methods combining all 6 models
- Uncertainty quantification with prediction intervals
- Explainability with SHAP or LIME

### Integration
- Real shopping API integration (with proper authorization)
- Weather forecast integration for multi-day planning
- Calendar integration for event-aware recommendations
- Mobile app with camera-based outfit capture

---

## 19. Conclusion

This project demonstrates a **complete end-to-end AI system** for outfit recommendation, combining:

✅ **6 distinct models** (Rules, XGBoost, RandomForest, MLP, ANN, CNN1D, LSTM)
✅ **Rigorous evaluation** with stratified splits and multiple metrics
✅ **Production deployment** with Flask REST API and modern UI
✅ **Premium visualization** with 2.5D avatar and CSS 3D depth
✅ **Personalization** through user profiles and style preferences
✅ **Educational value** with model comparison and hybrid reasoning

The system successfully maps `(weather, context, user_profile)` → `multi-piece outfit recommendations` while maintaining:
- **Correctness**: Domain constraints ensure valid outfit combinations
- **Explainability**: Rule-based baseline and constraint logic provide interpretability
- **Scalability**: Modular architecture supports easy extension
- **Reproducibility**: Complete documentation and training scripts

**Key Achievement**: This project bridges the gap between academic ML concepts and real-world deployment, demonstrating that effective AI systems require both statistical learning and domain expertise.

---

## 20. License & Attribution

**Project**: Outfit Recommendation AI  
**Purpose**: Educational demonstration of tabular ML, deep learning, and production deployment  
**Models**: XGBoost, RandomForest, MLP (sklearn), ANN/CNN1D/LSTM (PyTorch)  
**Visualization**: 2.5D Avatar Try-On with CSS 3D transforms  

**Dependencies**:
- scikit-learn (BSD License)
- PyTorch (BSD License)
- Flask (BSD License)
- pandas, numpy (BSD License)

**Shopping Integration**: Boyner search links (no scraping, educational use only)

**Note**: This is an educational project. For production use, ensure compliance with all applicable terms of service and data privacy regulations.

---

**Built with ❤️ for AI/ML Education**
