# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 18:00:52 2019

@author: Joy Hill
"""

#ICF calculation

import pandas as pd
import numpy as np
import os

#d=pd.read_excel('Synthetic_streamflows/BPA_hist_streamflow.xlsx')
#d=d['TDA5ARF']

def calc(sim_years,job_id): 
    #os.chdir("C:\\Users\\ss9vz\\Downloads\\CAPOW_PY36-master\\CAPOW_PY36-master\\Stochastic_Engine_4\\")
    #job_id=14
    #sim_years=5
    """
    sim_years=24
    job_id=455
    print("job_id is")
    print(job_id)
    #d=pd.read_csv('Synthetic_streamflows/synthetic_streamflows_TDA_{}.csv'.format(job_id),header=None)
    res_df=pd.read_excel(r'D:\All Daily Data\daily\daily\TDA6ARF_daily.xlsx')
    res_df["datetime"]=pd.to_datetime(res_df["date"])
    res_df=res_df.set_index("datetime")
    res_df=res_df.loc['1994-01-01':'2017-12-31']
    res_df['leapday'] = (res_df.index.month==2) & (res_df.index.day==29)
    res_df=res_df[res_df['leapday']==False]
    res_df.index=np.arange(len(res_df))
    
    d=pd.DataFrame(index=np.arange(len(res_df)))
    d[0]=res_df["ARF (unit:cfs)"]
    d = d.iloc[0:(sim_years+3)*365,:]
    doy = np.arange(1,366)
    doy_array = np.tile(doy,int(len(d)/365))
    doy_array = pd.DataFrame(doy_array)
    d = np.array(pd.concat([doy_array,d],axis=1))
    d = d[243:len(d)-122,:]
    years = int(len(d)/365)
    ICFs = np.zeros((years,1))
    
    for i in range(0,years):
        
        j = d[i*365:i*365+365,0]
        a = d[i*365:i*365+365,1]
    
        b = np.argwhere(a>450000)
        if len(b) > 0:
            jb = j[b]
            c=np.argwhere(jb>80)[:,0]
            jc = jb[c]
            ICFs[i] = min(jc)[0]
        
        
        else:
            ICFs[i] = np.argwhere(a>max(a)-1)
    """   
    d=pd.read_csv('Synthetic_streamflows/synthetic_streamflows_TDA_{}.csv'.format(job_id),header=None)
    d = d.iloc[0:(sim_years+3)*365,:]
    doy = np.arange(1,366)
    doy_array = np.tile(doy,int(len(d)/365))
    doy_array = pd.DataFrame(doy_array)
    d = np.array(pd.concat([doy_array,d],axis=1))
    d = d[243:len(d)-122,:]
    years = int(len(d)/365)
    ICFs = np.zeros((years,1))
    
    for i in range(0,years):
        
        j = d[i*365:i*365+365,0]
        a = d[i*365:i*365+365,1]
    
        b = np.argwhere(a>450000)
        if len(b) > 0:
            jb = j[b]
            c=np.argwhere(jb>80)[:,0]
            jc = jb[c]
            ICFs[i] = min(jc)[0]
        
        
        else:
            ICFs[i] = np.argwhere(a>max(a)-1)
                       
    np.savetxt('PNW_hydro/FCRPS/ICFcal_{}.csv'.format(job_id),ICFs,delimiter=',')
    np.savetxt('PNW_hydro/FCRPS/ICFcal_historical_{}.txt'.format(job_id),ICFs,fmt='%f',delimiter=' ')
    
    
    return None
        
    
 