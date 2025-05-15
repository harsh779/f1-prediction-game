# F1 Prediction Game

A web application for predicting F1 race outcomes and competing with friends.

## Features
- User registration and authentication
- Race prediction submission
- Real-time leaderboard
- Points calculation based on prediction accuracy
- Historical race results

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Game Rules
- Predict the top 3 finishers for each race
- Points are awarded based on prediction accuracy:
  - Correct position: 3 points
  - Correct driver in wrong position: 1 point
- Maximum points per race: 9 points
- Leaderboard is updated after each race

## Deployment
This application is deployed on Streamlit Cloud. Visit [streamlit.io](https://streamlit.io) to deploy your own version. 