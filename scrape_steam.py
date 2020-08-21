#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

url = "https://steamcommunity.com/profiles/76561199000516379/friends"

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser', from_encoding="iso-8859-1")
for element in soup.find_all("div", class_="in-game"):
  game = element.find("span", class_="friend_game_link")
  if game:
    if(game.text.split("\n")[0][-12:] == ": REMASTERED"):
      name = element.find("div",  class_="friend_block_content")
      if name:
        print(name.text.split("\n")[0])

