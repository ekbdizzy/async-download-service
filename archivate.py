import os
import asyncio

path = 'test_photos/'
archive_file_name = 'archive.zip'

if os.path.exists(archive_file_name):
    os.remove(archive_file_name)
    print('Old archive removed')


def convert_to_bytes(kylobytes: int) -> int:
    return kylobytes * 1024


async def archivate(path):
    command = f'zip -r - {path}'

    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    while True:
        stdout = await process.stdout.read(n=convert_to_bytes(100))

        if not stdout:
            break

        with open(archive_file_name, 'a+b') as f:
            bytes = bytearray(stdout)
            f.write(bytes)


if __name__ == '__main__':
    asyncio.run(archivate(path))
