

def handle_uploaded_file(fs) -> str:
    ret = []
    for chunk in fs.chunks():
        ret.append(str(chunk, 'utf-8'))
    return ','.join(ret)


# 当前处理是读取数据的list
def handle_uploadedExcelFile(fileHandler):
    if fileHandler is not None:
        return [str(record[0]) for record in fileHandler.iget_array() if record is not None and len(record) > 0]
    else:
        return None


def file_iterator(file, chunk_size=512):
    with open(file) as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break
