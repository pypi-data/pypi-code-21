'''
Created on Jan 17, 2014

@author: stauffer
'''


#!/usr/bin/python
import math;
import random
import numpy as np;

def bcubed_suff_stats(gid,cid):
    # This function returns the per entry precision and recall estimates
    #   gid- the groundtruth id
    #     groundtruth id of -1 is reserved for "not annotated" (false positive)
    #   cid- the cluster id
    #     cluster id of -1 is reserved for "not in cluster" (treated as singlet)

    # check lengths
    lg=len(gid)
    lc=len(cid)
    if (lg!=lc):
        return None
    
    # calc stats
    stats=np.zeros([lc,2])
    for ind in range(0,lc):
        # get gt and cluster labels
        gval=gid[ind]
        cval=cid[ind]
        #print i,gval,cval
        # get indices for gt and cluster matches
        gmatches=[i for i in range(0,len(gid)) if gid[i]==gval]
        cvals=[cid[i] for i in gmatches]
        cmatches=[i for i in range(0,len(cid)) if cid[i]==cval]
        gvals=[gid[i] for i in cmatches]
        # calculate the per item precision and recall
        prec=float(gvals.count(gval))/len(gvals);
        recall=float(cvals.count(cval))/len(cvals);
        #fmeasure=2*prec*recall/(prec+recall) # not sufficient statistics
        #print i,gval,cval,prec, recall
        stats[ind,0]=prec;
        stats[ind,1]=recall;
        
    return stats


def bcubed(gid,cid):
    # This function performs standard bcubed metrics
    
    garr=np.array(gid)
    carr=np.array(cid)
    #get bcubed sufficient statistics
    stats=bcubed_suff_stats(gid,cid)
    if (stats==None):
        return None;
    # HANDLE SPECIAL CASES
    #print stats
    # false negatives are zero precision and zero recall
    cmask=np.where(carr==-1)
    stats[cmask,0]=0;
    stats[cmask,1]=0
    # do not use stats from false positives
    gmask=np.where(garr==-1)
    stats=np.delete(stats,gmask,axis=0)
    
    # calculate mean p,r,f scores
    prf=np.mean(stats,axis=0).tolist();
    # return prf
    f=2*prf[0]*prf[1]/(prf[0]+prf[1])
    prf.append(f);
    return prf


def generate_cids(gid, method='randperm',K=2):
    #print "method is "+method;
    N=len(gid);
    if (method=='singlets'):
        return range(0,N)
    elif (method=='oneclass'):
        return [1]*N
    elif (method=='randperm'):
        cid=list(gid);
        random.shuffle(cid);
        return cid;
    elif (method=='random'):
        # must specify K or get default value for K
        if (K==None):
            K=math.ceil(math.sqrt(N))
        cid=[]
        for _ in range(N):
            cid.append(random.randint(1,K))
        return cid
    elif (method=='perfect'):
        return list(gid)  
    else:
        print "cid generation method not recognized: "+method;
        
    return None

    

def bcubed_conf_range(gid,cid,conf):
    # This returns bcubed precision/recall stats for sets with decreasing conf

    # get statistics
    stats=bcubed_suff_stats(gid,cid)
    prf=[];
    
    # determine ordering
    ##ind=(range(0,len(conf)));
    ##d=dict(zip(conf,ind));
    indtup=sorted(enumerate(conf),key=lambda x:x[1],reverse=True)
    ind=[i[0] for i in indtup];
    
    # determine skip rate
    psum=0;
    rsum=0;
    n=0;
    for i in ind:
        # maintain sufficient statistics
        psum+=stats[i][0]
        rsum+=stats[i][1]
        n+=1
        # if skip iteration, add stats to list
        p=psum/n
        r=rsum/n
        f=2*p*r/(p+r)
        prf.append([p,r,f])
        
        
    # return stat lists
    return prf


def test_simple():
    print "Running simple test..."
    # make id list
    gid=range(-1,1)*5;
    # make cluster list(s)  {singlet,complete,permutation}
    cid0=generate_cids(gid,'singlets')
    cid1=generate_cids(gid,'oneclass')
    cid2=generate_cids(gid,'randperm')
    cid3=generate_cids(gid,'perfect')
    cid4=generate_cids(gid,'random',K=6)
    cid5=generate_cids(gid,'random')
    
    cidlist=[cid0,cid1,cid2,cid3,cid4,cid5]
    #cidlist=[cid2]
    # for each cluster list
    for cid in cidlist:
        
        # run/store statistics
        print gid
        print cid
        prf=bcubed(gid,cid);
        print prf
        print
    # output results
    print "  Completeed Simple Test."
    
    return

def test_conf():
    gid=range(-1,1)*5
    cid=generate_cids(gid,'randperm')
    N=len(gid)
    conf=[float(x)/N for x in range(0,N)]
    
    prf=bcubed_conf_range(gid, cid, conf)
    print prf
    

if __name__ == '__main__':

    gt_fn = '/proj/janus3/data/Janus_CS3/CS3_2.0/clustering_protocols/test7_clustering/cs3_clustering_test7_ground_truth.csv'
    c_fn = '/proj/janus/nate.crosswhite/eval/11JAN16_clustering/results_D3.1_cluster_32_100/clustering/clustering_7/cluster_32.txt'

    gt_sids = {}
    with open(gt_fn, 'r') as f:
        next(f) # header
        for l in f:
            v = l.split(',')
            tid = int(v[0])
            sid = int(v[1])
            gt_sids[tid] = sid
    cids = []
    gids = []
    with open(c_fn, 'r') as f:
        for l in f:
            parts = l.strip().split(',')
            tid = int(parts[0])
            sid = int(parts[1])
            cid = int(parts[2])
            score = float(parts[3])
            cids.append(cid)
            gids.append(gt_sids[tid])

    prf = bcubed(gids, cids)
    print 'Precision: %.6f\nRecall: %.6f\nF-Score: %.6f' % (prf[0], prf[1], prf[2])

    # print("This is a test script.")

    #test_simple()
    # test_conf()

    print("Done!")

