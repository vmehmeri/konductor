from typing import Dict


def get_weather_report(city: str) -> Dict:
    """
    Fetches the current weather for a given city.

    Args:
        city: The city for which to retrieve the weather report.

    Returns:
        A dictionary containing the weather information.
        Example success: {'status': 'success', 'report': 'The weather is sunny.'}
        Example error: {'status': 'error', 'message': 'City not found.'}
    """
    print(f"TOOL: Called get_weather_report for city: {city}")
    # This is a mock implementation for the POC.
    # In a real scenario, this would call a weather API.
    city_lower = city.lower()
    if city_lower == "stockholm":
        return {
            "status": "success",
            "report": "It is currently sunny with a temperature of 18 degrees Celsius in Stockholm.",
        }
    elif city_lower == "london":
        return {"status": "success", "report": "It is cloudy with a high chance of rain in London."}
    else:
        return {
            "status": "error",
            "message": f"Sorry, weather information for '{city}' is not available.",
        }
