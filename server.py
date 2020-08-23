import os
import asyncio
from aiohttp import web
import aiofiles

INTERVAL_SECS = 1
PATH_TO_PHOTO = os.path.join(os.getcwd(), 'test_photos/')


def convert_to_bytes(kylobytes: int) -> int:
    return kylobytes * 1024


async def archivate(request):
    archive_hash = request.match_info['archive_hash']
    path = os.path.join(PATH_TO_PHOTO, archive_hash)
    command = f'cd {path} && zip -r - .'

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    response = web.StreamResponse()
    response.headers['Content-Disposition'] = 'form-data; name="field1"; filename="archive.zip"'
    await response.prepare(request)

    while True:
        stdout = await process.stdout.read(n=convert_to_bytes(100))
        bytes = bytearray(stdout)

        await response.write(bytes)
        await asyncio.sleep(INTERVAL_SECS * 0.1)

        if not stdout:
            break
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


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archivate),
        # web.get('/archive/{archive_hash}/', uptime_handler),
    ])
    web.run_app(app)
