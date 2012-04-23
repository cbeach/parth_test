import socket, json


class Subscriber:
    def __init__(self,host,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))
        self.sock.send( json.dumps({'command':'subscriber'}))

    def start_listening(self, callback):
        while True:
            data = self.sock.recv(1024)
            data = json.loads(data)
            callback(data)
            self.sock.send(json.dumps({'command':'ack','time_stamp':data.get('time_stamp')}))


def print_message(data):
    print(data)

s = Subscriber('localhost',8080)
s.start_listening(print_message)
            

