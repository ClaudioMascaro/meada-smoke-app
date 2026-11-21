"""Record the two POST URLs without performing any network requests."""

import json
from pathlib import Path
import runpy
import sys
from types import ModuleType


def main():
    source = Path(__file__).resolve().parents[1] / 'orders/clients/python/class_probe.py'
    requests = ModuleType('requests')
    sys.modules['requests'] = requests
    clients = runpy.run_path(str(source))
    records = []
    for name in ('Changed', 'Ordinary'):
        caller = f'{name}.send'

        def post(url):
            records.append({'caller': caller, 'method': 'POST', 'url': url})

        requests.post = post
        clients[name]().send()
    print(json.dumps(records))


if __name__ == '__main__':
    main()
