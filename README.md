# cogbre-nexus

"cogbre" = Cognitive Binary Reverse Engineering

This is the server / "nexus" component for "cogbre." 

This application supports research of the [Auburn CSSE Program Understanding Lab](https://program-understanding.github.io/).

It supports the VR front end at https://github.com/AugCogVR/cogbre-vr

This has been developed against Python 3.9.


## To run the API server:

Ensure you have the packages in requirements.txt installed.

Relative to the top-level Nexus path, Oxide is usually installed at `../oxide/` and Capa rules are usually installed at `../oxide/datasets/capa-rules/`

When those defaults are true, `> python api` will start the API server.

Otherwise, you can set `oxidepath` and/or `caparulespath` on the command line, e.g., 
`> python api --oxidepath ../somewhere/oxide`


## To test:

Start the API, then:

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



