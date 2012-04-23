import socket, json, time

class Publisher:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost',8080))
        self.sock.send( json.dumps({'command':'publisher'}))

    def publish(self, data):
        self.sock.send(json.dumps({'body':data}))

p = Publisher() 

while True:
    line = raw_input()
    if line == 'quit':
        break
    p.publish(line)

