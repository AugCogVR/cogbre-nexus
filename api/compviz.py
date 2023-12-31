import json
import os
import re


# THIS IS LIKELY TO BE DEPRECATED SOON AS IT SUPPORTS A DORMANT INITIATIVE. 


class Stage:
    def __init__(self, folder, rootname, type):
        self.stageDict = {}
        self.stageDict["type"] = type

        if (type == "c"):
            self.stageDict["id"] = "0"
            self.stageDict["code"] = self.readCodeFromFile(os.path.join(folder, rootname + ".c"))
            self.stageDict["blocks"] = self.parseBlocksFromSourceCfg(os.path.join(folder, rootname + ".sourcecfg"))
        
        # FUTURE: Handle multiple LLVM IR stages with different optimizations
        elif (type == "llvm"):
            self.stageDict["id"] = "1"
            self.stageDict["code"] = self.readCodeFromFile(os.path.join(folder, rootname + ".ll"))
            self.stageDict["blocks"] = self.parseBlocksFromLLVM(os.path.join(folder, rootname + ".ll"))

        elif (type == "asm"):
            self.stageDict["id"] = "2"
            self.stageDict["code"] = self.readCodeFromFile(os.path.join(folder, rootname + ".s"))
            self.stageDict["blocks"] = self.parseBlocksFromAsm(os.path.join(folder, rootname + ".s"))

        else:
            print(f"ERROR: Stage init: unknown type: {type}")


    def readCodeFromFile(self, filename):
        code = {}
        lineno = 0
        with open(filename) as file:
            for line in file:
                line = line.replace("\t", " ")
                line = line.replace("\n", "")
                code[str(lineno)] = line
                lineno += 1
        return code


    def parseBlocksFromSourceCfg(self, filename):
        blocks = {}
        with open(filename) as file:
            # Painful, fragile parsing
            for line in file:
                currblock = {}
                if (line.startswith("[B")):
                    label = re.search(r'\[(.*?)\]', line).group(1)
                    currblock["targets"] = []
                    while (len(line.strip()) > 0):
                        if (line.startswith("Succs")):
                            currblock["targets"].append(line.split()[-1])
                        line = next(file)
                    blocks[label] = currblock
                # if (line.startswith("=>Entry")):
                #     currblock["targets"]= ["B" + line.split()[-1]]
                #     blocks["Entry"] = currblock
                # if (line.startswith("<=Exit")):
                #     currblock["targets"] = []
                #     blocks["Exit"] = currblock                    
                #     exitpred = line.split()[-1]
                #     blocks["B"+exitpred]["targets"].append("Exit")

        # HACK TIME -- hard-code the source code references for certain programs.
        # Someday we can automatically determine these references. I hope.
        if ("perfect-func" in filename):
            blocks["B8"]["lines"] = ["0"]
            blocks["B7"]["lines"] = ["3", "4"]
            blocks["B6"]["lines"] = ["7", "8"]
            blocks["B5"]["lines"] = ["9"]
            blocks["B4"]["lines"] = ["10"]
            blocks["B3"]["lines"] = ["11"]
            blocks["B2"]["lines"] = ["12"]
            blocks["B1"]["lines"] = ["15"]
            blocks["B0"]["lines"] = ["16"]
            # blocks["Entry"]["lines"] = []
            # blocks["Exit"]["lines"] = []

        elif ("fib-func" in filename):
            blocks["B6"]["lines"] = ["0"]
            blocks["B5"]["lines"] = ["3", "6", "9"]
            blocks["B4"]["lines"] = ["10"]
            blocks["B3"]["lines"] = ["12", "13", "14"]
            blocks["B2"]["lines"] = ["15"]
            blocks["B1"]["lines"] = ["17"]
            blocks["B0"]["lines"] = ["18"]

        return dict(sorted(blocks.items(), reverse = True))


    def parseBlocksFromLLVM(self, filename):
        blocks = {}
        with open(filename) as file:
            # Painful, fragile parsing
            lineno = -1
            for line in file:
                lineno += 1
                currblock = {}
                if ((line.endswith("{\n")) or (line[0].isdigit())): # start of function or start of block
                    label = ""
                    if (line[0].isdigit()): # start of block
                        currblock["lines"] = [str(lineno)]
                        currblock["targets"] = []
                        line = line.replace(":", "")
                        label = line.split()[0]
                    else: # start of function: add "startfunc" block for the function header then parse the remaining blocks normally
                        currblock["lines"] = [str(lineno)]
                        currblock["targets"] = ["1"]
                        blocks["startfunc"] = currblock
                        currblock = {}
                        currblock["lines"] = []
                        currblock["targets"] = []
                        label = "1"
                    blocks[label] = currblock
                    line = next(file)
                    lineno += 1
                    while (len(line.strip()) > 0):
                        if (line.startswith("}")): # found endfunc block
                            currblock = {}
                            currblock["lines"] = [str(lineno)]
                            currblock["targets"] = []
                            blocks["endfunc"] = currblock
                            break 
                        else:
                            currblock["lines"].append(str(lineno))
                            if ("label" in line):
                                line = line.replace(",", "")
                                line = line.replace("%", "")
                                tokens = iter(line.split());
                                for token in tokens:
                                    if (token == "label"):
                                        currblock["targets"].append(next(tokens))
                            if ("ret" in line):
                                currblock["targets"] = ["endfunc"]
                            line = next(file)
                            lineno += 1
        return blocks


    def parseBlocksFromAsm(self, filename):
        blocks = {}
        lineno = -1
        with open(filename) as file:
            # Painful, fragile parsing
            line = next(file, "end")
            lineno += 1
            prevlabel = ""
            previnstr = ""
            foundStartFunc = False
            foundEndFunc = False
            while True:
                if (line == "end"):
                    break
                if (":" in line): # possible start of block
                    if (("bb" in line) or ("BB" in line)): # start of block after startfunc
                        currblock = {}
                        line = line.replace(":", "")
                        line = line.replace("#", "")
                        line = line.strip()
                        label = line.split()[0]
                        blocks[label] = currblock
                        if ((not(prevlabel == "")) and (not(previnstr == "jmp"))):
                            blocks[prevlabel]["targets"].append(label)
                        prevlabel = label
                        currblock["lines"] = [str(lineno)]
                        currblock["targets"] = []
                        line = next(file, "end")
                        lineno += 1
                        while (line.startswith("\t")):
                            currblock["lines"].append(str(lineno))
                            tokens = line.strip().split()                        
                            previnstr = tokens[0]
                            if (previnstr.startswith("j")):
                                currblock["targets"].append(tokens[1])
                            if ("ret" in line):
                                currblock["targets"] = ["endfunc"]
                            line = next(file, "end")
                            lineno += 1
                    elif (not (foundStartFunc)): # startfunc
                        foundStartFunc = True
                        currblock = {}
                        blocks["startfunc"] = currblock
                        currblock["lines"] = [str(lineno), str(lineno + 1)]
                        currblock["targets"] = ["%bb.0"]
                        line = next(file, "end")
                        lineno += 1
                    elif (not (foundEndFunc)): # endfunc
                        foundEndFunc = True
                        currblock = {}
                        blocks["endfunc"] = currblock
                        currblock["lines"] = [str(lineno), str(lineno + 1), str(lineno + 2)]
                        currblock["targets"] = []
                        line = next(file, "end")
                        lineno += 1
                        line = next(file, "end")
                        lineno += 1
                else:
                    line = next(file, "end")
                    lineno += 1
        return blocks


class CompVizStages:
    def __init__(self, folder, rootname):
        self.stageDicts = []

        # for now, assume 3 stages: source, LLVM IR, asm
        stage = Stage(folder, rootname, "c")
        self.stageDicts.append(stage.stageDict)

        stage = Stage(folder, rootname, "llvm")
        self.stageDicts.append(stage.stageDict)

        stage = Stage(folder, rootname, "asm")
        self.stageDicts.append(stage.stageDict)

        self.blockRelationsLists = self.findBlockRelations(folder, rootname)


    def findBlockRelations(self, folder, rootname):
        blockRelations = []

        # HACK TIME -- hard-code the block relations for certain programs. 
        # Someday we can automatically determine these relations. I hope.
        # FORMAT: 
        # - Each innermost list identifies a block by [stage ID, block name]
        # - The next higher list is a group of related blocks. Note there 
        #   may be multiple blocks per stage or no blocks in a stage.
        # - The highest level list (blockRelations) is the set of all relation groups.
        if (rootname == "perfect-func"):
            blockRelations.append([["0", "B8"], ["1", "startfunc"], ["2", "startfunc"]])
            blockRelations.append([["0", "B7"], ["1", "1"], ["2", "%bb.0"]])
            blockRelations.append([["0", "B6"], ["1", "5"], ["2", ".LBB0_1"]])
            blockRelations.append([["0", "B5"], ["1", "9"], ["2", "%bb.2"]])
            blockRelations.append([["0", "B4"], ["1", "14"], ["2", "%bb.3"]])
            blockRelations.append([["0", "B3"], ["0", "B2"], ["1", "18"], ["2", ".LBB0_4"]])
            blockRelations.append([["0", "B1"], ["1", "21"], ["2", ".LBB0_5"]])
            blockRelations.append([["0", "B0"], ["1", "endfunc"], ["2", "endfunc"]])

        elif (rootname == "fib-func"):
            blockRelations.append([["0", "B6"], ["1", "startfunc"], ["2", "startfunc"]])
            blockRelations.append([["0", "B5"], ["1", "1"], ["2", "%bb.0"]])
            blockRelations.append([["0", "B4"], ["1", "10"], ["2", ".LBB0_1"]])
            blockRelations.append([["0", "B3"], ["1", "14"], ["2", "%bb.2"]])
            blockRelations.append([["0", "B2"], ["1", "20"], ["2", "%bb.3"]])
            blockRelations.append([["0", "B1"], ["1", "23"], ["2", ".LBB0_4"]])
            blockRelations.append([["0", "B0"], ["1", "endfunc"], ["2", "endfunc"]])

        return blockRelations
        

    def getStagesJson(self):
        return json.dumps({"stages": self.stageDicts, "blockRelations": self.blockRelationsLists})
    