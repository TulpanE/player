from bs4 import BeautifulSoup
import requests
from settings import HITMO_URL


def hitmo_available() -> bool:
    try:
        response: requests.Response = requests.get(HITMO_URL)
        return True if response.status_code == 200 else False

    except requests.exceptions.ConnectionError:
        return False


def find_tracks(track_name: str) -> list[dict[str, str]]:
    if not hitmo_available():
        return []

    response: requests.Response = requests.get(f'{HITMO_URL}/search?q={track_name}')
    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
    tracks = soup.findAll('li', class_='tracks__item track mustoggler')

    if not tracks:
        return []

    track_list: list[dict[str, str]] = []

    for track in tracks:
        image_url: str = track.find('div', class_='track__img').get('style').replace("background-image: url('", '').replace("');", '')
        title: str = track.find('div', class_='track__title').text.strip()
        artist: str = track.find('div', class_='track__desc').text.strip()
        href: str = track.find('a', class_='track__download-btn').get('href')

        track_list.append(
            {
                'picture_url': image_url,
                'title': title,
                'author': artist,
                'url_down': href
            }
        )

    return track_list
