from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.config import Config

import pymongo

from re import match

from pickle import  dump, load

# from random import choice

client = pymongo.MongoClient("mongodb+srv://user1:honeycake123@cluster0.zd1jh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.get_database("database_main")
rec1 = db.doctor
rec2 = db.parent

pop_text = ""
main_mail = ""
main_user_type = -1

def get_accounts(cond):
    if(cond == 0):
        return list(map(lambda item: list(item.values()), rec1.find()))
    else:
        return list(map(lambda item: list(item.values()), rec2.find()))

def generate_unique_id(case):
    # li = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'a', 'b', 'c', 'd', 'e', 'f']
    id = str(len(get_accounts(case))+1)

    for i in range(6-len(id)):
        id = "0" + id

    if(case == 0):
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
    global main_mail, main_user_type, sm, pop_text
    print(case)
    print(email)
    print(passwd)
    print(logged_in)
    print(user_type)
    if(case == 0):
        par = get_accounts(0)
        doc = get_accounts(1)
        flag1, flag2 = False, False
        id = None
        for i in par:
            if i[2] == email and i[3] == passwd:
                flag1 = True
                id = i[1]
                break
        if(flag1 == False):
            for i in doc:
                if i[2] == email and i[3] == passwd:
                    flag2 = True
                    id = i[1]
                    break
        u_type = None
        if(flag1):
            u_type = 0
        elif(flag2):
            u_type = 1

        if(u_type == None):
            pop_text = "Email or password entered is wrong!! Please re-enter the credentials"
            Pop().open()
        else:
            main_mail = email
            main_user_type = u_type
            if(logged_in):
                with open("logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            sm.current = "lobby"

    if(case == 1):
        par = get_accounts(0)
        doc = get_accounts(1)

        flag1, flag2 = True, True

        for i in doc:
            if i[2] == email:
                flag1 = False
                break
        if(flag1):
            for i in par:
                if i[2] == email:
                    flag2 = False
                    break

        if(flag1 == False or flag2 == False):
            pop_text = "The given email id already has an account linked with it\nPlease login in to continue"
        else:
            main_mail = email
            main_user_type = user_type
            id = generate_unique_id(user_type)
            if(user_type == 0):
                rec2.insert_one({"id": id,"email": email, "password": passwd, "children": []})
            else:
                rec1.insert_one({"id": id, "email": email, "password": passwd, "patient": []})
            if(logged_in):
                with open("logged_in", "wb") as file:
                    dump(email, file)
                    dump(id, file)
            sm.current = "lobby"
            

class PageOne(Screen):
    def sign_in_up(self, case):
        Window.clearcolor = (230.0 / 255.0, 1, 1, 1)
        if(case == 0):
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
            if(self.user == ""):
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
    def menu_clicked(self, value):
        global sm
        if(value == "Sign Out"):
            self.ids.menu.text = "Home"
            with open("logged_in", "wb"):
                pass
            sm.current = "one"

            


# class ForgotPswd(Screen):
#     pass


class WindowManager(ScreenManager):
    pass



Builder.load_file('Main.kv')


class Main(App):
    def build(self):
        global sm, main_mail, main_user_type
        sm = WindowManager(transition=NoTransition())
        sm.add_widget(PageOne(name="one"))
        sm.add_widget(Login(name="login"))
        sm.add_widget(SignUp(name="signup"))
        sm.add_widget(Lobby(name="lobby"))        
        Window.clearcolor = (1, 1, 1, 1)
        Window.size = (800, 750)


        try:
            with open("logged_in", "rb") as file:
                x = load(file)
                y = load(file)
            main_mail = x
            if(y[0] == 'P'):
                main_user_type = 0
            else:
                main_user_type = 1
            sm.current = "lobby"
        except:
            pass


        return sm


app = Main()
app.title = "Illimmunate"
app.run()