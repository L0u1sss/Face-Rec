import cv2
import face_recognition
import numpy as np
import os
import time
import pygsheets
from parinya import LINE
import datetime

gc = pygsheets.authorize(service_file='credentials.json')
sheet = gc.open_by_key("1DCa6UzNV7qPbyKid8NhcnMqyDF5vbTE1xU97yNohijk")
worksheet = sheet[0]
cells = worksheet.get_all_values(include_tailing_empty_rows=False, include_tailing_empty=False, returnas='matrix')
last_row = len(cells)

path = "facedatastudent"
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


def findEncodeing(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


#def markAttendance(name):
    #with open('Attendace.csv', 'r+') as f:
        #myDataList = f.readlines()
        #nameList = []
        #for line in myDataList:
            #entry = line.split(',')
            #nameList.append(entry[0])
            #f.writelines(f'\n{name},{dtStringtime},{dtStringdate}')


def linenotify(name):
    nameL = "พบ" + name + "แล้ว" + "เวลา" + dtStringtime + "วันที่" + dtStringdate
    line = LINE("tapo1wg2giZhq1Cd0TXrzT7hxY5BEuaqBgwgRnXOA0o")
    line.sendtext(nameL)
    line.sendimage(imgS)

def googlesheets():
    last_row = len(cells)
    data = [name, str(dtStringtime), str(dtStringdate)]
    worksheet.insert_rows(last_row, number=1, values=data, inherit=False)
    last_row = last_row + 1

encodeListKnow = findEncodeing(images)
print("encode found", len(encodeListKnow))

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    now = datetime.datetime.now()
    dtStringtime = now.strftime('%H:%M:%S')
    dtStringdate = now.strftime('%d/%m/%Y')
    for encoderFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnow, encoderFace)
        faceDis = face_recognition.face_distance(encodeListKnow, encoderFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            #markAttendance(name)
            linenotify(name)

            data = [name, str(dtStringtime), str(dtStringdate)]
            worksheet.insert_rows(last_row, number=1, values=data, inherit=False)
            last_row = last_row + 1
        time.sleep(5)
    #cv2.imshow('Webcam', imgS)
    cv2.waitKey(1)