import sqlite3 as sql
import json
import requests
import hashlib
import os, os.path
from PIL import Image
#from Crypto.Hash import MD5

count = 0

def identify_object(image):
    session = requests.Session()
    URL="http://image-dnn-sgh-jpbarraca.ws.atnog.av.it.pt/process"
    with open('./Storage/Originals/' + image, 'rb') as f:
        file = {'img': f.read()}
        r = session.post(url=URL, files=file, data=dict(thr=0.5))
        image_ori = Image.open('./Storage/Originals/' + image)
        # image_ori.save('Storage/Originals/' + image, 'JPEG')
        if r.status_code == 200:
            i = 0
            j = r.json()
            for s in j:
                #fname_ori = str(os.path.basename(image))
                x = image.split(".")

                objFileName = ('cropped_' + str(i) + '_' + x[0])
                limits = (s["box"]["x"], s["box"]["y"], s["box"]["x1"], s["box"]["y1"])
                image_obj = image_ori.crop(limits)


                #objFileName_md5 = md55(objFileName)
                objPath = './Storage/Objects/' + objFileName
                image_obj.save(objPath, 'JPEG')

                putObject(s, x[0], objFileName, image_obj)
                i += 1

# def md55(fname):
#     hash_md5 = hashlib.md5()
#     with open(fname, 'rb') as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_md5.update(chunk)
#     return str(hash_md5.hexdigest())

# def md5(fname):
#     h = MD5.new()
#     data = b""
#     size = 0
#     tipo = fname.split(".")
#     tipo = tipo[len(tipo) -1]
#
#     while True:
#         block = fname.read(4096)
#         if not block:
#             break
#         data = data + block
#         h.update(block)
#         size += len(block)
#
#     name=h.hexdigest()
#     name=name[0:16]


def toWrite(cursor, row):
	x = {}
	for i, col in enumerate(cursor.description):
		x[col[0]] = row[i]
	return x

def typeEqName():
    dataB = sql.connect("imagens.db")
    dataB.row_factory = toWrite
    curs = dataB.cursor()

    name = curs.execute("""SELECT class FROM images""").fetchall()

    return json.dumps(name)

def typeEqDetected():
    dataB = sql.connect("imagens.db")
    dataB.row_factory = toWrite
    curs = dataB.cursor()

    name = curs.execute("""SELECT class, original, image, confidence FROM images""").fetchall()

    return json.dumps(name)


def typeEqDetectedName(nome):
    dataB = sql.connect("imagens.db")
    dataB.row_factory = toWrite
    curs = dataB.cursor()

    name = curs.execute("""SELECT original, image, confidence FROM images WHERE class LIKE ?""",(nome, )).fetchall()

    return json.dumps(name)


def typeEqDetectedNameAndColor(nome, color):
    dataB = sql.connect("imagens.db")
    dataB.row_factory = toWrite
    curs = dataB.cursor()

    name = curs.execute("""SELECT original, image, confidence FROM images WHERE class LIKE ? AND color LIKE ?""",(nome, color)).fetchall()

    return json.dumps(name)


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

# def getID(image):
#     db = sql.connect('imagens.db')
#     curs = db.cursor()
#
#     curs.execute(''' SELECT class FROM''')

def putObject(jFile, original, objectt, img):
    db = sql.connect('imagens.db')
    curs = db.cursor()
    x = dominantRGB_img(img)


    curs.execute('''INSERT INTO images VALUES (NULL, ?, ?, ?, ?, ?)''', (str(jFile['class']), original, objectt, jFile['confidence'] * 100, x))

    db.commit()
    curs.close()
