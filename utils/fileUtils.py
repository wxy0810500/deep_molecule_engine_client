

def handleUploadedFile(fs) -> str:
    ret = []
    for chunk in fs.chunks():
        ret.append(str(chunk, 'utf-8'))
    return ','.join(ret)


# 当前处理是读取数据的Set，有效值100个
def getInputDataSetFromUploadedExcel(fileHandler):
    if fileHandler is not None:
        smilesSet = set()
        i = 0
        for record in fileHandler.iget_array():
            if record is not None:
                smilesSet.add(str(record[0]))
                i = i + 1
                if i == 100:
                    break
        return smilesSet
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
