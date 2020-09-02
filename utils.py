def increment(counter=0) -> int:
    while True:
        counter += 1
        yield counter


def convert_to_bytes(kilobytes: int) -> int:
    return kilobytes * 1024
