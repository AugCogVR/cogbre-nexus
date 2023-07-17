import requests
import json

print("\n========================")
print("TEST: get_compviz_stages fib-func")
print("========================")

r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"get_compviz_stages fib-func"})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))

print("\n========================")
print("TEST: get_canned_oxide_program elf_fib_recursive")
print("========================")

r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"get_canned_oxide_program elf_fib_recursive"})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))

print("\n========================")

