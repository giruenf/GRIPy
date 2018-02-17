# -*- coding: utf-8 -*-

#
# Universidade Estadual do Norte Fluminense - UENF
# Laboratório de Engenharia de Petróleo - LENEP
# Grupo de Inferência em Reservatório - GIR
# Adriano Paulo Laes de Santana
# May 11th, 2017

from wx.lib.pubsub import pub

"""

                    Gripy messaging pattern module
                    ==============================

"In the publish–subscribe model, subscribers typically receive only 
a subset of the total messages published. 
The process of selecting messages for reception and processing 
is called filtering. There are two common forms of filtering: 
topic-based and content-based."
Source: http://en.wikipedia.org/wiki/Publish-subscribe_pattern  (1)

Our flavor of publish–subscribe (PubSub) is based on PyPubSub.
PyPubSub was born as wxPython module but it has grown and nowadays 
has its own project hosted in GitHub 
http://github.com/schollii/pypubsub.        

Despite its growth, PyPubSub remains accessible as a wxPython module
located at wx.lib.pubsub.
This wxPython version of PyPubSub fulfills our needs.

PyPubSub is topic-based PubSub. "In a topic-based system, messages are 
published to 'topics' or named logical channels. Subscribers in a topic-based 
system will receive all messages published to the topics to which they 
subscribe, and all subscribers to a topic will receive the same messages. 
The publisher is responsible for defining the classes of messages to which 
subscribers can subscribe." (1)

We developed a "topic system" to add a flavor of content-based to PyPubSub.
"In a content-based system, messages are only delivered to a subscriber if the
attributes or content of those messages match constraints defined by the 
subscriber. The subscriber is responsible for classifying the messages."  (1)

"""

# TODO: corrigir Docs

def pubuid_to_uid(value):
    try:
        tid, oid = value.split('&')
        return tid, int(oid)
    except:
        return value


def uid_to_pubuid(value):
    try:
        tid, oid = value
        return tid + '&' + str(oid)
    except:
        return value
    
'''
def decode_topic(topic):
    topic_parts = topic.split('.')
    root_topic = topic_parts[0]
    sub_topics = topic_parts[1:] 
    try:
        func_name, publisher = root_topic.split('@')
    except ValueError as ve:
        if ve.message == 'need more than 1 value to unpack':
            raise Exception('Publisher not found on topic: "{}"'.format(topic))
        elif ve.message == 'too many values to unpack':
            raise Exception('Wrong Publisher type found on topic: "{}". Are there more than 1 Publisher?'.format(topic))
    publisher = pubuid_to_uid(publisher)
    for idx in range(len(sub_topics)):
        sub_topics[idx] = pubuid_to_uid(sub_topics[idx])   
    return publisher, func_name, sub_topics
'''

ALL_TOPICS = pub.ALL_TOPICS
AUTO_TOPIC = pub.AUTO_TOPIC



class PublisherMixin(object):
    
    # TODO: Unsubscribe
    def subscribe(self, listener, topic):
        """
        Subscribe a listener, creating a inner (encoded) topic to identify it.
        
        Parameters
        ----------
            listener : callable
                Who will be called.
            function_tag: str
                An identifier name.
            args: 
                Additional parameters to help acting as 'content-based system'.

        Returns
        -------
            listener: pubsub.core.Listener
                    "The pub.core.Listener wraps the callable subscribed and 
                    provides introspection-based info about the callable."
                    Source: wxPhoenix docs for PublisherBase class. 
            success: bool
                False listener was already subscribed. Otherwise True.

        Notes
        -----
            function_tag and args will compose the actual inner topic.
            
        Examples
        --------
            Subscribing for ObjectManager objects addition can be written as:
            >>> OM = ObjectManager(self)
            >>> listener, ok = OM.subscribe(func_on_add_obj, 'object_added')
            * Actual topic would be "on_add_object@ObjectManager"
        
            Function func_on_change can be notified for b.width changes with: 
            >>> b = B()
            >>> listener, ok = b.subscribe(func_on_change, 'attr_changed', 
                                                                       'width')
            * Actual topic would be "on_change@ObjectManager.width"
        """    
        # TODO: Refazer docs
        if not callable(listener):
            return None, False
        # TODO: Check for caller 'can subscribe'
        # TODO: Check for function_ 'can be subscribed'
        topic = self.get_publisher_name() + '.' + topic
        return pub.subscribe(listener, topic)    


    def subsALL(self, listener):
        return pub.subscribe(listener, ALL_TOPICS) 
    
    
    def unsubscribe(self, listener, topic):
        topic = self.get_publisher_name() + '.' + topic
        return pub.unsubscribe(listener, topic)   
    
    
    def unsubAll(self):
        return pub.unsubAll(topicFilter=self._topic_filter)  
    
    def _topic_filter(self, topic_name):
        return topic_name.startswith(self.get_publisher_name())


    def isSubscribed(self, listener, topic):
        topic = self.get_publisher_name() + '.' + topic
        return pub.isSubscribed(listener, topic)        


    def send_message(self, topic, **data):
        """
        Execute the listener associated with topic_tuple passing data as 
        argument.
        
        Parameters
        ----------
            topic_tuple : tuple
                Tuple used to create (encode) the actual inner topic that 
                identifies the listener.
            data: dict
                Parameters that will be passed to the listener callable
                as a set of "key=value".
            
        Examples
        --------
            Messaging new object creation.
            >>> OM = ObjectManager(self)
            >>> OM.send_message('add', objuid=obj.uid)  
            
            Messaging object attribute change.
            >>> b = B()
            >>> b.send_message(('attr_changed', 'width'), arg1=value, arg2=old_value)
        """
        # TODO: Refazer docs
        # print 'publisher: {} - topic: {} - data: {}'.format(self.get_publisher_name(), topic, data)
        try:
            print '\n\nPublisherMixin.send_message'
            topic = self.get_publisher_name() + '.' + topic
            print 'topic:', topic, data
            pub.sendMessage(topic, **data)
            print 'OK send message'
        except Exception as e:
            print 'ERROR [PublisherMixin.send_message]:', self, topic, data, e
            print '\n\n'
            pass

    def get_publisher_name(self):
        try:
            return self._PUB_NAME
        except AttributeError:
            try:
                return uid_to_pubuid(self.uid)
            except:
                raise
    

     