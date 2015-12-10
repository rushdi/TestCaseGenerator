import os
import random
import re

class MakeRobotFile:
    
    filePath = ""
    
    def __init__(self, filename, filePath):
        self.filePath = filename
        self.readFromFile(filename, filePath)
    
    def readFromFile(self, fileNmae, filePath):
    
        path, testcaseFileName = os.path.split(fileNmae)
        robotTestcaseFileName, extension = testcaseFileName.split(".")
        
        keyWordDist = {}
        
        with open(fileNmae, "r") as f:
            contentList = f.readlines()   
        f.closed
        
        writeRobotTestcase = self.createFile(filePath , robotTestcaseFileName, ".robot")
        
        for i in range(0, len(contentList)):    
            if "<<" in contentList[i]:
                if "<<Meta Data>>" in contentList[i]:
                    descriptionCommentStartPoint = i
                if "<<Environment>>" in  contentList[i]:
                    descriptionCommentEndPoint = i
                    variableStartPoint = i
                if "<<Cases>>" in  contentList[i]:
                    variableEndPoint = i    
     
        
        
        for i in range(0, len(contentList)):    
            
            if "<<" in contentList[i]:
                keyWordDist[i] = contentList[i]
                
                if "<<Meta Data>>" in contentList[i]:
                    writeRobotTestcase.write("*** Settings ***" + "\n")
                    writeRobotTestcase.write("Documentation" + "\t \t" + "Current Testcase Documentation" + "\n")
                    i+=1
                   
                if "<<Environment>>" in  contentList[i]:
                    writeRobotTestcase.write("\nLibrary" + "\t\t" + "SSHLibrary\n")
                    writeRobotTestcase.write("Library" + "\t\t" + "OperatingSystem\n")
                    writeRobotTestcase.write("Library" + "\t\t" + "Process\n")
                    inputFile = self.createFile(filePath, "input", ".txt")             
                    writeRobotTestcase.write("\nResource" + "\t\t" + "input.txt\n")  
                    
                    resourceFile = self.createFile(filePath, "resource", ".txt") 
                    resourceFile.write("*** Variables ***" + "\n\n")       
                    writeRobotTestcase.write("\nResource" + "\t\t" + "resource.txt\n")  
                    writeRobotTestcase.write("\nResource" + "\t\t" + "referenceOutput.txt\n")
                      
                    outputFile = self.createFile(filePath, "output", ".txt")
                    outputFile.write("*** Variables ***" + "\n\n")  
                    outputFile.write("${output}\t\t0") 
                    outputFile.closed
                    writeRobotTestcase.write("\nResource" + "\t\t" + "output.txt\n")  
                   
                    i+=1
                
                if "<<Input>>" in  contentList[i]:     
                    i+=1
                
                if "<<Cases>>" in  contentList[i]:
                    writeRobotTestcase.write("\n" + "*** Test Cases ***" + "\n")
                    i+=1
            
            else:
                
                if(":" in contentList[i]):
                    key, value = contentList[i].split(":")
                    
                    if len(value) > 1:
                        value = self.extractValue(value)
                        if (i > variableStartPoint) & (i < variableEndPoint):
                            resourceFile.write("${" + self.extractKey(key) + "}" + "\t\t" + value + "\n")
                            resourceFile.closed
                                    
                        elif (i > descriptionCommentStartPoint) & (i < descriptionCommentEndPoint):
                            writeRobotTestcase.write("..." + self.extractKey(key) + "\t" + value + "\n")
                        elif "<Case>" in key:
                            makeCaseTitle = value
                            makeCaseKey = key
                            
                            i+=1
                            key, value = contentList[i].split(":")
                            if "<Case Title>" in key:
                                writeRobotTestcase.write("\n" + self.extractKey(makeCaseKey) + " " + makeCaseTitle + ": " + self.extractValue(value) + "\n")
                                
                            else:
                                i-=1
                                writeRobotTestcase.write("\n" + self.extractKey(makeCaseKey) + " " + makeCaseTitle + "\n")
                                
                        elif "<Case Title>" in key:
                            continue
                        elif "<Case Description>" in key:
                            writeRobotTestcase.write("\t" + "[Documentation]" + "\t\t" + value + "\n")
                            
                        elif "<Value>" in key:
                            if "ssh-login" in value.lower():
                                resourceFile = open(filePath + "resource.txt","r")
                                hostName, username, userPass = "", "","" 
                                for line in resourceFile:
                                    if "host" in line.lower():
                                        hostName, hostAddress = line.split("\t\t")
                                    if "username" in line.lower():
                                        username, user = line.split("\t\t")
                                    if "password" in line.lower():
                                        userPass, password = line.split("\t\t")
                                
                                resourceFile.closed
                                    
                                writeRobotTestcase.write("\t" + "Open Connection" + "\t\t" + hostName + "\n")
                                writeRobotTestcase.write("\t" + "Login" + "\t\t" + username + "\t\t" + userPass + "\n")
                            
                            if re.search('\\b'+'mkdir'+'\\b', value.lower()) and re.search('\\b'+'remote'+'\\b', value.lower()):
                                resourceFile = open(filePath + "resource.txt","a+")
                                resourceFile.write("${Directory Created Command}\t\tmkdir -m 777")
                                resourceFile.closed
                                resourceFile = open(filePath + "resource.txt","r")
                                remotePath, remoteDirName, createDirCmd = "", "", ""
                                for line in resourceFile:
                                    if re.search("\\bremote\\b", line.lower()) and re.search("\\bpath\\b", line.lower()):
                                        remotePath, remotePathValue = line.split("\t\t")
                                    if re.search("\\bcreated\\b", line.lower()) and re.search("\\bremote\\b", line.lower()) and re.search("\\bfolder\\b", line.lower()):
                                        remoteDirName, remoteDirNameValue = line.split("\t\t")
                                    if re.search("\\bcreated\\b", line.lower()) and re.search("\\bdirectory\\b", line.lower()):
                                        createDirCmd, createDirCmdValue = line.split("\t\t")
                                
                                resourceFile.closed        
                                writeRobotTestcase.write("\tExecute Command\t\t" + createDirCmd + " " + remotePath + remoteDirName + "\t\tboth" + "\n")   
                                writeRobotTestcase.write("\tSleep\t\t3s" + "\n") 
                            
                            if re.search('\\b'+'scp'+'\\b', value.lower()) and re.search('\\b'+'source\s+to\s+remote'+'\\b', value.lower()):
                                resourceFile = open(filePath + "resource.txt","r")
                                sourcePath, sourceFolderName, tagetPath, targetFolderName, copyFileName = "", "", "", "", ""
                                for line in resourceFile:
                                    if re.search("\\bsource\s+path\\b", line.lower()):
                                        sourcePath, sourcePathValue = line.split("\t\t")
                                    
                                    if re.search("\\bsource\s+folder\s+name\\b", line.lower()):
                                        sourceFolderName, sourceFolderNameValue = line.split("\t\t")
                                    
                                    if re.search("\\bremote\s+path\\b", line.lower()):
                                        tagetPath, tagetPathValue = line.split("\t\t")
                                    
                                    if re.search("\\bcreated\s+remote\s+folder\s+name\\b", line.lower()):
                                        targetFolderName, targetFolderNameValue = line.split("\t\t")
                                    
                                    if re.search("\\bcopy\s+source\s+file\s+name\\b", line.lower()):
                                        copyFileName, copyFileNameValue = line.split("\t\t")
                                
                                resourceFile.closed
                                writeRobotTestcase.write("\tPut File\t\t" + sourcePath + sourceFolderName + copyFileName + "\t\t" + tagetPath + targetFolderName + "\t\t" + "mode=0770" + "\n")        
                                writeRobotTestcase.write("\tSleep\t\t3s" + "\n") 
                                
                            if re.search('\\b'+'scp'+'\\b', value.lower()) and re.search('\\b'+'remote\s+to\s+source'+'\\b', value.lower()): 
                                resourceFile = open(filePath + "resource.txt","r")    
                                sourcePath, sourceFolderName, tagetPath, targetFolderName, copyFileName = "", "", "", "", ""
                                for line in resourceFile:
                                    if re.search("\\bsource\s+path\\b", line.lower()):
                                        sourcePath, sourcePathValue = line.split("\t\t")
                                    
                                    if re.search("\\bsource\s+folder\s+name\\b", line.lower()):
                                        sourceFolderName, sourceFolderNameValue = line.split("\t\t")
                                    
                                    if re.search("\\bremote\s+path\\b", line.lower()):
                                        tagetPath, tagetPathValue = line.split("\t\t")
                                    
                                    if re.search("\\bcreated\s+remote\s+folder\s+name\\b", line.lower()):
                                        targetFolderName, targetFolderNameValue = line.split("\t\t")
                                    
                                    if re.search("\\bcopy\s+target\s+file\s+name\\b", line.lower()):
                                        copyFileName, copyFileNameValue = line.split("\t\t")
                                
                                resourceFile.closed
                                writeRobotTestcase.write("\tGet File\t\t" + tagetPath + targetFolderName + copyFileName + "\t\t" + sourcePath + sourceFolderName + "/\n")
                                writeRobotTestcase.write("\tSleep\t\t3s" + "\n") 
                            
                            if re.search('\\b'+'del'+'\\b', value.lower()) and re.search('\\b'+'target\s+files'+'\\b', value.lower()): 
                                resourceFile = open(filePath + "resource.txt","r") 
                                tagetPath, delFolderName, delFileName = "", "", ""
                                for line in resourceFile:
                                    if re.search("\\bremote\s+path\\b", line.lower()):
                                        tagetPath, tagetPathValue = line.split("\t\t")
                                    
                                    if re.search("\\bDelete\s+Remote\s+Folder\s+Name\\b".lower(), line.lower()):
                                        delFolderName, delFolderNameValue = line.split("\t\t")
                                        
                                    if re.search("\\bDelete\s+Remote\s+File\s+Name\\b".lower(), line.lower()):
                                        delFileName, delFileNameValue = line.split("\t\t")
                                        
                                resourceFile.closed
                                writeRobotTestcase.write("\tRemove File\t\t" + tagetPath + delFolderName + delFileName + "\n")
                                
                            if re.search('\\b'+'logout'+'\\b', value.lower()) and re.search('\\b'+'remote\s+machine'+'\\b', value.lower()): 
                                writeRobotTestcase.write("\tClose All Connections" + "\n")
                                writeRobotTestcase.write("\tSleep\t\t3s" + "\n")
                            
                            if re.search('\\b'+'compare'+'\\b', value.lower()) and re.search('\\b'+'reference\s+output'+'\\b', value.lower()) and re.search('\\b'+'original\s+output'+'\\b', value.lower()):
                                referenceOutputFile = open(filePath + "referenceOutput.txt", "r")
                                referenceOutput, output = "", ""
                                for line in referenceOutputFile:
                                    if "${refOutput}" in line:
                                        referenceOutput, referenceOutputValue = line.split("\t\t")
                                        
                                referenceOutputFile.closed
                                
                                outputFile = open(filePath + "output.txt", "r")
                                for line in outputFile:
                                    if "${output}" in line:
                                        output, outputValue = line.split("\t\t")
                                outputFile.closed
                                '''print outputValue
                                writeRobotTestcase.write("\t${x}=\t\tGet Variable Value\t\t" + output  + "\t\t" + "default=None" + "\n")
                                writeRobotTestcase.write("\tShould be equal\t\t" + referenceOutput + "\t\t" + output + "\t\t" + "msg=None" + "\t\t" + "values=True" + "\n")'''
                                writeRobotTestcase.write("\t${x}=\t\tRun Process\t\t" + "python" + "\t\t" +"../src/controller/valueCompare.py" + "\t\t" + "print 'Execute python'" + "\n")
                                
                                
                        elif '<Method Name>' in key:
                            resourceFile = open(filePath + "resource.txt","r")
                            exeFileName = ""
                            for line in resourceFile:
                                if re.search("\\bExecute\s+Remote\s+File\s+Name\\b".lower(), line.lower()):
                                    exeFileName, exeFileNameValue = line.split("\t\t")
                                    
                            resourceFile.closed
                            writeRobotTestcase.write("\tExecute Command\t\t" + "python " + exeFileName + "\t\tboth" + "\n")
                            
                        elif '<Passing Parameter>' in key:
                            
                            resourceFile = open(filePath + "resource.txt","r")
                            valueRange, valueRangeValue = "", ""
                            
                            
                            for line in resourceFile:
                                if re.search("\\bvalue\s+Range\\b".lower(), line.lower()):
                                    valueRange, valueRangeValue = line.split("\t\t")
                                    bitValue, bitName = valueRangeValue.split(" ")
                                    
                                    inputFile.write("dataRange="+ bitValue + "\n")
                            if ";" in  value:
                                passingParamList = value.split(';')
                                
                                for param in passingParamList:
                                    if "64 bit" in valueRangeValue.strip():
                                        inputFile.write(param + "=" + self.getRandomValue(64) + "\n")
                                    elif "32 bit" in valueRangeValue.strip():
                                        inputFile.write(param + "=" + self.getRandomValue(32) + "\n")
                                    elif "16 bit" in valueRangeValue.strip():
                                        inputFile.write(param + "=" + self.getRandomValue(16) + "\n")
                                    else:
                                        inputFile.write(param + "=" + self.getRandomValue(8) + "\n")
                                
                                inputFile.closed
                            else:     
                                if "64 bit" in valueRangeValue.strip():
                                    inputFile.write(value + "=" + self.getRandomValue(64) + "\n")
                                elif "32 bit" in valueRangeValue.strip():
                                    inputFile.write(value + "=" + self.getRandomValue(32) + "\n")
                                elif "16 bit" in valueRangeValue.strip():
                                    inputFile.write(value + "=" + self.getRandomValue(16) + "\n")
                                else:
                                    inputFile.write(value + "=" + self.getRandomValue(8) + "\n")   
                                
                                inputFile.closed
                            
                            resourceFile.closed    
                            print "Sample input file generated"
                                        
                        else:
                            writeRobotTestcase.write(contentList[i])
                            '''writeRobotTestcase.write(extractKey(key) + "\t\t" + value + "\n")'''
                    
                    else:   
                        i+=1
                        
                else:
                    i+=1
            
    
        print "Robot Testcase file generated"
        
        return
                         
     
    def createFile(self, filePath, fileName, extension):
        filePath = filePath + fileName + extension
        if(os.path.exists(filePath)):
            os.remove(filePath)    
        
        return open(filePath, 'a+')
    
    def extractKey(self, string):
        start='<' 
        stop='>'
        
        return string[string.index(start)+1:string.index(stop)]
    
    def extractValue(self, string):
        start='['
        stop=']'
            
        return string[string.index(start)+1:string.index(stop)]
    
    def  getRandomValue(self, bit):
        return str(random.getrandbits(bit))



def main():
    projectPath, tail = os.path.dirname(__file__).split("src")

    print projectPath

    filename = projectPath + 'testcase/' + 'vectorAdditionTestcase.txt'
    filePath = projectPath + "robotTestcase/"
    MakeRobotFile(filename, filePath)
    
    conversion = 0
    sumAllValue = 0
    inputFileName = filePath + 'input.txt'
    
    with open(inputFileName, "r") as files:
        inputList = files.readlines()
        files.closed
        
    for i in range(0, len(inputList)):  
        if "dataRange" in inputList[i]:
            conversionVariable, conversionValue = inputList[i].split("=")
            conversion = int(conversionValue)
        else:
            variable, Value = inputList[i].split("=")
            sumAllValue += long(Value)
        
    referenceOutputFile = open(filePath + "referenceOutput.txt", "w")
    referenceOutputFile.write("*** Variables ***" + "\n\n") 
    referenceOutputFile.write("${refOutput}\t\t" + str(sumAllValue))       
    print "Reference output file generated" 
if __name__ == "__main__": main()
