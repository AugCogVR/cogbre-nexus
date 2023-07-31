import requests
import json

userId = "User123"

def postCommand(commandList):
    # r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":json.dumps(commandList)})
    r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":commandList})
    # print(f"JSON: {r.json()}")
    parsed = json.loads(r.json())
    return parsed

def runTest(commandList):
    print("\n========================")
    print(f"TEST: {commandList}")
    print("========================")
    parsed = postCommand(commandList)
    print(json.dumps(parsed, indent = 4))
    return parsed


# Grab "compviz_stages" data for a function
runTest(["get_compviz_stages", "fib-func"])

# Grab "canned_oxide_program" data for a program
runTest(["get_canned_oxide_program", "elf_fib_recursive"])


# Oxide tests below assume Oxide is enabled on the server/api side, and that it contains at least one collection

# TEST: Grab list of all collection names
parsed = runTest(["oxide_collection_names"])
# Grab the first collection name returned
collectionName = "<NOT FOUND>"
if (len(parsed) > 0):
    collectionName = parsed[0]

# TEST: Get CID for the first returned collection
parsed = runTest(["oxide_get_cid_from_name", collectionName])

# TEST: Get collection info for the first returned collection
parsed = runTest(["oxide_get_collection_info", collectionName, "files"])
# Grab the first file name returned
fileName = "<NOT FOUND>"
if (parsed["files"] is not None):
    if (len(parsed["files"]) > 0):
        fileName = parsed["files"][0]

# TEST: Get info for a filename
# This call returns None and I'm not sure why. I'm probably not giving it a proper filename...???
# TODO: Fix it
# parsed = runTest(["oxide_get_file_info", fileName])

# TEST: Get oids for a filename. THIS IS SO SLOW. 
# Cheat: 'apt-ftparchive' = "78fc002331ad21a9cec9b300f009ce9693f3eee3" on my system
parsed = runTest(["oxide_get_oids_with_name", fileName])
# Grab the first oid returned
fileOid = list(parsed.keys())[0]
# fileOid = "78fc002331ad21a9cec9b300f009ce9693f3eee3"

# TEST: See available modules
parsed = runTest(["oxide_get_available_modules", "all"])
moduleNames = parsed

# TEST: See doc strings for some modules
if (len(moduleNames) > 0):
    for moduleName in moduleNames[0:3]:
        parsed = runTest(["oxide_documentation", moduleName])
else:
    print("ERROR: No module names returned")

# TEST: See types for some modules
if (len(moduleNames) > 0):
    for moduleName in moduleNames[0:3]:
        parsed = runTest(["oxide_get_mod_type", moduleName])
else:
    print("ERROR: No module names returned")

# TEST: Call the basic_blocks module on our fileOid
moduleName = "basic_blocks"
commandList = ["oxide_get_mod_type", moduleName]
moduleType = postCommand(commandList)
commandList = ["oxide_single_call_module", moduleType, moduleName]
fileOids = [ fileOid ]
commandList.append(fileOids)
opts = { "disassembler":"ghidra_disasm" }
commandList.append(opts)
parsed = runTest(commandList)



print("\n========================")

