import requests
import json
r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"get_compviz_stages fib-func"})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))
