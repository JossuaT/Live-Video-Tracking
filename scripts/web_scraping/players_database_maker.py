from bs4 import BeautifulSoup
import requests
import re
import json

## Fonction get_soup
def get_soup(url: str) -> BeautifulSoup:
    """
    Get soup from url
    """
    result = requests.get(url)
    soup = BeautifulSoup(result.content, 'html5lib')
    return soup

def get_full_url(url: str, base_url: str = "https://www.lequipe.fr/"):
    """
    Concatenate base_url and url
    """
    return (base_url + url[1:])

def get_players_id (url : str) -> int:
    """
    Find the id of the player in his card's url
    """
    pos = re.search(r'\d+$', url[:-5]).start()
    return url[pos:-5]

def get_position_number (pos: str) -> str:
    """
    Find the position number with position name
    """
    positions = {
        "Pilier": "1_3",
        "Talonneur": "2",
        "2e ligne": "4_5",
        "3e ligne": "6_7_8",
        "Mêlée" : "9",
        "Ouverture": "10",
        "3/4 centre": "12_13",
        "3/4 aile": "11_14",
        "Arrière": "15",
    }
    return positions[pos]

def get_links_to_clubs_pages(url: str) -> list:
    """
    Get the soup and collect the links of every top 14 club pages
    """
    soup = get_soup(url)
    exts = []
    for element in soup.find_all('div', {'class': 'DataSelect__item'}):
        exts.extend([child['href'] for child in element.children if child['href'].count('/') == 3])
    links = [get_full_url(ext) for ext in exts]
    return links

def get_links_to_clubs_cards(urls: list) -> list:
    """
    Get the soup and collect the links of every top 14 club cards
    """
    exts = []
    for url in urls:
        soup = get_soup(url)
        for element in soup.find_all('a', {'class': 'Link NavItem'}):
            exts.extend(element['href'] for child in element.children if 'fiche' in str(child.string))
    links = [get_full_url(ext) for ext in exts]
    return links

def get_links_to_players_cards (urls: list) -> list:
    """
    Get the soup and collect the links to the pages of every top 14 players
    """
    exts = []
    for url in urls:
        soup = get_soup(url)
        section = soup.find_all('section', {'class': 'Palmares effectifclub'})[0]
        for element in section.find_all('td', {'class': 'nom'}):
            exts.extend(child['href'] for child in element.children)           
    links = [get_full_url(ext) for ext in exts]
    return links

def get_players_database(urls: list) -> dict:
    """
    Get the soup and collect the data of every top 14 player
    """
    players = {}
    for url in urls:
        if urls.index(url)%30 == 0:
            import time
            time.sleep(1.5)
        
        soup = get_soup(url)
        identite = []    

        for element in soup.find_all('section', {'class': 'titre data-content'}):
            name = element.find('h1', {'class': 'nom_sportif'}).string
            team = element.find('a', {'class': 'FG_club'}).string
            img = element.find('img')['src']
        for element in soup.find_all('div', {'class': 'identite'}):
            for ligne in element.find_all('tr'):
                identite.extend(strong.string for strong in ligne.find('strong'))
        try:
            players[get_players_id(url)] = {
                "name": name,
                "team": team,
                "img": img,
                "nationality": identite[0],
                "birth": identite[1],
                "height": identite[2],
                "weight": identite[3],
                "position": identite[4],
                "position_number": get_position_number(identite[4]),
            }
        except IndexError:
            try:
                print(" =  =  =  =  =  =  =  =  =  =  =  =  =  =  = ")
                print(f"Error on player id : {get_players_id(url)}. \n Il s'agit de {name}, qui joue à {team}")
                print(" =  =  =  =  =  =  =  =  =  =  =  =  =  =  = ")
            except:
                pass
            pass
    return players


##### ##### #####
##### ##### #####


base_url = "https://www.lequipe.fr/"
top14_url = "https://www.lequipe.fr/Rugby/Top-14/"

club_pages_urls = get_links_to_clubs_pages(top14_url)

club_cards_urls = get_links_to_clubs_cards(club_pages_urls)

player_cards_urls = get_links_to_players_cards(club_cards_urls)

players_database = get_players_database(player_cards_urls)


# Enregistrer les données dans un fichier JSON
with open('project/data/top14_players_database.json', 'w') as f:
    json.dump(players_database, f, indent=4)
    
