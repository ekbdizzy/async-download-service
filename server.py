import os
import asyncio
from aiohttp import web
import aiofiles
import logging

logger = logging.getLogger('archivate')

INTERVAL_SECS = 1
PATH_TO_PHOTO = os.path.join(os.getcwd(), 'test_photos/')


def increment(counter=0) -> int:
    while True:
        counter += 1
        yield counter


def convert_to_bytes(kylobytes: int) -> int:
    return kylobytes * 1024


async def archivate(request):
    """Zip photos from PATH_TO_PHOTO/{archive_hash}/ and return it to user."""

    archive_hash = request.match_info['archive_hash']
    path = os.path.join(PATH_TO_PHOTO, archive_hash)
    if not os.path.exists(path):
        raise web.HTTPNotFound(text='Архив не существует или был удален', content_type='text/html')

    connection = asyncio.open_connection()

    command = f'cd {path} && zip -r - .'
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'form-data; name="field1"; filename="archive.zip"'
    await response.prepare(request)

    counter = increment()
    try:
        while True:
            stdout = await process.stdout.read(n=convert_to_bytes(100))
            logger.info(f'Sending archive {archive_hash} chunk {next(counter)}')
            bytes = bytearray(stdout)

            await response.write(bytes)
            await asyncio.sleep(INTERVAL_SECS)

            if not stdout:
                break

            # raise asyncio.CancelledError

    except asyncio.CancelledError:
        logging.debug('Download was interrupted')
        kill_command = f'/bin/bash -c "kill $(pgrep -P {process.pid})"'
        # kill_command = f'/bin/bash -c "echo $(pgrep -P {process.pid})"'
        kill_process = await asyncio.create_subprocess_shell(
            kill_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        process.kill()

    finally:
        connection.close()

    return response


async def uptime_handler(request):
    response = web.StreamResponse()

    response.headers['Content-Type'] = 'text/html'
    await response.prepare(request)

    archive_hash = request.match_info['archive_hash']
    message = os.path.join(PATH_TO_PHOTO, archive_hash)

    await response.write(message.encode('utf-8'))
    await asyncio.sleep(INTERVAL_SECS)


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    logging.basicConfig(
        format='%(levelname)s [%(asctime)s] %(message)s',
        level=logging.DEBUG)


if __name__ == '__main__':
    main()
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
        # web.get('/archive/{archive_hash}/', uptime_handler),
    ])
    web.run_app(app)
