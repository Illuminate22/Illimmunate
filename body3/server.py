import smtplib
import ssl
from datetime import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import certifi
import pymongo

ca = certifi.where()

connection = pymongo.MongoClient(
    "mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=ca)

db = connection.database_main
childcol = db["child"]
vaxcol = db["vaccine"]


def send_mail(case, child):
    receiver = child["pmail"]

    if(case == 0):
        subject = "Vaccine Reminder"
    else:
        subject = "Vaccine Date Lapse WARNING!!"

    msg = get_vac_text(case, child)
    sender_email = "iiitbbyte22@gmail.com"
    receiver_email = receiver
    password = "honeycake123$"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    msg_part = MIMEText(msg, "plain")

    message.attach(msg_part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def upcomingStartingDate(child):
    dob = child["dob"]
    yetVaccines = child["yetVaccines"]
    earliestStartDate = datetime(9999, 12, 31)
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        startDate = dob + timedelta(days=vaccine["date_start"])
        if startDate < earliestStartDate:
            earliestStartDate = startDate
    child["upcomingStartDate"] = earliestStartDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingStartDate": earliestStartDate}})
    child = childcol.find_one({"cid": child["cid"]})


def upcomingMidDate(child):
    dob = child["dob"]
    yetVaccines = child["yetVaccines"]
    dueVaccines = child["dueVaccines"]
    earliestMidDate = datetime(9999, 12, 31)
    if dueVaccines == []:
        dueVaccines = yetVaccines
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        timeDifference = timedelta(days=vaccine["date_end"]) - timedelta(days=vaccine["date_start"])
        midDate = dob + timedelta(days=vaccine["date_start"]) + timeDifference / 2
        if midDate < earliestMidDate:
            earliestMidDate = midDate
    if earliestMidDate > datetime.today():
        child["upcomingMidDate"] = earliestMidDate
        childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingMidDate": earliestMidDate}})
        return
    earliestMidDate = datetime(9999, 12, 31)
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        timeDifference = timedelta(days=vaccine["date_end"]) - timedelta(days=vaccine["date_start"])
        midDate = dob + timedelta(days=vaccine["date_start"]) + timeDifference / 2
        if midDate < earliestMidDate:
            earliestMidDate = midDate
    child["upcomingMidDate"] = earliestMidDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingMidDate": earliestMidDate}})
    child = childcol.find_one({"cid": child["cid"]})


def upcomingEndDate(child):
    dob = child["dob"]
    dueVaccines = child["dueVaccines"]
    warningList = child["warningList"]
    if warningList != [] or dueVaccines == []:
        dueVaccines = child["yetVaccines"]
    earliestEndDate = datetime(9999, 12, 31)
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        endDate = dob + timedelta(days=vaccine["date_end"])
        if endDate < earliestEndDate:
            earliestEndDate = endDate
    child["upcomingEndDate"] = earliestEndDate
    childcol.update_one({"cid": child["cid"]}, {"$set": {"upcomingEndDate": earliestEndDate}})
    child = childcol.find_one({"cid": child["cid"]})


def startDateScenario(child):
    dob = child["dob"]
    presentDay = datetime.today()
    yetVaccines = child["yetVaccines"]
    dueVaccines = child["dueVaccines"]
    startedList = []
    for vid in yetVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        if presentDay > dob + timedelta(days=vaccine["date_start"]):
            startedList.append(vid)
    for vid in startedList:
        yetVaccines.remove(vid)
    dueVaccines.extend(startedList)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"dueVaccines": dueVaccines, "yetVaccines": yetVaccines}})
    child = childcol.find_one({"cid": child["cid"]})


def endDateScenario(child):
    dob = child["dob"]
    presentDay = datetime.today()
    dueVaccines = child["dueVaccines"]
    warningList = child["warningList"]
    for vid in dueVaccines:
        vaccine = vaxcol.find_one({"vid": vid})
        if presentDay > dob + timedelta(days=vaccine["date_end"]):
            if vid not in warningList:
                warningList.append(vid)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"warningList": warningList}})
    child = childcol.find_one({"cid": child["cid"]})


def warningListCheck(child):
    warningList = child["warningList"]
    dueVaccines = child["dueVaccines"]
    delList = []
    for vid in warningList:
        if vid not in dueVaccines:
            delList.append(vid)
    for vid in delList:
        warningList.remove(vid)
    childcol.update_one({"cid": child["cid"]}, {"$set": {"warningList": warningList}})
    child = childcol.find_one({"cid": child["cid"]})


def get_vac_text(case, child):
    if(case == 0):
        text = f"""\
Hello,
This is to inform you that the for the following vaccines can now be administered to you child, {child["name"]}"""
        li = child["dueVaccines"]

        for i in range(len(li)):
            name = vaxcol.find_one({"vid": li[i]})["name"]
            text += "\n" + name
        return text
    else:
        text = f"""\
Hello,
This is to inform u that the due date for the following vaccines for you child, {child["name"]},  has lapsed.
Please administer him/her with a dose of vaccine so soon as possible"""
        li = child["warningList"]

        for i in range(len(li)):
            name = vaxcol.find_one({"vid": li[i]})["name"]
            text += "\n" + name
        return text

def main():
    presentDate = datetime.today()
    isWarningDay = False
    if presentDate.day % 6 == 0:
        isWarningDay = True

    for child in childcol.find():


        if presentDate > child["upcomingStartDate"]:
            startDateScenario(child)
            child = childcol.find_one({"cid": child["cid"]})
            upcomingStartingDate(child)
            child = childcol.find_one({"cid": child["cid"]})
            send_mail(0, child)
        if presentDate > child["upcomingMidDate"]:
            upcomingMidDate(child)
            child = childcol.find_one({"cid": child["cid"]})
            send_mail(0, child)
        if presentDate > child["upcomingEndDate"]:
            endDateScenario(child)
            child = childcol.find_one({"cid": child["cid"]})
            upcomingEndDate(child)
            child = childcol.find_one({"cid": child["cid"]})

        if isWarningDay:
            warningListCheck(child)
            child = childcol.find_one({"cid": child["cid"]})
            if child["warningList"] != []:
                send_mail(1, child)

        print(child)
# for child in childcol.find():
#     try:
#         send_mail(0, child)
#     except:
#         send_mail(1, child)

main()