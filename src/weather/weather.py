# /// script
# dependencies = ["requests"]
# ///

"""
Weather tool using wttr.in API.

No API key required. Provides current weather and forecasts.
"""

import requests
from typing import Optional


def get_weather(location: str, format: str = "text") -> str:
    """
    Get current weather for a location.
    
    Args:
        location: City name (e.g., "Gothenburg", "Stockholm", "London")
        format: Output format - "text" for simple text, "json" for structured data
    
    Returns:
        Weather information as a string
    """
    try:
        # Use wttr.in API (no API key needed)
        if format == "json":
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10, headers={"User-Agent": "openaurio/1.0"})
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_condition", [{}])[0]
                return f"""Weather in {location}:
Temperature: {current.get('temp_C', 'N/A')}°C (feels like {current.get('FeelsLikeC', 'N/A')}°C)
Condition: {current.get('weatherDesc', [{}])[0].get('value', 'N/A')}
Humidity: {current.get('humidity', 'N/A')}%
Wind: {current.get('windspeedKmph', 'N/A')} km/h {current.get('winddir16Point', '')}
"""
            else:
                return f"Could not get weather for {location}. Please try again."
        else:
            # Simple text format
            url = f"https://wttr.in/{location}?format=%l:+%c+%t+Humidity:+%h+Wind:+%w"
            response = requests.get(url, timeout=10, headers={"User-Agent": "openaurio/1.0"})
            if response.status_code == 200:
                return f"Weather: {response.text.strip()}"
            else:
                return f"Could not get weather for {location}. Please try again."
                
    except requests.exceptions.Timeout:
        return f"Weather request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error getting weather: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def get_forecast(location: str, days: int = 3) -> str:
    """
    Get weather forecast for a location.
    
    Args:
        location: City name
        days: Number of days (1-3)
    
    Returns:
        Forecast information as a string
    """
    try:
        url = f"https://wttr.in/{location}?format=j1"
        response = requests.get(url, timeout=10, headers={"User-Agent": "openaurio/1.0"})
        
        if response.status_code != 200:
            return f"Could not get forecast for {location}."
        
        data = response.json()
        weather_data = data.get("weather", [])[:days]
        
        result = f"Weather forecast for {location}:\n\n"
        
        for day in weather_data:
            date = day.get("date", "Unknown")
            max_temp = day.get("maxtempC", "N/A")
            min_temp = day.get("mintempC", "N/A")
            avg_temp = day.get("avgtempC", "N/A")
            
            # Get hourly data for morning/afternoon
            hourly = day.get("hourly", [])
            morning = hourly[4] if len(hourly) > 4 else {}  # ~8am
            afternoon = hourly[8] if len(hourly) > 8 else {}  # ~2pm
            
            morning_desc = morning.get("weatherDesc", [{}])[0].get("value", "N/A")
            afternoon_desc = afternoon.get("weatherDesc", [{}])[0].get("value", "N/A")
            
            result += f"📅 {date}\n"
            result += f"   🌡️ {min_temp}°C - {max_temp}°C (avg: {avg_temp}°C)\n"
            result += f"   🌅 Morning: {morning_desc}\n"
            result += f"   ☀️ Afternoon: {afternoon_desc}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error getting forecast: {str(e)}"


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get weather information")
    parser.add_argument("location", help="City name")
    parser.add_argument("--forecast", "-f", action="store_true", help="Show forecast")
    parser.add_argument("--days", "-d", type=int, default=3, help="Days for forecast (1-3)")
    
    args = parser.parse_args()
    
    if args.forecast:
        print(get_forecast(args.location, args.days))
    else:
        print(get_weather(args.location))