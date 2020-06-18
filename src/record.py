import os
import re
import myBuffer
path = './dbFile/Record/'


def create_table(tablename):
	p = open(path+tablename+'.rec','a+')
	p.close()

def delete_table(tablename):
	myBuffer.delete_table(tablename)
	os.remove(path+tablename+'.rec')


def insert(tablename,values):
	encode = '1'#第一位用于之后的校验
	for i in values:
		encode += '{:\0<255}'.format(str(i))
	#print('encode:',encode)
	return myBuffer.save_block(tablename, encode)

# 这个函数的作用是分割存入buffer中的code，返回结果为有效位（即insert中的那个“1”）和对应的属性
def decrypt(code):
	valid_bit= int(code[0])
	attributes = re.split('\0+',code[1:].strip('\0'))
	return valid_bit, attributes

# 输出函数 需要传入的参数分别为：
# tablename:表的名称
# columnname:要输出的列的名称（列表）
# clauses:是一个二重列表，每一个元素(clause)为一个where子句的条件，其中各个元素的意义分别为：第一个属性，运算符，第二个属性，第一个属性的数据类型（如int,char等）
# where:要提取的数据所在区域(通过index中的select函数进行参数传入)
# length:每条数据的长度
def select_record(tablename, columnname, clauses, where, length):
	results=[]
    ##如果where子句为空，直接把表中的数据映射到指定的列中进行输出
	if where==None:
        ##遍历全表 初始化位置为0
		loc=0
		while 1:
            ##使用buffer模块中的函数从表中的指定位置读取对应的数据
			code=myBuffer.get_block(tablename,loc,length).decode('utf-8')
			if code==b'' or code==None or code=="":
				break
			loc += length
			valid,result=decrypt(code)
			if valid==1:
				flag=True
				for clause in clauses:
					if clause[3]=='char':
						if not eval(result[clause[-1]]+clause[1]+clause[2]):
							flag=False
					else:
						if not eval(result[clause[-1]]+clause[1]+clause[2]):
							flag=False
				if flag==True:
					results.append(result)
	else:
		for loc in where:
            # 使用buffer模块中的函数从表中的指定位置读取对应的数据
			code=myBuffer.get_block(tablename,loc,length).decode('utf-8')
			valid, result = decrypt(code)
			if valid==1:
				flag = True
				for clause in clauses:
					if clause[3]=='char':
						if not eval(result[clause[-1]]+clause[1]+clause[2]):
							flag = False
					else:
						if not eval(str(eval(result[clause[-1]]))+clause[1]+clause[2]):
							flag = False
				if flag:
					results.append(result)          
    # 编辑sql输出表的格式（边框）
	print('+',end='')
	print(('-'*16+'+')*len(columnname))
	for i in columnname:
		if len(str(i)) > 14:
			output = str(i)[0:14]
		else:
			output = str(i)
		print('|',output.center(15),end='')
	print('|')
	print('+',end='')
	print(('-'*16+'+')*len(columnname))
    # 输出指定的数据
	for i in results:
		for j in range(len(columnname)):
			if len(str(i[j])) > 14:
				output = str(i[j])[0:14]
			else:
				output = str(i[j])
			print('|',output.center(15) ,end='')
		print('|')
	print('+',end='')
	print(('-'*16+'+')*len(columnname))

# 删除函数
# 各个参数的含义与上面select同名参数的意义相同，返回的参数where用于在index模块中找到相应的节点并删除
def delete_record(tablename, clauses,length):
	loc = 0
	where = []
	while 1:
		code = myBuffer.get_block(tablename,loc,length).decode('utf-8')
		if code ==b'' or code==None or code=="":
			break
		valid, result = decrypt(code)
		if valid:
			flag = True
			for clause in clauses:
				if clause[3]=='char':
					if not eval(result[clause[-1]]+clause[1]+clause[2]):
						flag = False
				else:
					if not eval(str(eval(result[clause[-1]]))+clause[1]+clause[2]):
						flag = False
			if flag:
				myBuffer.change_valid_bit(tablename,loc)
				where.append(result)
		loc += length
	return where

def create_index(tablename, id, type,length):
	loc = 0
	where = []
	while 1:
		code = myBuffer.get_block(tablename, loc, length).decode('utf-8')
		if code == b'' or code == None or code == '':
			break
		valid, entry = decrypt(code)
		if valid:
			if type=='char':
				where.append((loc,entry[id]))
			else:
				where.append((loc,eval(entry[id])))
		loc += length
	return where

def truncate(tablename, where):
	myBuffer.truncate(tablename, where)

def init():
	myBuffer.init()

def finalize():
	myBuffer.finalize()