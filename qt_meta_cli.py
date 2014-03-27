import quicktime

if __name__ == '__main__':
    movie = open('tim-drm-ref.mov','rb').read()
    movie_atoms = quicktime.AtomTree(movie)
    udta_atoms = movie_atoms.findAllAtomsOfType('udta')
    for atom in udta_atoms:
        print atom
