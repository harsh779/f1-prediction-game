import requests
from datetime import datetime
import pandas as pd
import streamlit as st

class F1Data:
    def __init__(self):
        self.base_url = "http://ergast.com/api/f1"
        self.current_year = datetime.now().year

    def get_upcoming_races(self):
        """Fetch upcoming races for the current season"""
        # Hardcoded upcoming races for testing
        races = [
            {
                'id': 1,
                'name': 'Australian Grand Prix',
                'date': '2025-03-14',
                'circuit': 'Albert Park Circuit',
                'country': 'Australia'
            },
            {
                'id': 2,
                'name': 'Chinese Grand Prix',
                'date': '2025-03-21',
                'circuit': 'Shanghai International Circuit',
                'country': 'China'
            },
            {
                'id': 3,
                'name': 'Japanese Grand Prix',
                'date': '2025-04-04',
                'circuit': 'Suzuka Circuit',
                'country': 'Japan'
            },
            {
                'id': 4,
                'name': 'Bahrain Grand Prix',
                'date': '2025-04-11',
                'circuit': 'Bahrain International Circuit',
                'country': 'Bahrain'
            },
            {
                'id': 5,
                'name': 'Saudi Arabian Grand Prix',
                'date': '2025-04-18',
                'circuit': 'Jeddah Corniche Circuit',
                'country': 'Saudi Arabia'
            },
            {
                'id': 6,
                'name': 'Miami Grand Prix',
                'date': '2025-05-02',
                'circuit': 'Miami International Autodrome',
                'country': 'United States'
            },
            {
                'id': 7,
                'name': 'Emilia Romagna Grand Prix',
                'date': '2025-05-16',
                'circuit': 'Imola Circuit',
                'country': 'Italy'
            },
            {
                'id': 8,
                'name': 'Monaco Grand Prix',
                'date': '2025-05-23',
                'circuit': 'Circuit de Monaco',
                'country': 'Monaco'
            },
            {
                'id': 9,
                'name': 'Spanish Grand Prix',
                'date': '2025-05-30',
                'circuit': 'Circuit de Barcelona-Catalunya',
                'country': 'Spain'
            },
            {
                'id': 10,
                'name': 'Canadian Grand Prix',
                'date': '2025-06-13',
                'circuit': 'Circuit Gilles Villeneuve',
                'country': 'Canada'
            },
            {
                'id': 11,
                'name': 'Austrian Grand Prix',
                'date': '2025-06-27',
                'circuit': 'Red Bull Ring',
                'country': 'Austria'
            },
            {
                'id': 12,
                'name': 'British Grand Prix',
                'date': '2025-07-04',
                'circuit': 'Silverstone Circuit',
                'country': 'United Kingdom'
            },
            {
                'id': 13,
                'name': 'Belgian Grand Prix',
                'date': '2025-07-25',
                'circuit': 'Circuit de Spa-Francorchamps',
                'country': 'Belgium'
            },
            {
                'id': 14,
                'name': 'Hungarian Grand Prix',
                'date': '2025-08-01',
                'circuit': 'Hungaroring',
                'country': 'Hungary'
            },
            {
                'id': 15,
                'name': 'Dutch Grand Prix',
                'date': '2025-08-29',
                'circuit': 'Circuit Zandvoort',
                'country': 'Netherlands'
            },
            {
                'id': 16,
                'name': 'Italian Grand Prix',
                'date': '2025-09-05',
                'circuit': 'Monza Circuit',
                'country': 'Italy'
            },
            {
                'id': 17,
                'name': 'Azerbaijan Grand Prix',
                'date': '2025-09-19',
                'circuit': 'Baku City Circuit',
                'country': 'Azerbaijan'
            },
            {
                'id': 18,
                'name': 'Singapore Grand Prix',
                'date': '2025-10-03',
                'circuit': 'Marina Bay Street Circuit',
                'country': 'Singapore'
            },
            {
                'id': 19,
                'name': 'United States Grand Prix',
                'date': '2025-10-17',
                'circuit': 'Circuit of the Americas',
                'country': 'United States'
            },
            {
                'id': 20,
                'name': 'Mexico City Grand Prix',
                'date': '2025-10-24',
                'circuit': 'Autódromo Hermanos Rodríguez',
                'country': 'Mexico'
            },
            {
                'id': 21,
                'name': 'São Paulo Grand Prix',
                'date': '2025-11-07',
                'circuit': 'Interlagos Circuit',
                'country': 'Brazil'
            },
            {
                'id': 22,
                'name': 'Las Vegas Grand Prix',
                'date': '2025-11-20',
                'circuit': 'Las Vegas Strip Circuit',
                'country': 'United States'
            },
            {
                'id': 23,
                'name': 'Qatar Grand Prix',
                'date': '2025-11-28',
                'circuit': 'Lusail International Circuit',
                'country': 'Qatar'
            },
            {
                'id': 24,
                'name': 'Abu Dhabi Grand Prix',
                'date': '2025-12-05',
                'circuit': 'Yas Marina Circuit',
                'country': 'United Arab Emirates'
            }
        ]
        
        # Debug output
        st.write(f"Number of races loaded: {len(races)}")
        return races

    def get_drivers(self):
        """Fetch current season drivers"""
        # Hardcoded current F1 drivers for 2025
        return [
            {'id': 'oscar_piastri', 'name': 'Oscar Piastri', 'number': '81'},
            {'id': 'lando_norris', 'name': 'Lando Norris', 'number': '4'},
            {'id': 'max_verstappen', 'name': 'Max Verstappen', 'number': '1'},
            {'id': 'george_russell', 'name': 'George Russell', 'number': '63'},
            {'id': 'charles_leclerc', 'name': 'Charles Leclerc', 'number': '16'},
            {'id': 'kimi_antonelli', 'name': 'Kimi Antonelli', 'number': '12'},
            {'id': 'lewis_hamilton', 'name': 'Lewis Hamilton', 'number': '44'},
            {'id': 'alex_albon', 'name': 'Alexander Albon', 'number': '23'},
            {'id': 'esteban_ocon', 'name': 'Esteban Ocon', 'number': '31'},
            {'id': 'lance_stroll', 'name': 'Lance Stroll', 'number': '18'},
            {'id': 'yuki_tsunoda', 'name': 'Yuki Tsunoda', 'number': '22'},
            {'id': 'pierre_gasly', 'name': 'Pierre Gasly', 'number': '10'},
            {'id': 'carlos_sainz', 'name': 'Carlos Sainz', 'number': '55'},
            {'id': 'nico_hulkenberg', 'name': 'Nico Hulkenberg', 'number': '27'},
            {'id': 'oliver_bearman', 'name': 'Oliver Bearman', 'number': '87'},
            {'id': 'isack_hadjar', 'name': 'Isack Hadjar', 'number': '61'},
            {'id': 'fernando_alonso', 'name': 'Fernando Alonso', 'number': '14'},
            {'id': 'liam_lawson', 'name': 'Liam Lawson', 'number': '30'},
            {'id': 'jack_doohan', 'name': 'Jack Doohan', 'number': '7'},
            {'id': 'gabriel_bortoleto', 'name': 'Gabriel Bortoleto', 'number': '5'},
            {'id': 'franco_colapinto', 'name': 'Franco Colapinto', 'number': '43'}
        ]

    def get_constructors(self):
        """Fetch current season constructors"""
        # Hardcoded current F1 constructors
        return [
            {'id': 'red_bull', 'name': 'Red Bull Racing'},
            {'id': 'mercedes', 'name': 'Mercedes'},
            {'id': 'ferrari', 'name': 'Ferrari'},
            {'id': 'mclaren', 'name': 'McLaren'},
            {'id': 'aston_martin', 'name': 'Aston Martin'},
            {'id': 'alpine', 'name': 'Alpine'},
            {'id': 'williams', 'name': 'Williams'},
            {'id': 'kick_sauber', 'name': 'Kick Sauber'},
            {'id': 'haas', 'name': 'Haas F1 Team'},
            {'id': 'racing_bulls', 'name': 'Racing Bulls'}
        ]

    def get_driver_constructor_mapping(self):
        """Fetch current season driver-constructor mappings"""
        url = f"{self.base_url}/{self.current_year}/driverStandings.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            standings_lists = data['MRData']['StandingsTable']['StandingsLists']
            if standings_lists:  # Only proceed if standings exist
                standings = standings_lists[0]['DriverStandings']
                return {
                    standing['Driver']['driverId']: standing['Constructors'][0]['constructorId']
                    for standing in standings
                }
        return {} 