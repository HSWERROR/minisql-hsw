import os
import math
import json
import catalog
import re
#import sys
#import codecs


path = './dbFile/Index/'
fp = {} # store all the files(containg B+ tree json form)  according to the table_name and index_name, separating by '_'
tree_root = {} # store all the tree_root nodes according to table_name and index_name, separating by '_'
root = None # store the current tree_root node
N = 4 # the order of the B+ tree

# define a class for the nodes in B+
class Node():
    def __init__(self, is_leaf, keys, sons, parent = None, left = None, right = None):
        self.is_leaf = is_leaf
        self.keys = keys
        self.sons = sons
        self.parent = parent
        self.left = left
        self.right = right

    # define a pointer to the node, for the print operation
    def ptr(self):
        print(self.keys)
        if self.is_leaf == False:
            for x in self.sons:
                x.ptr()

# dict(json) only store the keys and sons of each node, we need to maintain the left and right brothers 
prev = None 
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

# load a tree from json form
def load_tree_from_json(j,parent=None):
    if j['is_leaf']==True: # if j is a leaf node,sons store data info
        node = Node(j['is_leaf'],j['keys'],j['sons']) 
    else:
        node = Node(j['is_leaf'],j['keys'],[load_tree_from_json(x) for x in j['sons']])
        for son in node.sons:
            son.parent = node
    return node

# turn a tree into json form, j is the root
def turn_tree_into_json(j):
    m = {}
    m['is_leaf'] = j.is_leaf
    m['keys'] = j.keys
    m['sons'] = [(turn_tree_into_json(x)) for x in j.sons] if m['is_leaf']==False else j.sons
    return m

# find the place of the corresponding leaf node
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


# insert into leaf
def insert_into_leaf(node,_key,data,is_insert = True):
    for index,key in enumerate(node.keys):
        if key == _key:
            if not is_insert:
                return node.sons[index]
            else:
                # primary key already exists
                raise Exception('key named '+_key+' already exists!')
        # find the appropriate place
        if is_insert and key>_key:
            node.sons.insert(index,data) # insert(self, index: int, object: _T)
            node.keys.insert(index,_key)
            return None
    if is_insert: # the last place( _key > all the keys)
        node.sons.insert(len(node.sons),data) #new index:len(node.sons)
        node.keys.insert(len(node.sons),_key)
        return None

# update the parent when splits happen
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

## insert into B+ tree
# usage : find_leaf_place(node,_key)
# usage : insert_into_leaf(node,_key,data,is_insert = True)
# usage : insert_into_parent(Inode,Nnode)
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

# get the index of one node from its parent
def get_id(f_node, node):
    for index,n in enumerate(f_node.sons):
        if n == node:
            return index
    raise Exception('get_id error!')

# delete the keys of a non-leaf node
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

## delete the leaf node
# usage: find_leaf_place(node,_key)
# usage: delete_nonleaf_key(node, index)
def delete(node,key):
    cur_node = find_leaf_place(node,key)
    flag = True
    least = math.ceil((N - 1) / 2)  # the least length of a node
    for index,_key in enumerate(cur_node.keys):
        #print('--->',key,_key)
        if key == _key:
            #print('here',key,_key)
            flag = False
            cur_node.sons.pop(index)
            cur_node.keys.pop(index)
            break
    if flag: # can't find
        raise Exception('No point whose key named'+key+'to delete!')

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
                delete_nonleaf_key(cur_node.parent, 0)
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
                delete_nonleaf_key(cur_node.parent,id)

def get_leftest_child(node):
    TmpNode = node
    while not TmpNode.is_leaf:
        TmpNode = TmpNode.sons[0] 
    return TmpNode

def get_data_list_right(node, exclude = None):
    l = []
    for index,x in enumerate(node.sons):
        if not node.keys[index]==exclude:
            l.append(x)
    if node.right!=None:
        l+=get_data_list_right(node.right,exclude)
    return l

def get_rightest_child(node):
    TmpNode = node
    while not TmpNode.is_leaf:
        TmpNode = TmpNode.sons[-1] # get the last son
    return TmpNode

def get_data_list_left(node, exclude = None):
    l = []
    for index,x in enumerate(node.sons):
        if not node.keys[index]==exclude:
            l.append(x)
    if node.left!=None:
        l+=get_data_list_left(node.left,exclude)
    return l

# print all the keys in left-to-right order
def prt(node):
    for x in node.keys:
        print(x,end=' ')
    if node.right != None:	
        prt(node.right)

#print all the keys in right-to-left order
def prtl(node):
    for x in node.keys:
        print(x)
    if node.left != None:	
        prtl(node.left)

# read in all the trees from json
def init_index():
    file_list = os.listdir(path)
    for file in file_list:
        name = file[:-4]
        fp[name] = open(path+file,'a+')
        #fp[file[:-4]] = codecs.getwriter("utf-8")(fp[file[:-4]].detach())
        fp[name].seek(0)
        #if fp[file[:-4]].read()=="":  
            #fp[file[:-4]].write('{"is_leaf":true,"sons":[],"keys":[]}')
            #fp[file[:-4]].seek(0)
        tree_root[name]=load_tree_from_json(json.loads(fp[name].read()))
        global prev 
        prev = None
        maintain_left_right_pointer(tree_root[name])

# store all the trees back to json
def finalize_index():
    file_list = os.listdir(path)
    for file in file_list:
        name = file[:-4]
        fp[name].seek(0)
        fp[name].truncate()
        fp[name].write(json.dumps(turn_tree_into_json(tree_root[name])))
        fp[name].close()

# create a new table with a unique key
def create_table(table_name,unique_key):
    fp[table_name+'_'+unique_key] = open(path+table_name+'_'+unique_key+'.ind','a+')
    fp[table_name+'_'+unique_key].write('{"is_leaf":true,"sons":[],"keys":[]}')
    tree_root[table_name+'_'+unique_key]=load_tree_from_json(json.loads('{"is_leaf":true,"sons":[],"keys":[]}'))
    global prev 
    prev = None
    maintain_left_right_pointer(tree_root[table_name+'_'+unique_key])

# delete a table and all its index
def delete_table(table_name):
    list = catalog.get_index_list(table_name)
    for index_name in list:
        fp[table_name+'_'+index_name].close()
        os.remove(path+table_name+'_'+index_name+'.ind')

# delete an index
def delete_index(index_name):
    file_list = os.listdir(path)
    for file in file_list:
        if index_name == file.split('_')[1]:
            fp[file[:-4]].close()
            os.remove(path+file)
            return file.split('_')[0]
    raise Exception('No index named '+index_name+'!')

# create an index on an attr
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

# insert a node to a table according to an index		
def insert_entry(table_name,index_name, key, data):
    global root
    root = tree_root[table_name+'_'+index_name]
    res = insert(tree_root[table_name+'_'+index_name],key,data)
    tree_root[table_name+'_'+index_name] = root
    # prt(get_leftest_child(tree_root[table_name+'_'+index_name]))
    # print('---------------------------')
    # prtl(get_rightest_child(tree_root[table_name+'_'+index_name]))

# select nodes in a table according to where clauses
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

# delete an index on a table
def delete_table_index(table_name, index_name):
    tree_root[table_name+'_'+index_name] = load_tree_from_json(json.loads('{"is_leaf":true,"sons":[],"keys":[]}'))
    global prev
    prev = None
    maintain_left_right_pointer(tree_root[table_name+'_'+index_name])

# delete some nodes according to an index
def delete_entries(keylist, table_name, index_name):
    for key in keylist:
        global root
        root = tree_root[table_name+'_'+index_name]
        delete(tree_root[table_name+'_'+index_name],key)
        tree_root[table_name+'_'+index_name] = root
        prt(get_leftest_child(tree_root[table_name+'_'+index_name]))
        #print('---------------------')

# check if column with index satisfies unique constraint
def check_unique(table_name, index_name, value):
    if table_name + '_' + index_name in tree_root.keys():
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
    else:
        raise Exception("Index Module : index '%s' does not exists. " % index_name)