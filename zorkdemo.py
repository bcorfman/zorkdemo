import argparse
from adventure.app import Adventure
from adventure.output import MarkdownToHTML
try:
    from adventure.util import BUILD_NUMBER  # this is appended to the util module during GitHub Actions deployment
except ImportError:
    BUILD_NUMBER = ""  # default to an empty string if we can't find a build number

VERSION = '0.3'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--web', action='store_true')
    args = parser.parse_args()
    if args.version:
        print('ZorkDemo ' + VERSION + ' Build ' + BUILD_NUMBER)
    else:
        if args.web:
            output_strategy = MarkdownToHTML()
            adventure = Adventure(output_strategy)
            adventure.start_page()
        else:
            adventure = Adventure()
            adventure.start_console()
