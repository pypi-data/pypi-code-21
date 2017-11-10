"""
Thestral.py
V0.1.0

Edited by Kevin Fang
~~~~~~~~~~

Single-cell RNA-SEQ analysis pipeline for Qu lab USTC.
"""

#### Libraries
import numpy as np
import pandas as pd
#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid",font_scale=1.2)
import matplotlib.patches as mpatches
from scipy.io import mmread
import scipy.sparse as sp_sparse
from scipy import stats
import random
from scipy.stats.mstats import gmean
from scipy.stats.mstats import zscore
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import kneighbors_graph
from sklearn.manifold import SpectralEmbedding
from sklearn.cluster import MiniBatchKMeans
from sklearn import cluster
from . import SIMLR
from scipy.spatial.distance import squareform
from scipy.spatial.distance import pdist
#from Tenebrus import tenebrus

#### S&L DATA
def create_Tenebrus_object(mtx,gene,barcode):
    """
    Read Gene X Barcodes matrix from 10X mapping output files
    mtx_file, gene_file, barcode_file

    """
    return Tenebrus(pd.DataFrame(mmread(mtx).todense(),index=[line.rstrip().split()[-1] for line in open(gene)],columns=[line.rstrip() for line in open(barcode)]).astype(int))

def scatter(data,label,vmin=None,vmax=None,kind='label',cmap="nipy_spectral",s=10,fontsize=20,markerscale=3):
    if kind=="distribution":
        fig=plt.figure()
        plt.scatter(data.ix[:,0], data.ix[:,1],s, label,cmap=cmap,vmin=vmin,vmax=vmax)
        plt.colorbar()
        plt.show()
    else:
        colormap=getattr(plt.cm,cmap)
        colorst=[colormap(i) for i in np.linspace(0,1,len(set(label.values)))]
        temp=0
        for x in set(label.values):
            plt.scatter(data.ix[label==x].ix[:,0],data.ix[label==x].ix[:,1],s,label=x,color=colorst[temp])
            temp+=1
        plt.legend(fontsize=fontsize,markerscale=markerscale,bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.show()

def heatmap():
    #sns.heatmap(CSPA_weight_matrix)
    colormap=getattr(plt.cm,"Vega20")
    lut=pd.Series([colormap(i) for i in np.linspace(0,1,len(set(category.values)))],index=set(category.values))
    colorst=category.map(lut)
    g=sns.clustermap(pd.DataFrame(CSPA_matrix,index=data.columns,columns=data.columns),row_cluster=False,col_cluster=False,row_colors=colorst,col_colors=colorst,linewidths=0, xticklabels=False, yticklabels=False)
    for label in np.unique(category.values):
        g.ax_col_dendrogram.bar(0, 0, color=lut[label],label=label, linewidth=0)
    g.ax_col_dendrogram.legend(loc="center", ncol=6)
    g.cax.set_position([.15, .2, .03, .45])
    plt.show()

def p_adjust_bh(p):
    p = np.asfarray(p)
    by_descend = p.argsort()[::-1]
    by_orig = by_descend.argsort()
    steps = float(len(p)) / np.arange(len(p), 0, -1)
    q = np.minimum(1, np.minimum.accumulate(steps * p[by_descend]))
    return q[by_orig]

def tsne(data,dim_use="all",dimension=2,iteration=1000,epsilon=500,rs=0):
    if dim_use!="all":
        data=data[[x for x in range(dim_use)]]
    model=TSNE(init="pca",n_components=dimension,n_iter=iteration,learning_rate=epsilon,random_state=rs)
    return pd.DataFrame(model.fit_transform(data),index=data.index,columns=["tsne_"+str(x) for x in range(1,dimension+1)])


def KNN(data,nCluster,n_neighbors):
    connectivity = kneighbors_graph(data, n_neighbors=n_neighbors, include_self=False)
    connectivity = 0.5*(connectivity + connectivity.T)
    ward_linkage = cluster.AgglomerativeClustering(n_clusters=nCluster, linkage="ward", connectivity=connectivity)
    return pd.Series(ward_linkage.fit(data).labels_,index=data.index)



#### Class Tenebrus

class Tenebrus(object):

    def __init__(self,data):
        if data.index[0][:5]=="hg19_":
            data.index=[x[5:] for x in data.index]
        self.raw_data=data
        self.data=data
        self.label={}

### FUNCTION FOR QUALITY CONTROL

    def QC(self):
        """
        Get distributino of UMI counts , detected gene counts and MT UMI ratio in all detected cells

        """
        self.cell_umi=self.data.apply(lambda x:x.sum())
        self.cell_gene=self.data.apply(lambda x:(x>0).sum())
        self.cell_mt_ratio=self.data.ix[[x for x in self.data.index if x[:3]=="MT-"]].apply(lambda x:x.sum())/self.cell_umi
        self.gene_detected=self.data.apply(lambda x:(x>0).sum(),axis=1)
        #self.gene_detected=self.gene_detected[self.gene_detected>0]
        fig=plt.figure()
        #sns.set(style="white",font_scale=1.2)
        ax1=fig.add_subplot(1,3,1)
        ax1=sns.boxplot(self.cell_umi,orient='v')
        ax1.set_xlabel("UMI",fontsize=14)
        ax2=fig.add_subplot(1,3,2)
        ax2=sns.boxplot(self.cell_gene,orient='v')
        ax2.set_xlabel("GENE",fontsize=14)
        ax3=fig.add_subplot(1,3,3)
        ax3=sns.boxplot(self.cell_mt_ratio,orient='v')
        ax3.set_xlabel("MT_Ratio",fontsize=14)
        #ax4=fig.add_subplot(1,4,4)
        #ax4=sns.boxplot(self.gene_detected,orient='v')
        #ax4.set_xlabel("GENE_NUM",fontsize=14)
        plt.subplots_adjust(wspace=0.4)
        plt.show()
        #plt.close()



    def saturation_curve(self,step=20):
        """
        Calculate the saturation curve for the experiment

        """
        def trans_list(a,b):
            temp=[[a[x]]*b[x] for x in range(len(a))]
            temp=[x for y in temp for x in y]
            random.shuffle(temp)
            return temp
        temp_cell=sp_sparse.csr_matrix(self.data).indices
        temp_gene=sp_sparse.csc_matrix(self.data).indices
        umi=sp_sparse.csc_matrix(self.data).data
        cell=np.asarray(trans_list(temp_cell,umi))
        gene=np.asarray(trans_list(temp_gene,umi))
        scale=range(0,sum(umi),sum(umi)/step)[1:]
        total_gene=[]
        percell_gene=[]
        for x in scale:
            temp=random.sample(range(sum(umi)),x)
            total_gene.append(len(set(gene[[temp]])))
            percell_gene.append(len(set(zip(gene[[temp]],cell[[temp]])))/len(set(cell[[temp]])))
        self.scale=scale
        self.percell_gene=percell_gene
        self.total_gene=total_gene
        fig=plt.figure()
        ax1=fig.add_subplot(1,2,1)
        ax1=plt.plot(self.scale,self.total_gene)
        ax1=plt.scatter(self.scale,self.total_gene)
        ax1=plt.xlabel("UMI_Number")
        ax1=plt.ylabel("Total_detected_gene")
        ax2=fig.add_subplot(1,2,2)
        ax2=plt.plot(self.scale,self.percell_gene)
        ax2=plt.scatter(self.scale,self.percell_gene)
        ax2=plt.xlabel("UMI_Number")
        ax2=plt.ylabel("Per_cell_gene")
        plt.subplots_adjust(wspace=0.4)
        plt.show()
        #plt.close()


    def filter(self,umi_thresholds=None,gene_thresholds=None,MT_thresholds=None,detected_thresholds=None):
        """

        Filter irrgegular cell or gene

        """
        if detected_thresholds:
            self.data=self.data.loc[(self.gene_detected<=detected_thresholds[1]) & (self.gene_detected>=detected_thresholds[0])]
        if umi_thresholds:
            self.data=self.data.loc[:,((self.cell_umi<=umi_thresholds[1]) & (self.cell_umi>=umi_thresholds[0]))]
        if gene_thresholds:
            self.data=self.data.loc[:,((self.cell_gene<=gene_thresholds[1]) & (self.cell_gene>=gene_thresholds[0]))]
        if MT_thresholds:
            self.data=self.data.loc[:,((self.cell_mt_ratio<=MT_thresholds[1]) & (self.cell_mt_ratio>=MT_thresholds[0]))]


### FUNCTION FOR NORMLISATION

    def norm(self,method):
        """

        We provide DESeq_norm, mean_norm, total_size_norm, Seurat_norm, possion_norm and fang_norm to normlise your raw data

        """
        #try:
        #    self.norm_data=self.data
        #except:
        #    self.norm_data=self.data

        if method=="DESeq":
            self.data=np.log2(self.data/(self.data.T/self.data.apply(gmean,axis=1)).dropna(axis=1,how='any').apply(np.median,axis=1)+1)
        if method=="total_log2":
            self.data=np.log2(self.data*(np.median(self.cell_umi)/self.cell_umi)+1)
        if method=="total_log10":
            self.data=np.log10(self.data*(np.median(self.cell_umi)/self.cell_umi)+1)
        if method=="mean_norm":
            self.data=np.log(self.data*(np.median(self.cell_umi/self.cell_gene)/(self.cell_umi/self.cell_gene))+1)
        if method=="Seurat_norm":
            self.data=np.log(self.data/self.data.apply(lambda x:x.sum())*10000+1)
        if method=="qnorm":
            rank_mean = self.data.stack().groupby(self.data.rank(method='first').stack().astype(int)).mean()
            self.data=np.log2(self.data.rank(method='min').stack().astype(int).map(rank_mean).unstack()+1)

### FUNCTION FOR FINDVARGENES
    def Calculate_disperson(self,steps=20,mean_thresholds=[0.0125,3],zscore_thresholds=0.5,loged=True):
        """
        We provide gene disperson calculated method, as the same as seurat, to select high_var gene
        """
        data=self.data[self.data.apply(sum,axis=1)>0].copy()
        if loged==False:
            data=np.log1p(data)
        self.disperson=pd.DataFrame({"disperson":data.apply(lambda x:np.log(np.var(np.expm1(x),ddof=1)/np.mean(np.expm1(x))),axis=1),"mean":data.apply(lambda x:np.log1p(np.mean(np.expm1(x))),axis=1)})
        self.disperson["zscore"]=self.disperson.groupby(pd.cut(self.disperson["mean"],steps))["disperson"].transform(zscore)
        self.disperson=self.disperson.fillna(0)
        self.var_genes=self.disperson.ix[(self.disperson["mean"]>mean_thresholds[0]) & (self.disperson["mean"]<mean_thresholds[1]) & (self.disperson["zscore"]>zscore_thresholds)]
        self.high_var_data=self.data.ix[(self.disperson["mean"]>mean_thresholds[0]) & (self.disperson["mean"]<mean_thresholds[1]) & (self.disperson["zscore"]>zscore_thresholds)]
        plt.scatter(x=self.disperson["mean"],y=self.disperson["zscore"])
        plt.show()



### FUNCTION FOR CLUSTER
    def pca(self,dimension=10):
        pca=PCA(n_components=dimension)
        pca.fit(self.high_var_data)
        self.pca_data=pd.DataFrame(np.transpose(pca.components_),index=self.high_var_data.columns,columns=["PC_"+str(x) for x in range(1,dimension+1)])
        self.pca_ratio=pca.explained_variance_ratio_


    def label_append(self,name,label):
        if self.label.has_key(name):
            print "Warning: Label %s is exist, re-append this label will overwrite the old Label %s\n"%(name,name)
        self.label[name]=label[self.data.columns]

    def cluster(self,n_clusters,n_neighbors=10,tune_parameter=None):
        def cal_cosine(data):
            similarity = np.dot(data, data.T)
            square_mag = np.diag(similarity)
            inv_square_mag = 1 / square_mag
            inv_square_mag[np.isinf(inv_square_mag)] = 0
            inv_mag = np.sqrt(inv_square_mag)
            cosine = similarity * inv_mag
            cosine = cosine.T * inv_mag
            return(pd.DataFrame(cosine,index=data.index,columns=data.index))


        cosine=cal_cosine(self.data)
        self.cosine=cosine
        if tune_parameter==None: tune_parameter=self.data.shape[1]
        temp=MiniBatchKMeans(n_clusters=tune_parameter,max_iter=300,batch_size=1000,reassignment_ratio=0.005).fit_predict(cosine)
        self.gene_cluster=pd.Series(temp,index=cosine.index)
        self.mean_score=self.data.groupby(temp).mean().T.fillna(0)
        self.var_score=self.data.groupby(temp).var().T.fillna(0)
        self.label_append("mean_cluster",KNN(self.mean_score,nCluster=n_clusters,n_neighbors=n_neighbors))
        self.label_append("var_cluster",KNN(self.var_score,nCluster=n_clusters,n_neighbors=n_neighbors))

    def SIMLR_cluster(self,cluster_num,pca_dimuse,tune_parameter,**kargs):
        print "Notice: SIMLR Cluster method recommand \"total_log10\" normalization"
        simlr=SIMLR.SIMLR_LARGE(cluster_num,tune_parameter,0)
        S, F,val, ind = simlr.fit(SIMLR.SIMLR_helper.fast_pca(self.data.T,pca_dimuse))
        cluster =pd.Series(simlr.fast_minibatch_kmeans(F,cluster_num),index=self.data.columns)
        self.SIMLR_distance=S.todense()
        #g=sns.clustermap(S.todense(),vmin = 0, vmax=0.1, cbar_kws={"ticks":[0,0.1]},xticklabels=False,yticklabels=False)
        g=sns.clustermap(S.todense(),xticklabels=False,yticklabels=False)
        g.ax_row_dendrogram.set_visible(False)
        g.ax_col_dendrogram.set_visible(False)
        plt.show()
        self.SIMLR_tsne=tsne(pd.DataFrame(S.todense(),index=self.data.columns),**kargs)
        self.label_append("SIMLR_cluster",cluster)
        scatter(self.SIMLR_tsne,cluster)

    def SC3_cluster(self,n_cluster,eigen_use=None,tune_parameter=8,n_neighbors=10,**kargs):
        print "Notice: SC3 Cluster method recommand \"total_log2\" normalization"
        if eigen_use==None:
            eigen_use=int(self.data.shape[1]*0.06)
        dim=self.data.shape[1]
        CSPA_matrix=np.zeros([dim,dim])
        dist_P=self.data.corr()
        dist_S=self.data.corr("spearman")
        dist_E=pd.DataFrame(squareform(pdist(self.data.T,"euclidean")),index=self.data.columns,columns=self.data.columns)
        pca_E=pd.DataFrame(PCA(n_components=eigen_use).fit_transform(dist_E),index=self.data.columns,columns=["PC_"+str(x) for x in range(1,eigen_use+1)])
        se_E=pd.DataFrame(SpectralEmbedding(n_components=eigen_use).fit_transform(dist_E),index=self.data.columns,columns=["SE_"+str(x) for x in range(1,eigen_use+1)])
        pca_S=pd.DataFrame(PCA(n_components=eigen_use).fit_transform(dist_S),index=self.data.columns,columns=["PC_"+str(x) for x in range(1,eigen_use+1)])
        se_S=pd.DataFrame(SpectralEmbedding(n_components=eigen_use).fit_transform(dist_S),index=self.data.columns,columns=["SE_"+str(x) for x in range(1,eigen_use+1)])
        pca_P=pd.DataFrame(PCA(n_components=eigen_use).fit_transform(dist_P),index=self.data.columns,columns=["PC_"+str(x) for x in range(1,eigen_use+1)])
        se_P=pd.DataFrame(SpectralEmbedding(n_components=eigen_use).fit_transform(dist_P),index=self.data.columns,columns=["SE_"+str(x) for x in range(1,eigen_use+1)])
        km=KMeans(n_clusters=tune_parameter,max_iter=10**9,n_init=1000)
        for x in range(eigen_use):
            temp_pe=km.fit_predict(pca_E[[y for y in range(x+1)]])
            temp_se=km.fit_predict(se_E[[y for y in range(x+1)]])
            CSPA_matrix+=np.reshape([x==y for x in temp_pe for y in temp_pe],(dim,dim)).astype(int)
            CSPA_matrix+=np.reshape([x==y for x in temp_se for y in temp_se],(dim,dim)).astype(int)
            temp_ps=km.fit_predict(pca_S[[y for y in range(x+1)]])
            temp_ss=km.fit_predict(se_S[[y for y in range(x+1)]])
            CSPA_matrix+=np.reshape([x==y for x in temp_ps for y in temp_ps],(dim,dim)).astype(int)
            CSPA_matrix+=np.reshape([x==y for x in temp_ss for y in temp_ss],(dim,dim)).astype(int)
            temp_pp=km.fit_predict(pca_P[[y for y in range(x+1)]])
            temp_sp=km.fit_predict(se_P[[y for y in range(x+1)]])
            CSPA_matrix+=np.reshape([x==y for x in temp_pp for y in temp_pp],(dim,dim)).astype(int)
            CSPA_matrix+=np.reshape([x==y for x in temp_sp for y in temp_sp],(dim,dim)).astype(int)
        self.CSPA_matrix=pd.DataFrame(CSPA_matrix,index=self.data.columns,columns=self.data.columns)
        #g=sns.clustermap(self.CSPA_matrix,vmin = 0, vmax=0.1, cbar_kws={"ticks":[0,0.1]},xticklabels=False,yticklabels=False)
        g=sns.clustermap(self.CSPA_matrix,xticklabels=False,yticklabels=False)
        g.ax_row_dendrogram.set_visible(False)
        g.ax_col_dendrogram.set_visible(False)
        plt.show()
        self.SC3_tsne=tsne(pd.DataFrame(self.CSPA_matrix,index=self.data.columns),**kargs)
        self.label_append("SC3_cluster",KNN(self.CSPA_matrix,n_cluster,n_neighbors))
        scatter(self.SC3_tsne,self.label["SC3_cluster"])

    def kmeans_cluster(self,k=None,min_k=3,max_k=20,max_iter=300,random_state=0):
        if k==None:
            K_range = range(min_k, max_k+1)
            s = []
            for x in K_range:
                kmeans = KMeans(n_clusters=x,max_iter=max_iter,random_state=random_state)
                kmeans.fit(self.data.T)
                labels = kmeans.labels_
                s.append(silhouette_score(self.data.T, labels, metric='euclidean'))
            k=min_k+np.argmax(s)
        kmeans=KMeans(n_clusters=k,max_iter=max_iter,random_state=random_state)
        kmeans.fit(self.data.T)
        cluster=pd.Series(kmeans.labels_,index=self.data.columns)
        self.label_append("KMEAN_cluster",cluster)


    def KNN_cluster(self,nCluster,n_neighbors):
        self.label_append("KNN_cluster",KNN(self.data.T,nCluster,n_neighbors))

### FUNCTION FOR FIND GROUP MARKER GENE
    def get_expression(self, gene_name,label_name,cmap="Set3"):
        spegene=self.data.ix[gene_name]
        fig=plt.figure()
        sns.violinplot(x=self.label[label_name],y=spegene,scale='width',palette=cmap,cut=0)
        plt.xlabel("Group")
        plt.show()

    def group_overlap(self,name,cmap=None):
        label=[self.label[x] for x in name]
        ratio=pd.DataFrame(dict(zip(name,label))).groupby(name)[name[-1]].count().unstack().apply(lambda x: 100*x/float(x.sum()),axis=1)
        fig=plt.figure()
        ratio.plot(kind='bar',stacked=True,colormap=cmap)
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.show()
        #sefl.ratio=ratio
        #self.ratio_name="_".join(name)
        return ratio

    def diff_express_gene(self,label_name,target_group,background_group=None,log=True):
        data=self.data
        if background_group:
            data=data.loc[:,(self.label[label_name]==target_group) | (self.label[label_name]==background_group)]
        data=self.data[self.data.apply(sum,axis=1)>0]
        background,target=[x[1] for x in list(data.groupby(self.label[label_name]==target_group,axis=1))]
        if log==False:
            test_func=lambda x : np.log2(np.mean(x)+1)
        else:
            test_func=lambda x :np.mean(x)
        background_umi=background.apply(test_func,axis=1)
        target_umi=target.apply(test_func,axis=1)
        mean_FD=target_umi-background_umi
        p_value=stats.ttest_ind(target,background,axis=1)[1].T
        fdr=p_adjust_bh(p_value)
        temp=pd.DataFrame({'background':background_umi,'target_group':target_umi,'mean_FD':mean_FD,'p_value': p_value, 'FDR': fdr}).sort_values('mean_FD',ascending=False)
        self.diff_express_gene_temp=temp
        return temp

    def sig_gene(self,label_name,pvalue=0.05,fdr=0.01,mean_fd=1,background_value=0,target_value=0,print_matrix=True,rank=10):
        self.all_gene={}
        for x in set(self.label[label_name]):
            temp=self.diff_express_gene(label_name,x)
            self.all_gene["cluster_"+str(x)+"_marker_gene"]=temp[(temp.p_value<pvalue) & (temp.FDR<fdr) & (temp.background>background_value) & (temp.target_group>target_value) & (temp.mean_FD>mean_fd)]
        if print_matrix:
            for x in self.all_gene:
                print "cluster_"+str(x)+"_marker_gene\n"
                print self.all_gene[x].iloc[:rank]
                print "\n"
        #return data.ix[set([x for y in all_gene for x in y])].groupby(label,axis=1).mean()
'''
    def sig_gene_clustermap(data,name,label,color,method="average",metric="euclidean",vmax=None):
        lut=[]
        networks_colors=[]
        legend=[]
        for x in range(len(name)):
            colormap=plt.get_cmap(color[x])
            colorst=[colormap(i) for i in np.linspace(0,1,len(pd.unique(label[x])))]
            lut.append(dict(zip(pd.unique(label[x]),colorst)))
            networks_colors.append(pd.Series(label[x]).map(lut[-1]))
            legend.append([mpatches.Patch(color=v, label=k) for k, v in lut[-1].items()])
        ipalette=dict(zip(name,lut))
        icolor=pd.DataFrame(networks_colors).T
        icolor.index=data.columns
        icolor.columns=name
        g=sns.clustermap(data=data,col_colors=icolor,method=method,metric=metric,xticklabels=False,vmax=vmax)
        for x in range(len(legend)-1):
            l1 = g.ax_heatmap.legend(bbox_to_anchor=(-0.35,0.9-x*0.3,0.2,0.102),handles=legend[x])
            g.ax_heatmap.add_artist(l1)
        g.ax_heatmap.legend(bbox_to_anchor=(-0.35,0.9-(len(legend)-1)*0.3,0.2,0.102),handles=legend[-1])
        plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
        g.ax_row_dendrogram.set_visible(False)
        g.ax_col_dendrogram.set_visible(False)
        plt.savefig("sig_gene_clustermap.pdf")
        plt.show()
        plt.close()

'''
