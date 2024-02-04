# cogbre-nexus

"cogbre" = Cognitive Binary Reverse Engineering

This is the server / "nexus" component for "cogbre." 

This application supports research of the [Auburn CSSE Program Understanding Lab](https://program-understanding.github.io/).

It supports the VR front end at https://github.com/AugCogVR/cogbre-vr

This has been developed against Python 3.9.


## To run:

Ensure you have the packages in requirements.txt installed.

`python api --oxidepath ../oxide` with Oxide (change path as needed)


## To test:

Start the api, then:

`python apitest`


## API endpoints & parameters

`sync_portal` is currently the only endpoint
- Expects two parameters, `userId` and `command`
- `userId` can be any string for now
- `command` is the string representation of a JSON list, where each list item is an argument 
- Command[0] should be a string for a supported command, followed by the arguments required for that command
- Examples: 
```
"['session_init']"

"['get_session_update']"

"['get_compviz_stages', 'fib-func']"

"['get_canned_oxide_program', 'elf_fib_recursive']"

"['oxide_collection_names']"

"['oxide_get_cid_from_name', 'usrbinh']"

"['oxide_get_collection_info', 'usrbinh', 'all']"

"['oxide_get_oids_with_name', 'head']"

"['oxide_get_available_modules', 'all']"

"['oxide_documentation', 'collections']"

"['oxide_get_mod_type', 'collections']"

"['oxide_retrieve', 'basic_blocks', ['bafd0386f3cf5b88cae09428538109de22866132'], {'disassembler': 'ghidra_disasm'}]"
```

## Data formats

### Oxide

Whatever is returned from the Oxide function call is dumped into a JSON string and returned to the client. There are minor exceptions for when the Oxide return value includes unserializable fields; see the code for those.

### Compiler Stage Visualization:
- Dict of "stages" list and "blockRelations" list
- Each stage in the `stages` list consists of a type (C, llvm, asm), an identifier, the original code listing (dict of line number:code line), and the CFG blocks (dict of block name:block info, where block info includes the targeted blocks and the associated lines of code). 
- `blockRelations` is a triple-nested list (forgive me) and works as follows: 
  - Each innermost list identifies a block by [stage ID, block name]. 
  - The next higher list is a group of related blocks; in this list, note there may be multiple blocks per stage or no blocks in a stage. 
  - The highest level list (blockRelations) is just the set of all relation groups.


