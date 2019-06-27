import os, os.path
import cherrypy
from cherrypy.lib.static import serve_file
from Crypto.Hash import MD5
import db

cherrypy.config.update({"server.socket_port" : 10021})
baseDir = os.path.dirname(os.path.abspath(__file__))

config = {
    "/":      {
             "tools.sessions.on": True,
             "tools.staticdir.root": baseDir
    },
    "/js":    { "tools.staticdir.on": True,
             "tools.staticdir.dir": "./Frontend/js" },
    "/css":   { "tools.staticdir.on": True,
             "tools.staticdir.dir": "./Frontend/css" },
    "/html":  { "tools.staticdir.on": True,
             "tools.staticdir.dir": "./Frontend/" },
    "/images":{ "tools.staticdir.on": True,
             "tools.staticdir.dir": "./Frontend/images" },
}

class List(object):
    @cherrypy.expose
    def index(self, type=None, name=None, color=None):
        if type == "names":
            return db.typeEqName()
        elif type == "detected":
            if name is None and color is None:
                return db.typeEqDetected()
            elif name is not None and color is None:
                return db.typeEqDetectedName(name)
            elif name is not None and color is not None:
                return db.typeEqDetectedNameAndColor(name, color)

class Get(object):
    @cherrypy.expose
    def index(self, id=None):
        if "cropped" in id:
            return serve_file(os.path.join(baseDir, "Storage/Objects/" + id + ".jpeg/") , "application/x-download", "attachment")
        return serve_file("./Storage/Originals/" + id + "/", "application/x-download", "attachment")

class Put(object):
    @cherrypy.expose
    def index(self, photo):

        h = MD5.new()
        data = b""
        size = 0
        tipo = photo.filename.split(".")
        tipo = tipo[len(tipo) -1]

        while True:
            block = photo.file.read(4096)
            if not block:
                break
            data = data + block
            h.update(block)
            size += len(block)

        name = h.hexdigest()
        file = os.path.join("./Storage/Originals/" + name )
        with open(file, 'wb') as fout:
            fout.write(data)

        db.identify_object(name)

        raise cherrypy.HTTPRedirect("/page3")

class Root(object):
    def __init__(self):
        self.list = List();
        self.put = Put();
        self.get = Get();

    @cherrypy.expose
    def index(self):
        return open("./Frontend/index.html").read()

    @cherrypy.expose
    def page2(self):
        return open("./Frontend/pagina2.html").read()

    @cherrypy.expose
    def page3(self):
        return open("./Frontend/pagina3.html").read()

    @cherrypy.expose
    def page4(self):
        return open("./Frontend/pagina4.html").read()

    @cherrypy.expose
    def page5(self):
        return open("./Frontend/pagina5.html").read()

    index.exposed = True

if __name__ == "__main__":
    cherrypy.tree.mount(Root(), "/", config=config)
    cherrypy.server.start()
