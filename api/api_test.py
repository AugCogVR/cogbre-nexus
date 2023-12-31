import requests
import json
import uuid
import glob
import os

userId = "Test123"

# Post a command to the Nexus API, get the response, parse it as JSON, and return it
def postCommand(commandList):
    # r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":json.dumps(commandList)})
    r = requests.post('http://127.0.0.1:5000/sync_portal', json={"userId":userId, "command":commandList})
    # print(f"JSON: {r.json()}")
    parsed = json.loads(r.json())
    return parsed

# Run a test given the provided command list. Return the result.
def runTest(commandList, dumpToOutput = True):
    print("\n========================")
    print(f"TEST: {commandList}")
    print("========================")
    parsed = postCommand(commandList)
    if (dumpToOutput):
        print(json.dumps(parsed, indent = 4))
    return parsed

# Dump provided output to a temporary file. Filename is based on testName. 
def dumpToTmpFile(parsedOutput, testName):
    fileName = f"apitesttmp_{testName}_{userId}_{uuid.uuid4().hex}"
    with open(fileName, mode="wt") as f:
        f.write(json.dumps(parsedOutput, indent = 4))
    print(f"OUTPUT dumped to {fileName}")


# ============================
# PREPARATION
# ============================

# Delete old test output files. Rename/move any prior test results you want to keep!
for f in glob.glob("apitesttmp*"):
    os.remove(f)


# ============================
# RUN THE TESTS
# ============================

# Test an API call developed for a dormant initiative -- comment it out for now. 
# # Grab "compviz_stages" data for a function
# parsed = runTest(["get_compviz_stages", "fib-func"], False)
# dumpToFile(parsed, f"tmp_get_compviz_stages_fib-func_{userId}_{uuid.uuid4().hex}")

# Test an API call developed for a dormant initiative -- comment it out for now. 
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

# TEST: Get basic blocks for file represented by OID
parsed = runTest(["oxide_get_basic_blocks", fileOid], False)
dumpToTmpFile(parsed, f"basicblocks_{fileName}")

# TEST: Exercise the "retrieve" command -- in this case, just get basic blocks again
parsed = runTest(["oxide_retrieve", "basic_blocks", [ fileOid ], { "disassembler":"ghidra_disasm" }], False)
dumpToTmpFile(parsed, f"basicblocksviaretrieve_{fileName}")

# TEST: Get names for OID
parsed = runTest(["oxide_get_names_from_oid", fileOid])

# TEST: Get file size for file represented by OID
parsed = runTest(["oxide_get_oid_file_size", fileOid])

# TEST: Get disassembly for file represented by OID (default)
parsed = runTest(["oxide_get_disassembly", fileOid], False)
dumpToTmpFile(parsed, f"disasm_{fileName}")

# TEST: Get disassembly for file represented by OID (complete)
parsed = runTest(["oxide_get_disassembly_complete", fileOid], False)
dumpToTmpFile(parsed, f"disasm_complete_{fileName}")

# TEST: Get disassembly for file represented by OID (just instruction strings)
parsed = runTest(["oxide_get_disassembly_strings_only", fileOid], False)
dumpToTmpFile(parsed, f"disasm_strings_{fileName}")

# # ***TEMP*** TEST: Get disassembly for specific file
# parsed = runTest(["oxide_get_disassembly_strings_only", "53acc9e9b3f092d205281b0a51ba8d070e7e3128"], False)
# dumpToTmpFile(parsed, f"disasmstr_host")

# TEST: Get function info for a binary file
parsed = runTest(['oxide_get_function_info', fileOid])

# # ***TEMP*** TEST: Get function info for specific file
# parsed = runTest(['oxide_get_function_info', "53acc9e9b3f092d205281b0a51ba8d070e7e3128"])

# TEST: Retrieve strings for a binary
parsed = runTest(["oxide_retrieve", "strings", [ fileOid ], {}])

# TEST: Retrieve file stats for a binary
parsed = runTest(["oxide_retrieve", "file_stats", [ fileOid ], {}])

# TEST: Retrieve function_extract
parsed = runTest(["oxide_retrieve", "function_extract", [ fileOid ], {}], False)
dumpToTmpFile(parsed, f"function_extract_{fileName}")

# TEST: Retrieve ghidra_decmap
parsed = runTest(["oxide_retrieve", "ghidra_decmap", [ fileOid ], {}], False)
dumpToTmpFile(parsed, f"ghidra_decmap_{fileName}")


print("\n========================")

