import mmap


def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


def data_response(data):
    return {"data": data}


def error_response(error):
    return {"error": error}
