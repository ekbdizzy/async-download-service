import os
import argparse

from dotenv import load_dotenv

load_dotenv()
PHOTO_FOLDER = os.getenv('PHOTO_FOLDER') or 'test_photos'


def parse_args():
    """Parse args from command line. Available args:
    --log, -l: switch logging level from ERROR to DEBUG
    --timeout, -t: add timeout in seconds
    --path, -p: set path to folder with photos."""

    parser = argparse.ArgumentParser(description='Start server with async download service')

    parser.add_argument('--log', '-l',
                        action='store_true',
                        default=False,
                        help='switch logging level from ERROR to INFO',
                        dest='logging_is_active'
                        )

    parser.add_argument('--timeout', '-t',
                        action='store',
                        type=int,
                        default=os.getenv('TIMEOUT') or 0,
                        help='add timeout in seconds',
                        dest='timeout'
                        )

    parser.add_argument('--path', '-p',
                        action='store',
                        type=str,
                        dest='path_to_photos',
                        help=f'set path to folder with photos, default is {PHOTO_FOLDER}',
                        default=os.path.join(os.getcwd(), PHOTO_FOLDER)
                        )

    return parser.parse_args()
