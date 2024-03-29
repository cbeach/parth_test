#
#   Twisted is an asyncronous connection manager
#   Every time a new connection is made the SubPubFactory
#   creates a new protocol class, which handles the
#   communication with the connection.  This is where
#   messages are organized and stored while awating
#   acknowledgement
#

from twisted.internet.protocol import Protocol, Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor
import json, redis, time, parthenon, signal

class SubPubFactory(Factory):
    
    protocol = parthenon.ParthenonMQ

    subscribers = []
    message_id = 0
    r_server = redis.Redis('localhost')
    ack_queue = {}
    
    def __init__(self):
        signal.signal(signal.SIGALRM, self.timer)
        signal.setitimer(signal.ITIMER_REAL,.01,.01)
        self.protocol.factory = self
        
    def timer(self, signal, _):
        """
            automattically trigger the distribute function so that 
            messages don't pile up.
        """
        self.distribute()

    def send_message(self, sub):
        sub.deliver_message(self.message,self.now)

    def distribute(self):
        """ 
            check the ack_queue for messages that are stale and need to be
            resent.  If a message has been attempted 5 times it is deleted.
            Then check the redis database for new messages and send them
            along.

        """
        message_count = len(self.r_server.lrange('message_queue',0,-1))
        for i in self.ack_queue.keys():
            if len(self.ack_queue.keys()) > 0 and self.now - i > 2 and self.ack_queue[i][1] < 5:
                for j in self.ack_queue[i][0]:
                    j.deliver_message(self.ack_queue[i][2])
                self.ack_queue[i][1] += 1

            elif len(self.ack_queue.keys()) > 0 and self.now - i > 2 and self.ack_queue[i][1] == 5:
                self.ack_queue.pop(i)
        
        for i in range(message_count):
            self.now = time.time()
            message = self.r_server.lpop('message_queue')
            self.ack_queue[self.now] = [self.subscribers[:],0,message]
            for j in self.ack_queue[self.now][0]:
                j.deliver_message(message, self.now)

    def ack(self, time_stamp, subscriber):
        """
            keep the acknowledgement queue clean.
        """
        try:
            self.ack_queue.get(time_stamp)[0].remove(subscriber)
            if len(self.ack_queue.get(time_stamp)[0]) == 0:
                self.ack_queue.pop(time_stamp)
        except ValueError:
            pass #should never happen
        except KeyError:
            pass #should never happen

factory = SubPubFactory()
endpoint = TCP4ServerEndpoint(reactor, 8080)
endpoint.listen(factory)
reactor.run()






