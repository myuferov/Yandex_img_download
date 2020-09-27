from selenium import webdriver  # pip install Selenium
from selenium.webdriver.chrome.options import Options

import requests  # pip install requests
from bs4 import BeautifulSoup  # pip install beautifulsoup4 + pip install lxml
import sys
import os
from PIL import Image, ImageDraw, ImageFont  # pip install Pillow
from rutermextract import TermExtractor  # pip install rutermextract

global driver

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")     #
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")       # для вызова Chrome в режиме без головы
chrome_options.add_argument("--no-sandbox")     # Для обхода модели безопасности ОС.

chrome_options.add_argument('disable-infobars')
chrome_options.add_argument("--disable-notifications")      # убрать всплывающее окна уведомлений

prefs = {"profile.managed_default_content_settings.images": 2}  # запрет загрузки изображений так как мы получаем только ссылки
chrome_options.add_experimental_option("prefs", prefs)


#chrome_options.headless = True # also works
driver = webdriver.Chrome("chromedriver\chromedriver.exe", options=chrome_options)

def normalized_text(text: str):
    term_extractor = TermExtractor()
    normalized = []
    for term in term_extractor(text):
        normalized.append(term.normalized)
    return normalized






def get_html(url):

    driver.get(url)
    html_source = driver.page_source

    #driver.quit()
    return html_source


def get_data(html: object) -> object:
    """


    Parameters
    ----------
    html : Код страницы

    Returns
    -------
    imgUrl : list
        Список ссылок на картинки

    """
    soup = BeautifulSoup(html, 'lxml')
    # Получаем адреса картинок с запроса
    hs = soup.find_all('a', {'class': 'serp-item__link'})

    # Создаем список ссылок для скачивания картинок
    img_url = []
    for h in hs:
        img_url.append("https://yandex.ru" + h['href'])
        # print(img_url)
    return img_url


def save_img(img_ya, text_img, index: int, watermark: bool, cleardir: bool = False):
    """
    

    Parameters
    ----------
    img_ya : TYPE
         Список ссылок на картинки.
    text_img : str
        Текст нанесения на картинку/подпись картинки.
    index : int
        Колличество требуемых изображений.
    watermark : bool
        Нанесение водяного знака.

    Returns
    -------
    None.

    """


    # Очищаем диррикторию '_img'
    if os.path.exists("static\images") is True and cleardir is True:
        dir = os.listdir('static\images')
        for i in range(len(dir)):
            os.remove('static\images' + chr(92) + dir[i])

    # Создаем диррикторию '_img' если не существует
    if os.path.exists("static\images") is False:
        os.mkdir("static\images")
    j = 0
    i = 0
    while j < index:
        # получаем оригинальную ссылку отдельной картинки
        html = get_html(url=img_ya[i])
        soup = BeautifulSoup(html, 'lxml')
        hs = soup.find('img', {'class': 'MMImage-Origin'})
        i = i + 1
        # Бывает такое что некоторые ссылки не срабатывают
        # Если ссылка рабочая то сохраняем изображение в файл
        if hs is not None:
            # загружаем изображение 
            p = requests.get(hs['src'], stream=True).raw
            im = Image.open(p)
            # Добавляем водяной знак
            if watermark is True:
                font = ImageFont.truetype("font\Montserrat.ttf", size=80)
                draw_text = ImageDraw.Draw(im)
                draw_text.text(
                    (100, 1720),  # 1080/(1080/150) //// 1920-150 (-50)
                    text_img,
                    # Добавляем шрифт к изображению
                    font=font,
                    fill='#FF0000')
            # Сохраняем полученное изображение
            im.save("static\images" + chr(92) + text_img + str(j) + ".jpg")
            j += 1
    return


def dowload_ya(text: str, iw: int = None, ih: int = None, kol: int = 5, watermark: bool = False):
    """
    

    Parameters
    ----------
    text : str
        Поисковой запрос.
    iw : int, optional
        Размер изображения по горизонтали. The default is None.
    ih : int, optional
        Размер изображения по вертикали. The default is None.
    kol : int, optional
        Колличество требуемых изображений. The default is 5.
    watermark : bool, optional
        Добавление водяного знака на изображение. The default is False.

    Returns
    -------
    Функция делает запрос в яндекс картинки и скачивает их в папку "_img"

    """
    # Выделяем основыную мысль из текста
    text1 = normalized_text(text)

    # Формируем поисковый запрос
    for i in range(len(text1)):
        text_url = text1[i].replace(' ', '%20')

        if iw is None and ih is not None:
            url = "https://yandex.ru/images/search?text=" + text_url + "&itype=jpg"
        if iw is not None and ih is not None:
            url = "https://yandex.ru/images/search?text=" + text_url + "&isize=eq&iw=" + str(iw) + "&ih=" + str(
                ih) + "&itype=jpg"
        if (iw is None and ih is not None) or (iw is not None and ih is None):
            print("\033[31m Error:" + "\033[37m не правильно задан размер")
            sys.exit()

        # Делаем запрос в яндекс картинки и получаем ссылки на картинки
        html = get_html(url=url)
        img_ya = get_data(html)

        # Передаем полученные сссылки в Save_img которая сохраняет изображения
        if i == 0:
            save_img(img_ya=img_ya, text_img=text1[i], index=kol, watermark=watermark, cleardir=True)
        else:
            save_img(img_ya=img_ya, text_img=text1[i], index=kol, watermark=watermark, cleardir=False)
    #driver.quit()
    return


if __name__ == "__main__":
    dowload_ya(text="Красивые девушки", kol=2, iw=1080, ih=1920, watermark=True)
