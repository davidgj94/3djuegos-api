from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote
from urllib.error import HTTPError
import re
from datetime import datetime

_3DJUEGOS_URL = "http://www.3djuegos.com/"

_3DJUEGOS_REVIEWS_URL = _3DJUEGOS_URL + "novedades/analisis/"

_3DJUEGOS_RELEASES_URL = _3DJUEGOS_URL + "lanzamientos-juegos/"


PLATFORMS = {"pc": 1,
             "ps4": 37,
             "xbox-one": 38,
             "nintendo-switch": 41,
             "3ds": 34,
             "ps3": 2,
             "x360": 4,
             "wiiu": 35,
             "wii": 3,
             "psvita": 36,
             "psp": 6,
             "ios": 9,
             "android": 32}

# PLATFORMS_URLS = {"pc": _3DJUEGOS_REVIEWS_URL + "juegos-pc/0f1f0f0/fecha/",
#                   "ps4": _3DJUEGOS_REVIEWS_URL + "juegos-ps4/0f37f0f0/fecha/",
#                   "xone": _3DJUEGOS_REVIEWS_URL + "juegos-xbox-one/0f38f0f0/fecha/",
#                   "switch": _3DJUEGOS_REVIEWS_URL + "juegos-nintendo-switch/0f41f0f0/fecha/",
#                   "3ds": _3DJUEGOS_REVIEWS_URL + "juegos-3ds/0f34f0f0/fecha/",
#                   "ps3": _3DJUEGOS_REVIEWS_URL + "juegos-ps3/0f2f0f0/fecha/",
#                   "x360": _3DJUEGOS_REVIEWS_URL + "juegos-x360/0f4f0f0/fecha/",
#                   "wiiu": _3DJUEGOS_REVIEWS_URL + "juegos-wiiu/0f35f0f0/fecha/",
#                   "wii": _3DJUEGOS_REVIEWS_URL + "juegos-wii/0f3f0f0/fecha/",
#                   "vita": _3DJUEGOS_REVIEWS_URL + "juegos-psvita/0f36f0f0/fecha/",
#                   "psp": _3DJUEGOS_REVIEWS_URL + "juegos-psp/0f6f0f0/fecha/",
#                   "ios": _3DJUEGOS_REVIEWS_URL + "juegos-ios/0f9f0f0/fecha/",
#                   "android": _3DJUEGOS_REVIEWS_URL + "juegos-android/0f32f0f0/fecha/"}

ALL_URL = _3DJUEGOS_REVIEWS_URL + "juegos/0f0f0f0/fecha/"

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 ",
    "(KHTML, like Gecko) Chrome/15.0.87")
driver = webdriver.PhantomJS(desired_capabilities=dcap)
driver.set_page_load_timeout(10)
wait = WebDriverWait(driver, 6)

session = requests.Session()
headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) ",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}


##########################################
# HELPERS
##########################################

# def get_platform(soup):
#   content = soup.select("div.fftit.s20.b").pop().text
#   platform = re.search(r'\((.*?)\)', content).group(1)
#   return platform


# def get_scores(soup):
#   return zip([div.span.text for div in soup.select("div.dtc.wi36")],
#              ["3DJuegosScore", "UserScore"])


def get_info(soup):

  info = []

  content = soup.select("div.fftit.s20.b").pop()
  info.append(content.span.text)
  info.append(re.search(r'\((.*?)\)', content.text).group(1))

  for dt, dd in zip(soup.findAll("dt"), soup.findAll("dd")):
    if dt.text == "Desarrollador:":
      info.append(dd.text)
    elif dt.text == "Editor:":
      info.append(dd.text)
    elif dt.text == "Género:":
      info.append(dd.text)

  info.append(soup.find("span", {"itemprop": "releaseDate"}).attrs['content'])

  info.extend([div.span.text for div in soup.select("div.dtc.wi36")])

  return zip(["name", "platform", "study", "publisher", "genre", "releaseDate", "3DJuegosScore", "userScore"], info)


def get_soup_obj(url):
  html = session.get(url, headers=headers).text
  return BeautifulSoup(html, "html.parser")


def is_valid_url(game, url):
  game_norm = "-".join(re.sub('[^a-zA-Z0-9 ]', '', game.lower()).split())
  if re.search("\/([^/]+)\/$", url):
    return game_norm == re.search("\/([^/]+)\/$", url).group(1)
  else:
    return False


##########################################


def get_game_review(game):

  url = _3DJUEGOS_URL + "?q=" + quote(game) + "&zona=resultados-buscador&ni=1"

  try:
    driver.get(url)
  except TimeoutException:
    driver.execute_script("window.stop();")

  try:
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a.xXx.b")))
  except TimeoutException:
    print("The game has not been analysed yet!!!")
    return None

  results = {}
  results["reviews"] = []
  for element in elements:
    if is_valid_url(game, element.get_attribute("href")):
      try:
        soup = get_soup_obj(element.get_attribute("href"))
      except HTTPError:
        print("{} not reachable".format(element.get_attribute("href")))
        continue
      results["reviews"].append({
          key: value for key, value in get_info(soup)})

  return results


def get_latest_games_reviewed(platform="all", limit=5):

  # url = PLATFORMS_URLS.get(platform.lower(), ALL_URL)
  # soup = get_soup_obj(url)
  # divs = soup.select("div.nov_int_txt.wi100")
  # results = {}
  # results["LatestGames"] = [
  #     re.sub(" - Análisis", "", div.h2.a.text) for div in divs[:limit]]

  platform_num = PLATFORMS.get(platform.lower(), 0)

  if platform_num == 0:
    url = _3DJUEGOS_REVIEWS_URL + "juegos/0f0f0f0/fecha/"
  else:
    url = _3DJUEGOS_REVIEWS_URL + "juegos-" + \
        platform + "/0f{}f0f0/fecha/".format(platform_num)

  soup = get_soup_obj(url)
  divs = soup.select("div.nov_int_txt.wi100")
  results = {}
  results["latestGames"] = [
      {"name": re.sub(" - .*$", "", div.h2.a.text)} for div in divs[:limit]]

  return results


def get_releases(platform="all", year=datetime.now().year, month=datetime.now().month):

  platform_num = PLATFORMS.get(platform.lower(), 0)

  if platform_num == 0:
    url = _3DJUEGOS_RELEASES_URL + "todos/por-mes/0/{}/{}/".format(year, month)
  else:
    url = _3DJUEGOS_RELEASES_URL + platform + \
        "/por-mes/{}/{}/{}/".format(platform_num, year, month)

  soup = get_soup_obj(url)
  results = {}
  results["games"] = []
  root = soup.find("div", {"class": "pad_rl10"})
  for div in root.findAll("div"):
    if div.attrs["class"] == ["s20", "ffnav", "b", "mar_t50"]:
      release_date = "{}-{}-{}".format(year, month,
                                       re.search(r'\d+', div.span.text).group())
    elif div.attrs["class"] == ["dtc", "vam"]:
      name = div.a.span.text
      platform = div.div.span.text
      results["games"].append(
          {"name": name, "platform": platform, "releaseDate": release_date})

  return results


print(get_game_review("F1 2017"))
print()
# print(get_latest_games_reviewed("ps4"))
# print()
# print(get_releases("ps4", 2017, 10))
# print()
# print(get_releases())
