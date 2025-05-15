# F1 Prediction Game

A web application for predicting F1 race results and competing with friends. Make predictions for each race weekend and earn points based on your accuracy!

## Features

- User registration and login
- Make predictions for each F1 race
- Predict driver positions (P1, P2, P3, P10, P11, P19, P20)
- Predict constructor positions (P1, P2, P5, P6, P10)
- Wildcard predictions for extra points
- View leaderboard and your prediction history
- Real-time F1 data integration

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/f1-prediction-game.git
   cd f1-prediction-game
   ```

2. **Create a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run f1_prediction_game/app.py
   ```

5. **Access the application**
   - Open your web browser
   - Go to http://localhost:8501

## How to Use

1. **Register an Account**
   - Click "Register" in the sidebar
   - Enter your username, email, and password
   - Click "Register" to create your account

2. **Make Predictions**
   - Log in to your account
   - Click "Make Prediction" in the sidebar
   - Select a race from the dropdown
   - Make your predictions for:
     - Driver positions (P1, P2, P3, P10, P11, P19, P20)
     - Constructor positions (P1, P2, P5, P6, P10)
     - Wildcard predictions
   - Click "Submit Prediction" to save your predictions

3. **View Results**
   - Check the "Leaderboard" to see overall standings
   - View "My Predictions" to see your prediction history

## Scoring System

- Driver position predictions:
  - Exact position: +2 points
  - Each position off: -1 point
- Constructor position predictions:
  - Exact position: +2 points
  - Each position off: -1 point
- Wildcard predictions:
  - Correct prediction: +5 points

## Requirements

- Python 3.8 or higher
- Streamlit
- FastAPI
- SQLAlchemy
- Other dependencies listed in requirements.txt

## Contributing

Feel free to submit issues and enhancement requests! 