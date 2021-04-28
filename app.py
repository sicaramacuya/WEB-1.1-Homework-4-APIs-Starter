import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""

    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        "appid": API_KEY,
        "q": city,
        "units": units
    }

    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    # pp.pprint(result_json)

    context = {
        'date': datetime.now().strftime("%A, %B %-d, %Y"),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': datetime.fromtimestamp(result_json['sys']['sunrise']).strftime("%-I:%M %p"),
        'sunset': datetime.fromtimestamp(result_json['sys']['sunset']).strftime("%-I:%M %p"),
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""

    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    def get_weather(city, units):

        params = {
            "appid": API_KEY,
            "q": city,
            "units": units
        }

        return requests.get(API_URL, params=params).json()

    city1_weather_json = get_weather(city1, units)
    city2_weather_json = get_weather(city2, units)

    # pp.pprint(city1_weather_json)
    # pp.pprint(city2_weather_json)

    context = {
        'date': datetime.now().strftime("%A, %B %-d, %Y"),
        'units_letter': get_letter_for_units(units),
        'city1': city1_weather_json['name'],
        'temp1': city1_weather_json['main']['temp'],
        'humidity1': city1_weather_json['main']['humidity'],
        'wind_speed1': city1_weather_json['wind']['speed'],
        'sunrise1': datetime.fromtimestamp(city1_weather_json['sys']['sunrise']),
        'sunset1': datetime.fromtimestamp(city1_weather_json['sys']['sunset']).hour,
        'city2': city2_weather_json['name'],
        'temp2': city2_weather_json['main']['temp'],
        'humidity2': city2_weather_json['main']['humidity'],
        'wind_speed2': city2_weather_json['wind']['speed'],
        'sunrise2': datetime.fromtimestamp(city2_weather_json['sys']['sunrise']),
        'sunset2': datetime.fromtimestamp(city2_weather_json['sys']['sunset']).hour,
        'abs_difference_in_temp': round(abs(city1_weather_json['main']['temp'] - city2_weather_json['main']['temp']), 2),
        'abs_difference_in_humidity': round(abs(city1_weather_json['main']['humidity']-city2_weather_json['main']['humidity']), 2),
        'abs_difference_wind_speed': round(abs(city1_weather_json['wind']['speed'] - city2_weather_json['wind']['speed']), 2),
        'abs_difference_sunset': abs(datetime.fromtimestamp(city1_weather_json['sys']['sunset']).hour - datetime.fromtimestamp(city2_weather_json['sys']['sunset']).hour)
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
