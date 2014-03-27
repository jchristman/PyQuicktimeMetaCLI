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

def find_all(string, sub, listindex=[], offset=0):
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex
### END HELPER FUNCTIONS ###

### Atom Tree Class ###
class AtomTree:
    def __init__(self, movie):
        self.movie = movie
        offset = self.movie.find('moov')-4
        self.root = AtomTree.Atom(self, offset)
        self.root.getChildren()

    def printTree(self):
        depth = 0
        current = self.root
        while True:
            print '\t' * depth + current.type
            for child in current.children:
                
        
    ### Atom Data Class ###
    class Atom:
        def __init__(self, tree, offset):
            self.tree = tree
            self.size = struct.unpack('>L', self.tree.movie[offset : offset + 4])[0]
            self.type = self.tree.movie[offset + 4 : offset + 8]
            self.data = self.tree.movie[offset + 8 : offset + self.size]
            self.offset = offset
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
            
            if self.type == 'udta': # Then jump ahead 4
                offset += 4

            while offset < self.offset + self.size:
                child = AtomTree.Atom(self.tree, offset)
                self.children.append(child)
                offset += child.size

            return True

        def serialize(self):
            return struct.pack('>L', self.size) + self.type + self.data

        def __str__(self):
            return "Atom Data:\n\tSize: %d\n\tType: %s\n\tData: %s" % (self.size, self.type, hex_escape(self.data))


### Movie Metadata Editor
class MovieMetaEditor:
    def __init__(self, fileLoc):
        self.movie = open(fileLoc, 'rb').read()

    def getMetaAtom(self):
        udta_offsets = find_all(self.movie, 'udta')
        for offset in udta_offsets:
            offset -= 4 # Move from the tag backwards to the size
            udta = Atom(self.movie, offset)
            udta_end = offset + udta.size

            offset += 8 # Move the offset forwards past the type
            while offset < udta_end:
                atom = Atom(self.movie, offset)
                if atom.type == 'meta': # We found the metadata atom!
                    return atom
                offset += atom.size
        return None

    def setMetaAtom(self, new_atom):
        udta_offsets = find_all(self.movie, 'udta')
        for offset in udta_offsets:
            offset -= 4 # Move from the tag backwards to the size
            udta = Atom(self.movie, offset)
            udta_end = offset + udta.size

            offset += 8 # Move the offset forwards past the type
            while offset < udta_end:
                atom = Atom(self.movie, offset)
                if atom.type == 'meta': # We found the metadata atom. Now surgically implant the new atom.
                    self.movie = self.movie[ : offset] + new_atom.serialize() + self.movie[offset + atom.size : ]
                    return True
                offset += atom.size
        return False

    def deleteSubAtoms(self, atom, sub_atom_type):
        removeAtoms = []
        offset = 4 # Because meta atoms have 4 garbage bytes
        while offset < atom.size - 8:
            sub_atom = Atom(atom.data, offset)
            if sub_atom.type == sub_atom_type:
                removeAtoms.append((sub_atom, offset))
            offset += sub_atom.size

        for sub_atom,offset in reversed(removeAtoms):
            atom.data = atom.data[ : offset] + atom.data[offset + sub_atom.size : ]

        return atom

    def writeMovieToFile(self, fileLoc):
        with open(fileLoc, 'wb') as file:
            file.write(self.movie)

if __name__ == '__main__':
    movie = open('tim-drm-ref.mov','rb').read()
    movie_atoms = AtomTree(movie)
    print movie_atoms.root
            
