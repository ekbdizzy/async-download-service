import os
import asyncio
from aiohttp import web
import aiofiles
import logging
import utils
from argparser import parse_args
from typing import Union

args = parse_args()
PATH_TO_PHOTOS = args.path_to_photos
TIMEOUT = args.timeout

logger = logging.getLogger('archivate')


def set_logging_level(logging_is_active: bool):
    if logging_is_active:
        return logging.DEBUG
    return logging.ERROR


def main():
    logging.basicConfig(
        format='%(levelname)s [%(asctime)s] %(message)s',
        level=set_logging_level(args.logging_is_active))


async def archivate(request):
    """Zip photos from PATH_TO_PHOTO/{archive_hash}/ and return it to user."""

    archive_hash = request.match_info['archive_hash']
    path = os.path.join(PATH_TO_PHOTOS, archive_hash)
    if not os.path.exists(path):
        raise web.HTTPNotFound(text='Архив не существует или был удален', content_type='text/html')

    connection = asyncio.open_connection()

    command = ['zip', '-r', '-', '.']
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'form-data; name="field1"; filename="archive.zip"'
    await response.prepare(request)

    counter = utils.increment()
    try:
        while True:
            stdout = await process.stdout.read(n=utils.convert_to_bytes(100))
            logger.info(f'Sending archive {archive_hash} chunk {next(counter)}')
            bytes = bytearray(stdout)

            await response.write(bytes)
            await asyncio.sleep(TIMEOUT)

            if not stdout:
                break

    except asyncio.CancelledError:
        logging.info('Download was interrupted')

        try:
            stdout, stderr = await process.communicate()
            process.kill()
        except ProcessLookupError:
            asyncio.set_event_loop(asyncio.new_event_loop())
            logger.warning('KeyboardInterrupt')

    finally:
        connection.close()

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    main()
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
    ])
    web.run_app(app)
