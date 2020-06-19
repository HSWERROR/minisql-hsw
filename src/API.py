import re
import os
import index
import catalog
import record

"""extract_condition用以将interpreter传入的条件转换成二级条件list，如果传入'*'则直接返回空list，仅在本模块内调用"""
"""def extract_condition(table,condition):
    clauses=[]
    if len(condition) == 1 and condition[0] == '*':
        return None
    cnt=0
    tran=condition.split()
    print(tran)
    while(1):
        if cnt+3 > len(tran):
            raise Exception('The query condition is illegal')
        if tran[cnt+1] not in ['<','>','=','<>','>=','<=']:
            raise Exception('The operator '+tran[cnt+1]+' in query is illegal')
        if tran[cnt+1] == '<>':
            tran[cnt+1] = '!='
        if tran[cnt+1] == '=':
            tran[cnt+1] = '=='
        clauses.append([tran[cnt],tran[cnt+1],tran[cnt+2],catalog.get_type_of_attribute(table,tran[cnt]),catalog.get_index_of_attribute(table,tran[cnt])])
        if cnt+3 == len(tran):
            indexname = catalog.get_column_with_index(table)
            index_clause = None
            for clause in clauses:
                if clause[0] in indexname:
                    index_clause = clause
                    break
            res = None

        cnt += 4"""

#利用正则表达式给condition加空格，避免split错误
def add_space(condition):
    condition.replace('>=',' >= ').replace('<=',' <= ').replace('<>',' <> ')
    condition = re.sub('<(?![=>])',' < ',condition)
    condition = re.sub('(?<!<)>(?!=)',' > ',condition)
    condition = re.sub('(?<![<>])=',' = ', condition)
    return condition

"""创建table"""
def create_table(name, attribute, PK):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(name,True)
    pidx=[x[0] for x in attribute].index(PK)
    if len(attribute[pidx]) != 5 or attribute[pidx][-1] != 1:
        raise Exception('Primary key is not a unique attribute!')
    catalog.create_table(name,attribute,PK)
    record.create_table(name)
    for x in attribute:
        if len(x)==5 and x[-1]==1:
            #print(name,x[0])
            index.create_table(name,x[0])
            catalog.create_index(name,x[0],x[0])
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""创建索引"""
def create_index(tname,iname,iattr):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_index(iname,True)
    catalog.create_index(tname,iname,iattr)
    res=record.create_index(tname,catalog.get_index_of_attribute(tname,iattr),catalog.get_type_of_attribute(tname,iattr),catalog.get_length(tname))
    try:
        index.create_index(tname,iname,res)
    except Exception as e:
        raise Exception('Entries sharing same key on the column that is creating index on!')
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""插入新tuple"""
def insert(tname,values):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname,False)
    catalog.check_type(tname,values)
    where=record.insert(tname,values)-catalog.get_length(tname)
    for idx,key in enumerate(values):
        if catalog.get_index_name_by_seq(tname,idx)!=[]:
            for indexname in catalog.get_index_name_by_seq(tname, idx):
                try:
                    index.insert_entry(tname,indexname,key,where)
                except Exception as err:
                    temp_list=catalog.get_index_name_by_seq(tname,idx)
                    for index_del in temp_list[:temp_list.index(indexname)]:
                        index.delete_entries([err],tname,index_del)
                    record.truncate(tname,where)
                    raise Exception('Insertion fails. Data with key: '+str(key)+' already exists.')
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""删除表"""
def drop_table(tname):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname, False)
    index.delete_table(tname)
    catalog.delete_table(tname)
    record.delete_table(tname)
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""删除元组"""
def delete_tuple(tname,condition):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname,False)
    clauses=[]
    if len(condition) == 1 and condition[0] == '*':
        record.delete_record(tname,clauses,catalog.get_length(tname))
        for index_name in catalog.get_index_list(tname):
            index.delete_table_index(tname,index_name)
    else:
        condition=add_space(condition)
        cnt = 0
        tran = condition.split()
        # print(tran)
        while (1):
            if cnt + 3 > len(tran):
                raise Exception('The query condition is illegal')
            if tran[cnt + 1] not in ['<', '>', '=', '<>', '>=', '<=']:
                raise Exception('The operator ' + tran[cnt + 1] + ' in query is illegal')
            if tran[cnt + 1] == '<>':
                tran[cnt + 1] = '!='
            if tran[cnt + 1] == '=':
                tran[cnt + 1] = '=='
            clauses.append([tran[cnt], tran[cnt + 1], tran[cnt + 2], catalog.get_type_of_attribute(tname, tran[cnt]),
                            catalog.get_index_of_attribute(tname, tran[cnt])])
            if cnt+3==len(tran):
                indexname=catalog.get_column_with_index(tname)
                res=record.delete_record(tname,clauses,catalog.get_length(tname))
                for cnt,i in enumerate(catalog.get_type_list(tname)):
                    if i!='char':
                        for j in res:
                            j[cnt]=eval(j[cnt])
                for attribute in catalog.get_column_with_index(tname):
                    attr_id=catalog.get_index_of_attribute(tname,attribute)
                    for indexname in catalog.get_index_name_by_seq(tname,attr_id):
                        index.delete_entries([x[attr_id] for x in res],tname,indexname)
                break
            if tran[cnt + 3] != 'and':
                raise Exception('and expected but ' + tran[cnt + 3] + ' found.')
            cnt += 4
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""删除索引"""
def drop_index(iname):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_index(iname,False)
    catalog.delete_index(iname)
    index.delete_index(iname)
    index.finalize_index()
    catalog.finalize()
    record.finalize()

"""表的查询，返回查询结果"""
def select(table,condition):
    record.init()
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(table,False)
    clauses = []
    if len(condition) == 1 and condition[0] == '*':
        record.select_record(table,catalog.get_column_name(table),clauses,None,catalog.get_length(table))
    else:
        condition=add_space(condition)
        cnt = 0
        tran = condition.split()
        #print(tran)
        while (1):
            if cnt + 3 > len(tran):
                raise Exception('The query condition is illegal')
            if tran[cnt + 1] not in ['<', '>', '=', '<>', '>=', '<=']:
                raise Exception('The operator ' + tran[cnt + 1] + ' in query is illegal')
            if tran[cnt + 1] == '<>':
                tran[cnt + 1] = '!='
            if tran[cnt + 1] == '=':
                tran[cnt + 1] = '=='
            clauses.append([tran[cnt], tran[cnt + 1], tran[cnt + 2], catalog.get_type_of_attribute(table, tran[cnt]),
                            catalog.get_index_of_attribute(table, tran[cnt])])
            if cnt + 3 == len(tran):
                indexname = catalog.get_column_with_index(table)
                index_clause = None
                for clause in clauses:
                    if clause[0] in indexname:
                        index_clause = clause
                        break
                res = None
                if index_clause != None:
                    clauses.remove(index_clause)
                    indexname = catalog.get_index_name(table,index_clause[0])
                    res=index.select_from_table(table,index_clause,indexname[0])
                record.select_record(table,catalog.get_column_name(table),clauses,res,catalog.get_length(table))
                break
            if tran[cnt + 3] != 'and':
                raise Exception('and expected but ' + tran[cnt + 3] + ' found.')
            cnt += 4
    index.finalize_index()
    catalog.finalize()
    record.finalize()

def init_all():
    record.init()
    catalog.init_catalog()
    index.init_index()


def finalize_all():
    index.finalize_index()
    catalog.finalize()
    record.finalize()