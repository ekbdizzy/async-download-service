import os
import argparse
from dotenv import load_dotenv

load_dotenv()


def parse_args():
    """Parse args from command line. Available args:
    --log, -l: switch logging level from ERROR to DEBUG
    --timeout, -t: add timeout in seconds
    --path, -p: set path to folder with photos."""

    parser = argparse.ArgumentParser(description='Description of parser')

    parser.add_argument('--log', '-l',
                        action='store_true',
                        default=False,
                        help='switch logging level from ERROR to INFO',
                        dest='logging_is_active'
                        )

    parser.add_argument('--timeout', '-t',
                        action='store',
                        metavar='',
                        type=int,
                        default=os.getenv('TIMEOUT') or 0,
                        help='add timeout in seconds',
                        dest='timeout'
                        )

    parser.add_argument('--path', '-p',
                        action='store',
                        metavar='',
                        type=str,
                        dest='path_to_photos',
                        help='set path to folder with photos',
                        default=os.path.join(os.getcwd(), os.getenv('PHOTO_FOLDER'))
                        )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    print(args)
