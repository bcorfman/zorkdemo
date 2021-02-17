import argparse
from adventure.app import Adventure
try:
    from adventure.util import BUILD_NUMBER  # this is appended to the util module during GitHub Actions deployment
except AttributeError:
    BUILD_NUMBER = ""  # default to an empty string if we can't find a build number

VERSION = '0.2'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true')
    args = parser.parse_args()
    if args.version:
        print('ZorkDemo ' + VERSION + ' Build ' + BUILD_NUMBER)
    else:
        adventure = Adventure()
        adventure.start_game_loop()
