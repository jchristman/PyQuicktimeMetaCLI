import struct, string

### GLOBALS ###
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
        parent.getChildren()
        for child in parent.children:
            self.expandTreeHelper(child)

    def findAllAtomsOfType(self, type):
        atoms = []
        self.findAllAtomsHelper(self.root, type, atoms)
        return atoms
        
    def findAllAtomsHelper(self, parent, type, atoms):
        for child in parent.children:
            if child.type == type:
                atoms.append(child)
            self.findAllAtomsHelper(child, type, atoms)

    def serialize(self):
        self.fixAtomSizes()
        return self.root.serialize()

    def fixAtomSizes(self):
        self.fixAtomSizesHelper(self.root)

    def fixAtomSizesHelper(self, parent):
        size = 8
        if len(parent.children) == 0:
            return
        for child in parent.children:
            size += child.size
            self.fixAtomSizesHelper(child)
        parent.size = size

    def printTree(self):
        self.printTreeHelper(self.root, 0)

    def printTreeHelper(self, parent, depth):
        print '  ' * depth + parent.type + ' - %d bytes' % parent.size
        for child in parent.children:
            self.printTreeHelper(child, depth + 1)
        
    ### Atom Data Class ###
    class Atom:
        def __init__(self, tree, offset=False, type=False, data=False):
            self.tree = tree
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

        def getChildren(self):
            try: offset = self.offset + 8 # If we don't know our offset, we can't get our children
            except: return False
            
            if not self.type in ATOM_CONTAINER_TYPES: # Then we aren't a container of atoms
                return False
            
            while offset < self.offset + self.size:
                if self.type == 'udta':
                    if offset + 4 >= self.offset + self.size: # This is the optional null terminating 32 bit integer
                        break
                child = AtomTree.Atom(self.tree, offset)
                self.children.append(child)
                offset += child.size

            return True

        def serialize(self):
            return struct.pack('>L', self.size) + self.type + self.data

        def __str__(self):
            return "Atom Data:\n\tSize: %d\n\tType: %s\n\tData: %s" % (self.size, self.type, hex_escape(self.data))
