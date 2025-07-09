import tkinter as tk
import random
from tkinter import messagebox
from tkinter import ttk
from pymongo import MongoClient, ASCENDING, DESCENDING
#from extra.redefinir_banco import redefinir_banco
from datetime import datetime, timedelta
import serial
import time
from requests import post
from threading import Thread, Timer

##infos para o telegram e o widget :
chave = "7942492796:AAHtr3uc3wb7OGEu6krMUnqDcUtaArqS714"
endereco_base = "https://api.telegram.org/bot" + chave
# url_do_macrobot = "https://trigger.macrodroid.com/fadfdd5c-a124-4e7a-88be-630601394a11/smartcup_puc_rio"

#redefinir_banco()

# Conexão com a serial do ser
porta = "COM10"
baud_rate = 9600
time.sleep(2)

try:
    # Inicializa a comunicação serial
    ser = serial.Serial(porta, 9600, timeout=2)
    print("Conectado à porta", porta)
except serial.SerialException as e:
    print("Erro ao conectar à porta serial do leitor de tag: ", e)
    exit()

#redefinir_banco()

#cliente = MongoClient("localhost", 27017)		#para se tiver sem internete / o servidor n estiver funcionando (n vai ter os dados atualizados)
#banco = cliente["SmartCup"]
#colecao_de_usuarios = banco["usuarios"]

try:
    cliente = MongoClient("mongodb+srv://testes:1234@cluster0.pychheh.mongodb.net/")
    print("Conectado ao banco de dados")
    banco = cliente["SmartCup"]
    colecao_de_usuarios = banco["usuarios"]
except:
    print("Erro ao conectar ao banco de dados")
    exit()

print("Aguardando leitura do arduino...")

usuario1 = {"nome": "Léna", "meta": "2000", "idchats": "id1", "tara": 148, "idtag": "d0a04a10", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [1,2,0.6, 2.1,1.8], "cor": "0"}
usuario2 = {"nome": "Pablo", "meta": "1000", "idchats": "id2",  "tara": 104, "idtag": "e0e09513", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [1,5,1.6, 2.1,1.8], "cor": "2"}
usuario3 = {"nome": "Mathias", "meta": "1500", "idchats": "id3",  "tara": 99, "idtag": "e0ad4613", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [1,2,1.6, 2.1,1.3], "cor": "1"}
usuario4 = {"nome": "Anna", "meta": "2000", "idchats": "id4", "tara": 148, "idtag": "05F9", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [1,2,1.6, 18,1.8], "cor": "3"}
usuario5 = {"nome": "Alessandra", "meta": "1000", "idchats": "id5",  "tara": 104, "idtag": "05F5", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [1,2,1.6, 2.1,0.8], "cor": "4"}
usuario6 = {"nome": "Gustavo", "meta": "1500", "idchats": "id6",  "tara": 99, "idtag": "05F3", "ultimo_peso": 178, "streak": 0, "dias": [datetime(2025, 6, 5),datetime(2025, 6, 6), datetime(2025, 6, 7), datetime(2025, 6, 8), datetime(2025, 6, 9)], "volume": [0.7,2,1.6, 2.7,1.8], "cor": "5"}

cores = ["Vermelho", "Verde", "Azul", "Amarelo", "Rosa", "Laranja", "Branco"]

#tests iniciais
#lista_usuarios = [usuario1, usuario2,usuario3, usuario4, usuario5, usuario6]
# 
#  
#for usuario in lista_usuarios :
#    colecao_de_usuarios.insert_one(usuario)


def alertaTelegram():
    
    endereco = endereco_base + "/sendMessage"
    
    dado_da_busca = {} #todos os usuarios
    usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca) )
    
    for usuario in usuarios_atuais :
        
        streak = usuario["streak"]
        id_da_conversa = usuario["idchats"]
        litros_objetivo = float(usuario["meta"])
        litros_objetivo = round(litros_objetivo, 2)
        ml_bebidas = float(usuario["volume"][-1])
        ml_bebidas = round(ml_bebidas, 2)
        diferenca = round((litros_objetivo-ml_bebidas) , 2)
        
        if (ml_bebidas < litros_objetivo):
            if streak == 0 :
                dados1 = {"chat_id": id_da_conversa, "text": f" 💧Ei, hidratado ou desidratado? 💧\nVocê já bebeu {ml_bebidas/1000}L de água hoje.\nMeta do dia: {litros_objetivo/1000}L.\nFalta só {diferenca}mL pra virar um aquário ambulante! 🐠🥤"}
            else :
                dados1 = {"chat_id": id_da_conversa, "text": f" 💧Ei, hidratado ou desidratado? 💧\nVocê já bebeu {ml_bebidas/1000}L de água hoje.\nMeta do dia: {litros_objetivo/1000}L.\nFalta só {diferenca}mL pra virar um aquário ambulante! 🐠🥤\n🔥 Bora manter a chama viva!🔥"}
                
        else:
            if streak == 0 :
                dados1 = {"chat_id": id_da_conversa, "text": f"🎉 Parabéns! Você já bebeu {ml_bebidas/1000}L de água hoje — missão cumprida!\nMeta do dia: {litros_objetivo/1000}L."}
            elif streak == 1 :
                dados1 = {"chat_id": id_da_conversa, "text": f"🎉 Parabéns! Você já bebeu {ml_bebidas/1000}L de água hoje — missão cumprida!\nMeta do dia: {litros_objetivo/1000}L.\n🔥 Sua rotina de bons goles segue firme há {streak} dia! Bora manter a chama viva! 💪"}
            else :
                dados1 = {"chat_id": id_da_conversa, "text": f"🎉 Parabéns! Você já bebeu {ml_bebidas/1000}L de água hoje — missão cumprida!\nMeta do dia: {litros_objetivo/1000}L.\n🔥 Sua rotina de bons goles segue firme há {streak} dias! Bora manter a chama viva! 💪"}
        resp1 = post(endereco, json=dados1)

def verif_streak() : 
    dado_da_busca = { "idtag": { "$ne": "" } } #todos os usuarios
    usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca))
    for usuario in usuarios_atuais :  
        if float(usuario["volume"][-1]) >= float(usuario["meta"]):
            nouveau = int(usuario["streak"]) + 1
        else :
            nouveau = 0
        dado_modif = { "idtag": usuario["idtag"] }
        novo_dados = {"$set": {"streak": nouveau}}
        colecao_de_usuarios.update_one(dado_modif, novo_dados)


def ajouter_jour() : 
    dado_da_busca = { "idtag": { "$ne": "" } } #todos os usuarios
    usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca))
    for usuario in usuarios_atuais :
        liste_jour = usuario["dias"]
        liste_volume = usuario["volume"].append(0)
        
        liste_jour.append(datetime.now())
        liste_volume.append(0)
        
        dado_modif = { "dias": usuario["dias"] }
        novo_dados = {"$set": {"dias": liste_jour}}
        colecao_de_usuarios.update_one(dado_modif, novo_dados)
        
        dado_modif = { "volume": usuario["volume"] }
        novo_dados = {"$set": {"volume": liste_volume}}
        colecao_de_usuarios.update_one(dado_modif, novo_dados)
    
def atualizaWidget() :
    
    dado_da_busca = { "urlwidget": { "$ne": "" } } #todos os usuarios
    usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca))

    for usuario in usuarios_atuais :
        print(usuario["nome"])
        streak = usuario["streak"]
        url_do_macrobot = usuario["urlwidget"]
        
    
        if (streak != 0):
            dados_macrobot = f"Parabens {streak} dias batendo a sua meta!"
        else:
            dados_macrobot = f"Voce deixou de fazer a sua meta... Mas hoje e um otimo dia para tentar novamente!"
    
        resp3 = post(url_do_macrobot, json=dados_macrobot)
    print("j'ai tout envoyé")

def verificacao_temporal_alerta():
    
    ##envoie une demande d'alerte sur telegram toutes les 2 heures
    while True : 
        instant = datetime.now()
        horaire = instant.strftime("%H:%M")
        heure = horaire[0:2]
        minute = horaire[3:5]
        
        if heure == "10" and minute == "00" :
            alertaTelegram()
        elif heure == "12" and minute == "00" : 
            alertaTelegram()
        elif heure == "14" and minute == "00" :
            alertaTelegram()
        elif heure == "17" and minute == "47" :
            alertaTelegram()
        elif heure == "18" and minute == "00" :
            alertaTelegram()
        elif heure == "20" and minute == "00" :
            alertaTelegram()
        elif heure == "23" and minute == "59" :
            verif_streak()
        elif heure == "00" and minute == "00" :
            ajouter_jour()
            atualizaWidget()
        time.sleep(60)

def test_tipo_float(entry):
    try:
        float(entry)
        return True
    except ValueError:
        return False

class JanelaInfo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cadastro do usuario")
        self.geometry("600x330")
        self.configure(bg="lightblue")

        label = tk.Label(self, text="Sistema de Cadastro", font=("Arial", 10))
        label.place(x=250,y=30)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="Nome :", font=("Arial", 10))
        label.place(x=150,y=60)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="Id chat telegram :", font=("Arial", 10))
        label.place(x=90,y=90)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="Meta diaria :", font=("Arial", 10))
        label.place(x=120,y=120)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Peso do copo :", font=("Arial", 10))
        label.place(x=104,y=150)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Tag do copo :", font=("Arial", 10))
        label.place(x=114,y=180)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Url do widget :", font=("Arial", 10))
        label.place(x=110,y=210)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Cor do LED :", font=("Arial", 10))
        label.place(x=117,y=240)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="L", font=("Arial", 10))
        label.place(x=445,y=120)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="g", font=("Arial", 10))
        label.place(x=445,y=150)
        label.configure(bg="lightblue", fg="midnight blue")

        self.Nome = tk.Entry(self, width=40)
        self.Nome.place(x=200,y=60)

        self.IdChat = tk.Entry(self, width=40)
        self.IdChat.place(x=200,y=90)

        self.Meta = tk.Entry(self, width=40)
        self.Meta.place(x=200,y=120)
        
        self.Peso = tk.Entry(self, width=40)
        self.Peso.place(x=200,y=150)

        self.Tag = tk.Entry(self, width=40)
        self.Tag.place(x=200,y=180)
        
        self.Url = tk.Entry(self, width=40)
        self.Url.insert(0, "https://trigger.macrodroid.com/fadfdd5c-a124-4e7a-88be-630601394a11/smartcup_puc_rio")
        self.Url.place(x=200,y=210)
        
        self.Cor = tk.StringVar()
        self.CorBox = ttk.Combobox(self, textvariable=self.Cor, values=cores)
        self.CorBox.place(x=200,y=240)
        
        botao = tk.Button(self, text="Auto")
        botao.place(x=475,y=150)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.medir_peso)
        
        botao = tk.Button(self, text="Auto")
        botao.place(x=475,y=180)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.ler_tag)

        botao = tk.Button(self, text="Seguir cadastro")
        botao.place(x=270,y=280)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.cadastrar_usuario)
    
    def cadastrar_usuario(self, event):
        NomeUsuario = self.Nome.get()
        MetaUsuario = self.Meta.get()
        IdChatUsuario = self.IdChat.get()
        PesoUsuario = self.Peso.get()
        TagUsuario = self.Tag.get()
        UrlUsuario = self.Url.get()
        CorUsuario = self.Cor.get()
        
        if not(NomeUsuario.strip()) or not(MetaUsuario.strip()) or not(IdChatUsuario.strip()) or not(PesoUsuario.strip()) or not(TagUsuario.strip()) or not(UrlUsuario.strip()) or not(CorUsuario.strip()):
            
            messagebox.showwarning("Atençao", "Você tem que recheiar tudo.")
            
        elif test_tipo_float(MetaUsuario) == False :
            
            messagebox.showwarning("Atençao", "A meta tem que ser um numero.")
        
        elif float(MetaUsuario) <= 0 :
            
            messagebox.showwarning("Atençao", "A meta tem que ser maior que 0.")
            
        else:
            numero_cor = cores.index(CorUsuario)
            usuario = {"nome": f"{NomeUsuario}", "cor": f"{numero_cor}", "meta": f"{float(MetaUsuario)*1000}", "idchats": f"{IdChatUsuario}", "tara": f"{PesoUsuario}", "idtag": f"{TagUsuario}", "ultimo_peso": 0, "streak": 0, "dias": [datetime.now()], "volume": [0], "urlwidget": f"{UrlUsuario}"}
            colecao_de_usuarios.insert_one(usuario)
            self.destroy()
            app = JanelaRecepcao()
            app.mainloop()
            
            
    def ler_tag(self, event):
        
        self.janela_espera = tk.Toplevel(self)          # nueva ventana
        self.janela_espera.title("Janela de espera")
        self.janela_espera.geometry("600x300")
        self.janela_espera.configure(bg="lightblue")
        
        label = tk.Label(self.janela_espera, text="Procurando o seu tag ...", font=("Arial", 12))
        label.place(x=230,y=110)
        label.configure(bg="lightblue", fg="midnight blue")
        
        self.progress = ttk.Progressbar(self.janela_espera, value=0)
        self.progress.place(x=260,y=150)
        
        texto = "Le o tag" + "\n"
        
        # Semaforo para a serial
        #semaforo.acquire()
        ser.write( texto.encode("UTF-8") )
        #semaforo.release()
        
        thread = Thread(target=self.serial_tag)
        thread.daemon = True
        thread.start()
        
        
    def medir_peso(self, event):
        
        self.janela_espera = tk.Toplevel(self)       # nueva ventana
        self.janela_espera.title("Janela de espera")
        self.janela_espera.geometry("600x300")
        self.janela_espera.configure(bg="lightblue")
        
        label = tk.Label(self.janela_espera, text="Pesando o seu copo ...", font=("Arial", 12))
        label.place(x=230,y=110)
        label.configure(bg="lightblue", fg="midnight blue")
        
        self.progress = ttk.Progressbar(self.janela_espera)
        self.progress.place(x=260,y=150)
        
        texto = "Mede tara" + "\n"
        
        #Semaforo para a serial
        #semaforo.acquire()
        ser.write( texto.encode("UTF-8") )
        #semaforo.release()
        
        thread_peso = Thread(target=self.serial_peso)
        thread_peso.daemon = True
        thread_peso.start()
        
    def serial_peso(self):
        time_delta = 10
        instant_limite = datetime.now() + timedelta(seconds=time_delta)
        peso = ""
        global serial_livre
        serial_livre = False	#trava a serial para o verificacao_peso()
        
        while datetime.now() < instant_limite : 
            # Lê uma linha da porta serial
            if ser != None :
                #Semaforo para a serial
                #semaforo.acquire()
                peso = ser.readline().decode().strip()
                #semaforo.release()
                print(peso)
                if peso.startswith("Tara") :
                    peso = peso[4::]
                    print("peso: " + peso)
                    self.Peso.insert(0, f"{peso}")
                    break
            time.sleep(0.01)
            delta = instant_limite - datetime.now()
            secondes = delta.total_seconds()
            pourcentage = 100 - secondes*100/time_delta
            self.progress.config(value=pourcentage)
        
        if peso == "" :
            messagebox.showwarning("Atençao", "A balança nao encontrou nenhum peso")
        
        serial_livre = True
            
        self.janela_espera.destroy()
        
    def serial_tag(self):
        
        time_delta = 10
        instant_limite = datetime.now() + timedelta(seconds=time_delta)
        tag = ""
        global serial_livre
        serial_livre = False	#trava a serial para o verificacao_peso()
        
        while datetime.now() < instant_limite : 
            # Lê uma linha da porta serial
            if ser != None :
                # Semaforo para a serial
                #semaforo.acquire()
                tag = ser.readline().decode().strip()
                #semaforo.release()
                if tag.startswith("Tag") :
                    tag = tag[3::]
                    already_usuario = colecao_de_usuarios.find_one({"idtag": tag})
                    if already_usuario == None : 
                        self.Tag.insert(0, f"{tag}")
                    else :
                        messagebox.showwarning("Atençao", "O tag ja pertenece a outra pessoa")
                    break
            time.sleep(0.01)   
            delta = instant_limite - datetime.now()
            secondes = delta.total_seconds()
            pourcentage = 100 - secondes*100/time_delta
            self.progress.config(value=pourcentage)
            
        if tag == "" :
            messagebox.showwarning("Atençao", "O leitor nao encontrou nenhum tag")
            
        serial_livre = True
            
        self.janela_espera.destroy()
    
    
class JanelaRecepcao(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Controla o seu consumo de agua !")
        self.geometry("600x300")
        self.configure(bg="lightblue")
        
        contador = 0
        
        ##letura do banco de dados :
        
        dado_da_busca = {} #todos os usuarios
        ordenacao = [["nome", ASCENDING]]
        usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca, sort=ordenacao) )
        
        for usuario in usuarios_atuais :
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=1)
            cuadro.place(x=220,y=50+23*contador)
            label = tk.Label(cuadro, text=usuario["nome"], font=("Arial", 11))
            label.pack(side=tk.TOP)
            label.configure(bg="midnight blue", fg="lightblue", width=10)
            
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=1)
            cuadro.place(x=310,y=50+23*contador)
            botao = tk.Button(cuadro, text="Ed")
            botao.pack(side=tk.TOP)
            botao.indice = contador
            botao.configure(fg="lightblue", bg="midnight blue", width=2, height=1)
            botao.bind('<Button-1>', self.editar_usuario)
            
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=1)
            cuadro.place(x=335,y=50+23*contador)
            botao = tk.Button(cuadro, text="X")
            botao.pack(side=tk.TOP)
            botao.indice = contador
            botao.configure(fg="lightblue", bg="midnight blue", width=2, height=1)
            botao.bind("<Button-1>",self.supprimir_usuario)
            
            contador = contador + 1
            
            if contador == 7 :
                break 
            
        if contador < 7 :
            
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=2.5)
            cuadro.place(x=220,y=50+23*contador)
            botao = tk.Button(cuadro, text="CADASTRAR-SE")
            botao.pack(side=tk.TOP)
            botao.configure(fg="lightblue", bg="midnight blue", width=18, height=1)
            botao.bind('<Button-1>', self.cadastrar_usuario)
            
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=2.5)
            cuadro.place(x=220,y=80+23*(contador))
            botao = tk.Button(cuadro, text="Ver RANKING")
            botao.pack(side=tk.TOP)
            botao.configure(fg="lightblue", bg="midnight blue", width=18, height=1)
            botao.bind('<Button-1>', self.ver_ranking)
        
        else :
            cuadro = tk.Frame(self, borderwidth = 0, highlightbackground="white", highlightthickness=2.5)
            cuadro.place(x=220,y=80+23*(contador))
            botao = tk.Button(cuadro, text="Ver RANKING")
            botao.pack(side=tk.TOP)
            botao.configure(fg="lightblue", bg="midnight blue", width=18, height=1)
            botao.bind('<Button-1>', self.ver_ranking)
            
            
    def editar_usuario(self, event):
        indice = event.widget.indice
        self.destroy()
        app_edicao = JanelaEdicao(indice)
        app_edicao.mainloop()
        
        
    def supprimir_usuario(self, event):
        indice = event.widget.indice
        self.destroy()
        dado_da_busca = {} #todos os usuarios
        ordenacao = [["nome", ASCENDING]]
        usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca, sort=ordenacao))
        usuario_chao = usuarios_atuais[indice]
        dado_delete = { "nome": usuario_chao["nome"], "idchats": usuario_chao["idchats"] }
        colecao_de_usuarios.delete_one(dado_delete) 
        app = JanelaRecepcao()
        app.mainloop()
        
    def cadastrar_usuario(self, event):
        self.destroy()
        app = JanelaInfo()
        app.mainloop()
    
    def ver_ranking(self, event):
        self.destroy()
        app = Ranking()
        app.mainloop()
        
class JanelaEdicao (tk.Tk):
    def __init__(self, indice):
        super().__init__()
        self.title("Controle o seu consumo de água!")
        self.geometry("600x330")
        self.configure(bg="lightblue")
        
        self.indice = indice
        
        
        dado_da_busca = {} #todos os usuarios
        ordenacao = [["nome", ASCENDING]]
        usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca, sort=ordenacao))
        self.usuario_editado = usuarios_atuais[indice]
        
        label = tk.Label(self, text="Edite os seus dados", font=("Arial", 10))
        label.place(x=250,y=30)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Nome :", font=("Arial", 10))
        label.place(x=150,y=60)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="Id chat telegram :", font=("Arial", 10))
        label.place(x=90,y=90)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="Meta diaria :", font=("Arial", 10))
        label.place(x=120,y=120)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Peso do copo :", font=("Arial", 10))
        label.place(x=104,y=150)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Tag do copo :", font=("Arial", 10))
        label.place(x=114,y=180)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Url do widget :", font=("Arial", 10))
        label.place(x=110,y=210)
        label.configure(bg="lightblue", fg="midnight blue")

        label = tk.Label(self, text="L", font=("Arial", 10))
        label.place(x=445,y=120)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="g", font=("Arial", 10))
        label.place(x=445,y=150)
        label.configure(bg="lightblue", fg="midnight blue")
        
        label = tk.Label(self, text="Cor do LED :", font=("Arial", 10))
        label.place(x=117,y=240)
        label.configure(bg="lightblue", fg="midnight blue")

        self.Nome = tk.Entry(self, width=40)
        self.Nome.insert(0, self.usuario_editado["nome"])
        self.Nome.place(x=200,y=60)

        self.IdChat = tk.Entry(self, width=40)
        self.IdChat.insert(0, self.usuario_editado["idchats"]) 
        self.IdChat.place(x=200,y=90)

        self.Meta = tk.Entry(self, width=40)
        self.Meta.insert(0, float(self.usuario_editado["meta"])/1000)
        self.Meta.place(x=200,y=120)
        
        self.Peso = tk.Entry(self, width=40)
        self.Peso.insert(0, self.usuario_editado["tara"])
        self.Peso.place(x=200,y=150)

        self.Tag = tk.Entry(self, width=40)
        self.Tag.insert(0, self.usuario_editado["idtag"])
        self.Tag.place(x=200,y=180)
        
        self.Url = tk.Entry(self, width=40)
        self.Url.insert(0, self.usuario_editado["urlwidget"])
        self.Url.place(x=200,y=210)
        
        self.Cor = tk.StringVar()
        self.CorBox = ttk.Combobox(self, textvariable=self.Cor, values=cores)
        input_cor = cores[int(self.usuario_editado["cor"])]
        self.CorBox.insert(0, input_cor)
        self.CorBox.place(x=200,y=240)
        
        botao = tk.Button(self, text="Auto")
        botao.place(x=475,y=150)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.medir_peso)
        
        botao = tk.Button(self, text="Auto")
        botao.place(x=475,y=180)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.ler_tag)

        botao = tk.Button(self, text="Editar")
        botao.place(x=270,y=270)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.modificar_usuario)
        
    def ler_tag(self, event):
        
        self.janela_espera = tk.Toplevel(self)          # nueva ventana
        self.janela_espera.title("Janela de espera")
        self.janela_espera.geometry("600x300")
        self.janela_espera.configure(bg="lightblue")
        
        label = tk.Label(self.janela_espera, text="Procurando o seu tag ...", font=("Arial", 12))
        label.place(x=230,y=110)
        label.configure(bg="lightblue", fg="midnight blue")
        
        self.progress = ttk.Progressbar(self.janela_espera, value=0)
        self.progress.place(x=260,y=150)
        
        texto = "Le o tag" + "\n"
        
        # Semaforo para a serial
        #semaforo.acquire()
        ser.write( texto.encode("UTF-8") )
        #semaforo.release()
        
        thread = Thread(target=self.serial_tag)
        thread.daemon = True
        thread.start()
        
        
    def medir_peso(self, event):
        
        self.janela_espera = tk.Toplevel(self)       # nueva ventana
        self.janela_espera.title("Janela de espera")
        self.janela_espera.geometry("600x300")
        self.janela_espera.configure(bg="lightblue")
        
        label = tk.Label(self.janela_espera, text="Pesando o seu copo ...", font=("Arial", 12))
        label.place(x=230,y=110)
        label.configure(bg="lightblue", fg="midnight blue")
        
        self.progress = ttk.Progressbar(self.janela_espera)
        self.progress.place(x=260,y=150)
        
        texto = "Mede tara" + "\n"
        
        #Semaforo para a serial
        #semaforo.acquire()
        ser.write( texto.encode("UTF-8") )
        #semaforo.release()
        
        thread_peso = Thread(target=self.serial_peso)
        thread_peso.daemon = True
        thread_peso.start()
        
    def serial_peso(self):
        time_delta = 10
        instant_limite = datetime.now() + timedelta(seconds=time_delta)
        peso = ""
        global serial_livre
        serial_livre = False	#trava a serial para o verificacao_peso()
        
        while datetime.now() < instant_limite : 
            # Lê uma linha da porta serial
            if ser != None :
                #Semaforo para a serial
                #semaforo.acquire()
                peso = ser.readline().decode().strip()
                #semaforo.release()
                print(peso)
                if peso.startswith("Tara") :
                    peso = peso[4::]
                    print("peso: " + peso)
                    self.Peso.insert(0, f"{peso}")
                    break
            time.sleep(0.01)
            delta = instant_limite - datetime.now()
            secondes = delta.total_seconds()
            pourcentage = 100 - secondes*100/time_delta
            self.progress.config(value=pourcentage)
        
        if peso == "" :
            messagebox.showwarning("Atençao", "A balança nao encontrou nenhum peso")
        
        serial_livre = True
            
        self.janela_espera.destroy()
        
    def serial_tag(self):
        
        time_delta = 10
        instant_limite = datetime.now() + timedelta(seconds=time_delta)
        tag = ""
        global serial_livre
        serial_livre = False	#trava a serial para o verificacao_peso()
        
        while datetime.now() < instant_limite : 
            # Lê uma linha da porta serial
            if ser != None :
                # Semaforo para a serial
                #semaforo.acquire()
                tag = ser.readline().decode().strip()
                #semaforo.release()
                if tag.startswith("Tag") :
                    tag = tag[3::]
                    already_usuario = colecao_de_usuarios.find_one({"idtag": tag})
                    if already_usuario == None : 
                        self.Tag.insert(0, f"{tag}")
                    else :
                        messagebox.showwarning("Atençao", "O tag ja pertenece a outra pessoa")
                    break
            time.sleep(0.01)   
            delta = instant_limite - datetime.now()
            secondes = delta.total_seconds()
            pourcentage = 100 - secondes*100/time_delta
            self.progress.config(value=pourcentage)
            
        if tag == "" :
            messagebox.showwarning("Atençao", "O leitor nao encontrou nenhum tag")
            
        serial_livre = True
            
        self.janela_espera.destroy()
        
    def modificar_usuario(self, event):
        NomeUsuario = self.Nome.get()
        MetaUsuario = self.Meta.get()
        IdChatUsuario = self.IdChat.get()
        PesoUsuario = self.Peso.get()
        TagUsuario = self.Tag.get()
        UrlUsuario = self.Url.get()
        CorUsuario = self.Cor.get()
        
        
        if not(NomeUsuario.strip()) or not(MetaUsuario.strip()) or not(IdChatUsuario.strip()) or not(PesoUsuario.strip()) or not(TagUsuario.strip()) or not(UrlUsuario.strip()) or not(CorUsuario.strip()):
            
            messagebox.showwarning("Atençao", "Você tem que recheiar tudo.")
            
        elif test_tipo_float(MetaUsuario) == False :
            
            messagebox.showwarning("Atençao", "A meta tem que ser um numero.")
        
        elif float(MetaUsuario) <= 0 :
            
            messagebox.showwarning("Atençao", "A meta tem que ser maior que 0.")
            
        else:
            ### recuperer les données de temps et de volumes d'eau de dernier poids, de flammes etc depuis usuario_editado ici avant de les mettres dans le nouveau usuario
            vecteur_temps = self.usuario_editado["dias"]
            vecteur_volume = self.usuario_editado["volume"]
            numero_cor = cores.index(CorUsuario)
            dado_delete = { "nome": self.usuario_editado["nome"], "idtag": self.usuario_editado["idtag"]}
            colecao_de_usuarios.delete_one(dado_delete) 
            usuario = {"nome": f"{NomeUsuario}", "cor": f"{numero_cor}", "meta": f"{float(MetaUsuario)*1000}", "idchats": f"{IdChatUsuario}", "tara": f"{PesoUsuario}", "idtag": f"{TagUsuario}", "ultimo_peso": 0, "streak": 0, "dias": vecteur_temps, "volume": vecteur_volume, "urlwidget": f"{UrlUsuario}" }
            colecao_de_usuarios.insert_one(usuario)
            self.destroy()
            app = JanelaRecepcao()
            app.mainloop() 

class Ranking (tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Campeonato do melhor bebedor")
        self.geometry("600x300")
        self.configure(bg="lightblue")
        
        dado_da_busca = {} #todos os usuarios
        ordenacao = [["nome", ASCENDING]]
        usuarios_atuais = list( colecao_de_usuarios.find(dado_da_busca, sort=ordenacao) )
        liste_moyenne_nome = []
        liste_moyenne = []
        liste_triee = []
        for usuario in usuarios_atuais :
            moyenne = 0
            for quantite in usuario["volume"] :
                moyenne = moyenne + quantite 
            moyenne = moyenne/(len(usuario["volume"]))
            liste_moyenne.append(moyenne)
            liste_moyenne_nome.append([moyenne,usuario["nome"]])

        for i in range  (len(liste_moyenne)) :
            max_atual = max(liste_moyenne)
            indice_max_atual = liste_moyenne.index(max_atual)
            liste_triee.append(liste_moyenne_nome[indice_max_atual])
            liste_moyenne.pop(indice_max_atual)
            liste_moyenne_nome.pop(indice_max_atual)
            
        if len(liste_triee) == 1 :
            liste_triee.append([0, ""])
            liste_triee.append([0, ""]) 
           
        if len(liste_triee) == 2 :
            liste_triee.append([0, ""])
        
        canvas = tk.Canvas(self, width=600, height=300, bg="lightblue")
        canvas.pack()
        
        canvas.create_text(300, 40, text=f"Parabens {liste_triee[0][1]} !", font=("Arial", 20), fill="darkblue")
        canvas.create_text(300, 80, text=f"Você ganhou a competiçao dos bebedores !", font=("Arial", 15), fill="darkblue")
    
        canvas.create_rectangle(400/3 + 100, 135, 2*400/3 + 100, 260, fill="darkblue", outline="grey", width=2)
        canvas.create_rectangle(100, 185, 400/3 + 100, 260, fill="darkblue", outline="grey", width=2)
        canvas.create_rectangle(2*400/3 + 100, 210, 400 + 100, 260, fill="darkblue", outline="grey", width=2)
        
        canvas.create_text(300, 195, text="1", font=("Arial", 30), fill="gold")
        canvas.create_text(400/6 + 100, 220, text="2", font=("Arial", 30), fill="silver")
        canvas.create_text(5*400/6 + 100, 235, text="3", font=("Arial", 30), fill="#CD7F32")
    
        canvas.create_text(300, 115, text=f"{liste_triee[0][1]}", font=("Arial", 20), fill="darkblue")
        canvas.create_text(400/6 + 100, 165, text=f"{liste_triee[1][1]}", font=("Arial", 20), fill="darkblue")
        canvas.create_text(5*400/6 + 100, 190, text=f"{liste_triee[2][1]}", font=("Arial", 20), fill="darkblue")
 
        botao = tk.Button(canvas, text="Ver os outros usuarios")
        botao.place(x=237,y=267)
        botao.configure(fg="lightblue", bg="midnight blue")
        botao.bind('<Button-1>', self.fechar)
        
    def fechar(self, event) :
        self.destroy()
        app = JanelaRecepcao()
        app.mainloop()
            
def verificacao_peso():
    while True:
        # Quantidade de dados que o ser enviou e que o Python ainda não leu
        # Semaforo para a serial
        #semaforo.acquire()
        global serial_livre
        #print(serial_livre)
        if serial_livre == False :	#verifica se a serial esta livre
            continue
        
        if ser.in_waiting:
            linha = ser.readline().decode().strip()
            print("Recebido do arduino:", linha)
            
            
            # 1. ser mandou uma tag
            if linha.startswith("TAG:"):
                uid = linha.replace("TAG:", "").strip()
                print("Tag detectada:", uid)
                
                # Busca a tag identificada no banco
                usuario = colecao_de_usuarios.find_one({"idtag": uid})
                
                if usuario:
                    nome = usuario["nome"]
                    meta = usuario["meta"]
                    tara = usuario["tara"]
                    idtag = usuario["idtag"]
                    ultimo_peso = usuario["ultimo_peso"]
                    id_da_conversa = usuario["idchats"]
                    streak = usuario["streak"]
                    ultimo_dia = usuario["dias"][-1].strftime("%Y-%m-%d")
                    consumo_dia = usuario["volume"][-1]
                    hoje = datetime.now().strftime("%Y-%m-%d")
                    cor = usuario["cor"]

                    dados = f"{nome};{meta};{tara};{idtag};{ultimo_peso};{streak};{ultimo_dia};{consumo_dia};{hoje};{cor}\n"
                    ser.write(dados.encode())
                    print("Enviado ao ser:", dados.strip())
                    
                else:
                    print("Usuário não encontrado!")
                    ser.write(b"NAO_ENCONTRADO\n")
                    
            if linha.startswith("tag:"):
                dados = {}
                for parte in linha.split(";"):
                    chave, valor = parte.split(":")
                    dados[chave] = valor
                
                print("Tag:", dados["tag"])
                print("Data:", dados["data"])
                print("Volume:", dados["volume"])
                print("Peso:", dados["peso"])
                
                usuario = colecao_de_usuarios.find_one({"idtag": dados["tag"]})
                dias = usuario["dias"]
                consumo_dia = usuario["volume"]
                id_da_conversa = usuario["idchats"]
                nova_data = datetime.strptime(dados["data"], "%Y-%m-%d")
                novo_volume = float(dados["volume"])
                novo_peso = float(dados["peso"])
                
                if dias and dias[-1].date() == nova_data.date():
                    consumo_dia[-1] = novo_volume
                    dias[-1] = nova_data
                else:
                    dias.append(nova_data)
                    consumo_dia.append(novo_volume)
                
                if consumo_dia[-1] >= float(meta) :
                    endereco = endereco_base + "/sendMessage"
                    dados = {"chat_id": id_da_conversa, "text": f"🎉 Parabéns!\nVocê atingiu sua meta de hidratação hoje! 🥤💧\nSeu corpo agradece! 😄💪"}
                    resp = post(endereco, json=dados)
                    
                colecao_de_usuarios.update_one(
                {"idtag": usuario["idtag"]},
                {
                    "$set": {
                        "dias": dias,
                        "volume": consumo_dia,
                        "ultimo_peso": novo_peso
                    }
                }
            )
        #semaforo.release()


serial_livre = True #booleano para a thread de verificacao saber se a serial esta livre

thread_telegram = Thread(target=verificacao_temporal_alerta)	#thread do telegram
thread_telegram.daemon = True
thread_telegram.start()

#semaforo = threading.Semaphore(1)
thread = Thread(target=verificacao_peso)
thread.daemon = True
thread.start()
    
app = JanelaRecepcao()
app.mainloop()
