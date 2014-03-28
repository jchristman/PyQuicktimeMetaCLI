# Library written by Joshua Christman
# This file is meant purely as an interface for Parsing the atom tree from a 
# quicktime movie file (mp4, m4v, mov, etc). It was written using Apple's 
# file format definition.

import struct, string

### GLOBALS ###
# This was stolen from a java library
ATOM_CONTAINER_TYPES = ["moov", "trak", "udta", "tref", "imap",
        "mdia", "minf", "stbl", "edts", "mdra", 
        "rmra", "imag", "vnrp", "dinf"]
# END GLOBALS #

### HELPER FUNCTIONS ###
printable = string.ascii_letters + string.digits + string.punctuation + ' '
def hex_escape(s):
    return ''.join(c if c in printable else r'\x{0:02x}'.format(ord(c)) for c in s)
### END HELPER FUNCTIONS ###

### Atom Tree Class ###
class AtomTree:
    def __init__(self, movie):
        self.movie = movie
        offset = self.movie.find('moov')-4
        self.root = AtomTree.Atom(self, offset)
        self.expandTree()

    def expandTree(self):
        self.expandTreeHelper(self.root)

    def expandTreeHelper(self, parent):
        parent.generateChildren()
        for child in parent.children:
            self.expandTreeHelper(child)

    # This function takes a path of form 'moov.udta.meta' and returns the atom object
    # or False if it does not exist
    def getAtomByPath(self, path):
        cur = self.root
        for step in path.split('.')[1:]: # We don't need the first step of moov
            prev = cur
            for child in cur.children:
                if child.type == step:
                    cur = child
                    break
            if prev == cur: # Then we didn't find a child with the next step of the path
                return False
        return cur
        
    def serialize(self):
        return self.root.serialize()

    def printTree(self):
        self.printTreeHelper(self.root, 0)

    def printTreeHelper(self, parent, depth):
        print '  ' * depth + parent.type + ' - %d bytes' % parent.size
        for child in parent.children:
            self.printTreeHelper(child, depth + 1)
        
    ### Atom Data Class ###
    class Atom:
        def __init__(self, tree, offset=False, type=False, data=False, parent=None):
            self.tree = tree
            self.parent = parent
            if not type and not data:
                self.size = struct.unpack('>L', self.tree.movie[offset : offset + 4])[0]
                self.type = self.tree.movie[offset + 4 : offset + 8]
                self.data = self.tree.movie[offset + 8 : offset + self.size]
                self.offset = offset
            else:
                self.setAtomData(type, data)
            self.children = []

        def setAtomData(self, type=False, data=False):
            if not type == False:   self.type = type
            if not data == False:   self.data = data
            self.size = 8 + len(self.data)

        def generateChildren(self):
            try: offset = self.offset + 8 # If we don't know our offset, we can't get our children
            except: return False
            
            if not self.type in ATOM_CONTAINER_TYPES: # Then we aren't a container of atoms
                return False
            
            while offset < self.offset + self.size:
                if self.type == 'udta':
                    if offset + 4 >= self.offset + self.size: # This is the optional null terminating 32 bit integer
                        break
                child = AtomTree.Atom(self.tree, offset, parent=self)
                self.children.append(child)
                offset += child.size

            return True

        def serialize(self):
            return struct.pack('>L', self.size) + self.type + self.data

        def __str__(self):
            return "Atom Data:\n\tSize: %d\n\tType: %s\n\tData: %s" % (self.size, self.type, hex_escape(self.data))
