# Catalog 模块
## 总体功能说明：
Catalog 模块负责管理数据库的所有模式信息，允许用户通过字符界面输入包括：  
1. 数据库中所有表的定义信息，允许用户通过字符界面输入包括表的名称、表中字段（列）数、主键、定义在该表上的索引。  
2. 表中每个字段的定义信息，允许用户通过字符界面输入包括字段类型、是否唯一等。 
3. 数据库中所有索引的定义，允许用户通过字符界面输入包括所属表、索引建立在那个字段上等。
本模块同时提供了访问及操作上述信息的接口，允许用户通过字符界面输入供Interpreter和API模块使用。

## 存储结构：
在catalog中，本数据库将引入json模块，将catalog以json的形式进行存取。格式如下：
```json
{"school": {
    "primary": 0,
    "columns": {
        "attribute0": ["int", 0, [" "], 0 ], 
        "attribute1": ["char", 20, ["index1"], 0], 
        "attribute2": ["int", 0, ["index2","index3"], 0]}
}
}
```
整个json文件采用字典列表的形式将catalog存在其中，每个键值代表一张数据表，键为数据表的名称，值为数据表的具体属性。
数据表的具体属性中，包含两对键值对，其中"primary"对应的值为本张表主键对应的序号，如在上方实例中主键则为"attribute0"；而"columns"对应的值为一个字典列表，存放着每个属性的具体参数，其中键为属性名称，值为一个列表，包含的内容依次为：[属性的名称，属性类型，char类型中含有的字符数（若为int、float类型则为0），空列表（用于存储index），是否unique（1表示unique）]。

## 具体接口：
### 文件操作与初始化：
```python
def init_catalog():
初始化，打开json并读入数据
def finalize():
将数据写入json并关闭文件
```

### 数据表操作：
```python
def exist_table(tablename, boolean):
判断tablename数据表是否存在，若不存在/存在，则对应类型报错
def create_table(tablename, attributes,primary):
创建一个包含attributes属性，主键为primary，名为tablename的数据表
attributes格式实例：[["area", "int", 0, [], 0]]
#list类型[属性的名称，属性类型，char类型中含有的字符数（若为int、float类型则为0），空列表（用于存储index），是否unique（1表示unique）]
```

### 属性操作：
```python
def delete_table(tablename):
    删除tablename数据表，无返回值
def get_index_of_attribute(tablename, attribute_name):
    获取tablename表中attribute_name这一属性所在的序号（并不是索引）；返回值为number类型
def get_type_list(tablename):
    返回一个包含当前tablename数据表中所有属性类型的list
def get_column_with_index(tablename):
    返回一个包含当前tablename数据表中所有拥有索引的列的list
def get_column_name(tablename):
    返回tablename数据表中所有的列名，返回值为包含所有列表名的list类型
def get_length(tablename):
    返回tablename数据表中列数对应的长度
```

### 索引操作：
```python
def create_index(tablename, indexname, columnname):
    在tablename表中，给columnname列创建一个名为indexname的索引。	若该列已经存在名为indexname的索引便报错。
def exist_index(indexname,boolean):
    判断索引是否存在，若不存在/存在，则对应类型报错
    indexname:string类型，索引名称
    boolean:boolean类型，若为True则当索引存在便报错，若为False则当索引不存在便报错
def delete_index(indexname):
    删除indexname这一索引，无返回值
def get_index_list(tablename):
    返回一个包含当前tablename数据表中所有索引名的list
def get_index_name(tablename,attribute):
    返回一个list，包含tablename中的attribute属性拥有的索引
def get_index_name_by_seq(tablename,index):
    返回一个list，包含tablename中第index个属性拥有的索引
```
### 检查输入:
```python
def check_type(tablename,input_list):
    检查输入是否合法,若不合法会报错，并返回经处理后该元组的list
```
## 心得体会：
在完成这次MiniSQL大作业的过程中，我负责编写catalog模块。在编写此模块的过程中，我收获颇多。首先最直观的收获便是我在Python语言上的收获，通过这次作业，我对于Python语言的json模块，以及字典和列表的使用变得更加熟练；此外，我对于数据库管理系统的理解也上升到了一个新的高度，对于catalog模块与interpreter模块及API模块之间的通信交互，catalog模块的接口设计，以及调用其他模块的接口来实现数据查询等相应的功能等更加得了解；另外，在小组合作中，我的交流沟通能力得到了增强以及对代码版本控制工具的使用愈发得心应手。在编写MiniSQL的过程中，虽然我们出现了一些接口没有对齐，文件读写出错等bug，但在我们的通力合作下，我们成功地让MiniSQL运行，并得到了预期结果。我感到十分具有成就感，并收获良多。