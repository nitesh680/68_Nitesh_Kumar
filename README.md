 # 💰 Personal Finance Assistant with AI-Powered Categorization

A full-stack web application that automatically categorizes personal expenses from CSV transaction data using a hybrid AI approach (rules, machine learning, and optional LLM fallback). Built with FastAPI backend and React frontend.

## Tech Stack

### Backend
- **FastAPI**: Modern async web framework
- **MongoDB**: Document storage via Motor (async driver)
- **Authentication**: JWT tokens with configurable expiration
- **ML Pipeline**: 
  - Primary: Custom RandomForest/DecisionTree ensemble (expense_model.joblib)
  - Fallback: TF-IDF + Logistic Regression (model.joblib)
  - Training: scikit-learn with advanced NLP feature extraction
- **LLM Integration**: Google Gemini 1.5 Flash via LangChain (optional)
- **Password Hashing**: pbkdf2_sha256 (bcrypt-compatible)

### Frontend
- **React 18**: Modern UI with hooks
- **Vite**: Fast development build tool
- **Tailwind CSS**: Utility-first styling
- **React Router**: Client-side routing
- **Axios**: HTTP client with JWT auth
- **Lucide React**: Icon library

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, dependencies
│   │   ├── db/            # MongoDB connection
│   │   ├── ml/            # Model training and storage
│   │   ├── routers/        # API endpoints
│   │   ├── schemas/        # Pydantic models
│   │   └── services/      # Business logic (categorizer, Gemini)
│   ├── artifacts/          # Trained ML models (expense_model.joblib)
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Route components
│   │   ├── lib/           # API client, storage
│   │   └── types/         # TypeScript definitions
│   ├── package.json
│   └── .env
└── archive (2)/            # Sample CSV datasets
```

## Requirements

- Python 3.10+
- Node.js 20.x (works with Vite 5 in this repo)
- MongoDB running locally

## Backend Setup

### 1) Create `backend/.env`

Copy `backend/.env.example` → `backend/.env` and set values:

```env
MONGODB_URI=mongodb://localhost:27017/deploy
MONGODB_DB=expense_ai
JWT_SECRET=CHANGE_ME_TO_A_LONG_RANDOM_STRING
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
GEMINI_API_KEY=
CORS_ORIGINS=http://localhost:5173
MODEL_DIR=./artifacts
CONFIDENCE_THRESHOLD=0.65
```

Notes:
- `GEMINI_API_KEY` is optional. If not set, Gemini features return an error or fall back.

### 2) Install deps

```bash
pip install -r requirements.txt
```

### 3) Start Backend

```bash
uvicorn app.main:app --reload --port 8005
```

4) **Health Check**
```bash
curl http://localhost:8005/api/health
# Expected: {"status":"ok"}
```

### Model Setup

Your custom model `expense_model.joblib` is already included in `backend/artifacts/`. The system automatically:

**Primary Model - expense_model.joblib**:
- ✅ **Loaded by default** (104MB, 22 categories)
- ✅ **RandomForest/DecisionTree ensemble** trained on historical data
- ✅ **Advanced NLP features** with semantic analysis
- ✅ **High accuracy** on real-world transaction descriptions
- ✅ **Confidence scoring** (0.0-1.0 probability)

**Fallback Model - model.joblib**:
- 📦 **Backup model** (2KB, 5 basic categories)
- 📦 **TF-IDF + Logistic Regression** for simple patterns
- 📦 **Only used** if custom model is unavailable

**Model Selection Logic**:
```python
# System checks for models in order:
1. expense_model.joblib (your custom model) ← ACTIVE
2. model.joblib (fallback) ← BACKUP ONLY
```

**No additional setup required** - your model is pre-integrated and active!

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Environment Variables**
```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8005
```

3. **Start Frontend**
```bash
npm run dev
```

4. **Open Application**
```
http://localhost:5173
```

## Usage

### 1. Create Account
- Visit `/signup`
- Enter name, email, password
- Redirected to dashboard

### 2. Upload Transactions
- Go to `/upload`
- Select CSV file with columns: `date,amount,description`
- System auto-categorizes each transaction using your custom model
- View results in dashboard

### 3. Add Single Transaction
- Go to `/add`
- Enter amount, date, description
- See live categorization preview
- Save to database

### 4. View Analytics
- Dashboard shows spending trends
- Filter by month
- View category breakdowns
- Export categorized data

## CSV Format

### Required Columns
```csv
date,amount,description
2026-01-01,120.5,Walmart groceries
2026-01-02,45.0,Uber ride
2026-01-03,25.0,Netflix subscription
```

### Date Formats Supported
- ISO: `2026-01-01`
- ISO with time: `2026-01-01T14:30:00`
- Unix timestamps

## AI Categorization Pipeline

### 1. Rules Engine (First Priority)
Fast pattern matching for known merchants using keyword detection:
- `"walmart", "target", "costco"` → Groceries
- `"uber", "lyft", "taxi"` → Transport
- `"netflix", "spotify", "hulu"` → Entertainment
- `"shell", "bp", "exxon"` → Fuel
- `"starbucks", "coffee"` → Restaurant
- `"amazon", "ebay"` → Shopping

### 2. Custom ML Model - expense_model.joblib (Primary)
**Algorithm**: RandomForest/DecisionTree Ensemble
- **Training Data**: Historical transaction descriptions with categories
- **Features**: Text patterns, keywords, amounts, transaction context
- **Categories**: 22 detailed expense categories:
  - Business lunch
  - Clothing
  - Coffee
  - Communal
  - Events
  - Entertainment
  - Fuel
  - Groceries
  - Health
  - Home
  - Insurance
  - Market
  - Other
  - Personal
  - Restaurant
  - Shopping
  - Subscriptions
  - Taxes
  - Transport
  - Travel
  - Utilities

**Model Details**:
- **Size**: 104MB (complex ensemble model)
- **Training Framework**: scikit-learn 1.6.1
- **Confidence Scoring**: 0.0-1.0 probability
- **Feature Extraction**: Advanced NLP with n-grams and semantic analysis

### 3. Fallback ML Model - model.joblib (Backup)
**Algorithm**: TF-IDF + Logistic Regression
- **Training Data**: Basic transaction patterns
- **Features**: TF-IDF vectorization (1-2 ngrams)
- **Categories**: 5 basic categories (Coffee, Market, Restaurant, Transport, Other)
- **Size**: 2KB (lightweight model)
- **Use Case**: Emergency backup when custom model is unavailable

### 4. LLM Fallback - Gemini (Optional)
**Model**: Google Gemini 1.5 Flash
- **Purpose**: Handle completely unseen transaction descriptions
- **Trigger**: ML confidence < 0.65 threshold
- **Process**: Sends description to Gemini for intelligent categorization
- **Output**: Structured JSON with category and explanation
- **Cost**: Requires API key, usage-based pricing

## Model Architecture & Training Details

### Model Comparison

| Feature | expense_model.joblib (Primary) | model.joblib (Fallback) |
|---------|--------------------------------|------------------------|
| **Algorithm** | RandomForest/DecisionTree Ensemble | TF-IDF + Logistic Regression |
| **Size** | 104MB | 2KB |
| **Categories** | 22 detailed categories | 5 basic categories |
| **Training Data** | Historical transactions with rich descriptions | Basic transaction patterns |
| **Feature Engineering** | Advanced NLP, semantic analysis, context | Simple TF-IDF vectorization |
| **Accuracy** | High (trained on real data) | Basic (rule-based patterns) |
| **Confidence** | 0.0-1.0 probability score | Basic confidence |
| **Use Case** | Production categorization | Emergency backup |

### Training Process for expense_model.joblib

**Data Preparation**:
- **Source**: Historical transaction data with descriptions
- **Features**: Transaction descriptions, amounts, merchant names
- **Preprocessing**: Text cleaning, normalization, feature extraction
- **Categories**: 22 expense types based on real spending patterns

**Model Architecture**:
```python
# Ensemble of multiple classifiers:
- DecisionTreeClassifier (depth-optimized)
- RandomForestClassifier (ensemble of trees)
- Feature extraction: Advanced NLP pipeline
- Text processing: N-grams, semantic analysis
```

**Training Parameters**:
- **Framework**: scikit-learn 1.6.1
- **Validation**: Cross-validation with historical data
- **Optimization**: Hyperparameter tuning for accuracy
- **Feature Selection**: Automatic feature importance ranking

### Model Categories (expense_model.joblib)

**Detailed Breakdown**:
1. **Business lunch** - Work-related meals
2. **Clothing** - Apparel, accessories
3. **Coffee** - Coffee shops, cafes
4. **Communal** - Shared expenses, group activities
5. **Events** - Tickets, concerts, entertainment
6. **Entertainment** - Movies, games, streaming
7. **Fuel** - Gas stations, vehicle fuel
8. **Groceries** - Supermarkets, food shopping
9. **Health** - Medical, pharmacy, fitness
10. **Home** - Home improvement, furniture
11. **Insurance** - Insurance premiums
12. **Market** - General shopping, markets
13. **Other** - Miscellaneous expenses
14. **Personal** - Personal care, services
15. **Restaurant** - Dining out, food delivery
16. **Shopping** - Retail purchases, online shopping
17. **Subscriptions** - Recurring services
18. **Taxes** - Tax payments, government fees
19. **Transport** - Public transport, rideshare
20. **Travel** - Flights, hotels, travel expenses
21. **Utilities** - Electricity, water, internet
22. **Work** - Work-related expenses

### Feature Engineering

**Text Processing**:
- **Tokenization**: Word and phrase extraction
- **N-grams**: 1-2 word combinations for context
- **Semantic Analysis**: Understanding transaction context
- **Merchant Recognition**: Identifying known merchants
- **Amount Patterns**: Using transaction amounts as features

**Advanced Features**:
- **Merchant Database**: Known merchant categorization
- **Amount Ranges**: Typical spending patterns per category
- **Temporal Patterns**: Time-based spending behavior
- **Description Context**: Understanding transaction purpose

## API Endpoints

### Authentication
```http
POST /api/auth/signup     # Create account
POST /api/auth/login      # Login
GET  /api/auth/me         # Get current user
```

### Transactions
```http
POST /api/transactions/           # Create single transaction
GET  /api/transactions/recent     # Recent transactions
POST /api/transactions/upload     # Bulk CSV upload
POST /api/transactions/categorize # Test categorization
```

### Analytics
```http
GET /api/analytics/dashboard?month=2026-01  # Summary stats
GET /api/analytics/trend                    # Spending trends
GET /api/analytics/anomalies?month=2026-01  # Unusual transactions
```

### Export
```http
GET /api/export/csv?month=2026-01  # Download categorized data
```

### Model Testing

**Test your custom model**:
```bash
curl -X POST "http://localhost:8005/api/transactions/categorize?description=walmart%20groceries" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Response: {"category":"Groceries","confidence":0.95,"source":"rules"}

curl -X POST "http://localhost:8005/api/transactions/categorize?description=online%20purchase" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Response: {"category":"Market","confidence":0.35,"source":"ml"}
```

## Model Performance & Metrics

### expense_model.joblib Performance
- **Accuracy**: High (trained on real transaction data)
- **Coverage**: 22 detailed expense categories
- **Confidence**: 0.0-1.0 probability scoring
- **Speed**: Fast inference (optimized ensemble)
- **Robustness**: Handles various description formats

### Fallback Performance
- **Accuracy**: Basic (rule-based patterns)
- **Coverage**: 5 essential categories
- **Speed**: Very fast (simple model)
- **Use Case**: Emergency backup only

### Model Selection Flow
```python
def categorize_transaction(description):
    # 1. Rules Engine (fastest)
    if matches_known_merchant(description):
        return rule_based_category()
    
    # 2. Custom ML Model (primary)
    prediction = expense_model.predict(description)
    if prediction.confidence > 0.65:
        return prediction
    
    # 3. Fallback ML Model (backup)
    if expense_model.unavailable:
        return fallback_model.predict(description)
    
    # 4. Gemini LLM (optional)
    if gemini_enabled and prediction.confidence < 0.65:
        return gemini_categorize(description)
    
    return "Other"  # Default fallback
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/deploy` |
| `JWT_SECRET` | JWT signing secret | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173` |
| `CONFIDENCE_THRESHOLD` | ML confidence threshold | `0.65` |
| `MODEL_DIR` | ML model storage | `./artifacts` |

### Security Notes
- Never commit `.env` files
- Use strong JWT secrets
- Rotate API keys regularly
- Enable HTTPS in production

## Troubleshooting

### Common Issues

**Backend crashes on startup**
- Check MongoDB is running
- Verify `.env` variables
- Check port conflicts

**Upload fails with "Network Error"**
- Ensure you're logged in
- Check `VITE_API_BASE_URL` in frontend
- Verify CORS origins

**Categorization always "Other"**
- Your custom model should handle most cases
- Check confidence threshold
- Verify descriptions aren't empty

**Gemini errors**
- Verify API key validity
- Check model availability
- Disable Gemini temporarily

### Logs

**Backend logs**:
```bash
# In backend terminal
# Logs show requests, errors, categorization decisions
```

**Frontend logs**:
- Open browser dev tools (F12)
- Check Console tab for errors
- Network tab shows API requests

---

**Built with ❤️ for better financial management**
