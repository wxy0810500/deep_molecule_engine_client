
def handle_uploaded_file(fs) -> str:
    ret = []
    for chunk in fs.chunks():
        ret.append(str(chunk, 'utf-8'))
    return ','.join(ret)


def handle_uploadedExcelFile(fileHandler):
    pass


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
