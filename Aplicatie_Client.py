#****************************************************************************************************************#
#
# Filename: Aplicatie_Client.py
# Description: Aplicatie de chat realizata in Python cu interfata grafica Tkinter si conexiune la server socket
# Author: Codreanu Dan
#
#
#****************************************************************************************************************#

#********************************************_IMPORT_AREA_*******************************************************#
import sqlite3              # importarea modulului sqlite3 pentru lucrul cu baza de date
from sqlite3 import Error   # importarea modulului Error din sqlite3
import random               # importarea modulului random pentru generarea de numere random (ID)
import time 
import socket               # importarea modulului socket pentru conexiunea la server
import threading            # importarea modulului threading pentru a rula mai multe threaduri (conexiunea la server, primirea de mesaje, trimiterea de mesaje)
import tkinter              # importarea modulului tkinter pentru interfata grafica
import tkinter as tk
import sys
from tkinter import *
from tkinter import ttk,Frame
from tkinter import scrolledtext
from tkinter import filedialog
from PIL import Image,ImageTk
from datetime import datetime # importarea modulului datetime pentru a obtine data si ora
import os                   # importarea modulului os pentru lucrul cu fisiere
from plyer import notification # importarea modulului plyer pentru notificari

#********************************************_VARIABILE_GLOBALE_**************************************************#
HOST = '169.254.21.143' # Adresa IP a serverului
PORT = 1234             # Portul pe care se face conexiunea

###################################################################################################################

#****************************************_Client_Messenger_CLASS_*************************************************#
"""
    NOTE:
    Clasa Client_Messenger este responsabila de functionarea aplicatiei de chat.
    Input: host, port, mainMenu, guiCommand, username
    Output: interfata grafica a aplicatiei de chat si conexiunea la server pentru trimiterea si primirea de mesaje
    Functii: parte_grafica_chat, trimite_mesaje, trimite_fisere, trimite_emoji, primeste_mesaje, oprire_messenger
    Variabile: fromLoginScreen, s, nume_in_aplicatie, nume_sv_fisiere, lista_emoji, Interfata_OK, Functioneaza_Client
    Threaduri: parte_grafica_chat_thread, primeste_mesaje_thread, trimite_mesaje_thread
"""
class Client_Messenger():
    #*************************************_CONSTRUCTOR_*********************************************************#
    def __init__(self,host,port,mainMenu,guiCommand,username):
        self.fromLoginScreen = Login_Screen(mainMenu, guiCommand)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.get_IPAddr()
        
        if self.hostname:
            self.s.connect((self.hostname,port))
            print(f"[MESS][CONN][INFO]: Conectat dinamic:{self.hostname}")
        else:
            self.s.connect((host,port))
            print(f"[MESS][CONN][INFO]: Conectat static:{host}")

        self.nume_in_aplicatie = username
        self.nume_sv_fisiere = username

        self.lista_emoji = ["😂", "😍", "😎", "😴", "😷", "😜", "😇", 
                            "🤪", "🤩", "🤔", "🤮","🤐", "🤢", "🤮", 
                            "🤒","😖","🤗","🇷🇴","🇲🇩	","🔴","✅","❌",
                            "♒","☦","💶","💻","🫢","🫣","🤫","🤔",
                            "🫡","🤐","🤨","😐","😑","😶",
                            "😶‍🌫️","😏","🤥","🥵","🤠","🥸"]

        self.Interfata_OK = False       # Va ramane fals pana se intializeaza interfata grafica
        self.Functioneaza_Client = True # Devine False cand aplicatia se inchide 

        parte_grafica_chat_thread = threading.Thread(target = self.parte_grafica_chat) # primul thread se ocupa de functionarea interfetei grafice
        primeste_mesaje_thread = threading.Thread(target = self.primeste_mesaje) # al doilea thread se ocupa de primirea de mesaje
        trimite_mesaje_thread = threading.Thread(target = self.trimite_mesaje) #al treiles thread responsabil de trimiterea mesajelor
        
        parte_grafica_chat_thread.start()
        primeste_mesaje_thread.start()
        trimite_mesaje_thread.start()
        
    #*************************************************************************_GET_IP_ADDRESS_***********************************************************************************#
    def get_IPAddr(self):                                                   # Functie pentru a obtine adresa IP a serverului
        self.hostname=socket.gethostname()                                  # Numele calculatorului
        self.IPAddr=socket.gethostbyname(socket.gethostname())              # Adresa IP a calculatorului
        print("Your Computer Name is:"+self.hostname)   
        print("Your Computer IP Address is:"+self.IPAddr) 
        time.sleep(2)
        
    #*************************************_PARTE_GRAFICA_CHAT_**************************************************#
    def parte_grafica_chat(self):
        #*********_Creeaza_fereastra_chat_*********#
        self.Chat_Window_root = tkinter.Tk()
        self.Chat_Window_root.title("Messenger App")
        #******************_Icon_******************#
        self.Chat_Window_root.iconbitmap('icon_logo.ico')
        self.Chat_Window_root.configure(bg = 'grey')
        #****************_Dimensiuni_***************#
        self.Chat_Window_root.geometry('600x750')
        self.Chat_Window_root.resizable(False, False)
        self.Chat_Window_root.attributes('-alpha',0.99)
        #*****************_Canvas_******************#
        '''
            NOTE: Ecran Messenger: Message Window, Text Box, Send Button, Send File Button, Log Out Button
        '''
        self.Label_Chat = Label(self.Chat_Window_root, 
                                text = 'Chat, User: ' + str(self.nume_in_aplicatie),
                                bg = 'light blue',font = ('consolas',12))
        self.Label_Chat.pack(padx = 20, pady = 5)
        #----------------------------------------------------------------------
        self.Chat_Text_Box = scrolledtext.ScrolledText(self.Chat_Window_root,
                                                       font = ('consolas',12), 
                                                       height = 15)
        self.Chat_Text_Box.config(state = 'disabled')
        self.Chat_Text_Box.pack(padx = 20, pady = 5)
        #----------------------------------------------------------------------
        self.Label_Mesaj = Label(self.Chat_Window_root,
                                 text = 'Mesaj', bg = 'lightgray',
                                 font = ('consolas',12))
        self.Label_Mesaj.pack(padx = 20, pady = 5)
        #----------------------------------------------------------------------
        self.Mesaj_Text_Box = Text(self.Chat_Window_root,
                                   font = ('consolas',12),
                                   height = 3)
        self.Mesaj_Text_Box.pack(padx = 20 ,pady = 5)
        #----------------------------------------------------------------------
        self.lista_emoji_combobox = ttk.Combobox(self.Chat_Window_root,
                                                 values=self.lista_emoji,
                                                 text = 'Emoji')
        self.lista_emoji_combobox.bind("<<ComboboxSelected>>", self.trimite_emoji)
        self.lista_emoji_combobox.pack(padx = 20, pady = 5)

        self.Buton_Trimite_Mesaj = Button(self.Chat_Window_root, text = 'Send', activebackground = 'light green',
                                          font = ('consolas',12), 
                                          command = self.trimite_mesaje, bg = 'light gray')
        self.Buton_Trimite_Mesaj.pack(padx = 20, pady = 5)
        #----------------------------------------------------------------------
        self.Buton_Trimite_File = Button(self.Chat_Window_root, text = 'Send file', activebackground= 'light green',
                                         font = ('consolas',12), 
                                         command =  self.trimite_fisere, bg = 'light gray')
        self.Buton_Trimite_File.pack(padx = 20, pady = 5)
        #----------------------------------------------------------------------
        self.Buton_Log_Out = Button(self.Chat_Window_root, text = 'Log Out',activebackground = 'red',
                                    font = ('consolas',12), 
                                    command = self.oprire_messenger, bg = 'light gray')
        self.Buton_Log_Out.pack(padx = 20, pady = 5)
        #*************************_Functionalitatii_*************************#
        self.Interfata_OK = True           # Interfata grafica a fost initializata
        self.Chat_Window_root.mainloop()   # Rularea interfetei grafice
        self.Chat_Window_root.protocol('WM_DELETE_WINDOW',self.oprire_messenger)  

    #*************************************_TRIMITE_MESAJE_******************************************************#
    '''
       NOTE: Functia trimite_mesaje: encoding: utf-8
    '''
    def trimite_mesaje(self):
        #*********_Data_si_ora_*********#
        time = datetime.now()
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
        #*********_Mesaj_trimis_*********#
        mesaj_trimis = '('+str(formatted_time)+') -> '+str(self.nume_in_aplicatie)+': '+str(self.Mesaj_Text_Box.get('1.0','end'))
        self.s.send(mesaj_trimis.encode('utf-8'))
        self.Mesaj_Text_Box.delete('1.0','end')
        print('[MESS][SEND_MSG][INFO]:Mesaj trimis: '+str(mesaj_trimis))

    #*************************************_TRIMITE_FISERE_******************************************************#
    '''
        NOTE: Functia trimite_fisere: filedialog.askopenfilename() -> deschide fereastra de dialog pentru alegerea fisierului
        TODO: Sa se trimita fisierul ales
    '''
    def trimite_fisere(self):
        #*********_Deschide_fereastra_de_dialog_*********#
        self.file_name =  filedialog.askopenfilename()
        #**************_Deschide_fisierul_***************#
        self.file = open(self.file_name,'rb')
        #*******_Citeste_dimensiunea_fisierului_*********#
        self.file_size = os.path.getsize(self.file_name)
        print('[MESS][SEND_FILE][INFO]:File path: '+str(self.file_name))
        print('[MESS][SEND_FILE][INFO]:File size: '+str(self.file_size))

    #*************************************_TRIMITE_EMOJI_******************************************************#
    def trimite_emoji(self,event):
        selected_emoji = self.lista_emoji_combobox.get()
        self.Mesaj_Text_Box.insert(tk.END, selected_emoji)

    #*************************************_PRIMESTE_MESAJE_******************************************************#
    '''
        NOTE: Functia primeste_mesaje: decode: utf-8
    '''
    def primeste_mesaje(self):
        while self.Functioneaza_Client:
            try:
                mesaj = self.s.recv(1024).decode('utf-8')
                print('[MESS][RECV_MSG][INFO]::Mesaj primit: '+str(mesaj))
                if mesaj != 'NAME':
                    notification.notify(title='Messenger', # notificare la primirea unui mesaj
                                        message=f'{mesaj}',
                                        timeout = 0.5)
                if mesaj == 'NAME' : # Serverul trimite acest mesaj iar clinetul rasupunde cu username.
                        self.s.send(self.nume_in_aplicatie.encode('utf-8')) 
                else:
                    if self.Interfata_OK: # inserare mesaj in chat box
                        self.Chat_Text_Box.config(state = 'normal')
                        self.Chat_Text_Box.insert('end',mesaj)
                        self.Chat_Text_Box.yview('end')
                        self.Chat_Text_Box.config(state = 'disabled')
            except ConnectionAbortedError:
                break
            except:
                print('[MESS][RECV_MSG][ERROR]:Eroare !')
                self.s.close()
                break

    #*************************************_OPRIRE_MESSENGER_******************************************************#
    def oprire_messenger(self):
            self.Functioneaza_Client = False
            self.Chat_Window_root.destroy()
            self.s.close()
            exit(0)



#*************************************_SQL_Lite_Connect_CLASS_**************************************************#
"""
    NOTE:
    Clasa SQL_Lite_Connect este responsabila de conectarea la baza de date.
    Input: -
    Output: conectarea la baza de date
    Functii: db_connection
    Variabile: connection, cursor, cursor_users, rezultat
"""
class SQL_Lite_Connect():
    #*************************************_db_connection_******************************************************#
    def db_connection(self):
        try:
            self.connection = sqlite3.connect('USERS.db')
            self.cursor = self.connection.cursor()
            self.cursor_users = self.connection.cursor()
            self.cursor.execute('select * from users;')
            self.cursor_users.execute("select * from users;")
            self.rezultat = self.cursor.fetchall()
            print('[SQLLITE][INFO]:S-a realizat conectarea la baza de date <OK>')
        except Error as e:
            print(f"[SQLLITE][ERROR]:Eroare la conectare cu baza de date {e}<!>")

#*************************************_GUI_Commands_CLASS_**************************************************#
"""
    NOTE:
    Clasa GUI_Commands este responsabila de comenzi pentru interfata grafica.
    Input: mainMenu
    Output: comenzi pentru interfata grafica
    Functii: raise_frame, stergeEntryLog, stergeEntryReg, logOut, quit_mess, show_password_frame2, show_password_frame3, show_password_frame4
    Variabile: mainMenu, fromLoginScreen, fromRegisterScreen, fromChangePasswordScreen
"""
class GUI_Commands():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self, mainMenu):
        self.mainMenu = mainMenu # mainMenu: instanta a clasei GUI_Config
        self.fromLoginScreen = Login_Screen(mainMenu, self)
        self.fromRegisterScreen = Regsiter_Screen(mainMenu, self)
        self.fromChangePasswordScreen = Change_Password_Screen(mainMenu, self)
        
    #*************************************_RAISE_FRAME_******************************************************#
    '''
        NOTE: Functia raise_frame: tkraise() -> change the frame
    '''
    def raise_frame(self, frame):
        frame.tkraise()
        
    #*************************************_STERGE_ENTRY_LOG_**************************************************#
    def stergeEntryLog(self, usernameLog, passwordLog):
        usernameLog.delete(0, END)
        passwordLog.delete(0, END)

    #*************************************_STERGE_ENTRY_REG_**************************************************#
    def stergeEntryReg(self, usernameReg, yourname, password2, conpassword):
        usernameReg.delete(0, END)
        yourname.delete(0, END)
        password2.delete(0, END)
        conpassword.delete(0, END)

    #*************************************_LOG_OUT_******************************************************#
    def logOut(self, Ecran_principal_frame1):
        self.raise_frame(Ecran_principal_frame1)
        mainMenu.OK_Log.destroy()
        mainMenu.NotOK_Log.destroy()

    #*************************************_QUIT_MESS_******************************************************#
    def quit_mess(self):
        mainMenu.App_Window_root.destroy()
        print('[GUI_COM][EXIT]:Aplicatie inchisa!')
        exit(0)
        
    #*************************************_SHOW_PASSWORD_FRAME2_******************************************************#
    def show_password_frame2(self):
        if self.fromLoginScreen.Checkbutton_frame2.var.get():
            self.fromLoginScreen.Entry_passwordLog_frame2['show'] = "*"
        else:
            self.fromLoginScreen.Entry_passwordLog_frame2['show'] = ""

    #*************************************_SHOW_PASSWORD_FRAME3_******************************************************#
    def show_password_frame3(self):
        if self.fromRegisterScreen.Checkbutton_frame3.var.get():
            self.fromRegisterScreen.Entry_passwordReg_frame3['show'] = "*"
            self.fromRegisterScreen.Entry_conpassword_frame3['show'] = "*"
        else:
            self.fromRegisterScreen.Entry_passwordReg_frame3['show'] = ""
            self.fromRegisterScreen.Entry_conpassword_frame3['show'] = ""

    #*************************************_SHOW_PASSWORD_FRAME4_******************************************************#
    def show_password_frame4(self):
        if self.fromChangePasswordScreen.Checkbutton_frame4.var.get():
            self.fromChangePasswordScreen.Entry_new_pass_frame4['show'] = "*"
            self.fromChangePasswordScreen.Entry_conf_new_pass_frame4['show'] = "*"
        else:
            self.fromChangePasswordScreen.Entry_new_pass_frame4['show'] = ""
            self.fromChangePasswordScreen.Entry_conf_new_pass_frame4['show'] = ""
        if self.fromChangePasswordScreen.Checkbutton_frame4.var.get():
            self.fromChangePasswordScreen.Entry_new_pass_frame4['show'] = "*"
            self.fromChangePasswordScreen.Entry_conf_new_pass_frame4 ['show'] = "*"
        else:
            self.fromChangePasswordScreen.Entry_new_pass_frame4['show'] = ""
            self.fromChangePasswordScreen.Entry_conf_new_pass_frame4 ['show'] = ""

#*************************************_GUI_Config_CLASS_**************************************************#
"""
    NOTE:
    Clasa GUI_Config este responsabila de configurarea interfetei grafice.
    Input: -
    Output: interfata grafica
    Functii: -
    Variabile: id, user, name, password_test1, password_test2, password, username_change_paswword, new_password, confirm_new_password, OK_Log, NotOK_Log, App_Window_root, Ecran_meniu_frame1, Ecran_login_frame2, Ecran_register_frame3, Ecran_chngpass_frame4
"""
class GUI_Config():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self):
        #*************************************_VARIABILE_******************************************************#
        self.id = ''
        self.user = ''
        self.name = ''
        self.password_test1 = ''
        self.password_test2 = ''
        self.password = ''
        self.username_change_paswword = ''
        self.new_password = ''
        self.confirm_new_password = ''
        
    #*************************************_LABELS_******************************************************#
        self.OK_Log = Label
        self.NotOK_Log = Label
        
    #*************************************_APP_WINDOW_ROOT_******************************************************#
        self.App_Window_root = tk.Tk()
        self.App_Window_root.title("Messenger App")
        ico = Image.open('icon_logo.ico')#logo sus bara
        photo = ImageTk.PhotoImage(ico)
        self.App_Window_root.wm_iconphoto(False, photo)
        self.App_Window_root.geometry('600x700')
        self.App_Window_root.configure( bg = 'grey')
        self.App_Window_root.resizable(False, False)
        self.App_Window_root.attributes('-alpha',0.99)
        self.Ecran_meniu_frame1 = Frame(self.App_Window_root)
        self.Ecran_login_frame2 = Frame(self.App_Window_root)
        self.Ecran_register_frame3 = Frame(self.App_Window_root)
        self.Ecran_chngpass_frame4 = Frame(self.App_Window_root)
        
    #*************************************_GRID_******************************************************#
        for frame in (self.Ecran_meniu_frame1, self.Ecran_login_frame2, self.Ecran_register_frame3,self.Ecran_chngpass_frame4):
            frame.canvas = tk.Canvas(self.App_Window_root, width = 600 , height = 450, bg= 'gray')
            frame.canvas.grid(columnspan = 3 , rowspan= 5)
            frame.grid(row = 3, column =1, sticky='news')
            
    #*************************************_ICON_CONFIG_******************************************************#
        main_icon = Image.open('main_icon.png')
        main_icon = ImageTk.PhotoImage(main_icon)
        main_icon_label = Label(image = main_icon)
        main_icon_label.image = main_icon
        main_icon_label.grid( column= 1, row= 1)  
        
#*************************************_MAIN_SCREEN_CLASS_******************************************************# 
"""
    NOTE:
    Clasa Main_Screen este responsabila de ecranul principal al aplicatiei.
    Input: mainMenu, guiCommand
    Output: interfata grafica
    Functii: -
    Variabile: Label_Welcome_frame1, Buton_Login_frame1, Buton_Register_frame1, Buton_Exit_frame1, Label_versiune_frame1
"""         
class Main_Screen():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self, mainMenu, guiCommand):
        self.mainMenu = mainMenu
        self.guiCommand = guiCommand
        self.dbConnection = SQL_Lite_Connect()
    #*************************************_Ecran_meniu_frame1_******************************************************#
        self.Label_Welcome_frame1 = Label(mainMenu.Ecran_meniu_frame1, text='Bun venit pe Messenger !', font=('consolas', 12))
        self.Label_Welcome_frame1.pack(padx=20, pady=5)
    #------------------------------------------------------------------------------------#
        self.Buton_Login_frame1 = Button(mainMenu.Ecran_meniu_frame1, text="Login",
                                    font=('consolas', 12), activebackground='light green',
                                    bg='light gray',
                                    height=2, width=18,
                                    command=lambda: guiCommand.raise_frame(mainMenu.Ecran_login_frame2))
        self.Buton_Login_frame1.pack(padx=20, pady=5)
    #------------------------------------------------------------------------------------#
        self.Buton_Register_frame1 = Button(mainMenu.Ecran_meniu_frame1, text="Register",
                                    font=('consolas', 12), activebackground='light green',
                                    bg='light gray',
                                    height=2, width=18,
                                    command=lambda: guiCommand.raise_frame(mainMenu.Ecran_register_frame3))
        self.Buton_Register_frame1.pack(padx=20, pady=5)
    #------------------------------------------------------------------------------------#
        self.Buton_Exit_frame1 = Button(mainMenu.Ecran_meniu_frame1, text="EXIT",
                                font=('consolas', 12), activebackground='red',
                                bg='light gray',
                                height=2, width=18, command=lambda: guiCommand.quit_mess())
        self.Buton_Exit_frame1.pack(padx=20, pady=5)
    #------------------------------------------------------------------------------------#
        self.Label_versiune_frame1 = Label(mainMenu.Ecran_meniu_frame1,
                                    text='Messenger vers. 1.0  1/10/2023',
                                    font=('consolas', 12), fg='blue')
        self.Label_versiune_frame1.pack(padx=20, pady=140)

#*************************************_LOGIN_SCREEN_CLASS_******************************************************#
"""
    NOTE:
    Clasa Login_Screen este responsabila de ecranul de login al aplicatiei.
    Input: mainMenu, guiCommand
    Output: interfata grafica   
    Functii: autentificare, login
    Variabile: Label_usernameLog_frame2, Entry_usernameLog_frame2, Label_passwordLog_frame2, Entry_passwordLog_frame2, Checkbutton_frame2, Label_Obligatoriu_frame2, Buton_link_frame2, Buton_Confirm_Login_frame2, Buton_Return_frame2
"""
class Login_Screen():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self, mainMenu, guiCommand):
        self.mainMenu = mainMenu
        self.guiCommand = guiCommand
        self.dbConnection = SQL_Lite_Connect()
        self.dbConnection.db_connection()
        #------------------------------------------------------------------------------------#
        self.Label_usernameLog_frame2 = Label(mainMenu.Ecran_login_frame2,  # type: ignore
                                        text='Enter Username*',
                                        font=('consolas', 12))
        self.Label_usernameLog_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_usernameLog_frame2 = Entry(mainMenu.Ecran_login_frame2, # type: ignore
                                        textvariable='',
                                        font=('consolas', 12))
        self.Entry_usernameLog_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_passwordLog_frame2 = Label(mainMenu.Ecran_login_frame2, # type: ignore
                                        text='Enter Password*', 
                                        font=('consolas', 12))
        self.Label_passwordLog_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_passwordLog_frame2 = Entry(mainMenu.Ecran_login_frame2,# type: ignore
                                        textvariable='', show='*',
                                        font=('consolas', 12))
        self.Entry_passwordLog_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Checkbutton_frame2 = Checkbutton(mainMenu.Ecran_login_frame2,# type: ignore
                                        text='Show/hide password',
                                        onvalue=False, offvalue=True,
                                        command=guiCommand.show_password_frame2)
        self.Checkbutton_frame2.var = tk.BooleanVar(value=True)
        self.Checkbutton_frame2['variable'] = self.Checkbutton_frame2.var
        self.Checkbutton_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_Obligatoriu_frame2 = Label(mainMenu.Ecran_login_frame2,# type: ignore
                                        text='Fields with * are mandatory',
                                        font=('consolas', 8), fg='red')
        self.Label_Obligatoriu_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Buton_link_frame2 = Button(mainMenu.Ecran_login_frame2, text="Forgot password?",# type: ignore
                                font=('consolas', 8), activebackground='light blue',
                                bg='light gray',
                                fg='blue', height=2, width=18,
                                command=lambda: guiCommand.raise_frame(mainMenu.Ecran_chngpass_frame4))
        self.Buton_link_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Buton_Confirm_Login_frame2 = Button(mainMenu.Ecran_login_frame2, text="Login", font=('consolas', 12),# type: ignore
                                            activebackground='light green', bg='light gray',
                                            height=2, width=18,
                                            command=lambda: self.login())
        self.Buton_Confirm_Login_frame2.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Buton_Return_frame2 = Button(mainMenu.Ecran_login_frame2, text="Back",# type: ignore
                                    font=('consolas', 12),
                                    activebackground='red', bg='light gray',
                                    height=2, width=18, command=lambda: guiCommand.raise_frame(mainMenu.Ecran_meniu_frame1))
        self.Buton_Return_frame2.pack(padx=20, pady=5)
    
    #*************************************_AUTENTIFICARE_******************************************************#
    '''
        NOTE: Functia autentificare: username, password -> select * from users where user = username and password = password
    '''
    def autentificare(self,username, password):
        self.dbConnection.cursor_users.execute(f"select * from users where user = '{username}' and password = '{password}'")
        user = self.dbConnection.cursor_users.fetchall()
        return user

    #*************************************_LOGIN_******************************************************#
    '''
        NOTE: Functia login: username, password -> autentificare(username, password)
    '''
    def login(self):
        user = self.Entry_usernameLog_frame2.get()
        print('[LOGIN][INFO]:User: ' + str(user))
        
        password = self.Entry_passwordLog_frame2.get()
        print('[LOGIN][INFO]:Password: ' + str(password))

        user_data = self.autentificare(user, password)

        if len(user_data) == 1:
            Client_Messenger(HOST, PORT, self.mainMenu, self.guiCommand, user)
            ID = user_data[0][0]
            welcome = str(mainMenu.userName.get(user))

            print('[LOGIN][PASSED]:: *Logged in successfully!')
            print('[LOGIN][INFO]:: *ID:' + str(ID) + 'NAME: ' + str(welcome) + '.')

            Label_OK_log_frame2 = Label(mainMenu.Ecran_login_frame2,
                                        text='OK te-ai logat cu succes!',
                                        font='consolas', bg='light green')
            Label_OK_log_frame2.pack()

            notification.notify(title='Messenger',
                                message=f'User {user}, conectat!',
                                timeout=5)

            self.guiCommand.stergeEntryLog(self.Entry_usernameLog_frame2, self.Entry_passwordLog_frame2)
        else:
            print('[LOGIN][FAILED]:<!Wrong password or user does not exists!>')
            print('[LOGIN][FAILED]:<!Repetati logarea in aplicatie!>')
 
            Label_NotOK_log_frame2 = Label(mainMenu.Ecran_login_frame2,
                                        text='Wrong password or user does not exists!',
                                        font='consolas', bg='red')
            Label_NotOK_log_frame2.pack()
     
     
#*************************************_REGISTER_SCREEN_CLASS_******************************************************#
"""
    NOTE:
    Clasa Regsiter_Screen este responsabila de ecranul de inregistrare al aplicatiei.
    Input: mainMenu, guiCommand
    Output: interfata grafica
    Functii: register
    Variabile: Label_usernameReg_frame3, Entry_usernameReg_frame3, Label_yourname_frame3, Entry_yourname_frame3, Label_passwordReg_frame3, Entry_passwordReg_frame3, Label_conpassword_frame3, Entry_conpassword_frame3, Checkbutton_frame3, Checkbutton_TrmsCondt_frame3, Label_Obligatoriu_frame3, Buton_Confirm_Reg_frame3, Buton_Return_frame3
"""       
class Regsiter_Screen():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self, mainMenu, guiCommand):
        self.mainMenu = mainMenu
        self.guiCommand = guiCommand
        self.dbConnection = SQL_Lite_Connect()
        self.dbConnection.db_connection()
        #------------------------------------------------------------------------------------#
        self.Label_usernameReg_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='Enter a username*',
                                        font=('consolas', 12))
        self.Label_usernameReg_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_usernameReg_frame3 = Entry(mainMenu.Ecran_register_frame3,
                                        textvariable='',
                                        font=('consolas', 12))
        self.Entry_usernameReg_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_yourname_frame3 = Label(mainMenu.Ecran_register_frame3,
                                    text='Enter your name*',
                                    font=('consolas', 12))
        self.Label_yourname_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_yourname_frame3 = Entry(mainMenu.Ecran_register_frame3,
                                    textvariable='',
                                    font=('consolas', 12))
        self.Entry_yourname_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_passwordReg_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='Choose a password*',
                                        font=('consolas', 12))
        self.Label_passwordReg_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_passwordReg_frame3 = Entry(mainMenu.Ecran_register_frame3,
                                        textvariable='', show='*',
                                        font=('consolas', 12))
        self.Entry_passwordReg_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_conpassword_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='Confirm your password*',
                                        font=('consolas', 12))
        self.Label_conpassword_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Entry_conpassword_frame3 = Entry(mainMenu.Ecran_register_frame3, textvariable='',
                                        show='*', font=('consolas', 12))
        self.Entry_conpassword_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Checkbutton_frame3 = Checkbutton(mainMenu.Ecran_register_frame3,
                                        text='Show/hide password',
                                        onvalue=False, offvalue=True,
                                        command= guiCommand.show_password_frame3)
        self.Checkbutton_frame3.var = tk.BooleanVar(value=True)
        self.Checkbutton_frame3['variable'] = self.Checkbutton_frame3.var
        self.Checkbutton_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Checkbutton_TrmsCondt_frame3 = Checkbutton(mainMenu.Ecran_register_frame3,
                                                text='Accept terms and conditions*',
                                                onvalue=False, offvalue=True)
        self.Checkbutton_TrmsCondt_frame3.var = tk.BooleanVar(value=True)
        self.Checkbutton_TrmsCondt_frame3['variable'] = self.Checkbutton_TrmsCondt_frame3.var
        self.Checkbutton_TrmsCondt_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Label_Obligatoriu_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='Fields with * are mandatory',
                                        font=('consolas', 8), fg='red')
        self.Label_Obligatoriu_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Buton_Confirm_Reg_frame3 = Button(mainMenu.Ecran_register_frame3, text="Register",
                                        font=('consolas', 12),
                                        activebackground='light green', bg='light gray',
                                        height=2, width=18,
                                        command=lambda: self.register())
        self.Buton_Confirm_Reg_frame3.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        self.Buton_Return_frame3 = Button(mainMenu.Ecran_register_frame3, text="Back",
                                    font=('consolas', 12),
                                    activebackground='red', bg='light gray',
                                    height=2, width=18,
                                    command=lambda: guiCommand.raise_frame(mainMenu.Ecran_meniu_frame1))
        self.Buton_Return_frame3.pack(padx=20, pady=5)
       
    #*************************************_REGISTER_******************************************************#
    '''
        NOTE: Functia register: username, name, password_test1, password_test2 -> insert into users (user, name, password) values (username, name, password)
    ''' 
    def register(self):
        # Generare ID automat
        id = random.randint(0, 100)  # Poți elimina această linie dacă ID-ul este autoincrementat în baza de date
        user = self.Entry_usernameReg_frame3.get()
        name = self.Entry_yourname_frame3.get()
        password_test1 = self.Entry_passwordReg_frame3.get()
        password_test2 = self.Entry_conpassword_frame3.get()

        # Verificare dacă utilizatorul există deja în baza de date
        self.dbConnection.cursor.execute('SELECT * FROM users WHERE user = ?', (user,))
        user_exists = dbConnection.cursor.fetchone()

        if password_test1 == password_test2 and not user_exists and password_test1 != '' and password_test2 != '' and user != '' and name != '' and self.Checkbutton_TrmsCondt_frame3.var.get() == False:
            self.dbConnection.cursor.execute('INSERT INTO users (user, name, password) VALUES (?, ?, ?)', (user, name, password_test2))
            self.dbConnection.connection.commit()
            print(f'[REGISTER][PASSED]:S-a creat un cont cu Username:<{user}> Parola:<{password_test2}> si ID-ul:<{id}>!')


            Label_OK_Reg_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='S-a creat un cont cu succes!',
                                        font='consolas', bg='light green')
            Label_OK_Reg_frame3.pack()

            notification.notify(title='Messenger',
                                message=f'User {user}, ti-ai creat cont!',
                                timeout=5)

            guiCommand.stergeEntryReg(self.Entry_usernameReg_frame3, self.Entry_yourname_frame3, self.Entry_passwordReg_frame3, self.Entry_conpassword_frame3)
            return self.dbConnection.cursor.lastrowid  # Poți elimina această linie dacă nu ai nevoie de ID-ul returnat

        else:
            print('REGISTER][FAILED]:<!Password mismatch or user already exists!>')
            print('REGISTER][FAILED]:<!Repetati inregistrarea in aplicatie!>')

            Label_NotOK_Reg_frame3 = Label(mainMenu.Ecran_register_frame3,
                                        text='Password mismatch or user already exists!',
                                        font='consolas', bg='red')
            Label_NotOK_Reg_frame3.pack()
      
#*************************************_CHANGE_PASSWORD_SCREEN_CLASS_******************************************************#
"""
    NOTE:
    Clasa Change_Password_Screen este responsabila de ecranul de schimbare a parolei al aplicatiei.
    Input: mainMenu, guiCommand
    Output: interfata grafica
    Functii: change_password
    Variabile: Label_new_pass_title_frame4, Label_username_frame4, Entry_username_frame4, Label_new_pass_frame4, Entry_new_pass_frame4, Label_conf_new_pass_frame4, Entry_conf_new_pass_frame4, Checkbutton_frame4, Label_Obligatoriu_frame4, Buton_chng_pass_frame4, Buton_Return_frame4
"""      
class Change_Password_Screen():
    #*************************************_CONSTRUCTOR_******************************************************#
    def __init__(self, mainMenu, guiCommand):
        self.mainMenu = mainMenu
        self.guiCommand = guiCommand
        self.dbConnection = SQL_Lite_Connect()
        self.dbConnection.db_connection()
        #------------------------------------------------------------------------------------#
        Label_new_pass_title_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                            text='Change your password',
                                            font=('consolas', 14), bg='light gray')
        Label_new_pass_title_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Label_username_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                    text='Your username*',
                                    font=('consolas', 8), bg='light gray')
        Label_username_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Entry_username_frame4 = Entry(mainMenu.Ecran_chngpass_frame4, textvariable='',
                                    font=('consolas', 12))
        Entry_username_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Label_new_pass_frame4 = Label(mainMenu.Ecran_chngpass_frame4, text='Type new password*',
                                    font=('consolas', 8), bg='light gray')
        Label_new_pass_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Entry_new_pass_frame4 = Entry(mainMenu.Ecran_chngpass_frame4, textvariable='', show='*',
                                    font=('consolas', 12))
        Entry_new_pass_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Label_conf_new_pass_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                        text='Please confirm your password*',
                                        font=('consolas', 8), bg='light gray')
        Label_conf_new_pass_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Entry_conf_new_pass_frame4 = Entry(mainMenu.Ecran_chngpass_frame4, textvariable='',
                                        show='*', font=('consolas', 12))
        Entry_conf_new_pass_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Checkbutton_frame4 = Checkbutton(mainMenu.Ecran_chngpass_frame4,
                                        text='Show/hide password', onvalue=False,
                                        offvalue=True, command= guiCommand.show_password_frame4)
        Checkbutton_frame4.var = tk.BooleanVar(value=True)
        Checkbutton_frame4['variable'] = Checkbutton_frame4.var
        Checkbutton_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Label_Obligatoriu_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                        text='Fields with * are mandatory',
                                        font=('consolas', 8), fg='red')
        Label_Obligatoriu_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Buton_chng_pass_frame4 = Button(mainMenu.Ecran_chngpass_frame4, text="Change Password",
                                        font=('consolas', 12),
                                        activebackground='light green', bg='light gray',
                                        height=2, width=18,
                                        command=lambda: self.change_password(mainMenu.username_change_paswword, mainMenu.new_password, mainMenu.confirm_new_password))
        Buton_chng_pass_frame4.pack(padx=20, pady=5)
        #------------------------------------------------------------------------------------#
        Buton_Return_frame4 = Button(mainMenu.Ecran_chngpass_frame4, text="Back", font=('consolas', 8),
                                    activebackground='red', bg='light gray',
                                    height=2, width=18,
                                    command=lambda: guiCommand.raise_frame(mainMenu.Ecran_meniu_frame1))
        Buton_Return_frame4.pack(padx=20, pady=5)
    
    #*************************************_CHANGE_PASSWORD_******************************************************#
    '''
        NOTE: Functia change_password: username_change_password, new_password, confirm_new_password -> select * from users where user = username_change_password
    '''
    def change_password(self,username_change_password, new_password, confirm_new_password):
        username_change_password = self.Entry_username_frame4.get()
        if username_change_password != '':
            new_password = self.Entry_new_pass_frame4.get()
            confirm_new_password = self.Entry_conf_new_pass_frame4.get()

            if new_password == confirm_new_password:
                print('[CHNG_PASS][PASSED]: New passwords match <OK>')

                for attempt in range(5):  # Retry up to 5 times
                    try:
                        with sqlite3.connect("USERS.db") as connection:
                            cursor = connection.cursor()

                            print('[CHNG_PASS][SQLLITE][PASSED]: Conectat la baza de date <OK>')

                            cursor.execute("SELECT * FROM users WHERE user = ?", (username_change_password,))
                            user_exists = cursor.fetchone()

                            if user_exists:
                                cursor.execute("UPDATE users SET password = ? WHERE user = ?", (new_password, username_change_password))
                                connection.commit()

                                print('[CHNG_PASS][SQLLITE][PASSED]: Parola a fost inlocuita in baza de date <OK>')
                                print(f"->New password: {new_password}, for user: {username_change_password}.")
                                print('\n')

                                Label_OK_new_password_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                                                    text=f'Parola schimbata({new_password})!',
                                                                    font=('consolas', 12), bg='light green')
                                Label_OK_new_password_frame4.pack(padx=20, pady=5)

                                notification.notify(title='Messenger',
                                                    message=f'User {username_change_password}, your password was changed!',
                                                    timeout=5)
                                break
                            else:
                                print('[CHNG_PASS][SQLLITE][FAILED]:Eroare la schimbarea parolei, username nu exista<!>')

                                Label_NotOK_new_password_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                                                        text='Eroare la schimbarea parolei, username nu exista!',
                                                                        font=('consolas', 12), bg='red')
                                Label_NotOK_new_password_frame4.pack(padx=20, pady=5)
                                break

                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e):
                            print('[CHNG_PASS][SQLLITE][ERROR]: Database is locked, retrying... <!>')
                            time.sleep(1)  # Wait for 1 second before retrying
                        else:
                            print('[CHNG_PASS][SQLLITE][FAILED]:Parola nu a fost inlocuita in baza de date <!>')
                            print(e)
                            print('\n')

                            Label_NotOK_new_password_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                                                    text='Parola nu a fost inlocuita in baza de date !',
                                                                    font=('consolas', 12), bg='red')
                            Label_NotOK_new_password_frame4.pack(padx=20, pady=5)
                            break

            else:
                print('[CHNG_PASS][FAILED]:Eroare la schimbarea parolei, parolele nu coincid <!>')

                Label_NotOK_new_password_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                                        text='Eroare la schimbarea parolei, parolele nu coincid !',
                                                        font=('consolas', 12), bg='red')
                Label_NotOK_new_password_frame4.pack(padx=20, pady=5)

        else:
            print('[CHNG_PASS][FAILED]:Eroare la schimbarea parolei, username nu exista<!>')

            Label_NotOK_new_password_frame4 = Label(mainMenu.Ecran_chngpass_frame4,
                                                    text='Eroare la schimbarea parolei, username nu exista !',
                                                    font=('consolas', 12), bg='red')
            Label_NotOK_new_password_frame4.pack(padx=20, pady=5)
    
    
    
#*************************************_MAIN_******************************************************#
'''
    NOTE: Functia main: dbConnection, mainMenu, guiCommand, guiMainScreen -> db_connection, raise_frame, stergeEntryLog, 
                                                                             stergeEntryReg, logOut, quit_mess, show_password_frame2, 
                                                                             show_password_frame3, show_password_frame4
'''
if __name__ == '__main__':
    db_con_flag = False
    try:
        dbConnection = SQL_Lite_Connect()
        test_con= dbConnection.db_connection()
        db_con_flag = True
        if test_con:
            print('[MAIN][SQLLITE][INFO]:Conectare la baza de date <OK>')
        else:
            print('[MAIN][SQLLITE][ERROR]:Conectare la baza de date <FAILED>')
            time.sleep(2)
            for i in range(5):
                print(f'[MAIN][SQLLITE][INFO]:Incercare de reconectare la baza de date {i}...')
                con_res = dbConnection.db_connection
            if not con_res:
                print('[MAIN][SQLLITE][ERROR]:Nu s-a putut realiza conectarea la baza de date <FAILED>')
                print('[MAIN][ERROR]:Aplicatia nu a putut porni!')
                dbConnection.connection.close()
                exit(1)
                
        if db_con_flag:
            menu_init = mainMenu = GUI_Config()
            menu_command = guiCommand = GUI_Commands(mainMenu)
            if menu_init and menu_command:
                guiMainScreen = Main_Screen(mainMenu, guiCommand)
                guiCommand.raise_frame(mainMenu.Ecran_meniu_frame1)
                mainMenu.App_Window_root.mainloop()
                print('--> vers. Tkinter: ' + tk.Tcl().eval('info patchlevel'))
                print ('[MAIN][INFO]:Aplicatie pornita cu succes!')
            else:
                print('[MAIN][ERROR]:Aplicatia nu a putut porni!')
                dbConnection.connection.close()
                exit(1)
                
    except Error as e:
        print(f"[MAIN][SQLLITE][ERROR]:Eroare la conectare cu baza de date {e}<!>")
        print('[MAIN][ERROR]:Aplicatia nu a putut porni!')
        dbConnection.connection.close()
        threading.Thread(target=sys.exit, args=(1,)).start()   # Create a thread that calls sys.exit(1)
        exit(1)
        
    finally:
        dbConnection.connection.close()
        print('[MAIN][ERROR]:Aplicatia nu a putut porni!')
        exit(1)
        