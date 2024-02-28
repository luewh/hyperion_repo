import csv

class WriteCSV:
    def AddlineCSV(self, path, data): #OK
        with open(path,'a' , newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([data])
            csvfile.close()

    def RazLogDefaut(self, path): #OK
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile , delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["Date,HeureMin,NumDef,DescriptionDef"])
            csvfile.close()

    def RazLogInfo(self, path): #OK
        with open(path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["NumInfo,DescriptionInfo"])
            csvfile.close()


if __name__ == "__main__":
    pathLogDefaut = 'LogDefaut.csv'
    pathLogInfo = 'LogInfo.csv'
    
    writerCSV  = WriteCSV()
    writerCSV.RazLogDefaut(pathLogDefaut)
    writerCSV.RazLogInfo(pathLogInfo)
    

    writerCSV.AddlineCSV(pathLogDefaut, "blabla")
    writerCSV.AddlineCSV(pathLogDefaut, "TEST.TEST,TEST|TEST|")
