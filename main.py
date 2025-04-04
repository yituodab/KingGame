from flask import *
import random
import os
main = Flask(__name__)
class Player():
    __ready = False
    __name = ""
    __number = 0
    __isKing = False
    def __init__(self,name:str):
        self.__name = name
    def isReady(self) -> bool:
        return self.__ready
    def ready(self, ready:bool):
        self.__ready = ready
    def getName(self) -> str:
        return self.__name
    def getNumber(self) -> int:
        return self.__number
    def setNumber(self,number:int):
        self.__number = number
    def isKing(self)->bool:
        return self.__isKing
    def king(self,king:bool):
        self.__isKing = king
class Room():
    players = []
    Id = 1
    __id = 1
    __started = False
    __request = None
    def __init__(self):
        self.__id = Room.Id
        Room.Id = Room.Id + 1
    def getId(self) -> int:
        return self.__id
    def addPlayer(self, player:Player):
        self.players.append(player)
    def isReady(self) -> bool:
        ready = True
        for player in self.players:
            if not player.isReady():
                ready = False
                break
        return ready
    def start(self):
        numberList = list(range(1,len(self.players)+1))
        random.shuffle(numberList)
        i = 0
        for player in self.players:
            player.setNumber(numberList[i])
            i = i + 1
        self.players[random.randint(0,len(self.players)-1)].king(True)
        self.__started = True
    def started(self) -> bool:
        return self.__started
    def end(self):
        for player in self.players:
            player.ready(False)
            player.setNumber(0)
    def ready(self,name:str):
        for player in self.players:
            if player.getName() == name:
                player.ready(True)
    def hasPlayer(self,name:str) -> bool:
        for player in self.players:
            if player.getName() == name:
                return True
        return False
    def getPlayer(self,name:str) -> Player:
        for player in self.players:
            if player.getName() == name:
                return player
        return None
    def getPlayers(self) -> list:
        return self.players
    def deletePlayer(self,player:Player):
        self.players.remove(player)
    def playerNumber(self)->int:
        return len(self.players)
    def setRequest(self,kingRequest:str):
        self.__request = kingRequest
    def hasRequest(self)->bool:
        return self.__request != None
    def getRequest(self)->str:
        return self.__request
roomList = []
@main.route('/')
def root():
    template_path = os.path.join(main.root_path, "templates", "index.html")
    if not os.path.exists(template_path):
        return "Template file not found!"
    return render_template("index.html")
@main.route('/joinRoom', methods=["POST"])
def joinRoom():
    data = request.data.decode("utf-8")
    roomNumber = int(data[0:data.find(",")])
    playerName = data[data.find(",")+1:len(data)]
    room = roomList[roomNumber-1]
    if not room.hasPlayer(playerName):
        player = Player(playerName)
        player.ready(True)
        room.addPlayer(player)
    response = Response()
    response.headers["Content-Type"] = "text/plain"
    if roomNumber <= Room.Id:
        response.data = str(roomNumber)
    else:
        response.data = "not found"
    return response
@main.route('/exitRoom', methods=["POST"])
def exitRoom():
    data = request.data.decode("utf-8")
    roomNumber = int(data[0:data.find(",")])
    playerName = data[data.find(",")+1:len(data)]
    room = roomList[roomNumber-1]
    if room.hasPlayer(playerName):
        player = room.getPlayer(playerName)
        player.ready(False)
        room.deletePlayer(player)
    response = Response()
    response.headers["Content-Type"] = "text/plain"
    if roomNumber <= Room.Id:
        response.data = str(roomNumber)
    else:
        response.data = "not found"
    return response
@main.route('/addRoom', methods=["POST"])
def addRoom():
    room = Room()
    roomList.append(room)
    response = Response()
    response.headers["Content-Type"] = "text/plain"
    response.data = str(room.getId())
    return response
@main.route('/update', methods=["POST"])
def update():
    data = request.data.decode("utf-8")
    playerName = data[data.find(",")+1:len(data)]
    roomNumber = int(data[0:data.find(",")])
    room = roomList[roomNumber-1]
    response = Response()
    response.headers["Content-Type"] = "text/plain"
    returnData = "false,0,Waiting other players"
    if room.isReady():
        if not room.started():
            room.start()
        returnData = "true"
        getPlayer = room.getPlayer(playerName)
        if getPlayer == None:
            returnData = "false,0,null"
        returnData = "true,1,"+str(getPlayer.getNumber())
        if getPlayer.isKing():
            returnData = "true,1,King"
    if room.hasRequest():
        returnData = "true,2,"+room.getRequest()
        getPlayer = room.getPlayer(playerName)
        if getPlayer == None:
            returnData = "false,0,null"
        getPlayer.ready(False)
    response.data = returnData
    return response
@main.route('/request', methods=["POST"])
def Request():
    data = request.data.decode("utf-8")
    roomNumber = int(data[0:data.find(",")])
    kingRequest = data[data.find(",")+1:len(data)]
    room = roomList[roomNumber-1]
    room.setRequest(kingRequest)
    return "OK"
@main.route('/room/<int:id>')
def room(id:int):
    if len(roomList) < id:
        return "Room Not Found"
    return render_template("room.html", id=id)
@main.route('/getPlayerList',methods=["POST"])
def getPlayerList():
    data = request.data.decode('utf-8')
    roomNumber = int(data[0:data.find(",")])
    room = roomList[roomNumber-1]
    playerName = data[data.find(",")+1:len(data)]
    if not room.hasPlayer(playerName):
        player = Player(playerName)
        player.ready(True)
        room.addPlayer(player)
    playerList = ''
    for player in room.getPlayers():
        playerList = playerList + player.getName() + ','
    playerList = playerList[0:len(playerList)-1]
    response = Response()
    response.headers["Content-Type"] = "text/plain"
    response.data = playerList
    return response
main.debug = True
main.run(port=11451)