#
#   This just sends imput from the stdin to the 
#   message server using sockets
#
#

import socket, json, time, sys


class Publisher:
    def __init__(self,host,port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))
        self.sock.send( json.dumps({'command':'publisher'}))

    def publish(self, data):
        """
            send a message to the message server
        """
        self.sock.send(json.dumps({'body':data}))


#------  Change these arguments to test over the internet ------#
p = Publisher('localhost',8080) 

print('Please enter a message.')


while True:
    sys.stdout.write('>>>')
    line = raw_input()
    if line == 'quit':
        break
    p.publish(line)


