# Interpreter

## 实现功能

Interpreter模块直接与用户交互，主要实现以下功能：

1. 程序流程控制，即“ 启动并初始化 --> '接收命令、处理命令、显示命令结果'循环 -->退出 ” 流程
2. 接收并解释用户输入的命令，生成命令的内部数据结构表示，同时检查命令的语法正确性和语义正确性，对正确的命令调用API层提供的函数执行并显示执行结果，对不正确的命令显示错误信息。

## 语法说明

注：支持语句中出现任意数目空格、换行符号

### 1、创建表

#### 输入

```mysql
Create table sc(cname char(10),grade int,primary key(cname));
Create table sc (cname char(10),grade int unique, primary key(cname));
Create table sc(cname char(10) unique ,grade int unique , primary key(cname));
```

#### 输出

调用API.create_table(table_name, Attribute_Value, Primary_Key)函数，参数传入值如下：

> sc [['cname', 'char', '10', [], 0], ['grade', 'int', '0', [], 0]] cname
>
> sc [['cname', 'char', '10', [], 0], ['grade', 'int', '0', [], 1]] cname
>
> sc [['cname', 'char', '10', [], 1], ['grade', 'int', '0', [], 1]] cname

Attribute_Value由列表构成，每一个列表里面第一个数据为属性名称；第二个数据为类型；若第二个数据为char、则第三个数据就是char后面的数字，否则补0；第四个数据为一个空列表；第五个数据表明是否为unique，若是则为1，不是则为0.

### 2、删除表

#### 输入

```mysql
drop table student;
```

#### 输出

调用API.drop_table(table_name)，参数传入值如下：

> student

### 3、创建索引

#### 输入

```mysql
create index stunameidx on student ( sname );
```

#### 输出

调用API.create_index(table_name, index_name, column_name)函数，参数传入值如下：

> stunameidx student sname

### 4、删除索引

#### 输入

```mysql
drop index stunameidx;
```

#### 输出

调用API.drop_index(index_name)函数，参数传入值如下：

> stunameidx

### 5、选择语句

#### 输入

```mysql
select * from student;
select * from student where sno = '888';
select * from student where sage > 20 and sgender = 'F';
```

#### 输出

调用API.select(table_name, where_condition)函数，参数传入值如下：

> student *
>
> student sno = '888'
>
> select * from student where sage > 20 and sgender = 'F';

当不存在where_condition的时候传入*

### 6、插入记录语句

#### 输入

```mysql
insert into student values ('12345678','wy',22,'M');
```

#### 输出

调用API.insert(table_name,values)函数，参数传入值如下：

> student ['12345678', 'wy', '22', 'm']

### 7、删除记录语句

#### 输入

```mysql
delete from student;
delete from student where sno = '88888888';
```

#### 输出

> student *
>
> student sno = '88888888'

### 8、退出系统语句

含有quit的所有语句均可

```
quit;
\quit;
```

### 9、执行SQL脚本文件语句

```mysql
execfile 文件名 ;
```

SQL脚本文件中可以包含任意多条上述8种SQL语句，MiniSQL系统读入该文件，然后按序依次逐条执行脚本中的SQL语句。该文件需要放在同一文件夹下。

### 10、帮助

只要含有help的语句均可

```
help;
\help;
```

