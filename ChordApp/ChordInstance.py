#!usr/bin/env python3
"""
    ChordInstance.py - Contains Node class and ChordInstance class
    Author: Nidesh Chitrakar (nideshchitrakar@bennington.edu)
            Hoanh An
    Date: 10/30/2017
"""
from node import Node
from utils import *

from const import m

class ChordInstance(object):
    """
        Each Chord Instance contains the information about its node and maintains
        a finger table, its successor, and its predecessor.
    """
    def __init__(self, IP_ADDRESS, PORT, ID):
        self.IP_ADDRESS = IP_ADDRESS
        self.PORT = PORT
        self.NODE = Node(IP_ADDRESS, PORT, ID)
        self.ID = ID
        self.finger_table = self.create_finger_table()
        # set own successor and predecessor to self, i.e., the node is unattached
        self.successor = self
        self.predecessor = self

    def create_finger_table(self):
        """
            Create a simple finger table of size m*2 with the start values generated
            by ID + 2^i where 0 <= i < m.
            All the successor values are set to self, i.e., the chord instance does
            not know about other nodes in the ring.
        """
        finger_table = []
        for i in range(0,m):
            finger_table.append({})
            finger_table[i]['start'] = constrain(self.NODE.ID + (2**i))
            finger_table[i]['successor'] = self
        return finger_table

    def print_finger_table(self):
        """
            Prints the finger table of a node.
        """
        print('finger_table of node {0}'.format(self.ID))
        for i in range (0,m):
            print(self.finger_table[i]['start'], self.finger_table[i]['successor'].ID)

    def find_successor(self, ID):
        print('Node{0}.find_successor({1}): finding successor of ID {2}'.format(self.ID,ID,ID))
        n0 = self.find_predecessor(ID)
        print('-> Successor: {0}'.format(n0.finger_table[0]['successor'].ID))
        return n0.finger_table[0]['successor']

    def find_predecessor(self,ID):
        print('Node{0}.find_predecessor({1}): finding predecessor of ID {2}'.format(self.ID,ID,ID))
        n0 = self
        while not is_between(ID, n0.ID, n0.finger_table[0]['successor'].ID, including_end=True):
            n0 = n0.closest_preceding_node(ID)
        print('-> Predecessor: {0}'.format(n0.ID))
        return n0

    def closest_preceding_node(self, ID):
        print('Node{0}.closest_preceding_node({1}): finding closest_preceding_node of ID {2}'.format(self.ID,ID,ID))
        n = m-1
        for i in range(n, -1, -1):    # from i = m-1 downto 0
            print(' -> i = {0}'.format(i))
            if is_between(self.finger_table[i]['successor'].ID, self.ID, ID):
                return self.finger_table[i]['successor']
        return self

    def join(self, NODE):
        print('')
        print('Node{0}.join({1}): joining {2} to {3}'.format(self.ID,NODE,self.ID,NODE))
        print('')
        if (NODE != None):
            self.init_finger_table(NODE)
            self.update_others()
            for i in range(1,m):
                self.predecessor.update_finger_table(self,i)
        else:
            for i in range(0,m):
                self.finger_table[i]['successor'] = self
            self.predecessor = self

    def init_finger_table(self, NODE):
        print('Node{0}.init_finger_table({1}): init finger_table of node {2}'.format(self.ID,NODE.ID,self.ID))
        self.finger_table[0]['successor'] = NODE.find_successor(self.finger_table[0]['start'])
        self.successor = self.finger_table[0]['successor']
        print('-> updated successor of finger_table[0][\'successor\'] of node {0} to {1}'.format(self.ID,self.finger_table[0]['successor'].ID))
        self.predecessor = self.successor.predecessor
        self.successor.predecessor = self
        self.predecessor.successor = self
        self.predecessor.finger_table[0]['successor'] = self
        print('-> set predecessor of node {0} to {1}'.format(self.ID, self.predecessor.ID))
        print('-> set predecessor of node {1} to {0}'.format(self.ID, self.finger_table[0]['successor'].ID))

        for i in range(0,m-1):
            print('i = {0}'.format(i))
            self.print_finger_table()
            if is_between(self.finger_table[i+1]['start'], self.ID, self.finger_table[i]['successor'].ID, including_start=True):
                print('Value {0} is in [{1},{2}]'.format(self.finger_table[i+1]['start'],self.ID,self.finger_table[i]['successor'].ID))
                self.finger_table[i+1]['successor'] = self.finger_table[i]['successor']
                print('-> updated the successor of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i+1,self.ID,self.finger_table[i]['successor'].ID))
            else:
                print('Value {0} is not in [{1},{2}]'.format(self.finger_table[i+1]['start'],self.ID,self.finger_table[i]['successor'].ID))
                self.finger_table[i+1]['successor'] = NODE.find_successor(self.finger_table[i+1]['start'])
                print('-> updated the successor of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i+1,self.ID,NODE.find_successor(self.finger_table[i-1]['start']).ID))

    def update_others(self):
        print('Node{0}.update_others(): update finger_table of other nodes'.format(self.ID))
        for i in range(0,m):
            val = constrain(self.ID - 2**(i))
            print('find predecessor of={1}, val={0}'.format(val, self.ID - 2**(i)))
            p = self.find_predecessor(val)
            print('predecessor of {0} is {1}'.format(val, p.ID))
            print('Update finger table of Node {0}'.format(p.ID))
            if (p != self):
                p.update_finger_table(self, i)
            else:
                p = p.predecessor
                p.update_finger_table(self,i)

    def update_finger_table(self, NODE, i):
        print('Node{0}.update_finger_table({1}, {2})'.format(self.ID, NODE.ID, i))
        if is_between(NODE.ID,self.finger_table[i]['start'], self.finger_table[i]['successor'].ID, including_start=True):
            self.finger_table[i]['successor'] = NODE
            print('-> updated the value of finger_table[{0}][\'successor\'] of Node {1} to {2}'.format(i,self.ID,NODE.ID))
            p = self.predecessor
            if (p != NODE):
                print('@update_finger_table: p = {0}'.format(p.ID))
                p.update_finger_table(NODE, i)
                self.print_finger_table()



if __name__ == '__main__':
    chord1 = ChordInstance('0.0.0.0', 9000, 4)
    chord2 = ChordInstance('127.0.0.1', 9001, 0)
    chord3 = ChordInstance('192.168.1.1', 9002, 1)
    # chord4 = ChordInstance('192.168.1.1', 9003, 13)
    # chord5 = ChordInstance('192.168.1.1', 9004, 255)
    # chord6 = ChordInstance('192.168.1.1', 9005, 35000)
    # chord1.print_finger_table()
    # chord2.print_finger_table()
    # chord3.print_finger_table()
    # chord4.print_finger_table()
    chord1.join(None)
    chord2.join(chord1)
    # chord1.print_finger_table()
    # chord2.print_finger_table()
    # #print('successor of node 1 = {0}'.format(chord1.successor.ID))
    chord3.join(chord2)
    # chord1.print_finger_table()
    # chord2.print_finger_table()
    # chord3.print_finger_table()
    # chord4.join(chord2)
    # chord5.join(chord4)
    # chord6.join(chord3)
    chord1.print_finger_table()
    chord2.print_finger_table()
    chord3.print_finger_table()
    # chord4.print_finger_table()
    # chord5.print_finger_table()
    # chord6.print_finger_table()
    # nodes = [chord1,chord2,chord3,chord4,chord5,chord6]
    # for node in nodes:
    #     print(' >> Node {0}\'s successor is node {1}.'.format(node.ID,node.successor.ID))
    # print(chord1.finger_table[0]['successor'].ID)
    # print(chord1.successor.ID)
