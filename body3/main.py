from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.window import Window
from datetime import *
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

import certifi
import pymongo
from re import match
from pickle import dump, load

ca = certifi.where()

client = pymongo.MongoClient(
    "mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
    tlsCAFile=ca)
db = client.get_database("database_main")
rec1 = db.parent
rec2 = db.doctor
childcol = db["child"]
vaxcol = db["vaccine"]

pop_text = ""
main_mail = ""
main_user_type = -1
children = list(map(lambda item: list(item.values()), childcol.find()))
vaxlist = []


def children_get():
    global children
    children = list(map(lambda item: list(item.values()), childcol.find()))


def vaccines_get():
    global vaxlist
    for vaccine in vaxcol.find():
        vaxlist.append(vaccine)


def create_popup(title, text):
    popup = Popup(title=title,
                  content=Label(text=text),
                  size_hint=(0.4, 0.4))
    popup.open()


def create_info_popup(title, text):
    popup = Popup(title=title,
                  content=TextInput(text=text, readonly=True),
                  size_hint=(0.6, 0.6))
    popup.open()


def validVaccines(dob, childVaxList=vaxlist):
    vaccines_get()
    presentDay = datetime.today()
    dueVaccines, overVaccines, yetVaccines = [], [], []
    for vaccine in childVaxList:
        if timedelta(days=vaccine["date_start"]) + dob < presentDay < timedelta(
                days=vaccine["date_end"]) + dob or timedelta(days=vaccine["date_end"]) + dob == presentDay:
            dueVaccines.append(vaccine["vid"])
        elif timedelta(days=vaccine["date_start"]) + dob > presentDay:
            yetVaccines.append(vaccine["vid"])
        elif timedelta(days=vaccine["date_end"]) + dob < presentDay:
            overVaccines.append(vaccine["vid"])
    return dueVaccines, overVaccines, yetVaccines


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
    if dueVaccines == []:
        dueVaccines = child["yetVaccines"]
    earliestMidDate = datetime(9999, 12, 31)
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
    if dueVaccines == []:
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


def get_accounts(cond):
    if (cond == 0):
        return list(map(lambda item: list(item.values()), rec1.find()))
    elif (cond == 1):
        return list(map(lambda item: list(item.values()), rec2.find()))
    elif (cond == 2):
        return list(map(lambda item: list(item.values()), childcol.find()))


def generate_unique_id(case):
    id = str(len(get_accounts(case)) + 1)

    for i in range(6 - len(id)):
        id = "0" + id

    if (case == 0):
        id = "P" + id
    elif (case == 1):
        id = "D" + id
    else:
        id = "C" + id
    return id


class Pop(Popup):

    def __init__(self, **kwargs):
        global pop_text
        super(Pop, self).__init__(**kwargs)
        self.title = "Notification\n" + pop_text
        self.auto_dismiss = False
        self.size_hint = (0.6, 0.2)
        self.pos_hint = {"x": 0.2, "top": 0.9}

        self.but1 = Button(text="Ok")
        self.but1.bind(on_press=self.press)
        self.add_widget(self.but1)

    def press(self, _):
        self.dismiss()


def email_process(case, email, passwd, logged_in, user_type=None):
    global main_mail, main_user_type, sm, pop_text, plob, lob
    print(case)
    print(email)
    print(passwd)
    print(logged_in)
    print(user_type)
    if (case == 0):
        par = get_accounts(0)
        doc = get_accounts(1)
        flag1, flag2 = False, False
        id = None
        for i in par:
            if i[2] == email and i[3] == passwd:
                flag1 = True
                id = i[1]
                break
        if (flag1 == False):
            for i in doc:
                if i[2] == email and i[4] == passwd:
                    flag2 = True
                    id = i[1]
                    break
        u_type = None
        if (flag1):
            u_type = 0
        elif (flag2):
            u_type = 1

        if (u_type == None):
            pop_text = "Email or password entered is wrong!! Please re-enter the credentials"
            Pop().open()
        else:
            main_mail = email
            main_user_type = u_type
            if (logged_in):
                with open("assets/logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            if main_user_type == 0:
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            elif main_user_type == 1:
                lob = Lobby(r=None, p=None, name="lobby")
                sm.add_widget(lob)
                sm.current = "lobby"

    if (case == 1):
        par = get_accounts(0)
        doc = get_accounts(1)

        flag1, flag2 = True, True

        for i in doc:
            if i[2] == email:
                flag1 = False
                break
        if (flag1):
            for i in par:
                if i[2] == email:
                    flag2 = False
                    break

        if (flag1 == False or flag2 == False):
            pop_text = "The given email id already has an account linked with it\nPlease login in to continue"
        else:
            main_mail = email
            main_user_type = user_type
            id = generate_unique_id(user_type)
            if (user_type == 0):
                rec1.insert_one({"id": id, "email": email, "password": passwd, "children": []})
            else:
                rec2.insert_one(
                    {"id": id, "email": email, "name": "", "password": passwd, "patient": [], "details": ["", "", ""],
                     "requests": []})
            if (logged_in):
                with open("assets/logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            if main_user_type == 0:
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            else:
                lob = Lobby(r=None, p=None, name="lobby")
                sm.add_widget(lob)
                sm.current = "lobby"


class PageOne(Screen):
    def sign_in_up(self, case):
        Window.clearcolor = (230.0 / 255.0, 1, 1, 1)
        if (case == 0):
            print("Login")
        else:
            print("Sign Up")


class Login(Screen):

    def get_cred(self, email, passwd, logged_in):
        global sm
        global pop_text
        self.ids.email.text = ""
        self.ids.passwd.text = ""
        self.ids.logged_in = False
        result = match('[0-9a-z_.-]+@[a-z]+\.[a-z]+', email)
        if result is None:
            pop_text = "Enter a valid email address"
            Pop().open()
        else:
            email_process(0, email, passwd, logged_in)


class SignUp(Screen):
    user = ""

    def get_cred(self, email, passwd, logged_in):
        global sm
        global pop_text

        result = match('[0-9a-z_.-]+@[a-z]+\.[a-z]+', email)
        if result is None:
            pop_text = "Enter a valid email address"
            Pop().open()
        else:
            if (self.user == ""):
                pop_text = "The parent/doctor field is compulsory\nPLease select to proceed"
                Pop().open()
            else:
                self.ids.email.text = ""
                self.ids.passwd.text = ""
                self.ids.logged_in = False
                email_process(1, email, passwd, logged_in, self.user)

    def check_box_act(self, instance, val, user_type):
        self.user = user_type


class Lobby(Screen):
    view1 = ObjectProperty(None)
    view2 = ObjectProperty(None)

    def menu_clicked(self, value):
        global sm, lob, edit_win
        if (value == "Sign Out"):
            self.ids.menu.text = "Home"
            with open("assets/logged_in", "wb"):
                pass
            sm.remove_widget(lob)
            sm.current = "one"
        elif (value == "Edit Account"):
            sm.remove_widget(lob)

            edit_win = DocEditProfile(name="deditprof")
            sm.add_widget(edit_win)
            sm.current = "deditprof"

    def get_data(self, mail):
        dic = rec2.find_one({"email": main_mail})
        req = dic["requests"]

        patient = dic["patient"]
        return req, patient

    def __init__(self, r, p, **kwargs):
        super().__init__(**kwargs)
        global main_mail
        if (r == None and p == None):
            self.req, self.patient = self.get_data(main_mail)
        else:
            self.req, self.patient = r, p

        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for i in range(20):

            try:
                tex = str(i + 1) + " " + self.req[i][2]
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
                b.bind(on_press=lambda idx=i: self.press(0, idx, self.req, self.patient))
            except:
                tex = ""
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0, 0, 0, 0),
                           color=(1, 1, 1, 1))
            layout.add_widget(b)

        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)

        self.view1.add_widget(scrollview)

        layout2 = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout2.bind(minimum_height=layout2.setter("height"))

        for i in range(50):

            try:
                tex = str(i + 1) + " " + self.patient[i][2]
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
                b.bind(on_press=lambda idx=i: self.press(1, idx, self.req, self.patient))
            except:
                tex = ""
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0, 0, 0, 0),
                           color=(1, 1, 1, 1))
            layout2.add_widget(b)
        scrollview2 = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview2.add_widget(layout2)

        self.view2.add_widget(scrollview2)

    def press(self, case, but, req, pat):
        global main_mail, sm, lob, view_pat

        if (case == 0):
            print("New request")
            print("Button Pressed : ", but.text)
            li = req.pop(int(but.text[0]) - 1)
            pat.append(li)
            rec2.update_one({"email": main_mail}, {"$set": {"patient": pat, "requests": req}})
            db = rec2.find_one({"email": main_mail})
            did = db["id"]
            print(li)
            childcol.update_one({"cid": li[1]}, {"$set": {"did": did}})
            sm.remove_widget(lob)
            lob = Lobby(r=None, p=None, name="lobby")
            sm.add_widget(lob)
            sm.current = "lobby"
        else:
            print("View Patient")
            print("Button Pressed : ", but.text)
            view_pat = ViewPatientProfile(pat_dat=pat[int(but.text[0]) - 1], name="view_pat")
            sm.add_widget(view_pat)
            sm.current = "view_pat"

    def search(self, case, search_name=None):
        global lob, main_mail
        if (case == 0):
            count = 0

            req, pat = self.get_data(main_mail)
            temp = self.patient.copy()
            for i in range(len(pat)):
                tex = pat[i - count][2].lower()
                if (search_name.lower() not in tex):
                    pat.pop(i - count)
                    count += 1
            sm.remove_widget(lob)

            if (len(temp) > len(self.patient)):
                lob = Lobby(r=req, p=temp, name="lobby")
            else:
                lob = Lobby(r=self.req, p=pat, name="lobby")

            sm.add_widget(lob)
            sm.current = "lobby"
        else:
            sm.remove_widget(lob)
            req, pat = self.get_data(main_mail)
            lob = Lobby(r=req, p=pat, name="lobby")
            sm.add_widget(lob)
            sm.current = "lobby"


class ParentLobby(Screen):
    view1 = ObjectProperty(None)

    def menu_clicked(self, value):
        global sm, plob
        if (value == "Sign Out"):
            self.ids.menu.text = "Home"
            with open("assets/logged_in", "wb"):
                pass
            sm.current = "one"
            sm.remove_widget(plob)

    def child_button_clicked(instance):
        global sm, ch1, childwin
        ch1 = childcol.find_one({"name": instance.text, "pmail": main_mail})
        childwin = ChildScreen(name="child")
        print(ch1, "ch1")
        childwin.ids.namel.text = instance.text + "'s vaccine chart"
        sm.add_widget(childwin)
        sm.current = "child"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for child in childcol.find({"pmail": main_mail}):
            btn = Button(text=child["name"], size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1),
                         color=(1, 1, 1, 1))
            btn.bind(on_release=ParentLobby.child_button_clicked)
            layout.add_widget(btn)

        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)

        self.view1.add_widget(scrollview)


class AddChildScreen(Screen):
    def addChild(self, name, dob, malestate, femalestate):
        global plob
        try:
            dateOfBirth = datetime(int(dob[6:]), int(dob[3:5]), int(dob[:2]))
        except:
            create_popup("Error!", "Enter a valid date!")
            self.ids.dobin.text = ""
            return
        if name == "":
            create_popup("Error!", "Enter a valid date!")
            self.ids.namein.text = ""
            return
        if malestate == "normal" and femalestate == "normal":
            create_popup("Error!", "Enter a gender!")
            return

        if malestate == "down":
            gender = "M"
        if femalestate == "down":
            gender = "F"
        childId = generate_unique_id(2)
        dueVaccines, overVaccines, yetVaccines = validVaccines(dateOfBirth)
        document = {"pmail": main_mail, "cid": childId, "did": "", "name": name, "dob": dateOfBirth, "gender": gender, "info": "",
                    "dueVaccines": dueVaccines, "overVaccines": overVaccines, "yetVaccines": yetVaccines, "warningList": []}
        childcol.insert_one(document)
        chil = childcol.find_one({"cid": childId})
        upcomingStartingDate(chil)
        upcomingMidDate(chil)
        upcomingEndDate(chil)
        children_get()
        create_popup("Success", "Account created successfully!")
        self.ids.dobin.text = ""
        self.ids.namein.text = ""
        sm.remove_widget(plob)
        plob = ParentLobby(name="plobby")
        sm.add_widget(plob)


class ChildScreen(Screen):
    view1 = ObjectProperty(None)
    view2 = ObjectProperty(None)
    view3 = ObjectProperty(None)
    text1 = StringProperty("")

    def doc_det(self):
        global ch1, view_doc, sm

        doc_id = ch1["did"]
        print("doc_id", doc_id)
        if (doc_id == ""):
            view_doc = ViewDoctor(doc_assign=False, name="view_doc")
        else:
            db = rec2.find_one({"id": doc_id})
            view_doc = ViewDoctor(doc_assign=True, data=db, name="view_doc")
            print(db["name"])
        sm.add_widget(view_doc)
        sm.current = "view_doc"

    def save_and_back(self):
        global chbl, ch1, sm, childwin
        actl = []
        for i in range(len(chbl) - 1, -1, -1):
            if chbl[i].active:
                actl.append(i)
        dueVaccines = ch1["dueVaccines"]
        overVaccines = ch1["overVaccines"]
        for j in actl:
            overVaccines.append(dueVaccines.pop(j))
        # print(dueVaccines, overVaccines)
        childcol.update_one({"cid": ch1["cid"]}, {"$set": {"dueVaccines": dueVaccines, "overVaccines": overVaccines}})
        ch1 = childcol.find_one({"cid": ch1["cid"]})
        sm.current = "plobby"
        sm.remove_widget(childwin)

    def info_button(instance):
        vaxname = instance.text[8:]
        vaccine = vaxcol.find_one({"name": vaxname})
        with open(vaccine["info"], "r") as f:
            s = f.read()
        create_info_popup("Info", s)

    def add_child_info(self, info):
        global ch1
        childcol.update_one({"cid":ch1["cid"]}, {"$set": {"info": info}})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global ch1, chbl
        self.text1 = ch1["info"]
        chbl = []

        dueVaccines = ch1["dueVaccines"]
        overVaccines = ch1["overVaccines"]
        yetVaccines = ch1["yetVaccines"]

        lay1 = GridLayout(cols=3, spacing=10, size_hint_y=None)
        lay1.bind(minimum_height=lay1.setter("height"))

        for i in range(24):
            try:
                vaccine = dueVaccines[i]
                vaxname = vaxcol.find_one({"vid": vaccine})["name"]

                lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                             color=(1, 1, 1, 1))
                btn1 = CheckBox()

                btn2 = Button(text="Info on " + vaxname, size_hint=(1, None), height=50,
                              background_color=(0.5, 0.5, 0.5, 1),
                              color=(1, 1, 1, 1))
                btn2.bind(on_release=ChildScreen.info_button)

                chbl.append(btn1)
            except:
                lab = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                             color=(1, 1, 1, 1))
                btn1 = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                              color=(1, 1, 1, 1))

                btn2 = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                              color=(1, 1, 1, 1))
            lay1.add_widget(lab)
            lay1.add_widget(btn1)
            lay1.add_widget(btn2)

        if dueVaccines == []:
            lay1 = Label(text="There are no vaccines due at the moment", pos_hint = {"top":1, "center_x":0.5}, font_size= 30)

        self.view1.add_widget(lay1)

        lay3 = GridLayout(cols=2, spacing=10, size_hint_y=None)
        lay3.bind(minimum_height=lay3.setter("height"))

        for i in range(24):
            try:
                vaccine = yetVaccines[i]
                vaxname = vaxcol.find_one({"vid": vaccine})["name"]

                lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                             color=(1, 1, 1, 1))
                btn1 = Button(text="Info on " + vaxname, size_hint=(1, None), height=50,
                              background_color=(0.5, 0.5, 0.5, 1),
                              color=(1, 1, 1, 1))
                btn1.bind(on_release=ChildScreen.info_button)
            except:
                lab = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                             color=(1, 1, 1, 1))
                btn1 = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                              color=(1, 1, 1, 1))
            lay3.add_widget(lab)

            lay3.add_widget(btn1)

        if yetVaccines == []:
            lay3 = Label(text="You have taken all vaccines!", pos_hint = {"top":1, "center_x":0.5}, font_size= 30)

        self.view3.add_widget(lay3)

        lay2 = GridLayout(cols=2, spacing=10, size_hint_y=None)
        lay2.bind(minimum_height=lay2.setter("height"))

        for i in range(24):
            try:
                vaccine = overVaccines[i]
                vaxname = vaxcol.find_one({"vid": vaccine})["name"]

                lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                             color=(1, 1, 1, 1))
                btn1 = Button(text="Info on " + vaxname, size_hint=(1, None), height=50,
                              background_color=(0.5, 0.5, 0.5, 1),
                              color=(1, 1, 1, 1))
                btn1.bind(on_release=ChildScreen.info_button)
            except:
                lab = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                             color=(1, 1, 1, 1))
                btn1 = Button(text="", size_hint=(1, None), height=50, background_color=(0, 0, 0, 0),
                              color=(1, 1, 1, 1))
            lay2.add_widget(lab)
            if overVaccines == []:
                lay2 = Label(text="You haven't taken any vaccine yet", pos_hint={"top": 1, "center_x": 0.5},
                             font_size=30)

            lay2.add_widget(btn1)

        self.view2.add_widget(lay2)

    def back(self):
        global childwin, sm
        sm.remove_widget(childwin)
        sm.current = "plobby"


class ViewPatientProfile(Screen):
    text1 = StringProperty("")
    text2 = StringProperty("")
    view4 = ObjectProperty(None)
    view5 = ObjectProperty(None)
    view6 = ObjectProperty(None)

    def __init__(self, pat_dat, **kwargs):
        super().__init__(**kwargs)
        self.patient_data = pat_dat
        print(pat_dat)
        dic = rec1.find_one({"id": pat_dat[0]})
        mail = dic["email"]
        gender = None
        if (pat_dat[3] == 0):
            gender = "Female"
        else:
            gender = "Male"
        print(pat_dat)
        print(mail)
        ch1 = childcol.find_one({"name": pat_dat[2], "pmail": mail})
        self.text2 = ch1["info"]
        dueVaccines = ch1["dueVaccines"]
        # dueVaccines = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        overVaccines = ch1["overVaccines"]
        yetVaccines = ch1["yetVaccines"]
        #
        self.text1 = "Name : " + pat_dat[2] + "\nAge :" + str(
            pat_dat[4]) + "\nSex : " + gender + "\nParent email : " + mail

        vac_list = [dueVaccines, overVaccines, yetVaccines]
        view_list = [self.view4, self.view5, self.view6]

        for j in range(3):
            layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            layout.bind(minimum_height=layout.setter("height"))

            for i in range(20):

                try:
                    tex = vaxcol.find_one({"vid": vac_list[j][i]})["name"]
                    b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                               color=(1, 1, 1, 1))
                except:
                    tex = ""
                    b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0, 0, 0, 0),
                               color=(1, 1, 1, 1))
                layout.add_widget(b)
            if(len(vac_list[j]) == 0):
                tex = "None"
                layout = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
            scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
            scrollview.add_widget(layout)

            view_list[j].add_widget(scrollview)

    def back(self):
        global view_pat
        sm.current = "lobby"
        sm.remove_widget(view_pat)


class DocEditProfile(Screen):
    text1 = StringProperty("")
    text2 = StringProperty("")
    text3 = StringProperty("")
    text4 = StringProperty("")

    def __init__(self, **kwargs):
        super(DocEditProfile, self).__init__(**kwargs)
        global main_mail
        dic = rec2.find_one({"email": main_mail})
        print(main_mail, "hoiiiiiiiiiiiiiiiihhhhhhhi")
        self.text1 = dic["name"]
        self.text2 = dic["details"][0]
        self.text3 = dic["details"][1]
        self.text4 = dic["details"][2]

    def press(self, name, qual, bio, edu):
        global lob, main_mail, edit_win
        rec2.update_one({"email": main_mail}, {"$set": {"name": name, "details": [qual, bio, edu]}})
        lob = Lobby(r=None, p=None, name="lobby")
        sm.add_widget(lob)
        sm.remove_widget(edit_win)
        sm.current = "lobby"

    def back(self):
        global lob, edit_win
        lob = Lobby(r=None, p=None, name="lobby")
        sm.add_widget(lob)
        sm.remove_widget(edit_win)
        sm.current = "lobby"


class ConfirmDoc(Popup):
    text1 = StringProperty("")

    def __init__(self, data, **kwargs):
        super(ConfirmDoc, self).__init__(**kwargs)
        self.title = "Confirm Doctor"
        self.text1 = "Name : " + data[3] + "\n\nemail : " + data[2] + "\n\nQualification : " + data[-2][
            0] + "\n\nEducation : " + data[-2][2]
        self.data = data

    def add_doc(self):
        global conf_doc, add_pop, ch1
        conf_doc.dismiss()
        add_pop.dismiss()
        req = self.data[-1]
        print("initial", req)
        db = rec1.find_one({"email": ch1["pmail"]})
        id = db["id"]
        gen = None
        if (ch1['gender'] == "M"):
            gen = 1
        else:
            gen = 0
        li = [id, ch1['cid'], ch1['name'], gen, ch1["dob"]]
        print(li)
        print(self.data)

        flag = True
        for i in req:
            if (i[1] == ch1['cid']):
                flag = False
                break
        req.append(li)
        print("req", req)
        if (flag):
            print("ola")
            rec2.update_one({"id": self.data[1]}, {"$set": {"requests": req}})


class AddDocPop(Popup):
    view7 = ObjectProperty("None")

    def __init__(self, d, **kwargs):
        super(AddDocPop, self).__init__(**kwargs)
        self.title = "Select Doctor"
        if (d == None):
            self.doc = []
        else:
            self.doc = d
        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for i in range(50):
            try:
                tex = str(i + 1) + " " + self.doc[i][3]
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
                b.bind(on_press=lambda idx=i: self.press(idx, self.doc))
            except:
                tex = ""
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0, 0, 0, 0),
                           color=(1, 1, 1, 1))
            layout.add_widget(b)
        scrollview = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview.add_widget(layout)

        self.view7.add_widget(scrollview)

    def press(self, idx, doc):
        global conf_doc
        conf_doc = ConfirmDoc(data=doc[int(idx.text[0]) - 1])
        conf_doc.open()

    def search(self, search_text):
        global add_pop
        if (search_text == ""):
            pass
        else:
            doc = get_accounts(1)
            li = []
            print(doc)
            for i in doc:
                tex = i[3].lower()
                if search_text.lower() in tex:
                    li.append(i)
            print("li : ", li)
            if (len(li) > 0):
                add_pop.dismiss()
                add_pop = AddDocPop(li)
                add_pop.open()


class ViewDoctor(Screen):
    text1 = StringProperty("")
    text2 = StringProperty("")

    def __init__(self, doc_assign=False, data=None, **kwargs):
        super(ViewDoctor, self).__init__(**kwargs)
        self.doc_assign = doc_assign
        self.doc_profile = data

        if (self.doc_assign == False):
            self.text1 = "Your are not referring to any doctor"
            self.text2 = "Please add a doctor"
        else:
            self.text1 = "Doctor Profile"
            self.text2 = "Name : " + data["name"] + "\n\nemail : " + data["email"] + "\n\nBio : " + data["details"][
                1] + "\n\nQualification : " + data["details"][0] + "\n\nEducation : " + data["details"][2]

    def remove_doc(self):
        global ch1
        childcol.update_one({"cid": ch1["cid"]}, {"$set": {"did": ""}})
        pat = self.doc_profile['patient']
        for i in pat:
            if (i[1] == ch1["cid"]):
                pat.remove(i)
                break

        rec2.update_one({"id": self.doc_profile["id"]}, {"$set": {"patient": pat}})
        print(self.doc_profile)

    def add_doc_pop(self):
        global add_pop
        add_pop = AddDocPop(d=[])
        add_pop.open()

    def back(self):
        global view_doc
        sm.remove_widget(view_doc)
        sm.current = "child"


class WindowManager(ScreenManager):
    pass


Builder.load_file('Illimmunate.kv')


class Main(App):
    def build(self):
        global sm, main_mail, main_user_type, plob, lob
        sm = WindowManager(transition=NoTransition())
        sm.add_widget(PageOne(name="one"))
        sm.add_widget(Login(name="login"))
        sm.add_widget(SignUp(name="signup"))
        sm.add_widget(AddChildScreen(name="addchild"))
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (800, 750)

        try:
            with open("assets/logged_in", "rb") as file:
                x = load(file)
                y = load(file)
            main_mail = x
            if (y[0] == 'P'):
                main_user_type = 0
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            else:
                lob = Lobby(r=None, p=None, name="lobby")
                sm.add_widget(lob)
                main_user_type = 1
                sm.current = "lobby"
        except:
            pass

        return sm


app = Main()
app.title = "Illimmunate"
app.run()
