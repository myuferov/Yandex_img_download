from flask import Flask, render_template, request       # pip install Flask
import os
import random
from Download_YA import dowload_ya, normalized_text


app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        textstr = request.form['textstr']  # получает текст из формы
        len_textstr = len(normalized_text(textstr))
        if len_textstr == 1:
            dowload_ya(text=textstr, kol=4, iw=1080, ih=1920, watermark=True)
        elif len_textstr == 2 or len_textstr == 3:
            dowload_ya(text=textstr, kol=2, iw=1080, ih=1920, watermark=True)
        elif len_textstr > 3:
            dowload_ya(text=textstr, kol=1, iw=1080, ih=1920, watermark=True)
        else:
            return render_template("clear.html")


        img1 = os.listdir('static\images')  # получаем список имен изображений
        img = random.sample(img1, len(img1))  # перемешиваем список чтоб выводить разные изображения
        for i in range(len(img)):
            img[i] = img[i].replace(' ', '%20')
            img[i] = "static\images" + chr(92) + img[i]

    else:
        return render_template("clear.html")
    return render_template("index.html", img=img)


if __name__ == "__main__":
    app.run()
