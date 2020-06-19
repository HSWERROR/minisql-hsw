import sys
import os
import API


def start():
    print("Welcome to MiniSQL!")
    print("Please input the command ")
    print("input \help if you need for help")


def Command():
    print("minisql>", end="")
    command = input().lower()
    while 1:
        if ';' in command:
            break
        print("\t  ->", end="")
        s = input()
        command = command + " " + s
    # print(command)
    return command


def Translate(SQL):
    if "help" in SQL:
        help_example()
    check = SQL.split()
    # print(check[0])
    if check[0] == "create":
        if check[1] == "table":
            table_name = check[2]
            end = table_name.find("(")
            if end != -1:
                table_name = table_name[:end]
            # print(table_name)

            # error:出现括号数量不一样
            count1 = SQL.count("(")
            count2 = SQL.count(")")
            # print(count1,count2)
            assert count1 == count2, "输入语法错误！括号未对应"

            start = SQL.find("(")
            end = SQL.rfind("primary")
            c = SQL[start + 1:end]
            # print(start, end, c)
            Attribute_Value = c.split(",")
            #print(Attribute_Value)
            for i in range(len(Attribute_Value)):
                Attribute_Value[i] = ' '.join(Attribute_Value[i].split())
            Attribute_Value = [x for x in Attribute_Value if x != ""]
            #print(Attribute_Value)

            for i in range(len(Attribute_Value)):
                Attribute_Value[i]=Attribute_Value[i].replace("(", " ").replace(")", "").split(" ")
                Attribute_Value[i] = [x for x in Attribute_Value[i] if x != ""]
                #print(Attribute_Value[i])
                pos = -1
                int_number = Attribute_Value[i].count("int")
                float_number = Attribute_Value[i].count("float")
                #print(int_number,float_number)
                if int_number == 1 :
                    Attribute_Value[i]=Attribute_Value[i]+["0"]
                # print(Attribute_Value[i])
                pos2 = -1
                if float_number == 1:
                    Attribute_Value[i]=Attribute_Value[i]+[0]
                if "unique" not in Attribute_Value[i]:
                    Attribute_Value[i]=Attribute_Value[i]+[[]]+[0]
                else:
                    pos = Attribute_Value[i].index("unique")
                    #print(pos)
                    del Attribute_Value[i][pos]
                    Attribute_Value[i] = Attribute_Value[i] +[[]]+ [1]
                #print(Attribute_Value[i])
            #print(Attribute_Value)

            base = SQL.find("primary key")
            start = SQL.find("(", base, len(SQL))
            end = SQL.find(")", base, len(SQL))
            Primary_Key = SQL[start + 1:end]
            Primary_Key = ' '.join(Primary_Key.split()).replace(" ","")
            #print(Primary_Key)
            # 在这里调用创建表的函数，
            API.create_table(table_name, Attribute_Value, Primary_Key)
            # 可以传入的参数有table_name，Attribute_Value，Attribute_num，Primary_Key

        elif check[1] == "index":
            index_name = check[2]
            table_name = check[4]
            start = SQL.find("(")
            end = SQL.find(")")
            column_name = SQL[start + 1:end].replace(" ", "")
            #print(index_name,table_name,column_name)
            # 在这里调用创建索引的函数，
            API.create_index(table_name, index_name, column_name)
            # 可以传入的参数有index_name,table_name,column_name


    elif check[0] == "drop":
        if check[1] == "table":
            table_name = check[2]
            if ";" in table_name:
                table_name = table_name.replace(";", "")
            #print(table_name)
            # 在这里调用删除表的函数，
            API.drop_table(table_name)
            # 可以传入的参数有table_name
        elif check[1] == "index":
            index_name = check[2]
            if ";" in index_name:
                index_name = index_name.replace(";", "")
            #print(index_name)
            # 在这里调用删除索引的函数，
            API.drop_index(index_name)
            # 可以传入的参数有index_name

    elif check[0] == "select":
        # 实际和API对接的时候发现并不需要判断是否有where，只要传入完整SQL语句即可
        if "where" not in SQL:
            start = SQL.find("from")
            end = SQL.find(";")
            table_name = SQL[start + 4:end].replace(" ", "")
            #print(table_name)
            # 在这里调用无where的选择函数（或在下面统一调用），
            s = SQL.find("select")
            e = SQL.find("from")
            API.select(table_name, SQL[s + 6:e].replace(" ", ""))
            # 可以传入的参数有table_name
        else:
            start = SQL.find("from")
            mid = SQL.find("where")
            end = SQL.find(";")
            table_name = SQL[start + 4:mid].replace(" ", "")
            where_condition = SQL[mid + 5:end]
            where_condition=' '.join(where_condition.split())
            #print(where_condition)
            # 在这里调用有where的选择函数，
            API.select(table_name, where_condition)
            # 可以传入的参数有table_name,where_condition

    elif check[0] == "insert":
        start = SQL.find("into")
        mid = SQL.find("values")
        end = SQL.find(";")
        table_name = SQL[start + 5:mid].replace(" ", "")
        values = SQL[mid + 6:end].replace(" ", "").replace("'", "").replace("’", "").replace("‘", "").replace("(", "").replace(")", "").split(",")
        # print(table_name, values)
        # 在这里调用插入函数，
        API.insert(table_name,values)
        # 可以传入的参数有table_name,values

    elif check[0] == "delete":
        # 实际和API对接的时候发现并不需要判断是否有where，只要传入完整SQL语句即可
        if "where" not in SQL:
            start = SQL.find("from")
            end = SQL.find(";")
            table_name = SQL[start + 4:end].replace(" ", "")
            # print(table_name)
            # 在这里调用无where的删除记录函数（或在下面统一调用）
            where_condition = "*"
            API.delete_tuple(table_name, where_condition)
            # 可以传入的参数有table_name
        else:
            start = SQL.find("from")
            mid = SQL.find("where")
            end = SQL.find(";")
            table_name = SQL[start + 4:mid].replace(" ", "")
            where_condition = SQL[mid + 5:end]
            where_condition = ' '.join(where_condition.split())
            #print(table_name,where_condition)
            # 在这里调用有where的删除记录函数，
            API.delete_tuple(table_name, where_condition)
            # 可以传入的参数有table_name,where_condition

    elif check[0] == "execfile":
        file_name = check[1].replace(";", "")
        # print(file_name)
        Execfile(file_name)

    else:
        print("ERROR INPUT ! Please check again !")


def help_example():
    print("Which opperation do you want to get help")
    command = input("Choose from Create,Drop,Select,Insert,Delete,Quit,Execfile: ")
    if "Create" in command:
        command2 = input("Table or Index ?")
        if "Table" in command2:
            print("create table 表名 (")
            print("列名 类型 ,")
            print("列名 类型 ,")
            print("primary key ( 列名 ));")
        else:
            print("create index 索引名 on 表名 ( 列名 );")
    elif "Drop" in command:
        command2 = input("Table or Index ?")
        if "Table" in command2:
            print("drop table 表名 ;")
        else:
            print("drop index 索引名 ;")
    elif "Select" in command:
        print("select * from 表名 ;")
        print("或")
        print("select * from 表名 where 条件 ;")
    elif "Insert" in command:
        print("insert into 表名 values ( 值1 , 值2 , … , 值n );")
    elif "Delete" in command:
        print("delete from 表名 ;")
        print("或")
        print("delete from 表名 where 条件 ;")
    elif "Quit" in command:
        print("any input which includes ';' ")
    elif "Execfile" in command:
        print("execfile 文件名 ;")


def Execfile(file_name):
    if os.path.exists(file_name):
        f = open(file_name, 'r')
        command = ""
        for eachline in f:
            command = command + eachline.replace("\n", "").replace("\t", "")
            if ";" in eachline:
                Translate(command)
                # print(command)
                command = ''
        f.close()
    else:
        print("ERROR：File does not exist ！")


def main():
    start()
    SQL = ""
    API.init_all()
    while 1:
        if "quit" in SQL:
            break
        SQL = Command()
        Translate(SQL)
    API.finalize_all()


if __name__ == '__main__':
    main()

