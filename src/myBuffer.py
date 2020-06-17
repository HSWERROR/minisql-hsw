import os
import re
import collections

buffer = collections.OrderedDict()
buffer_size = 4096
path = '../dbFile/Record/'

def init():
    pass
def finalize():
    namelist = []
    for name, code in buffer.items():
        tablename, where = re.split('\0', name)
        if tablename not in namelist:
            namelist.append(tablename)
            with open(path+tablename+'.rec','rb+') as fp:
                fp.seek(int(where))
                fp.write(code)

def save_block(tablename, code):
    with open(path+tablename+'.rec','rb+') as fp:
        fp.read()
        if len(buffer) == buffer_size:
            buffer.popitem(last=False)
        buffer[tablename+'\0'+str(fp.tell())] = code.encode(encoding='UTF-8',errors='strict')
        print(buffer[tablename + '\0' + str(fp.tell())])
        fp.write(buffer[tablename+'\0'+str(fp.tell())])
        return fp.tell()

def get_block(tablename, where, length):
    if tablename+'\0'+str(where) in buffer:
        return buffer[tablename+'\0'+str(where)]
    with open(path+tablename+'.rec','rb+') as fp:
        fp.seek(where)
        if len(buffer) == buffer_size:
            buffer.popitem(last=False)
        buffer[tablename+'\0'+str(where)] = fp.read(length)

def create_table(tablename):
    p = open(path+tablename+'.rec','a+')
    p.close()

def delete_table(tablename):
    pass

def change_valid_bit(tablename, loc):
    with open(path+tablename+'.rec','rb+') as fp:
        if tablename+'\0'+str(loc) not in buffer:
            buffer.popitem(last=False)
        lun=list(buffer[tablename+'\0'+str(loc)].decode('utf-8'))
        lun[0] = '\0'
        buffer[tablename+'\0'+str(loc)].join(lun).encode(encoding='UTF-8',errors='strict')
        fp.seek(loc)
        fp.write('0'.encode(encoding='UTF-8',errors='strict'))

def truncate(tablename, where):
    with open(path+tablename+'.rec','rb+') as fp:
        fp.seek(where)
        fp.truncate()
