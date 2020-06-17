import re
import os
import index
import catalog
import record

"""extract_condition用以将interpreter传入的条件转换成二级条件list，如果传入'*'则直接返回空list，仅在本模块内调用"""
def extract_condition(condition):
    clau=[]
    if len(condition) == 1 and condition[0] == '*':
        return None
    cnt=0
    while(1):
        if cnt+3 > len(condition):
            raise Exception('The query condition is illegal')
        if condition[cnt+1] not in ['<','>','=','<>','>=','<=']:
            raise Exception('The operator '+condition[cnt+1]+' in query is illegal')
        if condition[cnt+1] == '<>':
            condition[cnt+1] = '!='
        if condition[cnt+1] == '=':
            condition[cnt+1] = '=='
        clau.append([condition[cnt],condition[cnt+1],condition[cnt+2]])
        if cnt+3 == len(condition):
            return clau
        cnt += 4

"""创建table"""
def create_table(name, attribute, PK):
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
    index.finalize_index()
    catalog.finalize()

"""创建索引"""
def create_index(tname,iname,iattr):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_index(iname,True)
    index.create_index(tname,iname,iattr)
    catalog.create_index(tname,iname,iattr)
    index.finalize_index()
    catalog.finalize()

"""插入新tuple"""
def insert(tname,values):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname,False)
    catalog.check_type(tname,values)
    index_name=catalog.get_column_with_index(tname)
    key=[]
    for dex in index_name:
        idx=catalog.get_index_of_attribute(tname,dex)
        key.append(values[idx])
    index.insert_entry(tname,index_name,key,values)
    record.insert(tname,values)
    index.finalize_index()
    catalog.finalize()

"""删除表"""
def drop_table(tname):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname, False)
    index.delete_table(tname)
    catalog.delete_table(tname)
    record.delete_table(tname)
    index.finalize_index()
    catalog.finalize()

"""删除元组"""
def delete_tuple(tname,condition):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(tname,False)
    clause=extract_condition(condition)
    length=catalog.get_length(tname)
    index_name = catalog.get_column_with_index(tname)
    where=record.delete_record(tname, clause, length)
    index.delete_entries(where,tname,index_name)
    index.finalize_index()
    catalog.finalize()

"""删除索引"""
def drop_index(iname):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_index(iname,False)
    catalog.delete_index(iname)
    index.delete_index(iname)
    index.finalize_index()
    catalog.finalize()

"""表的查询，返回查询结果"""
def select(table,condition):
    catalog.init_catalog()
    index.init_index()
    catalog.exist_table(table,False)
    clause=extract_condition(condition)
    attr_list=catalog.get_column_name(table)
    length=catalog.get_length(table)
    index_name=catalog.get_column_with_index(table)
    where=index.select_from_table(table,clause,index_name)
    record.select_record(table,attr_list,clause,where,length)
    index.finalize_index()
    catalog.finalize()

def init_all():
    catalog.init_catalog()
    index.init_index()

def finalize_all():
    index.finalize_index()
    catalog.finalize()