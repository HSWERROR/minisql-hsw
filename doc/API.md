# API模块概述

## 功能描述

​	本模块主要用于连结Interpreter和底层的Record,Catalog和Index模块，API从Interpreter获得查询语句的条件部分并执行相应模块的函数，并将底层的执行结果返回Interpreter。对于一些特定的查询操作，由于传入的条件语句难以直接分割，将使用一些方法进行元素分割及参数提取。本模块实现了create_table, create_index, insert, select, drop_index, drop_table, delete共7种操作的调用，并实现各模块的初始化与写回。

## 函数说明

### 功能调用模块

> 功能模块是Interpreter与Record,Index,Catalog模块的连接，调用了Record,Index,Catalog中的接口，并作为Interpreter的接口，在Interpreter读取SQL语句时引发对应的模块操作并返回操作结果

#### 1.表的创建

```python
def create_table(name, attribute, PK)
```

#### 2.索引创建

```python
def create_index(tname,iname,iattr)
```

#### 3.插入

```python
def insert(tname,values)
```

本函数除需检测插入值的合法性之外，还需要调用Record模块进行数据偏移量的计算，并调用Index, Catalog模块进行index的插入。

#### 4.查询

```python
def select(table,condition)
```

分为有条件的查找与无条件的查找。若为无条件查找，直接通过Record返回查询表的所有tuple；若为有条件查询，则首先对条件进行拆分并调用Index进行查找，在将Index返回的偏移量传入Record，通过偏移量查询结果。

#### 5.删除特定元组

```python
def delete_tuple(tname,condition)
```

分为有条件删除和无条件删除，原理类似查询，查找到目标的tuple后同时删除Record和Index中的记录。

#### 6.删除索引

```python
def drop_index(iname)
```

#### 7.删除表

```python
def drop_table(tname)
```



### 辅助功能模块

> 辅助功能模块不实现SQL功能，仅作为数据库操作的补充

#### 1.初始化与结束

```python
def init_all()
#各模块初始化，用于查询的开始
def finalize_all()
#各模块内部数据写回与模块结束，用于查询结束的数据处理
```

#### 2.查询条件语句处理

```python
def add_space(condition)
```

condition为Interpreter传入的查询条件，考虑到condition可能为不带条件的字符串，分割较为困难，故使用正则方法对语句进行空格替换，将查询要素用空格分隔，方便之后语句分割及信息的提取。

> 例：
>
> condition: 'id>10 and grade<=90'
>
> return: 'id > 10 and grade <= 90'