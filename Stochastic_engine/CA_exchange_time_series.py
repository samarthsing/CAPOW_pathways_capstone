# -*- coding: utf-8 -*-
"""
Created on Mon May 14 17:29:16 2018

@author: jdkern
"""
from __future__ import division
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def exchange(year,scenario,job_id):
    
    filename = 'Synthetic_demand_pathflows/Load_Path_Sim_' + scenario + '_{}.csv'    
    df_data = pd.read_csv(filename.format(job_id),header=0)
    c = ['Path66_sim','Path46_sim','Path61_sim','Path42_sim','Path24_sim','Path45_sim']
    df_data = df_data[c]
    paths = ['Path66','Path46','Path61','Path42','Path24','Path45']
    df_data.columns = paths
    df_data = df_data.loc[year*365:year*365+364,:]
    
    # select dispatchable imports (positve flow days)
    imports = df_data
    imports = imports.reset_index()
    
    for p in paths:
        for i in range(0,len(imports)):     
            
            if p == 'Path42':
                if imports.loc[i,p] >= 0:
                    imports.loc[i,p] = 0
                else:
                    imports.loc[i,p] = -imports.loc[i,p]
            
            elif p == 'Path46':
                if imports.loc[i,p] < 0:
                    imports.loc[i,p] = 0
                else:
                    imports.loc[i,p] = imports.loc[i,p]*.404 + 424
            
            else:
                if imports.loc[i,p] < 0:
                    imports.loc[i,p] = 0
                    
                    
    imports.rename(columns={'Path46':'Path46_SCE'}, inplace=True)
    
    filename = 'Path_setup/CA_imports_' + scenario + '_{}.csv'
    imports.to_csv(filename.format(job_id))
    
    # convert to minimum flow time series and dispatchable (daily)
    df_mins = pd.read_excel('Path_setup/CA_imports_minflow_profiles.xlsx',header=0)
    lines = ['Path66','Path46_SCE','Path61','Path42']
    
    for i in range(0,len(df_data)):
        for L in lines:
            
            if df_mins.loc[i,L] >= imports.loc[i,L]:
                df_mins.loc[i,L] = imports.loc[i,L]
                imports.loc[i,L] = 0
            
            else:
                imports.loc[i,L] = np.max((0,imports.loc[i,L]-df_mins.loc[i,L]))
    
    dispatchable_imports = imports*24
    filename = 'Path_setup/CA_dispatchable_imports_' + scenario + '_{}.csv'
    dispatchable_imports.to_csv(filename.format(job_id))
    
    df_data = imports.copy(deep=True)
    
    # hourly minimum flow for paths
    hourly = np.zeros((8760,len(lines)))
    
    for i in range(0,365):
        for L in lines:
            index = lines.index(L)
            
            hourly[i*24:i*24+24,index] = np.min((df_mins.loc[i,L], df_data.loc[i,L]))
            
    H = pd.DataFrame(hourly)
    H.columns = ['Path66','Path46_SCE','Path61','Path42']
    filename = 'Path_setup/CA_path_mins_' + scenario + '_{}.csv'
    H.to_csv(filename.format(job_id))
    
    # hourly exports
    filename = 'Synthetic_demand_pathflows/Load_Path_Sim_' + scenario + '_{}.csv'
    df_data = pd.read_csv(filename.format(job_id),header=0)
    c = ['Path66_sim','Path46_sim','Path61_sim','Path42_sim','Path24_sim','Path45_sim']
    df_data = df_data[c]
    df_data.columns = [paths]
    
    df_data = df_data.loc[year*365:year*365+364,:]
    df_data = df_data.reset_index()
    
    e = np.zeros((8760,4))
    
    #Path 42
    path_profiles = pd.read_excel('Path_setup/CA_path_export_profiles.xlsx',sheet_name='Path42',header=None)
    pp = path_profiles.values
    
    for i in range(0,len(df_data)):
        if df_data.loc[i,'Path42'].values > 0:
            e[i*24:i*24+24,0] = pp[i,:]*df_data.loc[i,'Path42'].values
    
    #Path 24
    path_profiles = pd.read_excel('Path_setup/CA_path_export_profiles.xlsx',sheet_name='Path24',header=None)
    pp = path_profiles.values
    
    for i in range(0,len(df_data)):
        if df_data.loc[i,'Path24'].values < 0:
            e[i*24:i*24+24,1] = pp[i,:]*df_data.loc[i,'Path24'].values*-1
    
    #Path 45
    path_profiles = pd.read_excel('Path_setup/CA_path_export_profiles.xlsx',sheet_name='Path45',header=None)
    pp = path_profiles.values
    
    for i in range(0,len(df_data)):
        if df_data.loc[i,'Path45'].values < 0:
            e[i*24:i*24+24,2] = pp[i,:]*df_data.loc[i,'Path45'].values*-1  
            
    #Path 66
    path_profiles = pd.read_excel('Path_setup/CA_path_export_profiles.xlsx',sheet_name='Path66',header=None)
    pp = path_profiles.values
    
    for i in range(0,len(df_data)):
        if df_data.loc[i,'Path66'].values < 0:
            e[i*24:i*24+24,2] = pp[i,:]*df_data.loc[i,'Path66'].values*-1  
    
    e = e*24
    
    exports = pd.DataFrame(e) 
    exports.columns = ['Path42','Path24','Path45','Path66']
    filename = 'Path_setup/CA_exports_' + scenario + '_{}.csv'
    exports.to_csv(filename.format(job_id))
    
    
    
    ##########################3
    ##########################
    
    # HYDRO
    
    # convert to minimum flow time series and dispatchable (daily)
    
    df_data = pd.read_excel('CA_hydropower/CA_hydro_daily_{}.xlsx'.format(job_id),header=0,index_col=0)
    dhydro = df_data.loc[year*365:year*365+364,:]
    dhydro = dhydro.reset_index(drop=True)
    dhydro=dhydro.values
    for i in range(0,len(dhydro)):
        for j in range(0,2):
            if dhydro[i,j] < 0:
                dhydro[i,j] = 0
    PGE_ALL=dhydro[:,0]/0.837
    SCE_all=dhydro[:,1]/0.8016       
    dhydro=pd.DataFrame()
    dhydro['PGE_valley']=PGE_ALL
    dhydro['SCE']=SCE_all
    zones = ['PGE_valley','SCE']
    df_mins = pd.read_excel('Hydro_setup/Minimum_hydro_profiles.xlsx',header=0)
    
    for i in range(0,len(dhydro)):
        for z in zones:
            
            if df_mins.loc[i,z]*24 >= dhydro.loc[i,z]:
                df_mins.loc[i,z] = np.max((0,dhydro.loc[i,z]/24))
                dhydro.loc[i,z] = 0
            
            else:
                dhydro.loc[i,z] = np.max((0,dhydro.loc[i,z]-df_mins.loc[i,z]*24))
    
    dhydro.to_csv('Hydro_setup/CA_dispatchable_hydro_{}.csv'.format(job_id))
    
    # hourly minimum flow for hydro
    hourly = np.zeros((8760,len(zones)))
    
    df_data = pd.read_excel('CA_hydropower/CA_hydro_daily_{}.xlsx'.format(job_id),header=0,index_col=0)
    hydro = df_data.loc[year*365:year*365+364,:].values
    PGE_ALL=hydro[:,0]/0.837
    SCE_all=hydro[:,1]/0.8016
    hydro=pd.DataFrame()
    hydro['PGE_valley']=PGE_ALL
    hydro['SCE']=SCE_all
    zones = ['PGE_valley','SCE']
    
    for i in range(0,365):
        for z in zones:
            index = zones.index(z)
            
            h = np.max((0,hydro.loc[i,z]))
            
            hourly[i*24:i*24+24,index] = np.min((df_mins.loc[i,z],h))
            
    H = pd.DataFrame(hourly)
    H.columns = zones
    H.to_csv('Hydro_setup/CA_hydro_mins_{}.csv'.format(job_id))

    return None
