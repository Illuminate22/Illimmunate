from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ObjectProperty
from kivy.core.window import Window
from kivy.config import Config
import certifi
from datetime import *
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

ca = certifi.where()

import pymongo

from re import match

from pickle import dump, load

# from random import choice

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


def validVaccines(dob, childVaxList=vaxlist):
    vaccines_get()
    presentDay = datetime.today()
    dueVaccines, overVaccines, yetVaccines = [], [], []
    for vaccine in childVaxList:
        if timedelta(days=vaccine["date_start"]) + dob < presentDay and timedelta(
                days=vaccine["date_end"]) + dob > presentDay or timedelta(days=vaccine["date_end"]) + dob == presentDay:
            dueVaccines.append(vaccine["vid"])
        elif timedelta(days=vaccine["date_start"]) + dob > presentDay:
            yetVaccines.append(vaccine["vid"])
        elif timedelta(days=vaccine["date_end"]) + dob < presentDay:
            overVaccines.append(vaccine["vid"])
    return dueVaccines, overVaccines, yetVaccines


def get_accounts(cond):
    if (cond == 0):
        return list(map(lambda item: list(item.values()), rec1.find()))
    elif (cond == 1):
        return list(map(lambda item: list(item.values()), rec2.find()))
    elif (cond == 2):
        return list(map(lambda item: list(item.values()), childcol.find()))


def generate_unique_id(case):
    # li = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
    id = str(len(get_accounts(case)) + 1)

    for i in range(6 - len(id)):
        id = "0" + id

    if (case == 0):
        id = "P" + id
    else:
        id = "D" + id

    return id

    # for i in range(6):
    #     id += choice(li)


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
                if i[2] == email and i[3] == passwd:
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
                with open("logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            if main_user_type == 0:
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            elif main_user_type == 1:
                lob = Lobby(name="lobby")
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
                rec2.insert_one({"id": id, "email": email, "name": "", "password": passwd, "patient": [], "details": [],
                                 "requests": []})
            if (logged_in):
                with open("logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            if main_user_type == 0:
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            else:
                lob = Lobby(name="lobby")
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
        result = match('[0-9a-z]+@[a-z]+\.[a-z]+', email)
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

        result = match('[0-9a-z]+@[a-z]+\.[a-z]+', email)
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
            with open("logged_in", "wb"):
                pass
            sm.remove_widget(lob)
            sm.current = "one"
        elif (value == "Edit Account"):
            sm.remove_widget(lob)

            edit_win = DocEditProfile(name="deditprof")
            sm.add_widget(edit_win)
            sm.current = "deditprof"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global main_mail
        dic = rec2.find_one({"email": main_mail})
        req = dic["requests"]

        patient = dic["patient"]

        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for i in range(20):

            try:
                tex = str(i + 1) + " " + req[i][2]
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
                b.bind(on_press=lambda idx=i: self.press(0, idx))
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
                tex = str(i + 1) + " " + patient[i][2]
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0.5, 0.5, 0.5, 1),
                           color=(1, 1, 1, 1))
                b.bind(on_press=lambda idx=i: self.press(1, idx))
            except:
                tex = ""
                b = Button(text=tex, size=(50, 50), size_hint=(1, None), background_color=(0, 0, 0, 0),
                           color=(1, 1, 1, 1))
            layout2.add_widget(b)
        scrollview2 = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        scrollview2.add_widget(layout2)

        self.view2.add_widget(scrollview2)

    def press(self, case, but):
        global main_mail, sm, lob, view_pat
        dic = rec2.find_one({"email": main_mail})
        req = dic["requests"]
        patient = dic["patient"]
        if (case == 0):
            print("New request")
            print("Button Pressed : ", but.text)
            li = req[int(but.text[0]) - 1]
            req.pop(int(but.text[0]) - 1)
            patient.append(li)
            rec2.update_one({"email": main_mail}, {"$set": {"patient": patient, "requests": req}})
            sm.remove_widget(lob)
            lob = Lobby(name="lobby")
            sm.add_widget(lob)
            sm.current = "lobby"
        else:
            print("View Patient")
            print("Button Pressed : ", but.text)
            view_pat = ViewPatientProfile(pat_dat=patient[int(but.text[0]) - 1], name="view_pat")
            sm.add_widget(view_pat)
            sm.current = "view_pat"


class ParentLobby(Screen):
    view1 = ObjectProperty(None)

    def menu_clicked(self, value):
        global sm, plob
        if (value == "Sign Out"):
            self.ids.menu.text = "Home"
            with open("logged_in", "wb"):
                pass
            sm.current = "one"
            sm.remove_widget(plob)

    def child_button_clicked(instance):
        global sm, ch1
        ch1 = childcol.find_one({"name": instance.text, "pmail": main_mail})
        childwin = ChildScreen(name="child")
        print(ch1, "ch1")
        childwin.ids.namel.text = instance.text + "'s vaccine\n chart"
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
    def addChild(self, name, dob, docid):
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

        childId = "C" + str(len(children) + 1)
        dueVaccines, overVaccines, yetVaccines = validVaccines(dateOfBirth)
        document = {"pmail": main_mail, "did": docid, "cid": childId, "name": name, "dob": dateOfBirth,
                    "dueVaccines": dueVaccines, "overVaccines": overVaccines, "yetVaccines": yetVaccines}
        childcol.insert_one(document)
        children_get()
        create_popup("Success", "Account created successfully!")
        self.ids.dobin.text = ""
        self.ids.namein.text = ""
        self.ids.docin.text = ""
        sm.remove_widget(plob)
        plob = ParentLobby(name="plobby")
        sm.add_widget(plob)


class ChildScreen(Screen):
    view1 = ObjectProperty(None)
    view2 = ObjectProperty(None)
    view3 = ObjectProperty(None)

    def due_button(self):
        pass

    def over_button(self):
        pass

    def yet_button(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        global ch1

        dueVaccines = ch1["dueVaccines"]
        overVaccines = ch1["overVaccines"]
        yetVaccines = ch1["yetVaccines"]

        lay1 = GridLayout(cols=3, spacing=10, size_hint_y=None)
        lay1.bind(minimum_height=lay1.setter("height"))

        for vaccine in dueVaccines:
            vaxname = vaxcol.find_one({"vid": vaccine})["name"]

            lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                         color=(1, 1, 1, 1))
            btn1 = Button(text="Taken", size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1),
                          color=(1, 1, 1, 1))

            btn2 = Button(text="Info", size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1),
                          color=(1, 1, 1, 1))
            lay1.add_widget(lab)
            lay1.add_widget(btn1)
            lay1.add_widget(btn2)

        self.view1.add_widget(lay1)

        lay3 = GridLayout(cols=2, spacing=10, size_hint_y=None)
        lay3.bind(minimum_height=lay1.setter("height"))

        for vaccine in yetVaccines:
            vaxname = vaxcol.find_one({"vid": vaccine})["name"]

            lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                         color=(1, 1, 1, 1))
            btn1 = Button(text="Info", size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1),
                          color=(1, 1, 1, 1))
            lay3.add_widget(lab)

            lay3.add_widget(btn1)

        self.view3.add_widget(lay3)

        lay2 = GridLayout(cols=2, spacing=10, size_hint_y=None)
        lay2.bind(minimum_height=lay1.setter("height"))

        for vaccine in overVaccines:
            vaxname = vaxcol.find_one({"vid": vaccine})["name"]

            lab = Button(text=vaxname, size_hint=(1, None), height=50, background_color=(0, 0, 0, 1),
                         color=(1, 1, 1, 1))
            btn1 = Button(text="Info", size_hint=(1, None), height=50, background_color=(0.5, 0.5, 0.5, 1),
                          color=(1, 1, 1, 1))
            lay2.add_widget(lab)

            lay2.add_widget(btn1)
        self.view2.add_widget(lay2)

    def over_button(self):
        pass

    def yet_button(self):
        pass


# class ForgotPswd(Screen):
#     pass


class ViewPatientProfile(Screen):
    text1 = StringProperty("")
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
        lob = Lobby(name="lobby")
        sm.add_widget(lob)
        sm.remove_widget(edit_win)
        sm.current = "lobby"

    def back(self):
        global lob, edit_win
        lob = Lobby(name="lobby")
        sm.add_widget(lob)
        sm.remove_widget(edit_win)
        sm.current = "lobby"



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
        # sm.add_widget(Lobby(name="lobby"))
        sm.add_widget(AddChildScreen(name="addchild"))
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (800, 750)

        try:
            with open("logged_in", "rb") as file:
                x = load(file)
                y = load(file)
            main_mail = x
            if (y[0] == 'P'):
                main_user_type = 0
                plob = ParentLobby(name="plobby")
                sm.add_widget(plob)
                sm.current = "plobby"
            else:
                lob = Lobby(name="lobby")
                sm.add_widget(lob)
                main_user_type = 1
                sm.current = "lobby"
        except:
            pass

        return sm


app = Main()
app.title = "Illimmunate"
app.run()
