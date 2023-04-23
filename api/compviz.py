import json
import os
import re


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
            lineno = 0
            for line in file:
                currblock = {}
                if ((line.endswith("{\n")) or (line[0].isdigit())):
                    label = ""
                    if (line[0].isdigit()):
                        line = line.replace(":", "")
                        label = line.split()[0]
                    else:
                        label = "1"
                    currblock["lines"] = []
                    currblock["targets"] = []
                    line = next(file)
                    lineno += 1
                    while ((len(line.strip()) > 0) and (not(line.startswith("}")))):
                        currblock["lines"].append(str(lineno))
                        if ("label" in line):
                            line = line.replace(",", "")
                            line = line.replace("%", "")
                            tokens = iter(line.split());
                            for token in tokens:
                                if (token == "label"):
                                    currblock["targets"].append(next(tokens))
                        line = next(file)
                        lineno += 1
                    blocks[label] = currblock
                lineno += 1
        return blocks


    def parseBlocksFromAsm(self, filename):
        blocks = {}
        with open(filename) as file:
            # Painful, fragile parsing
            lineno = 0
            line = next(file, "end")
            prevlabel = ""
            previnstr = ""
            while True:
                if (line == "end"):
                    break
                if ((":" in line) and (("bb" in line) or ("BB" in line))):
                    currblock = {}
                    line = line.replace(":", "")
                    line = line.replace("#", "")
                    line = line.strip()
                    label = line.split()[0]
                    if ((not(prevlabel == "")) and (not(previnstr == "jmp"))):
                        blocks[prevlabel]["targets"].append(label)
                    prevlabel = label
                    currblock["lines"] = []
                    currblock["targets"] = []
                    line = next(file, "end")
                    lineno += 1
                    while (line.startswith("\t")):
                        currblock["lines"].append(str(lineno))
                        tokens = line.strip().split()                        
                        previnstr = tokens[0]
                        if (previnstr.startswith("j")):
                            currblock["targets"].append(tokens[1])
                        line = next(file, "end")
                        lineno += 1
                    blocks[label] = currblock
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
        if (rootname == "perfect-func"):
            blockRelations.append([["0", "B7"], ["1", "1"], ["2", "%bb.0"]])
            blockRelations.append([["0", "B6"], ["1", "5"], ["2", ".LBB0_1"]])
            blockRelations.append([["0", "B5"], ["1", "9"], ["2", "%bb.2"]])
            blockRelations.append([["0", "B4"], ["1", "14"], ["2", "%bb.3"]])
            blockRelations.append([["0", "B3"], ["0", "B2"], ["1", "18"], ["2", ".LBB0_4"]])
            blockRelations.append([["0", "B1"], ["1", "21"], ["2", ".LBB0_5"]])

        elif (rootname == "fib-func"):
            blockRelations.append([["0", "B5"], ["1", "1"], ["2", "%bb.0"]])
            blockRelations.append([["0", "B4"], ["1", "10"], ["2", ".LBB0_1"]])
            blockRelations.append([["0", "B3"], ["1", "14"], ["2", "%bb.2"]])
            blockRelations.append([["0", "B2"], ["1", "20"], ["2", "%bb.3"]])
            blockRelations.append([["0", "B1"], ["1", "23"], ["2", ".LBB0_4"]])

        return blockRelations
        

    def getStagesJson(self):
        return json.dumps({"stages": self.stageDicts, "blockRelations": self.blockRelationsLists})
    