import random
import string

filename='bigdata.txt'
fp=open(filename,'a')
create='create table bigbase (id int unique, point float, rstr char(10), grade int, sequence float unique, primary key(id));'
fp.write(create+'\n')
for i in range(1000):
    id=i
    float=random.randint(0,1000)/100
    rstr=''.join(random.sample(string.ascii_letters, 9))
    grade=random.randint(50,100)
    sequence=i/5
    clause='insert into bigbase values  ('+str(i)+', '+str(float)+', '+rstr+', '+str(grade)+', '+str(sequence)+');'
    fp.write(clause+'\n')
fp.write('create index seqDex on bigbase (sequence);'+'\n')
fp.write('select * from bigbase where id<=20;'+'\n')
fp.write('select * from bigbase where id<=20 and sequence>0.5;'+'\n')
fp.write('delete from bigbase where id>=10;'+'\n')
fp.write('select * from bigbase;'+'\n')
fp.write('delete from bigbase;'+'\n')
fp.write('select * from bigbase;'+'\n')
fp.write('drop index seqDex;'+'\n')
fp.write('drop table bigbase;'+'\n')
fp.write('create table city (cname char(20) unique, population int, avg float, primary key(cname));'+'\n')
