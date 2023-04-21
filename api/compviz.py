
import json
import os


class Stage:
    def __init__(self, folder, rootname, type):
        self.code = {}
        self.blocks = {}

        if (type == "c"):
            self.code = self.readCodeFromFile(os.path.join(folder, rootname + ".c"))
        
        elif (type == "llvm"):
            self.code = self.readCodeFromFile(os.path.join(folder, rootname + ".ll"))

        elif (type == "asm"):
            self.code = self.readCodeFromFile(os.path.join(folder, rootname + ".s"))

        else:
            print(f"ERROR: Stage init: unknown type: {type}")


    def readCodeFromFile(self, filename):
        code = {}
        lineno = 0
        with open(filename) as file:
            for line in file:
                code[str(lineno)] = line
                lineno += 1
        return code




class CompVizStages:
    def __init__(self, folder, rootname):
        self.stages = []

        # for now, assume 3 stages: source, LLVM IR, asm
        stage = Stage(folder, rootname, "c")
        self.stages.append(stage)

        stage = Stage(folder, rootname, "llvm")
        self.stages.append(stage)

        stage = Stage(folder, rootname, "asm")
        self.stages.append(stage)




# class OxideProgram:
#     def __init__(self, folder):
#         blocksFile = open(folder + '/basic_blocks')
#         self.blocks = json.load(blocksFile)
#         blocksFile.close()
#         self.blocks = self.blocks[0]['basic_blocks']

#         # for i in self.blocks:
#         #     print(f"{i}: {self.blocks[i]['members']}")

#         asmFile = open(folder + '/disassembly')                 
#         self.asm = json.load(asmFile)
#         asmFile.close()
#         self.asm = self.asm[0]['instructions']

#         # for i in self.asm:
#         #     print(f"{i}: {self.asm[i]['mnemonic']} {self.asm[i]['op_str']}")

#         for i in self.blocks.keys():
#             block = self.blocks[i]
#             instructions = {}
#             for j in block['members']:
#                 j = str(j)
#                 if (j in self.asm.keys()):
#                     # print(f"Block {i} Member {j}: {self.asm[j]['mnemonic']} {self.asm[j]['op_str']}")
#                     # print(f"{self.asm[j]['mnemonic']} {self.asm[j]['op_str']}")
#                     instructions[j] = f"{self.asm[j]['mnemonic']} {self.asm[j]['op_str']}"
#             block['insns'] = instructions
#             # print('==================')

#         # for i in self.blocks:
#         #     print(f"{i}: {self.blocks[i]}")

#         # print(json.dumps(self.blocks))


#     def getBlocksJson(self):
#         return json.dumps(self.blocks)
