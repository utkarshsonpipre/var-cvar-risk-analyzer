# 📉 VaR-CVaR Risk Analyzer (Streamlit App)

The **VaR-CVaR Risk Analyzer** is a Streamlit-based financial analytics dashboard that helps quantify risk in stock portfolios. It supports three powerful statistical methods to calculate **Value at Risk (VaR)** and **Conditional Value at Risk (CVaR)**:

* 📊 Historical Method
* 🧠 Parametric Method
* 🧪 Monte Carlo Simulation

Built using Python and interactive Plotly charts, this tool enables analysts to estimate potential portfolio losses across different time horizons and confidence levels.

---
![Screenshot_30-6-2025_205622_localhost](https://github.com/user-attachments/assets/e8c4f784-4185-4515-97b8-226c1298634c)

![Screenshot_30-6-2025_205638_localhost](https://github.com/user-attachments/assets/3ec209b9-f619-438d-a259-6a2f435bfe55)


## 📌 Features

* ✅ Accepts NSE or USA stock tickers (e.g., `RELIANCE.NS`, `AAPL`, `TCS.NS`)
* ✅ Custom portfolio weight assignment
* ✅ Calculates VaR and CVaR at chosen confidence levels
* ✅ Supports 3 statistical approaches: Historical, Parametric, Monte Carlo
* ✅ Visualizes distribution of portfolio returns
* ✅ Rolling window option to analyze risk trends over time
* ✅ Built-in validation and interactive UI using Streamlit

---

## 🧠 Methods Implemented

### 📊 Historical Method

Uses past return distributions to calculate losses.

### 🧠 Parametric Method

Assumes normally distributed returns for analytical risk modeling.

### 🧪 Monte Carlo Simulation

Generates thousands of random return scenarios based on historical mean and standard deviation.

---

## 📁 Project Structure

```plaintext
VAR-CVAR-RISK-ANALYZER/
├── .idea/                        # IDE settings
├── .streamlit/                  # Streamlit configuration
├── src/                         # Source code
│   ├── data/
│   │   └── fetcher.py           # Fetch stock price data using yfinance
│   └── models/
│       ├── var.py               # Value at Risk calculations
│       └── cvar.py              # Conditional VaR calculations
├── tests/                       # Unit tests
│   ├── test_data/
│   │   └── test_fetcher.py
│   └── test_models/
│       ├── test_var.py
│       └── test_cvar.py
├── .gitattributes
├── .gitignore
├── README.md                    # This file
├── requirements.txt             # Python dependencies
└── streamlit_app.py             # Main Streamlit interface
```

---

## 🚀 How to Run Locally

### 🔁 Clone the Repository

```bash
git clone https://github.com/utkarshsonpipre/var-cvar-risk-analyzer.git
```

### 🐍 Create Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 📦 Install Requirements

```bash
pip install -r requirements.txt
```

### ▶️ Run the App

```bash
streamlit run streamlit_app.py
```

Open browser to: [http://localhost:8501](http://localhost:8501)

---

## 📊 Example Usage

```text
Tickers: RELIANCE.NS, TCS.NS
Weights: 0.5, 0.5
Confidence Level: 95%
Time Horizon: 1 Day
Method: Monte Carlo (10,000 simulations)
```

---

