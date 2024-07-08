import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label

print (kivy.__version__)
###### ######
import psycopg2, datetime
dbname, user, host, password = ["", "", "", "", ]
# f = open("config_smh.txt", "r")
f = open("config.txt", "r")
for ex in f.readlines():
    line = ex.replace("\n", "").replace(" ", "")
    if "dbname" in line: dbname = line.split(":")[-1]
    if "user" in line: user = line.split(":")[-1]
    if "host" in line: host = line.split(":")[-1]
    if "password" in line: password = line.split(":")[-1]

conn = psycopg2.connect(dbname=dbname, user=user, host=host, password=password)
_curs = conn.cursor()
print ("connection initialized")
###### ######

class createAccountWindow(Screen):
    nname = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    def submit(self):
        _name, _email, _pass = self.nname.text, self.email.text, self.password.text
        today = datetime.datetime.today()
        if _name != "" and _email != "" and "@" in _email and "." in _email:
            if _pass != "":
                ##add user
                _curs.execute("""insert into test_accounts (email, password, created, nname) values (%s, %s, %s, %s)""", (_email, _pass, today, _name, ))
                _curs.execute("""commit;""")

                
                self.reset()
                sm.current = "login"
            else:
                invalidForm()
                pass
        else:
            invalidForm()
        # pass
    def login(self):
        self.reset()
        sm.current = "login"
    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.nname.text = ""
class loginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)
    def btnLogin(self):
        _email = self.email.text
        _password = self.password.text
        if _email != "" and _password != "":
            # mainWindow.currentUser = self.email.text
            mainWindow.currentUser = self.email.text
            # print (self.email.text, self.password.text)
            self.reset()
            _curs.execute("""select password from test_accounts where email = %s""", (_email, ))
            result = _curs.fetchone()
            if result:
                if _password == result[0]:
                    # mainWindow.currentUser = self.email.text
                    sm.current = "main"
                else: invalidLogin()
            else:
                invalidLogin()
        else:
            invalidLogin()
            pass
    def btnCreate(self):
        self.reset()
        sm.current = "create"
    def reset(self):
        self.email.text = ""
        self.password.text = ""
class mainWindow(Screen):
    nname = ObjectProperty(None)
    created = ObjectProperty(None)###these are like the widgets in pyqt, or bridge
    email = ObjectProperty(None)
    currentUser = ""
    def btnLogout(self):
        sm.current = "login"
        pass
    def on_enter(self, *args):
        ##get info using self.currentUser
        # print (self.currentUser)
        _curs.execute("""select email, nname, created from test_accounts where email = %s""", (self.currentUser, ))
        result = _curs.fetchone()
        # print (result)
        _email, _name, _created = result and result or ["", "", "", ]
        self.nname.text = "Account Name: %s"%_name
        self.email.text = "Email Address: %s"%_email
        self.created.text = "Date Created: %s"%_created
        pass

class windowManager(ScreenManager):
    pass

def invalidLogin():
    pop = Popup(title = "Invalid Login",
                content = Label(text = "Invalid Username or password."),
                size_hint = (None, None), size = (400, 400))
    pop.open()

def invalidForm():
    pop = Popup(title = "Invalid Form",
                content = Label(text = "Please fill in all inputs with valid information."),
                size_hint = (None, None), size = (400, 400))
    pop.open()

kv = Builder.load_file("mainTest11.kv")
sm = windowManager()
screens = [loginWindow(name="login"), createAccountWindow(name="create"), mainWindow(name="main")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"

class MyFirstApp(App):
    def build(self):
        return sm
if __name__ == "__main__":
    MyFirstApp().run()