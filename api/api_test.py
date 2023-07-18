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

# Oxide tests assume Oxide is enabled on the server/api side, and that it contains at least one collection

print("\n========================")
print("TEST: oxide_collection_names")
print("========================")
r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"oxide_collection_names"})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))

collectionName = parsed[0]

print("\n========================")
print("TEST: get_cid_from_name " + collectionName)
print("========================")
r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"oxide_get_cid_from_name " + collectionName})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))

print("\n========================")
print("TEST: get_collection_info " + collectionName)
print("========================")
r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId": "123", "command":"oxide_get_collection_info " + collectionName + " files"})
# print(r.status_code)
# print(r.json())
parsed = json.loads(r.json())
print(json.dumps(parsed, indent = 4))

print("\n========================")

