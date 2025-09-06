# Medicine Quality Monitor 🏥

A fully functional AI-powered web application for verifying medicine authenticity using machine learning anomaly detection.

## 🚀 Live Demo

**Frontend:** https://medverify-2.preview.emergentagent.com
**Admin Dashboard:** https://medverify-2.preview.emergentagent.com/admin/login

### Demo Credentials
- **Admin Username:** `admin`
- **Admin Password:** `admin123`

## 📋 Features

### 🔍 Medicine Verification (User Side)
- **Batch Code Input:** Enter or scan medicine batch codes
- **AI-Powered Detection:** Uses Isolation Forest model for anomaly detection
- **Real-time Results:** Instant verification with confidence scores
- **Status Types:**
  - ✅ **Valid** - Medicine is authentic and safe
  - ⚠️ **Expired** - Medicine has passed expiry date
  - ❌ **Fake** - Batch code not found in official database
  - 🤔 **Suspected Counterfeit** - AI detected suspicious patterns

### 📊 Admin Dashboard
- **Secure Login:** Admin authentication system
- **Verification Logs:** Complete history of all verification attempts
- **Real-time Analytics:** 
  - Status distribution pie chart
  - Daily verification trends bar chart
  - Statistics cards with key metrics
- **Data Export:** View detailed verification information

### 🤖 AI Anomaly Detection
- **Machine Learning Model:** Trained Isolation Forest model
- **Features Analyzed:**
  - Manufacturer reliability score
  - Days to expiry
  - Scan frequency patterns
  - Geographic distribution
  - Historical verification data
- **Confidence Scoring:** 0-100% confidence in predictions

### 💻 Technical Features
- **Responsive Design:** Works on desktop, tablet, and mobile
- **Real-time Updates:** Live data refresh and statistics
- **Error Handling:** Graceful error management with user feedback
- **Toast Notifications:** Instant feedback for user actions
- **Loading States:** Smooth animations and loading indicators

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database for scalability
- **Motor** - Async MongoDB driver
- **scikit-learn** - Machine learning library
- **Pydantic** - Data validation and serialization

### Frontend
- **React 19** - Latest React with modern hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Shadcn/UI** - Beautiful, accessible component library
- **Chart.js + react-chartjs-2** - Interactive data visualizations
- **Lucide React** - Modern icon library
- **Sonner** - Toast notifications

### AI/ML
- **Isolation Forest** - Unsupervised anomaly detection
- **StandardScaler** - Feature normalization
- **Joblib** - Model serialization and loading

## 📁 Project Structure

```
/app/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main API server
│   ├── train_model.py      # ML model training script
│   ├── database_seeder.py  # Database seeding utility
│   ├── models/            # Trained ML models
│   │   ├── anomaly_model.joblib
│   │   └── scaler.joblib
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.js         # Main React component
│   │   ├── App.css        # Global styles
│   │   └── components/    # React components
│   │       ├── HomePage.js
│   │       ├── AdminLogin.js
│   │       ├── AdminDashboard.js
│   │       └── ui/        # Shadcn UI components
│   ├── package.json       # Node.js dependencies
│   └── .env              # Environment variables
└── README.md             # This file
```

## 🔧 API Endpoints

### Public Endpoints
- `GET /api/` - Health check
- `POST /api/verify` - Verify medicine batch code

### Admin Endpoints
- `POST /api/admin/login` - Admin authentication
- `GET /api/logs` - Get verification logs (requires auth)
- `GET /api/stats` - Get dashboard statistics (requires auth)

### Sample API Request

```bash
curl -X POST "https://medverify-2.preview.emergentagent.com/api/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MED123456A",
    "lat": 40.7128,
    "lng": -74.0060
  }'
```

### Sample API Response

```json
{
  "status": "Valid ✅",
  "reason": "Medicine is authentic and valid (expires in 45 days)",
  "confidence": 0.95,
  "batch_info": {
    "name": "Paracetamol 500mg",
    "manufacturer": "PharmaCorp",
    "expiry_date": "2025-10-15T00:00:00",
    "scan_count": 3
  }
}
```

## 🚀 Local Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB running locally
- Yarn package manager

### Backend Setup

1. **Install Python dependencies:**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Train the ML model:**
```bash
python train_model.py
```

3. **Seed the database:**
```bash
python database_seeder.py
```

4. **Start the backend server:**
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Setup

1. **Install Node.js dependencies:**
```bash
cd /app/frontend
yarn install
```

2. **Start the development server:**
```bash
yarn start
```

## 🔬 Testing

The system comes pre-seeded with **50 medicine records** and includes comprehensive testing:

### Test Batch Codes
- **Valid Medicine:** `MED597233X`
- **Fake Medicine:** `FAKE999999Z`
- **Admin Login:** username: `admin`, password: `admin123`

### API Testing
All endpoints have been thoroughly tested and are working correctly.

## 🏆 Hackathon-Ready Features

✅ **Complete MVP** - Fully functional medicine verification system  
✅ **AI Integration** - Real anomaly detection using Isolation Forest  
✅ **Professional UI** - Modern, responsive design with charts  
✅ **Admin Dashboard** - Complete analytics and management interface  
✅ **Real Database** - 50+ seeded medicine records  
✅ **Comprehensive Testing** - All features tested and working  

---

**Built for healthcare safety and medicine authenticity verification**
