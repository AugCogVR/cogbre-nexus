import os
import json


# THIS IS LIKELY TO BE DEPRECATED SOON AS IT SUPPORTS A DORMANT INITIATIVE. 


class CannedOxideProgram: # For loading an Oxide program's JSON dump from a local file
    def __init__(self, folder):
        blocksFile = open(os.path.join(folder, "basic_blocks"))
        self.blocks = json.load(blocksFile)
        blocksFile.close()
        self.blocks = self.blocks[0]["basic_blocks"]

        # for i in self.blocks:
        #     print(f"{i}: {self.blocks[i]['members']}")

        asmFile = open(os.path.join(folder, "disassembly"))
        self.asm = json.load(asmFile)
        asmFile.close()
        self.asm = self.asm[0]["instructions"]

        # for i in self.asm:
        #     print(f"{i}: {self.asm[i]['mnemonic']} {self.asm[i]['op_str']}")

        for i in self.blocks.keys():
            block = self.blocks[i]
            instructions = {}
            for j in block["members"]:
                j = str(j)
                if (j in self.asm.keys()):
                    # print(f"Block {i} Member {j}: {self.asm[j]['mnemonic']} {self.asm[j]['op_str']}")
                    # print(f"{self.asm[j]['mnemonic']} {self.asm[j]['op_str']}")
                    instructions[j] = f"{self.asm[j]['mnemonic']} {self.asm[j]['op_str']}"
            block["insns"] = instructions
            # print('==================')

        # for i in self.blocks:
        #     print(f"{i}: {self.blocks[i]}")

        # print(json.dumps(self.blocks))


    def getBlocksJson(self):
        return json.dumps(self.blocks)
