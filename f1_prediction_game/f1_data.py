import requests
from datetime import datetime
import pandas as pd

class F1Data:
    def __init__(self):
        self.base_url = "http://ergast.com/api/f1"
        self.current_year = datetime.now().year

    def get_upcoming_races(self):
        """Fetch upcoming races for the current season"""
        url = f"{self.base_url}/{self.current_year}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            races = data['MRData']['RaceTable']['Races']
            
            # Filter only upcoming races
            upcoming_races = []
            for race in races:
                race_date = datetime.strptime(race['date'], '%Y-%m-%d')
                if race_date > datetime.now():
                    upcoming_races.append({
                        'id': race['round'],
                        'name': race['raceName'],
                        'date': race['date'],
                        'circuit': race['Circuit']['circuitName'],
                        'country': race['Circuit']['Location']['country']
                    })
            return upcoming_races
        return []

    def get_drivers(self):
        """Fetch current season drivers"""
        url = f"{self.base_url}/{self.current_year}/drivers.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            drivers = data['MRData']['DriverTable']['Drivers']
            return [{
                'id': driver['driverId'],
                'name': f"{driver['givenName']} {driver['familyName']}",
                'number': driver.get('permanentNumber', 'N/A')
            } for driver in drivers]
        return []

    def get_constructors(self):
        """Fetch current season constructors"""
        url = f"{self.base_url}/{self.current_year}/constructors.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            constructors = data['MRData']['ConstructorTable']['Constructors']
            return [{
                'id': constructor['constructorId'],
                'name': constructor['name']
            } for constructor in constructors]
        return []

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