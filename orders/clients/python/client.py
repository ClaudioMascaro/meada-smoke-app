import os

import requests


def use_host(host):
    def decorate(original):
        def replacement():
            return host

        return replacement

    return decorate


@use_host("https://shared.smoke.example")
def shared_base():
    return os.getenv("SMOKE_ORDERS_URL")


def configured_base():
    return os.getenv("SMOKE_ORDERS_URL")


def send_shared():
    return requests.post(shared_base() + "/orders")


def send_configured():
    return requests.post(configured_base() + "/orders")
