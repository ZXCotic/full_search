import requests
import sys
from PIL import Image
from io import BytesIO

def get_spn(toponym_json: dict) -> str:
    bounds = toponym_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]
    lower_corner_x, lower_corner_y = map(float, bounds["lowerCorner"].split())
    upper_corner_x, upper_corner_y = map(float, bounds["upperCorner"].split())
    x_long = str(round(upper_corner_x - lower_corner_x))
    y_long = str(upper_corner_y - lower_corner_y)
    return ",".join([x_long, y_long])

def fetch_geocoder_data(toponym_to_find: str) -> dict:
    geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "geocode": toponym_to_find,
        "format": "json"
    }
    response = requests.get(geocoder_api_server, params=geocoder_params)
    response.raise_for_status()
    return response.json()

def fetch_static_map(toponym_coords: str, spn: str) -> bytes:
    static_api_server = "https://static-maps.yandex.ru/v1"
    static_params = {
        "ll": toponym_coords,
        "spn": spn,
        "maptype": "map",
        "pt": f'{toponym_coords},round',
    }
    response = requests.get(static_api_server, params=static_params)
    response.raise_for_status()
    return response.content

def main():
    toponym_to_find = " ".join(sys.argv[1:])

    if not toponym_to_find:
        print("Ошибка: Необходимо ввести название места.")
        sys.exit(1)

    try:
        json_geocoder_response = fetch_geocoder_data(toponym_to_find)
        toponym = json_geocoder_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coords = toponym["Point"]["pos"]
        spn = get_spn(json_geocoder_response)

        static_map_content = fetch_static_map(toponym_coords, spn)
        Image.open(BytesIO(static_map_content)).show()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        sys.exit(1)
    except (KeyError, IndexError) as e:
        print(f"Ошибка обработки данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
