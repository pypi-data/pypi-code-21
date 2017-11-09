#!/usr/bin/python3
# TODO : 添加根据评分信息的批量删除功能函数，在数据苦衷还需要添加对于aifeature和page
# 对应触发器

import pymysql

def user_read(cur , conn ,name = None):
    answer = 'select * from user where '
    if name != None : answer += 'name = "%s"' % name
    else : print('Please input the name for searching')
    cur.execute(answer)
    return cur.fetchone()

def user_write(cur , conn , name = 'NULL' , passwd = 'NULL' , photo = 'NULL' , model = 'NULL'):
    try :
        if name == 'NULL' or passwd == 'NULL' : 
            raise Exception('ERROR for no name or no passwd')
        else:
            answer = 'insert into user(name , passwd , photo , model) values("%s","%s","%s","%s")' % (name , passwd , photo , model)
            cur.execute(answer)
            conn.commit()
    except Exception as e:
        print(e)

def page_read(cur , conn , md5url = None , content = None):
    if md5url == None : print('Please input the url for searching')
    else :
        print(md5url)
        answer = 'select * from page where '
        answer += 'md5url = "%s"' % md5url
        print(answer)
        cur.execute(answer)
        return cur.fetchall()    # 记得之后的网而言是加密过的

def page_write(cur , conn ,md5url = 'NULL' , content = 'NULL'):
    try :
        if md5url == 'NULL':
            raise Exception('ERROR for no url')
        else:
            answer = 'insert into page(md5url , content) values("%s" , "%s")' % (md5url , content)
            cur.execute(answer)
            conn.commit()
    except Exception as e:
        print(e)

def aifeature_read(cur , conn , md5url = None):
    if md5url == None :
        answer = 'select * from aifeature'
        cur.execute(answer)
        return cur.fetchall()    # 全返回
    else:
        answer = 'select * from aifeature where md5url = "%s"' % md5url
        cur.execute(answer)
        return cur.fetchone()
        
def aifeature_write(cur , conn , md5url = 'NULL' , size = 0 , number_reader = 0 , number_like = 0 , grade = 0.0 , number_code = 0 , number_photo = 0 , number_link = 0):
    try :
        if md5url == 'NULL' : 
            raise Exception('ERROR for no md5url')
        else:
            answer = 'insert into aifeature(md5url , size , number_reader , number_like , grade , number_code , number_photo , number_link) values("%s" , %d , %d , %d , %f , %d, %d , %d)' % (md5url , size , number_reader , number_like , grade , number_code , number_photo , number_link)
            cur.execute(answer)
            conn.commit()
    except Exception as e:
        print(e)

# 修改用户样本空间,目前只允许用户修改所谓的成绩策略
def aifeature_alter(cur , conn , md5url = 'NULL', grade = 0.0):
    try :
        if md5url == 'NULL' :
            raise Exception('ERROR for no md5url')
        else:
            answer = 'update aifeature set '
            if grade != 0.0 : 
                answer += 'grade = %f ' % grade
            answer += 'where md5url = "%s"' % md5url 
            cur.execute(answer)
            conn.commit()
            f = cur.fetchall()
            return f
    except Exception as e:
        print(e)

def user_alter(cur , conn , old_name = 'NULL', new_name = 'NULL' , passwd = 'NULL' , photo = 'NULL' , model = 'NULL'):
    try:
        a , b , c , d = user_read(cur , conn , name = old_name)
        if new_name == 'NULL' : new_name = a
        if passwd == 'NULL' : passwd = b
        if photo == 'NULL' : photo = c[2:-1]
        if model == 'NULL' : model = d
        if old_name == 'NULL':
            raise Exception('ERROR for no name to the user')
        else:
            answer = 'update user set name = "%s" , passwd = "%s" , photo = "%s" , model = "%s" where name = "%s"' % (new_name , passwd , photo , model , old_name)
            cur.execute(answer)
            conn.commit()
            f = cur.fetchall()
            return f
    except Exception as e:
        print(e)

def user_delete(cur , conn , name = None):
    '''
    根据用户名删除用户
    '''
    try:
        if name == None : 
            raise Exception('ERROR for no such user')
        answer = 'delete from user where name = "%s"' % name
        cur.execute(answer)
        conn.commit()
    except Exception as e:
        print(e)

def page_delete(cur , conn , md5url = None):
    '''
    在这里用户可以通过评分批量删除博文，需要增加对于aifeature和page的触发器和相应的路基实现，目前的该函数提供一个简单的接口用于根据md5url删除博文
    '''
    try:
        if md5url == None : 
            raise Exception('ERROR for no such blog')
        answer = 'delete from page where md5url = "%s"' % md5url
        print(answer)
        cur.execute(answer)
        conn.commit()
        return cur.fetchall()
    except Exception as e:
        print(e)

def page_batch_delete(cur , conn , grade = -1):
    '''
    该函数批量删除某一种评价的博文集合，在前端提供一种办理的操作，后端需要的数据库接口实现
    '''
    try:
        if grade == -1:
            raise Exception('ERROR for no grade!')
        else:
            answer = 'delete from page where md5url in (select md5url from aifeature where grade = %d)' % grade
            cur.execute(answer)
            conn.commit()
            return cur.fetchall()
    except Exception as e:
        print(e)

# 该函数提供对数据库操作的统一接口
def main(type_  , **argv):
    '''
    1 - user_read
    2 - user_write
    3 - page_read
    4 - page_write
    5 - aifeature_read
    6 - aifeature_write
    7 - aifeature_alter
    8 - user_alter
    9 - user_delete
    10 - page_delete
    11 - page_batch_delete
    '''
    # 建立连接
    conn = pymysql.connect(host = '127.0.0.1' , port = 3306 , user = 'root' \
            , passwd = 'lt970106' , db = 'fortest' , charset = 'utf8')
    cur = conn.cursor()
    save = None
    print("数据库和游标建立成功")
    if type_ == 1 : save = user_read(cur , conn , **argv)
    elif type_ == 2 : user_write(cur , conn , **argv)
    elif type_ == 3 : save = page_read(cur , conn , **argv)
    elif type_ == 4 : page_write(cur ,conn ,**argv)
    elif type_ == 5 : save = aifeature_read(cur , conn ,**argv)
    elif type_ == 6 : aifeature_write(cur , conn ,**argv)  
    elif type_ == 7 : save = aifeature_alter(cur , conn , **argv)
    elif type_ == 8 : save = user_alter(cur , conn , **argv)
    elif type_ == 9 : user_delete(cur , conn , **argv)
    elif type_ == 10 : save = page_delete(cur , conn , **argv)
    elif type_ == 11 : page_batch_delete(cur , conn , **argv)
    cur.close()
    conn.close()
    print("数据库顺利关闭，数据读写成功")
    return save

if __name__ == "__main__":
   main(11 , **{'grade' : 4})
