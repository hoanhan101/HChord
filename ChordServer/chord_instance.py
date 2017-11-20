#!usr/bin/env python3

"""
    chord_instance.py - A Chord Instance Class
    Author:
        - Nidesh Chitrakar (nideshchitrakar@bennington.edu)
        - Hoanh An (hoanhan@bennington.edu)
    Date: 10/30/2017
"""

import zerorpc

from node import Node
from utils import *
from const import *

class ChordInstance(object):
    """
    Each Chord Instance contains the information about its node and maintains
    a finger table, its successor, and its predecessor.
    """
    def __init__(self, IP_ADDRESS, PORT):
        """
        Initialize a ChordInstance.
        :param IP_ADDRESS: String
        :param PORT: Int
        :param ID: Int
        """
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT = PORT
        self.NODE = Node(IP_ADDRESS, PORT)
        self.ID = self.NODE.ID
        self.finger_table = self.create_finger_table()

        # set own successor and predecessor to self, i.e., the node is unattached
        self.successor = self
        self.predecessor = self

    def is_alive(self):
        return True

    def get_ID(self):
        return serialize(self.ID)

    def get_IP(self):
        return serialize(self.IP_ADDRESS)

    def set_successor(self, NODE):
        NODE = deserialize(NODE)
        self.finger_table[0]['successor'] = NODE
        self.successor = NODE
        print('Updated finger table:')
        self.print_finger_table()

    def find_successor_nw(self, NODE):
        return serialize(self.find_successor(NODE))

    def set_predecessor(self, NODE):
        NODE = deserialize(NODE)
        self.predecessor = NODE
        print('Updated finger table:')
        self.print_finger_table()

    def get_predecessor(self):
        return serialize(self.predecessor)

    def get_finger_table(self):
        return serialize(self.finger_table)

    def get_instance(self):
        return serialize(self)

    def connect_and_update(self, NODE, i):
        client = zerorpc.Client()
        client.connect('tcp://{0}:{1}'.format(NODE.IP_ADDRESS, NODE.PORT))
        client.update_finger_table(serialize(self),i)

    def create_finger_table(self):
        """
        Create a simple finger table of size m*2 with the start values generated
        by ID + 2^i where 0 <= i < m.
        All the successor values are set to self, i.e., the chord instance does
        not know about other nodes in the ring.
        :return: Finger Table
        """
        finger_table = []
        for i in range(0,m):
            finger_table.append({})
            finger_table[i]['start'] = constrain(self.ID + (2**i))
            finger_table[i]['successor'] = self
        return finger_table

    def print_finger_table(self):
        """
        Prints the finger table of a node.
        :return: None
        """
        print('finger_table of node {0}'.format(self.ID))
        print('Address: {0}:{1}'.format(self.IP_ADDRESS, self.PORT))
        print("successor: {0}, predecessor: {1}".format(self.successor.ID, self.predecessor.ID))
        for i in range (0,m):
            print(self.finger_table[i]['start'], self.finger_table[i]['successor'].ID)

    def find_successor(self, ID):
        """
        Find successor of a given ID.
        :param ID: Int
        :return: Node
        """
        # print('Node{0}.find_successor({1}): finding successor of ID {2}'.format(self.ID,ID,ID))
        n0 = self.find_predecessor(ID)
        # print('-> Successor: {0}'.format(n0.finger_table[0]['successor'].ID))
        return n0.finger_table[0]['successor']

    def find_predecessor(self, ID):
        """
        Find predecessor of a given ID.
        :param ID: Int
        :return: Node
        """
        # print('Node{0}.find_predecessor({1}): finding predecessor of ID {2}'.format(self.ID,ID,ID))
        n0 = self
        while not is_between(ID, n0.ID, n0.finger_table[0]['successor'].ID, including_end=True):
            n0 = n0.closest_preceding_node(ID)
        # print('-> Predecessor: {0}'.format(n0.ID))
        return n0

    def closest_preceding_node(self, ID):
        """
        Find the closest preceding node of a given ID.
        :param ID: Int
        :return: Node
        """
        # print('Node{0}.closest_preceding_node({1}): finding closest_preceding_node of ID {2}'.format(self.ID,ID,ID))
        # from i = m-1 down to 0
        for i in range(m - 1, -1, -1):
            # print(' -> i = {0}'.format(i))
            if is_between(self.finger_table[i]['successor'].ID, self.ID, ID):
                return self.finger_table[i]['successor']
        return self

    def join(self, NODE):
        """
        Join the network, given an arbitrary node in the network
        :param NODE: Node
        :return: None
        """
        if (NODE != None):
            print('')
            print('Node{0}.join({1}): joining {2} to {3}'.format(self.ID,NODE,self.ID,NODE.ID))
            print('')
            self.init_finger_table(NODE)
            self.update_others()

            for i in range(1,m):
                # self.predecessor.update_finger_table(self,i)
                self.connect_and_update(self.predecessor, i)
        else:
            print('No such node exists! Creating a new ring...')
            for i in range(0,m):
                self.finger_table[i]['successor'] = self
            self.predecessor = self

        # try:
        #     print("NODE {0} HAS SUCCESSFULLY JOINED".format(self.ID))
        #     self.print_finger_table()
        # except Exception as e:
        #     print(e)

    def init_finger_table(self, NODE):
        """
        Initialize finger table of local node, given an arbitrary node in the network.
        :param NODE: Node
        :return: None
        """
        self.finger_table[0]['successor'] = NODE.find_successor(self.finger_table[0]['start'])

        self.successor = self.finger_table[0]['successor']
        # print('-> updated successor of finger_table[0][\'successor\'] of node {0} to {1}'.format(self.ID,self.finger_table[0]['successor'].ID))

        successor = zerorpc.Client()
        successor.connect('tcp://{0}:{1}'.format(self.successor.IP_ADDRESS, self.successor.PORT))
        print('setting predecessor of successor({1}:{2}) to {0}'.format(self.ID, self.successor.IP_ADDRESS, self.successor.PORT))
        self.predecessor = deserialize(successor.get_predecessor())
        successor.set_predecessor(serialize(self))

        predecessor = zerorpc.Client()
        predecessor.connect('tcp://{0}:{1}'.format(self.predecessor.IP_ADDRESS, self.predecessor.PORT))
        print('setting successor of predecessor({1}:{2}) to {0}'.format(self.ID, self.predecessor.IP_ADDRESS, self.predecessor.PORT))
        predecessor.set_successor(serialize(self))

        # print('-> set predecessor of node {0} to {1}'.format(self.ID, self.predecessor.ID))
        # print('-> set predecessor of node {1} to {0}'.format(self.ID, self.finger_table[0]['successor'].ID))

        for i in range(0,m-1):
            # print('i = {0}'.format(i))
            # self.print_finger_table()
            if is_between(self.finger_table[i+1]['start'], self.ID, self.finger_table[i]['successor'].ID, including_start=True):
                # print('Value {0} is in [{1},{2}]'.format(self.finger_table[i+1]['start'],self.ID,self.finger_table[i]['successor'].ID))
                self.finger_table[i+1]['successor'] = self.finger_table[i]['successor']
                # print('-> updated the successor of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i+1,self.ID,self.finger_table[i]['successor'].ID))
            else:
                # print('Value {0} is not in [{1},{2}]'.format(self.finger_table[i+1]['start'],self.ID,self.finger_table[i]['successor'].ID))
                self.finger_table[i+1]['successor'] = NODE.find_successor(self.finger_table[i+1]['start'])
                # print('-> updated the successor of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i+1,self.ID,NODE.find_successor(self.finger_table[i-1]['start']).ID))

    def update_others(self):
        """
        Update all nodes whose finger tables should refer to itself.
        :return: None
        """
        # print('Node{0}.update_others(): update finger_table of other nodes'.format(self.ID))
        for i in range(0,m):
            val = constrain(self.ID - 2**(i))
            # print('find predecessor of={1}, val={0}'.format(val, self.ID - 2**(i)))
            p = self.find_predecessor(val)
            # print('predecessor of {0} is {1}'.format(val, p.ID))
            # print('Update finger table of Node {0}'.format(p.ID))

            # If p is not itself, which has already updated through init finger table,
            # then update finger tables of others
            if (p != self):
                # p.update_finger_table(self, i)
                self.connect_and_update(p, i)
            else:
                p = p.predecessor
                # p.update_finger_table(self,i)
                self.connect_and_update(p, i)

    def update_finger_table(self, NODE, i):
        """
        If a given node is ith finger of the node itself, update its finger table with that node
        :param NODE: A given node
        :param i: Int
        :return: None
        """
        NODE = deserialize(NODE)
        # print('Node{0}.update_finger_table({1}, {2})'.format(self.ID, NODE.ID, i))
        if is_between(NODE.ID,self.finger_table[i]['start'], self.finger_table[i]['successor'].ID, including_start=True):
            self.finger_table[i]['successor'] = NODE
            # print('-> updated the value of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i,self.ID,NODE.ID))
            p = self.predecessor
            if (p != NODE):
                # print('@update_finger_table: p = {0}'.format(p.ID))
                # p.update_finger_table(NODE, i)
                self.connect_and_update(p, i)
                self.print_finger_table()
