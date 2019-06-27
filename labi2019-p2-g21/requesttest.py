import sqlite3 as sql
import json
import requests
import hashlib
import os, os.path
from PIL import Image

count = 0


def identify_object(image):
    session = requests.Session()
    URL="http://image-dnn-sgh-jpbarraca.ws.atnog.av.it.pt/process"
    with open(image, 'rb') as f:
        file = {'img': f.read()}
        r = session.post(url=URL, files=file, data=dict(thr=0.5))
        image_ori = Image.open(image)
        image_ori.save('Storage/Originals/' + image, 'JPEG')
        if r.status_code == 200:
            i = 0
            j = r.json()
            for s in j:
                objFileName = 'croped_' + str(i) + '_' + str(os.path.basename(image))
                limits = (s["box"]["x"], s["box"]["y"], s["box"]["x1"], s["box"]["y1"])
                image_obj = image_ori.crop(limits)
                objPath = 'Storage/Objects/' + objFileName
                image_obj.save(objPath, 'JPEG')
                putObject(s, md5(image), md5(objPath), image_obj)
                i += 1

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return str(hash_md5.hexdigest())

def dominantRGB_img(image):
    width, height = image.size

    r_total = 0
    g_total = 0
    b_total = 0

    count = 0
    for x in range(0, width):
        for y in range(0, height):
            r, g, b = image.getpixel((x,y))
            r_total += r
            g_total += g
            b_total += b
            count += 1

    if r_total/count > g_total/count and r_total/count > b_total/count : 
        return 'red'
    elif g_total/count > r_total/count and g_total/count > b_total/count : 
        return 'green'
    elif b_total/count > g_total/count and b_total/count > r_total/count : 
        return 'blue'

def putObject(jFile, original, image, img):
    db = sql.connect('imagens.db')
    curs = db.cursor()
    x = dominantRGB_img(img)
    curs.execute('''INSERT INTO images VALUES (NULL, ?, ?, ?, ?, ?)''', (str(jFile['class']), original, image, jFile['confidence'] * 100, x))

    db.commit()
    curs.close()

identify_object('Bugatti-La_Voiture_Noire-2019-1600-03-Header.jpg')
