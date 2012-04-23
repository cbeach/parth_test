#
#   This is where most of the communication happens
#
#
#

from twisted.internet.protocol import Protocol, Factory
import json, redis, time



class ParthenonMQ (Protocol):
    """
      *  This is where most of the processing happens
    """
    def connectionMade(self):
        self.r_server = redis.Redis('localhost')

    def dataReceived(self, data):
        """
          If this is a new connection, the server will look for control
          sequences specifying whether the connection is to a publisher
          or subscriber.  If it is an acknowledgement of a received msg
          it will pass that information along to the factory.
        """
        message = json.loads(data)

        if message.get('command') == None:
            if self.role == 'subscriber':
                return None
            elif self.role == 'publisher':
                self.r_server.rpush('message_queue', message.get('body'))
                print('published ' + message.get('body'))
            
        elif message.get('command') == 'subscriber':
            self.role = 'subscriber'
            self.factory.subscribers.append(self)
            self.awaiting_ack = {}

        elif message.get('command') == 'publisher':
            self.role = 'publisher'
            self.awaiting_ack = None
            
            try:
                self.factory.subscribers.remove(self)
            except ValueError:
                pass
            

        elif message.get('command') == 'ack':
            try:
                self.factory.ack(message.get('time_stamp'),self)
            except KeyError:
                pass

    def deliver_message(self,message,time_stamp):
        now = time.time()
        self.transport.write(json.dumps({'time_stamp':time_stamp,'body':message}))
