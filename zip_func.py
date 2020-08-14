import os
import subprocess as sp

path = 'test_photos/'

archive: str

command = ['zip', '-r', '-', path]

result = sp.run(command, stdout=sp.PIPE)

with open('archive.zip', 'w+b') as f:
    bytes = bytearray(result.stdout)
    f.write(bytes)
