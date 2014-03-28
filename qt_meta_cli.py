#!/usr/bin/python

import quicktime, sys

usage = '''
./qt_meta_cli.py <MOVIE_PATH>
'''

if __name__ == '__main__':
    try: movie_path = sys.argv[1]
    except: print usage; exit()
    movie = open('tim-drm-ref.mov','rb').read()
    movie_atoms = quicktime.AtomTree(movie)
    meta_atom = movie_atoms.getAtomByPath('moov.udta.meta')
    if not meta_atom:
        print 'No metadata atom was found at path moov.udta.meta!'
        print 'Creating one now'
