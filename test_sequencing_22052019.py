import psycopg2

try:
    conn = psycopg2.connect("dbname='shahapurBusDepot' user='postgres' host='localhost' password='postgres'")
except:
    print "I am unable to connect to the database"
    
try:
    cur=conn.cursor()
    sql= "select v.vert_id, t.name, t12rs.rs_id as rs_id , count(distinct(virs.vert_id)) from t_31052019 as t inner join t1_t2_rs as t12rs on t.name = t12rs.termini1 inner join v  on v.geom = t.geom inner join v_inter_rs as virs on t12rs.rs_id =  virs.rs_id group by 1, 2, 3  order by 3;" 
    cur.execute(sql)
    res_v1_t1_rs = cur.fetchall() 
    for rs in res_v1_t1_rs:
        print rs[0], " ", rs[1], " ", rs[2], " ", rs[3]
        sql = "select v21e.vert1, v21e.vert2, v21e.edgeid, rse.rs_id from v1_v2_e as v21e inner join rs_e as rse on v21e.edgeid = rse.edge_id where rse.rs_id like '"+rs[2]+ "' order by 4;"
#        print sql
        
            
        cur.execute(sql)
        a= cur.fetchall()
        A = []
        vertSeq = []
        for c in a:
            A.append(c)
#        print A
        start = rs[0]
        vertSeq.append(start)
        k = 0
        j = 0 
        while (j <len(A) and k <= len(A)-1):
#            print "j =", j
#            print "k = ",  k
#            print A[j][0], " ", A[j][1], " ", A[j][2], " ", A[j][3]
            if (A[j][0] == start):
#                print start
                dir = +1
                start = A[j][1]
                vertSeq.append(start)
#                print "after changing start :", start
                seq = k + 1
                temp = A[j]
                A[j]= A[k]
                A[k]= temp
                j = k
                k = k+1
                
                
                print A[j][0], " ", A[j][1], " ", A[j][2], " ", A[j][3] , " ", dir , " ", seq
            elif (A[j][1] == start):
#                print start
                dir = -1
                start = A[j][0]
                vertSeq.append(start)
#                print "after changing start :", start
                seq = k + 1
                temp = A[j]
                A[j]= A[k]
                A[k]= temp
                j = k
                k = k+1
                print A[j][0], " ", A[j][1], " ", A[j][2], " ", A[j][3] , " ", dir , " ", seq
                
        
            j = j+1
            
#            print j
                
        if(k < rs[3] -1):
            print "error " +rs[2]
        print vertSeq
        vertSeq = [] 
 
        
        
#        for a in A:
#            print a[0], " ", a[1], " ", a[2], " ", a[3]
#    
except Exception as e:
    print (e)