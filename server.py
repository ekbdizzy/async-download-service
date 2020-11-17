import os
import asyncio
from aiohttp import web
import aiofiles
import logging
import itertools
from functools import partial
from parser_args import parse_args

CHUNK_SIZE_KB = 100

logger = logging.getLogger('main')


def kilobytes_to_bytes(kilobytes: int) -> int:
    return kilobytes * 1024


def set_logging_level(logging_is_active: bool):
    if logging_is_active:
        return logging.DEBUG
    return logging.ERROR


async def archivate(request, path_to_photos, timeout):
    """Zip photos from PATH_TO_PHOTO/{archive_hash}/ and return it to user."""

    archive_hash = request.match_info['archive_hash']
    path = os.path.join(path_to_photos, archive_hash)
    if not os.path.exists(path):
        raise web.HTTPNotFound(text='Архив не существует или был удален', content_type='text/html')

    command = ['zip', '-r', '-', '.']
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'form-data; filename="archive.zip"'
    await response.prepare(request)

    try:
        for counter in itertools.count(1):

            stdout_chunk = await process.stdout.read(n=kilobytes_to_bytes(CHUNK_SIZE_KB))

            if not stdout_chunk:
                logger.info('Archive is uploaded.')
                break

            logger.info(f'Sending archive {archive_hash} chunk {counter}')
            await response.write(stdout_chunk)
            await asyncio.sleep(timeout)

    except asyncio.CancelledError:
        logging.info('Download was interrupted.')
        try:
            process.kill()
        except ProcessLookupError:
            pass
        raise

    finally:
        await process.communicate()

        try:
            process.kill()
        except ProcessLookupError:
            pass

        if process.returncode == 9:
            logging.info('KeyboardInterrupt')

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


def main():
    args = parse_args()
    PATH_TO_PHOTOS = args.path_to_photos
    TIMEOUT = args.timeout

    logging.basicConfig(
        format='%(levelname)s [%(asctime)s] %(message)s',
        level=set_logging_level(args.logging_is_active))
    partial_archivate = partial(archivate, path_to_photos=PATH_TO_PHOTOS, timeout=TIMEOUT)

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', partial_archivate),
    ])
    web.run_app(app)


if __name__ == '__main__':
    main()
