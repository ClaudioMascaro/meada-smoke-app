import os
import requests

def install(cls):
    def replacement(self):
        return "https://shared.smoke.example"
    cls.changed_origin = replacement
    return cls

@install
class Changed:
    def changed_origin(self):
        return os.getenv("SMOKE_ORDERS_URL")
    def send(self):
        return requests.post(self.changed_origin() + "/orders")

class Ordinary:
    def ordinary_origin(self):
        return os.getenv("SMOKE_ORDERS_URL")
    def send(self):
        return requests.post(self.ordinary_origin() + "/orders")
