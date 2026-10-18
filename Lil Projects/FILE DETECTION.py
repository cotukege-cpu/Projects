#FILE DETECTION IN PYTHON
import csv
import os
import json


#file_path = ("C:\\Users\\Ege\\Desktop\\Folder\\zigotinho.txt")      #you can use /  as well

#file_path = ("C:/Users/Ege/Desktop/Folder/zigotinho.txt")

#if os.path.exists(file_path):
#    print(f"{file_path} exists")

#    if os.path.isfile(file_path):
#        print("that is a file")
#    elif os.path.isdir(file_path):
#        print("that is a directory")

#else:
#    print(f"{file_path} does not exist")







#TXT FILES WRITING




#employees = ["Eugeene","Squidward","Spongebob","Patrick"] #for txt files

#file_path = "C:/Users/Ege/Desktop/Folder/output.txt"


#txt_data = "I am GOATED"



#try:
    #with open(file_path,"w") as file:           #w is to write / x is also writing if file_path doesnt exists / r is read / a is appending
        #for employee in employees:
            #file.write(employee + "\n")
        #print(f"txt file {file_path} written successfully")
#except FileExistsError:
    #print("file  already exists")







#TXT FILES READING

#file_path = ("C:\\Users\\Ege\\Desktop\\Folder\\zigotinho.txt")
#try:
#    with open(file_path,"r") as file:
#        a = file.read()
#        print(a)
#except FileNotFoundError:
#    print("File not found")
#
#except PermissionError:
#    print("Permission denied")














#JSON FİLES WRİTİNG
#employee = {"Name": "Spongebob","age":21,"position":"cook"}

#file_path = "C:/Users/Ege/Desktop/Folder/output.json"

#try:
#    with open(file_path,"w")as file:
#        json.dump(employee,file, indent = 5 )                #indent means how many spaces between key-value pairs
#    print(f"json file {file_path} written successfully")
#except FileExistsError or FileNotFoundError:
#    print("something went wrong")








#jSON FILES READING

#file_path = "C:/Users/Ege/Desktop/Folder/output.json"

#try:
#    with open(file_path,"r")as file:
#        a = json.load(file)
#        print(a["position"])
#except FileNotFoundError:
#    print("File not found")














#CSV FİLES writing and reading(LİSTS)



#employee_list = [["Name" ,"Age","Job"],["Spongebob",30,"cook"],["Squidward",47,"manager"],["Squidward",24,"cashier"]]

#file_path ="C:/Users/Ege/Desktop/Folder/output.csv"

#try:
#    with open(file_path,"w",newline = "") as file:
#        writer = csv.writer(file)
#        for row in employee_list:
#           writer.writerow(row)
#        print(f"csv file {file_path} created successfully")
#except FileNotFoundError or FileExistsError:
#    print("csv file already exists or not found")















#CSV FILES READING

#file_path ="C:/Users/Ege/Desktop/Folder/output.csv"

#try:
#    with open(file_path,"r") as file:
#        content = csv.reader(file)
#        for line in content:
#            print(line[1])
#except FileNotFoundError:
#    print("File does not exist")