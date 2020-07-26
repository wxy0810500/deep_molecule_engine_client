from rdkit import Chem, DataStructs
from rdkit.Chem import Draw, AllChem, rdFMCS
from rdkit.Chem.rdchem import Mol
import time 
from rdkit import rdBase
rdBase.DisableLog('rdApp.error')
rdBase.DisableLog('rdApp.info')  

import numpy as np
import pandas as pd

import SMILES_clean as sc
from joblib import Parallel, delayed

def _similarity_matrix(fps):
    M = np.zeros((len(fps),len(fps)))
    for i in range(0,len(fps)):
        for j in range(0,len(fps)):
            M[j, i] = DataStructs.TanimotoSimilarity(fps[i], fps[j])
    return M

def similarity_to_distance(S):
    #simple function to transform similarity to distance
    D = 1-S
    return D

def clustering_recount(df, list1):
    c = 1
    df['clusters'] = -1
    df['cluster_count'] = 1
    for lists in list1:
        if lists[0] != -1:
            df['clusters'].iloc[lists] = c
            df['cluster_count'].iloc[lists] = len(lists)
            c += 1

    df_clusters = df.sort_values(by='cluster_count', ascending=False, axis=0)

    df_clusters['clusters_n'] = -1
    N = 1
    for i in list(df_clusters['clusters'].unique()):
        if i != -1:
            df_clusters['clusters_n'].loc[df_clusters[df_clusters['clusters'] == i].index] = N
            N += 1
    
    df_clusters = df_clusters.sort_values(by='clusters_n', ascending=False, axis=0).drop(['clusters', 'cluster_count'], axis=1)

    return df_clusters

def clustering_loop(df_smiles, df_clusters, threshold):
    # loop for clustering to use for parallel processing
    
    clusterlist_ = []
    
    for i in range(0,len(df_clusters)):
        if df_clusters['idx'].iloc[i] is not None:
            newlist = []
            newlist.append(df_clusters['idx'].iloc[i])
            seedmol = Chem.MolFromSmiles(df_smiles['cleaned_smiles'].iloc[df_clusters['idx'].iloc[i]])

            k = 0

            for idx in df_clusters['simidx'].iloc[i]:
                simmol = Chem.MolFromSmiles(df_smiles['cleaned_smiles'].iloc[idx])
                    
                if k < 10:
                    Mmol = rdFMCS.FindMCS([seedmol, simmol], completeRingsOnly=True, timeout=1)
                    try:
                        score = jaccardscore(seedmol.GetNumHeavyAtoms(), seedmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                    except ZeroDivisionError:
                        score = 0
                    except AttributeError:
                        score = jaccardscore(seedmol.numAtoms, seedmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                    except:
                        score = 0
                    if score > threshold:
                        newlist.append(idx)
                        seedmol = Chem.MolFromSmarts(Mmol.smartsString)
                        k += 1
                    else:
                        k = k

            if len(newlist) > 1:
                clusterlist_.append(newlist)
            else:
                clusterlist_.append([-1])

        else:
            clusterlist_.append([-1])
    
    return clusterlist_



def jaccardscore(a1, a2, s):
    score = s/(a1+a2-s)
    return score

def cluster_mapping(clusterlist):
    #reorganizes clusters into unique lists based on overlap of clusters
    clusterlist = sorted([sorted(x) for x in clusterlist])
    resultlist = []
    if len(clusterlist) >= 1: 
        resultlist = [clusterlist[0]] 
        if len(clusterlist) > 1: 
            for l in clusterlist[1:]: 
                listset = set(l) 
                merged = False
                for index in range(len(resultlist)):
                    rset = set(resultlist[index]) 
                    if len(listset & rset) != 0: 
                        resultlist[index] = list(listset | rset) 
                        merged = True 
                        break 
                if not merged: 
                    resultlist.append(l)
    return resultlist

### TODO: cluster combined dataset and keep clusters
def cluster_new_list(df, df1, column='blank1'):
    return df

##################################################################################################################
##################################################################################################################
##################################################################################################################

class MCS_clustering(object):
    def __init__(self, df, shuffle=True, random_state=42):
        self.df = df
        self.shuffle=shuffle
        self.random_state = random_state
    
    def sim_matrix(self, inputfield='smiles'):
        if type(self.df) is str:
            try:
                df1 = pd.read_csv(self.df, delimiter=',')
            except:
                df1 = pd.read_excel(self.df)
        else:
            df1 = self.df
            
        if self.shuffle is True:
            df1 = df1.sample(frac=1, random_state=self.random_state)
        
        df1 = sc.df_smiles_rename_columns(df1)
        correct_smiles, fps1 = sc.smiles_preprocessing(df1, inputfield=inputfield, fps=True, remove_error=True, remove_polymer=True, remove_inorganic=False)
        
        print(len(fps1))
        M = sc.similarity_matrix(fps1)
        self.df = correct_smiles #update df in object
        self.M = M
        
        return M, correct_smiles
    
    def clustering_p(self, M=None, correct_smiles=None, threshold=0.9, sim_threshold=0.7, n_cores=8, output='list'):
        if M is None:
            M = self.M
        
        if correct_smiles is None:
            correct_smiles = self.df
        
        M1 = (M > (sim_threshold*threshold))*1*M
        np.fill_diagonal(M1, 0)
        
        singletons = []
        idxlist = []
        simlist = []
        for i in range(0,len(M1)):
            #print(i)
            s1 = len(list(np.where(M1[i,:] > (sim_threshold*threshold)))[0])
            s2 = list(np.argsort(M1[i,:])[::-1][0:s1])
            if len(s2) > 0:
                idxlist.append(i)
                simlist.append(s2)
            else:
                singletons.append(i)
        
        print('Initial Clusters: ', len(idxlist))
        i = 0
        clusters = []
        cluster = 1
        nolist = []
        clusterlist = []

        df_sorted = pd.DataFrame(data={'idx':idxlist, 'simidx':simlist, 'len_s':[len(i) for i in simlist]})
        df_sorted = df_sorted.sort_values(by='len_s', ascending=False)
        
        cores = list(np.linspace(0, n_cores-1, n_cores).astype(int))
        sorted_n = np.array_split(df_sorted, n_cores)
        
        clusterlist__ = Parallel(n_jobs=n_cores)(delayed(clustering_loop)(correct_smiles, df_n, threshold) for core, df_n in zip(cores, sorted_n))
        clusterlist = list(np.concatenate(clusterlist__))
        if output == 'list':
            return cluster_mapping(clusterlist)
        
        else:
            clusterlist = cluster_mapping(clusterlist)
            correct_smiles = clustering_recount(correct_smiles, clusterlist)
            return correct_smiles
            
    
    def clustering(self, M=None, correct_smiles=None, threshold=0.9, sim_threshold=0.7, output='list'):
        if M is None:
            M = self.M
        
        if correct_smiles is None:
            correct_smiles = self.df
        M1 = (M > (sim_threshold*threshold))*1*M
        np.fill_diagonal(M1, 0)
        
        singletons = []
        idxlist = []
        simlist = []
        for i in range(0,len(M1)):
            s1 = len(list(np.where(M1[i,:] > (sim_threshold*threshold)))[0])
            s2 = list(np.argsort(M1[i,:])[::-1][0:s1])
            if len(s2) > 0:
                idxlist.append(i)
                simlist.append(s2)
            else:
                singletons.append(i)
        
        print('Initial Clusters: ', len(idxlist))
        i = 0
        clusters = []
        cluster = 1
        nolist = []
        clusterlist = []

        df_sorted = pd.DataFrame(data={'idx':idxlist, 'simidx':simlist, 'len_s':[len(i) for i in simlist]})
        df_sorted = df_sorted.sort_values(by='len_s', ascending=False)
        
        while i < len(df_sorted):
            #print(i)
            if df_sorted['idx'].iloc[i] not in nolist:
                newlist = []
                newlist.append(df_sorted['idx'].iloc[i])
                seedmol = Chem.MolFromSmiles(correct_smiles['cleaned_smiles'].iloc[df_sorted['idx'].iloc[i]])

                k = 0

                for idx in df_sorted['simidx'].iloc[i]:
                    simmol = Chem.MolFromSmiles(correct_smiles['cleaned_smiles'].iloc[idx])
                    if k < 10:
                        Mmol = rdFMCS.FindMCS([seedmol, simmol], completeRingsOnly=True, timeout=1)

                    try:
                        #score = Ss.jaccardscore(seedmol.GetNumHeavyAtoms(), simmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                        score = jaccardscore(seedmol.GetNumHeavyAtoms(), seedmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                    except ZeroDivisionError:
                        score = 0
                    except AttributeError:
                        #score = Ss.jaccardscore(seedmol.numAtoms, simmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                        score = jaccardscore(seedmol.numAtoms, seedmol.GetNumHeavyAtoms(), Mmol.numAtoms)
                    except:
                        score = 0
                        
                    #print(score)
                    if score > threshold:
                        nolist.append(idx)
                        newlist.append(idx)
                        seedmol = Chem.MolFromSmarts(Mmol.smartsString)
                        k += 1

                if len(newlist) > 1:
                    #print('length of cluster list:', len(newlist))
                    nolist.append(df_sorted['idx'].iloc[i])
                    clusterlist.append(newlist)
                else:
                    clusterlist.append([-1])

                #print('nolist', nolist)
                #print('list of cluster indices', newlist)
                #clusterlist.append(newlist)
                clusters.append(cluster)
                cluster += 1
                i += 1
            else:
                try:
                    i += 1
                except:
                    break 

        if output == 'list':
            return cluster_mapping(clusterlist)
        
        else:
            clusterlist = cluster_mapping(clusterlist)
            correct_smiles = clustering_recount(correct_smiles, clusterlist)
            return correct_smiles
