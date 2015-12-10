def compareValues(filePath):
    referenceOutputFile = open(filePath + "referenceOutput.txt", "r")
    referenceOutputValue, outputValue = 0, 0
    for line in referenceOutputFile:
        if "${refOutput}" in line:
            referenceOutput, referenceOutputValue = line.split("\t\t")
                                        
            referenceOutputFile.closed
                                
    outputFile = open(filePath + "output.txt", "r")
    for line in outputFile:
        if "${output}" in line:
            output, outputValue = line.split("\t\t")
            
            outputFile.closed
            
    result = long(outputValue) - long(referenceOutputValue)
    
    if (result >= 0) and (result < 1.1):
        return True
    else:
        return False 
            
def main():
    filePath = "../../robotTestcase/"
    returnVal = compareValues(filePath)
    print returnVal
if __name__ == "__main__": main()