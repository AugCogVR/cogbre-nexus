import requests
import json
import uuid

userId = "User123"

def postCommand(commandList):
    # r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":json.dumps(commandList)})
    r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":commandList})
    # print(f"JSON: {r.json()}")
    parsed = json.loads(r.json())
    return parsed


def runTest(commandList, dumpToOutput = True):
    print("\n========================")
    print(f"TEST: {commandList}")
    print("========================")
    parsed = postCommand(commandList)
    if (dumpToOutput):
        print(json.dumps(parsed, indent = 4))
    return parsed


def dumpToFile(parsedOutput, fileName):
    with open(fileName, mode="wt") as f:
        f.write(json.dumps(parsedOutput, indent = 4))
    print(f"OUTPUT dumped to {fileName}")


# Next two tests grab canned or semi-canned info from the API.
# They are likely commented out due to no longer being relevant.

# # Grab "compviz_stages" data for a function
# parsed = runTest(["get_compviz_stages", "fib-func"], False)
# dumpToFile(parsed, f"tmp_get_compviz_stages_fib-func_{userId}_{uuid.uuid4().hex}")

# # Grab "canned_oxide_program" data for a program
# parsed = runTest(["get_canned_oxide_program", "elf_fib_recursive"], False)
# dumpToFile(parsed, f"tmp_get_canned_oxide_program_elf_fib_recursive_{userId}_{uuid.uuid4().hex}")


# Oxide tests below assume Oxide is enabled on the server/api side, and that it contains 
# at least one collection with at least one binary file

# TEST: Grab list of all collection names
parsed = runTest(["oxide_collection_names"])
# Grab the first collection name returned
collectionName = "<NOT FOUND>"
if (len(parsed) > 0):
    collectionName = parsed[0]

# TEST: Get CID for the first returned collection
parsed = runTest(["oxide_get_cid_from_name", collectionName])
cid = parsed

# TEST: Get OIDs for the above CID
parsed = runTest(["oxide_get_oids_with_cid", cid])

# TEST: Get collection info for the first returned collection
parsed = runTest(["oxide_get_collection_info", collectionName, "all"])
# Grab the first file name returned
fileName = "<NOT FOUND>"
if (parsed["files"] is not None):
    if (len(parsed["files"]) > 0):
        fileName = parsed["files"][0]

# TEST: Get info for a filename
# This call returns None and I'm not sure why. I'm probably not giving it a proper filename...???
# TODO: Fix it
# parsed = runTest(["oxide_get_file_info", fileName])

# TEST: Get oids for a filename. THIS CAN BE SO SLOW IF THE COLLECTION IS HUGE. 
parsed = runTest(["oxide_get_oids_with_name", fileName])
fileOid = list(parsed.keys())[0]

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
parsed = runTest(commandList, False)
dumpToFile(parsed, f"tmp_test_basicblocks_{fileName}_{userId}_{uuid.uuid4().hex}")

# TEST: Get names from OID
parsed = runTest(['oxide_get_names_from_oid', fileOid])

# TEST: Get file size for file represented by OID
parsed = runTest(['oxide_get_oid_file_size', fileOid])

# TEST: Get disassembly for file represented by OID 
parsed = runTest(['oxide_get_disassembly', fileOid], False)
dumpToFile(parsed, f"tmp_test_disasm_{fileName}_{userId}_{uuid.uuid4().hex}")

# TEST: Use another method to get disassembly for file represented by OID 
# THIS METHOD IS NOT RECOMMENDED -- TEST COMMENTED OUT 
# moduleName = "disassembly"
# commandList = ["oxide_get_mod_type", moduleName]
# moduleType = postCommand(commandList)
# commandList = ["oxide_single_call_module", moduleType, moduleName]
# fileOids = [ fileOid ]
# commandList.append(fileOids)
# opts = { "disassembler":"ghidra_disasm", "decoder":"native" }
# commandList.append(opts)
# parsed = runTest(commandList, False)
# dumpToFile(parsed, f"tmp_test_disasm2_{fileName}_{userId}_{uuid.uuid4().hex}")


print("\n========================")

