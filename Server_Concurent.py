#****************************************************************************************************************#
#
# Filename: Server_Concurent.py
# Description: Serverul Messenger care permite comunicarea intre clienti prin intermediul unui server concurent TCP/IP 
# Author: Codreanu Dan
#
#
#****************************************************************************************************************#
############################################################################################################################################################################
#|                                                                        IMPORT AREA                                                                                      |            
############################################################################################################################################################################
import socket                                                          
import threading                                                       
import sqlite3
from sqlite3 import Error
from datetime import datetime

############################################################################################################################################################################
#|                                                                        SERVER CLASS                                                                                     |            
############################################################################################################################################################################
class ServerBroadcastService:
    
#****************************************************************************************************************************************************************************#
#|                                                                        CONSTRUCTOR                                                                                        |
#****************************************************************************************************************************************************************************#
    def __init__(self):                                                     # Constructorul clasei ServerBroadcastService
        self.lista_clienti = []                                             # Lista de clienti (IP+port) 
        self.lista_nume_clienti = []                                        # Lista de useri --> aici vine username-ul din login din Messenger
        self.threads = []                                                   # Lista de thread-uri, pentru a stoca thread-urile active
        self.running = True                                                 # Variabila de control daca ruleaza serverul sau nu
        self.init_server()                                                  # Functie de initializare server si conexiune la baza de date
        self.start_server()                                                 # Functie de start server

#****************************************************************************************************************************************************************************#
#|                                                                            METODE                                                                                         |
#****************************************************************************************************************************************************************************#

#*************************************************************************_GET_IP_ADDRESS_***********************************************************************************#
    def get_IPAddr(self):                                                   # Functie pentru a obtine adresa IP a serverului
        self.hostname=socket.gethostname()                                  # Numele calculatorului
        self.IPAddr=socket.gethostbyname(socket.gethostname())              # Adresa IP a calculatorului
        print("Your Computer Name is:"+self.hostname)   
        print("Your Computer IP Address is:"+self.IPAddr) 

#*************************************************************************_SERVER_INIT_**************************************************************************************#
    def init_server(self):                                                   # Initializare server si conexiune la baza de date
       
        self.get_IPAddr()
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Tipul de socket : request handler, TCP 
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     # Setare optiuni socket, pentru a putea reutiliza portul
            self.s.bind((str(self.IPAddr), 1234))                            # IP-ul meu local de pe care ruleaza serverul si portul 1234 pentru conexiune TCP 
            self.s.listen(5)                                                 # Serverul poate accepta maxim 5 conexiuni in acelasi timp
            print('<OK>Server Messenger a pornit!<OK>\n')
        except Exception as e:
            print('<!>Serverul nu a pornit<!>')
            self.running = False                                             # Daca serverul nu a pornit, se opreste
            print(e)
            return

        try:
            self.connection = sqlite3.connect("D:\\VS_Code\\Codreanu Dan 6304(Messenger) - retea\\Chat_History.db", check_same_thread=False) # Conectare la baza de date Chat_History.db
            self.cursor = self.connection.cursor()                                                                                           # Cursor pentru a executa comenzi SQL
            self.cursor.execute('SELECT * FROM chat;')
            print('<OK> Conexiune cu baza de data realizata! <OK>\n')                                                                   
        except Error as e:
            print('<!> Eroare de conectare la baza de date! <!>')
            print(e)
            return

#*************************************************************************_COMUNICARE_GLOBALA_******************************************************************************#
    def comunicare_globala(self,mesaj):                                                                                                # Un user trimite mesaj si ceilalti useri recepteaza mesajul 
        
        for client in self.lista_clienti:                                                                                              # Pentru fiecare client din lista de clienti
            try:
                client.send(mesaj)                                                                                                     # Trimite mesajul la toti clientii conectati la server
            except Exception as e:
                print(f"Eroare la trimiterea mesajului catre clinetul:  {client}: {e}")                                                             

#************************************************************************_MANAGE_CLIENT_***********************************************************************************#
    def manageClient(self,client):                                                                                                     # Functie de tratare a clientilor conectati la server
        
        while True:                                                                                                                    # Bucla infinita pentru a trata clientii conectati la server
            try:
                mesaj = client.recv(1024)                                                                                              # Primeste mesaj de la client cu dimensiunea de 1024 bytes
                if not mesaj:                                                                                                          # Daca mesajul este gol, iese din bucla
                    break

                time = datetime.now()                                                                                                  # Data si ora curenta
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")                                                                    # Formatarea datei si orei
                print(f'({formatted_time}) Utilizator {self.lista_nume_clienti[self.lista_clienti.index(client)]}: {mesaj.decode("utf-8")}')
                self.comunicare_globala(mesaj)                                                                                         # Mesajul este afisat la toti utilizatorii

                try:
                    self.cursor.execute('INSERT INTO chat VALUES(?)', (mesaj.decode("utf-8"),))                                        # Inserare mesaj in baza de date
                    self.connection.commit()                                                                                           # Salvare mesaj in baza de date
                    print('-> <OK>Mesajul s-a salvat in baza de date<OK>\n')
                    
                except Error as e:
                    print('-> <!> Eroare la inserarea datelor! <!>')
                    print(e)
                    print('\n')
                    
            except Exception as e:                                                                                                     # Daca cineva are vreo eroare este deconectat si sters lista de clienti
                
                eroare = self.lista_clienti.index(client)
                username_cu_eroare = self.lista_nume_clienti[eroare]                                                                   # Username-ul clientului cu eroare
                self.lista_clienti.remove(client)                                                                                      # Sterge clientul din lista de clienti
                self.lista_nume_clienti.remove(username_cu_eroare)                                                                     # Sterge username-ul clientului din lista de username-uri
                client.close()                                                                                                         # Inchide conexiunea cu clientul
    
                time = datetime.now()
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f'Client: {client}, ({username_cu_eroare}) a avut o eroare si a iesit ori s-a deconectat! ({formatted_time}).\n')
                break

#*************************************************************************_SERVER_STOP_*************************************************************************************#
    def stop_server(self):                                                                                                             # Functie de oprire server
         
        self.running = False                                                                                                           # Seteaza variabila de control a serverului pe False
        self.s.close()                                                                                                                 # Opresre socket-ul serverului pentru a nu mai accepta conexiuni
        for client in self.lista_clienti:
            client.close()  # Inchide conexiunea cu toti clientii
        for thread in self.threads:
            thread.join()                                                                                                              # Asteapta ca toate thread-urile sa se opreasca
        self.connection.close()                                                                                                        # Inchide conexiunea cu baza de date
        print("Server oprit!.")

#*************************************************************************_SERVER_START_***********************************************************************************#
    def start_server(self):                                                                                                            # Functie de start server
        
        try:
            while self.running:                                                                                                        # Bucla infinita pentru a accepta clienti
                client, address = self.s.accept()                                                                                      # Accepta conexiunea de la client
                client.send('NAME'.encode('utf-8'))                                                                                    # Cer username de la client pentru a-l adauga in lista de username-uri
                nume_in_aplicatie = client.recv(1024).decode('utf-8')                                                                  # Primeste username-ul de la client
                 
                self.lista_nume_clienti.append(nume_in_aplicatie)                                                                      # Adauga username-ul in lista de username-uri
                self.lista_clienti.append(client)                                                                                      # Adauga clientul in lista de clienti

                time = datetime.now()
                formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
                print(f'-> S-a conectat user cu adresa: {address} si username: {nume_in_aplicatie}. ({formatted_time})\n')

                self.comunicare_globala((f'{nume_in_aplicatie} s-a alautarat chat-ului 🤗 ! ({formatted_time}) \n').encode('utf-8'))      
                self.comunicare_globala((f'Salut, {nume_in_aplicatie}!\n').encode('utf-8'))

                self.t1 = threading.Thread(target= self.manageClient, args=(client,))                                                  # Thread pentru a trata clientul conectat la server
                self.t1.start()                                                                                                        # Porneste thread-ul
                self.threads.append(self.t1)                                                                                           # Adauga thread-ul in lista de thread-uri
        
        except Exception as e:                                                                                                         # Exceptie in caz de eroare la pornirea serverului
                print(f"Eroare la la pornirea serverlui: {e}")
        finally:
            if self.running:                                                                                                           # Daca serverul ruleaza 
                self.stop_server()                                                                                                     # Opreste serverul

############################################################################################################################################################################
#|                                                                        MAIN AREA                                                                                        |
############################################################################################################################################################################
if __name__ == "__main__":
     server_instance = ServerBroadcastService()                                                                                        # Instantierea clasei server_broadcast_service pentru a porni serverul
     