# cogbre-nexus

"cogbre" = Cognitive Binary Reverse Engineering

This is the server / "nexus" component for "cogbre." 

It supports the VR front end at https://github.com/AugCogVR/cogbre-vr

The README in that project is more informative than this one, at this time.

This has been developed against Python 3.9.

To run:
- Ensure you have the packages in requirements.txt installed.
- python api/api.py


## API endpoints & parameters

`sync_portal`
- Expects two parameters, `userId` (not currently used) and `command`
- Commands:
  - session_init
  - get_session_update
  - get_oxide_program <program name>
  - get_compviz_stages <program name>

## Data formats

Oxide: *To be populated -- currently, data is served almost as provided but with basic transformation to easily associate code lines with blocks*

Compiler Stage Visualization:
- Dict of "stages" list and "blockRelations" list
- Each stage in the `stages` list consists of a type (C, llvm, asm), an identifier, the original code listing (dict of line number:code line), and the CFG blocks (dict of block name:block info, where block info includes the targeted blocks and the associated lines of code). 
- `blockRelations` is a triple-nested list (forgive me) and works as follows: 
  - Each innermost list identifies a block by [stage ID, block name]. 
  - The next higher list is a group of related blocks; in this list, note there may be multiple blocks per stage or no blocks in a stage. 
  - The highest level list (blockRelations) is just the set of all relation groups.


