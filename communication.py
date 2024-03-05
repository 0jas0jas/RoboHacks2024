import json
import socket
import requests

class CommunicationInterface():
    data = {}
    ip_address = '192.168.4.1'
    port = 80
    sock = None
    hasConnection = False
    jsonData = None

    def __init__(self, config_path="user_config.json"):
        with open(config_path, 'r') as config_file:
            self.data = json.load(config_file)
    
    def sendCommand(self, command):
        try:
            response = requests.get(f"{self.base_url}/{command}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Failed to send command {command}: {str(e)}")


    def updateData(self, category, parameter, value):
        try:
            self.data[category][parameter] = value
            return 0
        except KeyError:
            return -1
        
    def createJSON(self):
        try:
            self.jsonData = json.dumps(self.data)
            return 0
        except:
            return -1
    def connectSocket(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1)
        try:
            self.sock.connect((self.ip_address, self.port))
            self.hasConnection = True
            return True
        except socket.error:
            return False
        
    def closeSocket(self):
        try:
            self.sock.close()
            self.hasConnection = False
            return True
        except:
            return False
        
    def sendUpdates(self):
        try:
            self.createJSON()
            self.sock.sendall(self.jsonData.encode('utf8'))
            return 0
        except socket.error:
            return 1
    
    def getSockConnection(self):
        return self.hasConnection
