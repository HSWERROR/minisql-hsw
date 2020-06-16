[TOC]

# 实现功能

Index Manager负责 **B+树索引**的实现，实现B+树的创建和删除(由索引的定义与删除引起)、等值查找、插入键值、删除键值等操作，并对外提供相应的接口。 

B+树中节点大小应与缓冲区的块大小相同，B+树的叉数由节点大小与索引键大小计算得到。

# 模块接口
## insert_entry(table_name,index_name, key, data)

根据索引在一个表格中添加节点

### insert(node,key,data,is_insert = True)

将一项插入b+树，is_insert为False时是伪插入，在做select等值查询操作的时候会被调用

#### find_leaf_place(node,_key)

找到插入项对应的叶子节点位置

#### insert_into_leaf(node,_key,data,is_insert = True)

向叶子节点插入

#### insert_into_parent(Inode, Nnode)

向非叶节点插入（在叶子节点需要分裂时递归地更新其父节点）

## delete_entries(keylist, table_name, index_name)

根据索引在一个表格中删除若干节点

### delete( node , key )

删除叶子节点

#### delete_nonleaf_key(node, index)

删除非叶节点的键值（在节点合并过程中其父节点的键值需要递归地改变）

## select_from_table(table_name, conditions, index_name)

在一个表格中，按照条件语句做选择操作，返回符合条件的节点的存储数据

## create_table(table_name,unique_key)

创建一个新的表格，给它的unique属性添加索引

## delete_table(table_name)

删除一个表, 删除该表格的所有索引

##  create_index(table_name, index_name, col)

为一个表格的某个属性添加索引

## delete_index(index_name)

删除所有名为index_name的索引

## delete_table_index(table_name, index_name)

删除一个表格上的某索引

## check_unique(table_name, index_name, value)

检查一个索引的唯一性


# 具体实现详解

## B+树的存取方法
* Node类来表示B+树的每一个节点

    ```python
    class Node():
    	def __init__(self, is_leaf, keys, sons, parent = None, left = None, right = None):
    		self.is_leaf = is_leaf #判断是否为叶子节点
    		self.keys = keys #存储键值的列表
    		self.sons = sons #存储子节点的指针（叶子节点中存储data）
    		self.parent = parent #存储父节点的指针
    		self.left = left #存储左节点的指针（叶子节点采用）
    		self.right = right #存储右节点的指针（叶子节点采用）
    ```
    
* 使用**`json`文件格式**存取b+树结构，因为`python`的`json`模块提供函数可以将字典类型数据转换为字符串类型从而保存在文件中，同时也提供了将字符串转换为字典的函数，这使得B+树的存储非常简单
	
	* 文件最终存储效果
	
	    ```json
	    {"is_leaf": false, "keys": [6], "sons": [{"is_leaf": true, "keys": [1, 4], "sons": [0, 452]}, {"is_leaf": true, "keys": [6, 7,9], "sons": [520, 2298, 3064]}]}
	    ```
	
* 将一棵树转化为json形式(j is the root)

    ```python
    def turn_tree_into_json(j):
    	m = {}
    	m['is_leaf'] = j.is_leaf
    	m['keys'] = j.keys
    	m['sons'] = [(turn_tree_into_json(x)) for x in j.sons] if m['is_leaf']==False else j.sons
    	return m
    ```

* 从json格式读取一棵树(j is the root)

    ```python
    def load_tree_from_json(j,parent=None):
    	if j['is_leaf']==True:
    		node = Node(j['is_leaf'],j['keys'],j['sons']) 
    	else:
    		node = Node(j['is_leaf'],j['keys'],[load_tree_from_json(x) for x in j['sons']])
    		for son in node.sons:
    			son.parent = node
    	return node
    ```

* 因为字典里只存储了每个节点的键值和儿子，没有存储兄弟节点（否则无法储存，会发生循环），因此在每次从json读取一棵树知乎还需要维护每个叶子节点的左右节点

    ```python
    prev = None #存储上一个处理节点的全局变量
    def maintain_left_right_pointer(node):
    	global prev
    	if node!=None:
    		if node.is_leaf:
    			if prev!=None:
    				prev.right = node
    				node.left = prev
    			prev = node
    		else:
    			for x in node.sons:
    				maintain_left_right_pointer(x)
    	node.right = None
    ```

    
## 创建、删除索引
* 创建一个新的表格，给它的unique属性添加索引（此时这个索引只是生成了空的B+树，要通过create_index添加数据；因为如果一个表格没有索引，它不需要存在于Index manager中）

    ```python
    def create_table(table_name,unique_key):
    	fp[table_name+'_'+unique_key] = open(path+table_name+'_'+unique_key+'.ind','a+')
    	fp[table_name+'_'+unique_key].write('{"is_leaf":true,"sons":[],"keys":[]}')
    	tree_root[table_name+'_'+unique_key]=load_tree_from_json(json.loads('{"is_leaf":true,"sons":[],"keys":[]}'))
    	global prev 
    	prev = None
    	maintain_left_right_pointer(tree_root[table_name+'_'+unique_key])
    ```
    
* 删除一个表格以及它所有的索引

    ```python
    def delete_table(table_name):
    	list = CatalogManager.catalog.get_index_list(table_name)
    	for index_name in list:
    		fp[table_name+'_'+index_name].close()
    		os.remove(path+table_name+'_'+index_name+'.ind')
    ```

* 为一个表格的某个属性添加索引：col为该属性的一列

    * 每一个r (row) 
        * r[0]：存数据
        * r[1]：存键值
    
    ```python
    def create_index(table_name, index_name, col):
    	fp[table_name+'_'+index_name] = open(path+table_name+'_'+index_name+'.ind','a+')
    	fp[table_name+'_'+index_name].write('{"is_leaf":true,"sons":[],"keys":[]}')
    	tree_root[table_name+'_'+index_name]=load_tree_from_json(json.loads('{"is_leaf":true,"sons":[],"keys":[]}'))
    	global prev 
    	prev = None
    	maintain_left_right_pointer(tree_root[table_name+'_'+index_name])	
    	for r in col:
    		key = r[1]
    		data = r[0]
    		insert_entry(table_name,index_name,key,data)
    ```
    
* 删除所有名为index_name的索引

    ```python
    def delete_index(index_name):
    	file_list = os.listdir(path)
    	for file in file_list:
    		if index_name == file.split('_')[1]:
    			fp[file.rstrip('.ind')].close()
    			os.remove(path+file)
    			return file.split('_')[0]
    	raise Exception('No index named '+index_name+'.')
    ```

* 删除一个表格上的某索引

    ```python
    def delete_table_index(table_name, index_name):
    	tree_root[table_name+'_'+index_name] = load_tree_from_json(json.loads('{"is_leaf":true,"sons":[],"keys":[]}'))# 将一棵树置空
    	global prev
    	prev = None
    	maintain_left_right_pointer(tree_root[table_name+'_'+index_name])
    ```

    

## 插入键值

* 根据索引在一个表格中添加节点

    ```python
    def insert_entry(table_name,index_name, key, data):
    	global root
    	root = tree_root[table_name+'_'+index_name]
    	res = insert(tree_root[table_name+'_'+index_name],key,data)
    	tree_root[table_name+'_'+index_name] = root
    ```

* 添加节点：

    * 空树直接添加节点作为叶节点
    * 找到应该添加的叶节点位置
        * 如果叶节点未满：直接添加进叶节点
        * 如果叶节点已满：分裂节点后递归地更新父节点

    ```python
    def insert(node,key,data,is_insert = True):
    	if len(node.keys) == 0:
    		# new tree  
    		node.keys.append(key)
    		node.sons.append(data)
    		return []
    
    	# find the current leaf node waiting to be inserted	
    	insert_node = find_leaf_place(node,key)
    	if len(insert_node.keys) < N - 1:
    		 # if it can fit in, use insert_into_leaf
    		res = insert_into_leaf(insert_node,key,data,is_insert)
    		if res != None:
    			return res
    	else:
    		# if not
    		res = insert_into_leaf(insert_node,key,data,is_insert)
    		if res != None:
    			return res
    
    		#depart the node and use insert_into_parent to update the parent node recursively
    		new_node=Node(True,[],[])
    		for i in range(N-math.ceil((N-1)/2)):
    			new_node.keys.append(insert_node.keys.pop(math.ceil((N-1)/2)))
    			new_node.sons.append(insert_node.sons.pop(math.ceil((N-1)/2)))
    
    		# put the new_node at the right of the insert_node
    		new_node.right = insert_node.right
    		if insert_node.right != None:
    				insert_node.right.left = new_node
    		insert_node.right = new_node
    		new_node.left = insert_node
    		insert_into_parent(insert_node,new_node)
    
    	return []
    ```

* 找到插入项对应的叶子节点位置：先向下找到叶节点层

    ```python
    def find_leaf_place(node,_key):
    	TmpNode = node
    	while not TmpNode.is_leaf:
    		flag = False
    		for index, key in enumerate(TmpNode.keys):
    			if key>_key:
    				TmpNode = TmpNode.sons[index]
    				flag = True
    				break
    		# if the given key is larger than any key, then in the last son	
    		if flag == False:
    			TmpNode = TmpNode.sons[-1]
    	return TmpNode
    ```

* 插入叶节点：

    * 提供伪插入（等值查询时使用）
    * 提供键值冲突的异常处理
    * 找到合适的位置，直接将数据插入到叶子节点的sons中（注意当键值大于节点任意键值时插入最后的位置）

    ```python
    def insert_into_leaf(node,_key,data,is_insert = True):
    	for index,key in enumerate(node.keys):
    		if key == _key:
    			if not is_insert:
    				return node.sons[index]
    			else:
    				# primary key already exists
    				raise Exception(_key)
    		# find the appropriate place
    		if is_insert and key>_key:
    			node.sons.insert(index,data) # insert(self, index: int, object: _T)
    			node.keys.insert(index,_key)
    			return None
    	if is_insert: # the last place( _key > all the keys)
    		node.sons.insert(len(node.sons),data) #new index:len(node.sons)
    		node.keys.insert(len(node.sons),_key)
    		return None
    ```

* 向非叶节点插入，用于在节点需要分裂时递归地更新其父节点：

    * 该非叶节点是根节点，那么分裂后需要新的根节点；不是根节点，找到父节点
    * 分裂节点不是叶子节点：将新节点的最左键值移向父节点，新节点的键值不需要保留；分裂节点是叶子节点：新节点的键值需要保留
    * 如果父节点满，递归地更新父节点

    ```python
    def insert_into_parent(Inode, Nnode):
    	# if Inode is the root, then need a new root
    	if Inode.parent==None:
    		global root
    		parent_node = Node(False,[],[],None)
    		root = parent_node
    		parent_node.sons.append(Inode)
    		Inode.parent =parent_node
    
    	else:
    		parent_node = Inode.parent
    	id = get_id(parent_node, Inode)
    	Nnode.parent = parent_node
    	if Inode.is_leaf==False:
    		parent_node.keys.insert(id, Nnode.keys.pop(0)) # don't need to save Nnode's key[0],remove it to parent
    	else:
    		parent_node.keys.insert(id,Nnode.keys[0]) # save the key in the leaf node
    	parent_node.sons.insert(id + 1, Nnode)
    	# update the parent recursively
    	if len(parent_node.keys)==N:
    		new_node=Node(False,[],[])
    		for i in range(N-math.ceil((N-1)/2)):
    			new_node.keys.append(parent_node.keys.pop(math.ceil((N-1)/2)))
    			new_node.sons.append(parent_node.sons.pop(math.ceil((N-1)/2)+1))
    		for x in new_node.sons:
    			x.parent = new_node
    		new_node.right = parent_node.right
    		if parent_node.right != None:
    			parent_node.right.left = new_node
    		parent_node.right = new_node
    		new_node.left = parent_node
    		insert_into_parent(parent_node,new_node)
    ```

    

## 删除键值

* 根据索引在一个表格中删除若干节点：

    * 此处需要一个keylist参数来指明哪些键值的节点需要被删除

    ```python
    def delete_entries(keylist, table_name, index_name):
    	for key in keylist:
    		global root
    		root = tree_root[table_name+'_'+index_name]
    		delete(tree_root[table_name+'_'+index_name],key)
    		tree_root[table_name+'_'+index_name] = root
    		prt(get_leftest_child(tree_root[table_name+'_'+index_name]))
    ```

* 删除叶子节点：

    * 提供找不到节点的异常处理
    * 如果节点在删除后长度过短（$\large len < \lceil\frac{N-1}{2}\rceil$）
        * 节点是最左端的儿子，不需要修改父节点的键值
            * 兄弟节点的长度够，将其补给该结点
            * 兄弟节点长度不够，合并该结点与兄弟节点
        * 节点不是最左端的儿子，需要对父节点作删除键值操作

    ```python
    def delete(node,key):
    	cur_node = find_leaf_place(node,key)
    	flag = True
    	least = math.ceil((N - 1) / 2)  # the least length of a node
    	for index,_key in enumerate(cur_node.keys):
    		print('--->',key,_key)
    		if key == _key:
    			print('here',key,_key)
    			flag = False
    			cur_node.sons.pop(index)
    			cur_node.keys.pop(index)
    			break
    	if flag: # can't find
    		raise Exception('No point to delete')
    
    	# if the leaf node's length is shorter than "least"
    	if cur_node.parent!=None and len(cur_node.keys)<least:
    		if cur_node.parent.sons[0] == cur_node:
    			# append node of the sibling to cur_node
    			if len(cur_node.parent.sons[1].keys)>least:
    				cur_node.sons.append(cur_node.parent.sons[1].sons.pop(0))
    				cur_node.keys.append(cur_node.parent.sons[1].keys.pop(0))
    				cur_node.parent.keys[0] = cur_node.parent.sons[1].keys[0]
    			# merge the cur_node and the next sibling
    			else:
    				for i in range(len(cur_node.parent.sons[1].keys)):
    					cur_node.sons.append(cur_node.parent.sons[1].sons[i])
    					cur_node.keys.append(cur_node.parent.sons[1].keys[i])
    				if cur_node.right.right!=None:
    					cur_node.right.right.left = cur_node
    				cur_node.right = cur_node.right.right
    				delete_node(cur_node.parent, 0)
    		# if the inappropriate node is not the first son, need to update parent
    		else:
    			id = get_id(cur_node.parent, cur_node) - 1
    			# append the last node of the previous sibling to cur_node's first node
    			if len(cur_node.parent.sons[id].keys)>least:
    				cur_node.sons.insert(0,cur_node.parent.sons[id].sons.pop(-1))
    				cur_node.keys.insert(0, cur_node.parent.sons[id].keys.pop(-1))
    				# update the parent's key using cur_node's first node
    				cur_node.parent.keys[id] = cur_node.keys[0]
    			# merge the cur_node and its previous sibling
    			else:
    				for i in range(len(cur_node.keys)):
    					cur_node.parent.sons[id].sons.append(cur_node.sons[i])
    					cur_node.parent.sons[id].keys.append(cur_node.keys[i])
    				if cur_node.right!=None:
    					cur_node.right.left = cur_node.left
    				cur_node.left.right = cur_node.right
    				delete_node(cur_node.parent,id)
    
    ```

* 删除非叶节点的键值，在节点合并过程中其父节点的键值需要递归地改变：

    * 如果节点删除键值之后长度达标，返回
    * 长度过短（$\large len < \lceil\frac{N-1}{2}\rceil$）
        * 该结点为根节点，此时根节点为空，将其第一个儿子作为新的根节点
        * 该结点不是根节点：类似于delete里对叶子节点的操作，递归地向上更新

    ```python
    def delete_nonleaf_key(node, index):
    	least = math.ceil((N-1)/2)
    	node.keys.pop(index)
    	node.sons.pop(index+1)
    	if len(node.keys) >= least:
    		return
    	# if node is the root node
    	if node.parent == None:
    		# use the first son as the new root
    		if len(node.keys)==0 and len(node.sons[0].keys)!=0:
    			global root
    			root = node.sons[0]
    			node.sons[0].parent = None		
    		return
    	# next part is similar to delete the leaf node
    	# if node is its parent's first son
    	if node.parent.sons[0] == node:
    		id = get_id(node.parent, node)
    		# append node of the sibling to cur_node
    		if len(node.parent.sons[1].keys) >least:
    			node.keys.append(node.parent.keys[id])
    			node.parent.keys[id] = node.parent.sons[1].keys.pop(0)
    			node.sons.append(node.parent.sons[1].sons.pop(0))
    			node.sons[-1].parent = node
    		# merge
    		else:
    			node.keys.append(node.parent.keys[id])
    			for i in range(len(node.parent.sons[1].keys)):
    				node.keys.append((node.parent.sons[1].keys[i]))
    				node.sons.append((node.parent.sons[1].sons[i]))
    				node.sons[-1].parent = node
    			node.right = node.right.right
    			delete_nonleaf_key(node.parent, id)
    	# if it isn't the first son, need to update parent_node
    	else:
    		id = get_id(node.parent, node) - 1
    		if len(node.parent.sons[id].keys)>least:
    			node.keys.insert(0,node.parent.keys[id])
    			node.parent.keys[id] = node.parent.sons[id].keys.pop(-1)
    			node.sons.insert(0,node.parent.sons[id].sons.pop(-1))
    			node.sons[0].parent = node
    		else:
    			node.parent.sons[id].keys.append(node.parent.keys[id])
    			for i in range(len(node.keys)):
    				node.parent.sons[id].keys.append(node.keys[i])
    				node.parent.sons[id].sons.append(node.sons[i])
    			node.left.right = node.right
    			delete_nonleaf_key(node.parent,id)
    ```

    

## 查找相关

* 在一个表格中，按照条件语句做选择操作，返回符合条件的节点的存储数据：

    * $!=$：在一棵B+树中至左向右读取除了键值为给定值的所有数据
    * $==$：使用is_insert为false的伪插入操作找到相应节点
    * $</>$：找到对应叶节点，从左向右或从右向左读取数据
    
```python
    def select_from_table(table_name, conditions, index_name):
    	res, value = [], eval(conditions[2])
    	if conditions[1] == '!=':
    		res = get_data_list_right(get_leftest_child(tree_root[table_name + '_' + index_name]), value)
    	elif conditions[1] == '==':
    		# a fake insert to find the node
    		res.append(insert(tree_root[table_name + '_' + index_name], eval(conditions[2]), None, False))
    	else:
    		# find the leaf node in condition
    		break_block = find_leaf_place(tree_root[table_name+'_'+index_name],value)
    		for index, key in enumerate(break_block.keys):
    			if eval('key' + conditions[1] + conditions[2]):
    				res.append(break_block.sons[index])
    		if '>' in conditions[1] and break_block.right != None:
    			res += get_data_list_right(break_block.right)
    		elif '<' in conditions[1] and break_block.left != None:
    			res += get_data_list_left(break_block.left)
    	return res
```


* 在不等值查找（<）中找到给定值左侧的所有叶子节点对应数据（不包括界线值）

    ```python
    def get_data_list_left(node, exclude = None):
    	l = []
    	for index,x in enumerate(node.sons):
    		if not node.keys[index]==exclude:
    			l.append(x)
    	if node.left!=None:
    		l+=get_data_list_left(node.left,exclude)
    	return l
    ```

    

* 在不等值查找（>）中找到给定值右侧的所有叶子节点对应数据（不包括界线值）

    ```python
    def get_data_list_right(node, exclude = None):
    	l = []
    	for index,x in enumerate(node.sons):
    		if not node.keys[index]==exclude:
    			l.append(x)
    	if node.right!=None:
    		l+=get_data_list_right(node.right,exclude)
    	return l
    ```

    

##  初始化、结束及测试用函数

* 判断Index是否符合唯一性

    ```python
    def check_unique(table_name, index_name, value):
    	check_root = tree_root[table_name + '_' + index_name]
    	TmpNode = check_root
    	while not TmpNode.is_leaf:
    		flag = False
    		for index, key in enumerate(TmpNode.keys):
    			if key>value:
    				TmpNode = TmpNode.sons[index]
    				flag = True
    				break
    		# if the given key is larger than any key, then in the last son	
    		if flag == False:
    			TmpNode = TmpNode.sons[-1]
    	for index,key in enumerate(TmpNode.keys):
    		if key == value:
            raise Exception("Index Module : index '%s' does not satisfy "
                                    "unique constrains." % index_name)
    ```

* 从文件夹中读入所有json文件并将其转化为树形式

    ```python
    def init():
    	file_list = os.listdir(path)
    	for file in file_list:
    		fp[file.rstrip('.ind')] = open(path+file,'a+')
    		fp[file.rstrip('.ind')].seek(0)
    		tree_root[file.rstrip('.ind')]=load_tree_from_json(json.loads(fp[file.rstrip('.ind')].read()))
    		global prev 
    		prev = None
    		maintain_left_right_pointer(tree_root[file.rstrip('.ind')])
    ```

* 将所有树存储为json文件，关闭文件

    ```python
    def finalize():
    	file_list = os.listdir(path)
    	for file in file_list:
    		name = file.rstrip('.ind') 
    		fp[name].seek(0)
    		fp[name].truncate()
    		fp[name].write(json.dumps(turn_tree_into_json(tree_root[name])))
    		fp[name].close()
    ```

* 将所有键值从左至右输出（用于测试）

    ```python
    def prt(node):
    	for x in node.keys:
    		print(x,end=' ')
    	if node.right != None:	
    		prt(node.right)
    ```

* 将所有键值从右至左输出（用于测试）

    ```python
    def prtl(node):
    	for x in node.keys:
    		print(x)
    	if node.left != None:	
    		prtl(node.left)
    ```

    
