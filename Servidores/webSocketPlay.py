import json
import sys
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import threading

"""
--------------------------------
        INICIO  Funções Socket
--------------------------------

"""
codesValidos = ["print"]

def find(self,obj):
    if len(self.ready) > 1:
        for conn in self.ready:
            if conn != (obj['username'],self):
                print(conn[0]," VS ",obj['username'])
                self.versus.append((conn[0],obj['username']))
                self.ready.remove(conn)
                self.ready.remove((obj['username'],self))
                vitoria,derrota,pontos = buscarDados(conn[0])
                vitoria1,derrota1,pontos1 = buscarDados(obj['username'])
                self.write_message(json.dumps({'response':'encontrado','usernameOP':conn[0],'vitoria':vitoria,'derrota':derrota,'pontos':pontos}))
                conn[1].write_message(json.dumps({'response':'encontrado','usernameOP':obj['username'],'vitoria':vitoria1,'derrota':derrota1,'pontos':pontos1}))
                return 
    else:
        print("Não há oponentes")
        self.write_message(json.dumps({'response':'no'}))


def buscarDados(nome):
    users = []
    with open('./dados/users.json','r') as f: #pega os players do arquivo ou servidor
        users = json.load(f)
    for user in users:
        if user['username'] == nome:
            return user['vitoria'],user['derrota'],user['pontos']
    return 0


def waitoponente(self,jogador,oponente):
    if jogador not in self.espera: 
        self.espera.append(jogador)
    print("Espera >> Jogador ",jogador, "Esperando", oponente)
    if not (jogador in self.espera and oponente in self.espera):
        print(">> Jogador ",jogador," terminou primeiro")
        return
    #um dos dois entra
    connOp = ''
    for y in self.playing:
        if y[0] == oponente:
            connOp=y[1]
    if connOp =='':
        print("ERR >> Ocorreu um erro de Jogador fantasta")
    pontosOponente = avalia(connOp,oponente,codesValidos)
    pontosJogador = avalia(self,jogador,codesValidos) # aqui adiciona os coódigos válidos do json
    self.points.append((pontosJogador,self))
    self.points.append((pontosOponente,connOp))
    if len(self.points)> 1:
        if self.points.index(0)[0] >= self.points.index(1)[0]:
            self.points.index(0)[1].write_message(json.dumps({"response":"fim","pontos":points.index(0)[0],"status":"1"}))
            self.points.index(1)[1].write_message(json.dumps({"response":"fim","pontos":points.index(1)[0],"status":"0"}))
            print("Jogador ",points.index(0)[0]," ganhou!")
            print("Jogador ",points.index(1)[0]," perdeu!")
        else:
            self.points.index(0)[1].write_message(json.dumps({"response":"fim","pontos":points.index(0)[0],"status":"0"}))
            self.points.index(1)[1].write_message(json.dumps({"response":"fim","pontos":points.index(1)[0],"status":"1"}))
            print("Jogador ",points.index(1)[0]," ganhou!")
            print("Jogador ",points.index(0)[0]," perdeu!")
        self.points.remove(points.index(0))
        self.points.remove(points.index(1))
    self.playing.remove((obj['username'],self))
    print("Fim da partida! ")

def avalia(self, jogador,codv):#codv Códigos válidos
    points = 0
    for (conn,nome,entrada,linha) in self.code:
        if nome == jogador:
            for y in codv:
                if entrada.count(y):
                    points += 1
            self.code.remove((conn,nome,entrada,linha))
    return points
                
    

"""
--------------------------------
        FIM     Funções Socket
--------------------------------

"""


class SocketPlay(tornado.websocket.WebSocketHandler):

    connections = set()
    ready = []
    versus = []
    playing = []
    waiting = []
    code = []
    espera = []
    points = []
    lock = 0

    def open(self):
        self.connections.add(self)

      
    def on_message(self, message):
        #print ('Printando:  %s' % message)
        print("---> Entrando no webSocketPlay <---")
        try:
            if message == "teste":
                self.write_message('ok')
            else:
                obj = json.loads(str(message)) 
                
                print("Json: >> ",obj)
                if ((obj['username'],self) not in self.ready) and ((obj['username'],self) not in self.playing): #adiciona novos players
                    self.ready.append((obj['username'],self))

                """
                    Funções de Ação do Game
                """
                if obj['function'] == 'jogar':
                    print("Jogador ",obj['username']," está querendo jogar!")
                    find(self,obj) #encontrar jogadores

                elif obj['function'] == 'ingame':
                    if ((obj['username'],self) in self.ready) and ((obj['username'],self) not in self.playing):
                        print("Jogador ",obj['username']," entrou no jogo!")
                        self.ready.remove((obj['username'],self))
                        self.playing.append((obj['username'],self))
                        #Aqui retorna o problema de cada um
                    else: 
                        self.code.append((self,obj['username'],obj['input'],obj['line']))
                        
                elif obj['function'] == 'end':
                    if (obj['username'],self) in self.playing:
                        oponente = ""
                        for (x,y) in self.versus:
                            if obj['username'] == x:
                                oponente = y
                                break
                            elif obj['username']==y:
                                oponente = x
                                break
                        waitoponente(self,obj['username'],oponente)
                        return 0 #fim do jogo




            print("---> Saindo no webSocketPlay <---")
            if (message == 'quit' or message == 'exit'):
                self.write_message(b'fodase')
                quit()


        except Exception as er: # sair cado der erro
            print("Erro (webSocketPlay) >> ",er)
            quit()
 
    def on_close(self):
        for x in self.ready: #retira players desconectados do lobby
            if self == x[1]:
                print ('Player: '+x[0]+' desconectado do lobby!')
                self.ready.remove(x)
        for x in self.playing: #retira players desconectados do game
            if self == x[1]:
                print ('Player: '+x[0]+' desconectado do jogo!')
                self.playing.remove(x)
        self.connections.remove(self)

 
    def check_origin(self, origin):
        return True