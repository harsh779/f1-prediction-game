# F1 Prediction Game

A web application for Formula 1 race predictions and scoring.

## Features

- Predict top 3 drivers, 10th, 11th, 19th, and 20th positions
- Predict constructor positions (top 2, 5th, 6th, and 10th)
- Wildcard predictions for biggest loser
- Sprint race predictions
- Season-long predictions
- Automatic scoring system
- User authentication
- Leaderboard

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

## Rules

1. Predictions must be made before Practice 1
2. Last message before P1 will be accepted (without "edited")
3. Points System:
   - Position difference scoring (e.g., predicting 4th and driver finishes 8th = -4 points)
   - Constructor ranking based on combined car positions
   - Wildcard correct prediction: +5 points
   - DNF positions counted as 20th
   - Missing predictions: 5 points less than lowest scorer
   - Season predictions: Driver Champion (+50), Constructor Champion (+25)

## Tournament Prize

Winner receives Rs. 500 from other participants 