#!/usr/bin/env python3
import csv

class ReadCSV :
    def ReadCSVAndPrint(self, path):
        path = __file__.replace("Read_CSV.py","") + path
        ListLog = []
        ListTitre = []
        with open(path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            ListReader = list(spamreader)
            ListTitre = ListReader[0]
            ListLog = ListReader[1:]
            # print(ListTitre)
            # print(ListLog)
            csvfile.close()

        return ListTitre, ListLog

if __name__ == "__main__":
    ReadCSV().ReadCSVAndPrint('LogDefaut.csv')
    ReadCSV().ReadCSVAndPrint('LogInfo.csv')
