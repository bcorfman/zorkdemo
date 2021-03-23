import argparse
from adventure.app import Adventure
from adventure.output import MarkdownToHTML
from version import VERSION, BUILD_NUMBER


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='store_true')
    parser.add_argument('--web', action='store_true')
    args = parser.parse_args()
    if args.version:
        print('ZorkDemo ' + VERSION + ' ' + BUILD_NUMBER)
    else:
        if args.web:
            output_strategy = MarkdownToHTML()
            adventure = Adventure(output_strategy)
            adventure.start_page()
        else:
            adventure = Adventure()
            adventure.start_console()


