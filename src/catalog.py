import json
import os
import index


path = './'

fp = None
tablelist = None

def init_catalog():
    '''
    初始化，打开json并读入数据
    '''
    global fp, tablelist
    fp = open(path+'table.sqlf','a+')
    fp.seek(0)
    if fp.read()=="":  
        fp.write("{}")
        fp.seek(0)
    fp.seek(0)
    tablelist = json.loads(fp.read())

def finalize():
    '''
    将数据写入json并关闭文件
    '''
    fp.seek(0)
    fp.truncate()
    fp.write(json.dumps(tablelist))
    fp.close()

def exist_table(tablename, boolean):
    '''
    判断数据表是否存在，若不存在/存在，则对应类型报错
    tablename:string类型，数据表名称
    boolean:boolean类型，若为True则当数据表存在便报错，若为False则当数据表不存在便报错
    '''
    if (tablename in tablelist) if boolean else (tablename not in tablelist):
        raise Exception('Table '+tablename+' already exists.') if boolean else Exception('Table '+tablename+' does not exist.')

def create_table(tablename, attributes,primary):
    '''
    新建数据表
    tablename：string类型，为数据表名称。
    attributes：list类型，包含若干个子list，子list为[属性名，属性类型，字符串中含有的字符数（若为int、float类型则为0）,空列表，0]。
    primary：string类型，为主键名称。
    '''
    if primary==None:
        raise Exception('primary key must be specified.')
    m = {"primary":[x[0] for x in attributes].index(primary),"columns":{}}
    for x in attributes:
        m["columns"][x[0]]=x[1:]
    m['columns'][primary][-1] = 1
    m['columns'][primary][-2].append(primary)
    tablelist[tablename]=m

def delete_table(tablename):
    '''
    删除数据表，无返回值
    tablename：string类型，为数据表名称。
    '''
    tablelist.pop(tablename)

def get_index_of_attribute(tablename, attribute_name):
    '''
    获取表中属性所在的序号（并不是索引）；返回值为number类型
    tablename\attribute_name：string类型，为数据表、属性的名称
    '''
    return list(tablelist[tablename]['columns'].keys()).index(attribute_name)

def get_type_of_attribute(tablename,attribute_name):
    '''
    获取表中属性的数据类型；返回值为string类型
    tablename\attribute_name：string类型，为数据表、属性的名称
    '''
    return tablelist[tablename]['columns'][attribute_name][0]

def get_type_list(tablename):
    '''
    返回一个包含当前数据表中所有属性类型的list
    tablename：string类型，为数据表名称。
    '''
    return [x[0] for x in  tablelist[tablename]['columns'].values()]

def get_index_list(tablename):
    '''
    返回一个包含当前数据表中所有索引名的list
    tablename：string类型，为数据表名称。
    '''
    l=[]
    [[l.append(y) for y in x[-2]] for x in tablelist[tablename]['columns'].values()]
    return l

def get_column_with_index(tablename):
    '''
    返回一个包含当前数据表中所有拥有索引的列的list
    tablename：string类型，为数据表名称。
    '''
    res = []
    for key,value in tablelist[tablename]['columns'].items():
        if value[2] != []:
            res.append(key)
    return res

def get_column_name(tablename):
    '''
    返回数据表中所有的列名，返回值为包含所有列表名的list类型
    tablename：string类型，为数据表名称
    '''
    return list(tablelist[tablename]['columns'].keys())

def get_index_name(tablename,attribute):
    '''
    返回一个list，包含tablename中的attribute属性拥有的索引
    '''
    return tablelist[tablename]['columns'][attribute][-2]

def get_index_name_by_seq(tablename,index):
    '''
    返回一个list，包含tablename中第index个属性拥有的索引
    '''
    return tablelist[tablename]['columns'][list(tablelist[tablename]['columns'].keys())[index]][-2]

def check_type(tablename,input_list):
    '''
    检查输入是否合法,若不合法会报错，并返回经处理后该元组的list
    input_list:为包含要insert的项的list，其中每一项均应为str类型（非强制）
    返回值为已经将input成功转换成对应类型的list(如input_list中为str，且合法，则输出为int)
    '''
    values = []
    for inp,(name,attribute) in zip(input_list,tablelist[tablename]['columns'].items()):
        if attribute[0]=='int':
            inp=str(inp)
            if inp.isdigit()==False:
                raise Exception('The '+inp+' should be int type.')
            value = int(inp)
            values.append(value)
        elif attribute[0]=='float':
            inp=str(inp)
            if inp.isdigit()==False:
                raise Exception('The '+inp+' should be float type.')
            value = float(inp)
            values.append(value)
        else:
            if len(inp)>int(attribute[1]):
                raise Exception(name + ' has maximum length '+ str(attribute[1])+'.')
            values.append(inp)
        index.check_unique(tablename,"Uni_"+name,inp)
    return values

def create_index(tablename, indexname, columnname):
    '''
    在tablename表中，给columnname列创建一个名为indexname的索引
    若该列已经存在名为indexname的索引便报错。
    '''
    for attr in tablelist[tablename]['columns'].keys():
        if indexname in tablelist[tablename]['columns'][attr][2]:
            raise Exception('Index already exists: {}->{}({})'.format(tablename,attr,indexname))
    tablelist[tablename]['columns'][columnname][2].append(indexname)

def delete_index(indexname):
    '''
    在tablename表中，删除indexname这一索引，无返回值
    '''
    for tablename in tablelist: 
        for attr in tablelist[tablename]['columns'].keys():
            if indexname in tablelist[tablename]['columns'][attr][-2]:
                tablelist[tablename]['columns'][attr][-2].remove(indexname)
def get_length(tablename):
    return 255*len(tablelist[tablename]['columns'].keys())+1

def exist_index(tablename,indexname,boolean):
    '''
    判断索引是否存在，若不存在/存在，则对应类型报错
    indexname:string类型，索引名称
    boolean:boolean类型，若为True则当索引存在便报错，若为False则当索引不存在便报错
    '''
    flag=0
    for tablename in tablelist:
        for attr in tablelist[tablename]['columns'].keys():
            if indexname in tablelist[tablename]['columns'][attr][-2] and boolean:
                raise Exception('Index already exists: {}->{}({})'.format(tablename,attr,indexname))
            if indexname in tablelist[tablename]['columns'][attr][-2] and not boolean:
                flag=1
    if flag==0 and not boolean:
        raise Exception('No {} index exists.'.format(indexname))
    


#init_catalog()
    ##exist_table("school1",True)
    #create_table("school3",[["cnmae", "char", 10, [], 0],["grade", "int", 0, [], 0]],"grade")
    ##create_index("school1","hello","teacher_num")
    ##check_type("school1",["12345","hellofhdjgi","20"])
    #exist_index("school1","hello1",False)
    #delete_index("school1")
#finalize()
