import falcon
import json


class MyResource(object):
    response = [{"id": 1, "name": "Company One"}, {"id": 2, "name": "Company Two"}]

    def on_get(self, req, resp):
        resp.body = json.dumps(self.response)

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_201
        resp.body = json.dumps({"success": True})


api = falcon.App()
my_endpoint = MyResource()
api.add_route('/v1', my_endpoint)
