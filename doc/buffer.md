# Buffer模块概述

## 功能描述

Buffer Manager负责缓冲区的管理，主要功能有：

1. 根据需要，读取指定的数据到系统缓冲区或将缓冲区中的数据写出到文件

2. 实现缓冲区的替换算法，当缓冲区满时选择合适的页进行替换

3. 记录缓冲区中各页的状态，如是否被修改过等
4. 提供缓冲区页的pin功能，及锁定缓冲区的页，不允许替换出去

为提高磁盘I/O操作的效率，缓冲区与文件系统交互的单位是块，块的大小应为文件系统与磁盘交互单位的整数倍，一般可定为4KB或8KB。

## 功能实现

本模块通过python库中的有序字典对象实现对Buffer的模拟，大小为4KB，并使用FIFO算法对缓冲区数据进行替换。以Buffer为媒介，表中数据在文件与Record模块之间进行流通。

## 接口描述

### Buffer的初始化与回收

```python
def init()
#buffer初始化
def finalize()
#查询结束，将buffer中脏数据写回文件
```

### 表定义操作

```python
def create_table(tablename)
#表的创建，创建新文件
def delete_table(tablename)
#表的删除，删除表文件
```

### 文件读写操作/Block操作

```python
def truncate(tablename, where)
#删除where之后的记录
def save_block(tablename, code)
#将block中table的脏数据写回表中
def get_block(tablename, where, length)
#从文件中读取给定长度数据并存入block
def change_valid_bit(tablename, loc)
#对脏数据进行标记
```

