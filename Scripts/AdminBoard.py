import tornado.web


class AdminHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("../static/html/AdminPanel.html")


