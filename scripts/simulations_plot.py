#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 15:28:50 2021

@author: alexandra
"""

import pandas as pd
import matplotlib.pyplot as plt
import scipy as sp
import numpy as np
import os

import seaborn as sbn
from statannot import add_stat_annotation

import itertools

##########################################################
### Parameters of the script : can be modified
##########################################################
# input file name
# here we read the output file generated by the disperison analysis script
analysis='disp-d7e-08-l6e-02RandomVeinsWT10'


#file_name='../output/disp_analysis/disp-d7e-08-l6e-02RandomWT10.csv'
file_name='../output/disp_analysis/'+analysis+'.csv'

# output folder
outputfolder='../output/figures/'+analysis+'/'

# selection of stages
stages=['baseline','stageNREM','stageIS','stageREM','stageAwakening']

# associated name in the figure
stagesname=['baseline','NREM','IS','REM','wake']

# selection of frequency bands
#bandnames=[ 'card-v1e-03', 'card-v5e-03','card-v1e-02']
bandnames=['VLF','LF']



# variable to plot
variable='Rfit'  # 'umax', 'pmax', 'amp'

# rescaling for the plotting (change of unit for example)
factor=100 #1e4, 0.1, 1

# max value for the x and y axis in the bubble plot
escale=1 #120e-4#0.12 # value before rescaling with factor

# unit and format when printing the values of the variable
unit=' %' # unit after rescaling with the factor
formatstr='%.1f'
formatminmax='( '+formatstr+','+formatstr+' )'
formatminmaxN='( '+formatstr+','+formatstr+' ), N= %i'

# to be added to the file name

length='L600um'

diffusioncoef='D7e-8'

complementname=length+diffusioncoef


complementname='600umD7e-8'

# use a log normal distibution to fit the variable distribution.
# if False, a normal distribution will be used instead (for velocity)
lognorm=True

# plot the sum of the frequency bands
showtotal=True




# style parameters

sbn.set(style="whitegrid")  

colors=['gray','darkorchid','mediumseagreen','darkorange']

# selection of color for each stage
my_pal = {"baseline":"gray","stageREM": "darkorchid", "stageNREM": "mediumseagreen", "stageIS":"darkorange","stageAwakening":"blue"}


##########################################################
### script
##########################################################

# Directory to store output data    

if not os.path.exists('../output/figures/'):
    os.makedirs('../output/figures/')

if not os.path.exists(outputfolder):
    os.makedirs(outputfolder)


combis=list(itertools.combinations(list(np.unique(stages)), 2))

def find_id (row):
    return row['job'].split('-id')[1]


data=pd.read_csv(file_name)
data['vessel id']=data.apply(find_id,axis=1)


data['u max (um/s)']= data['umax']*1e4
data['p max (Pa)']= data['pmax']/10

data['uformula']=2*np.pi*data['f']*data['amp']/100*600e-4

data['h0']=data['Rpvs']-data['Rv0']


# export data in a table
#listvariables=['stage','bandname','vessel id','Rv0','h0','L','DX','dt','D','amp','f','Pe','Destfit','Rfit','u max (um/s)', 'p max (Pa)']
#columnsname=['stage','frequency band name','vessel id','Vessel radius (cm)','PVS thickness (cm)','PVs length (cm)','cell size','time step','molecular diffusion coefficient (cm2/s)','Oscillation amplitude (pc)','Oscillation frequency (Hz)','Peclet number','Effective diffusion coefficient','Enhancement factor (R)','Peak velocity (um/s)', 'Peak pressure (Pa)']

#shorter lists that correspond to the paper
listvariables=['stage','bandname','vessel id','amp','f','Destfit','Rfit','u max (um/s)', 'p max (Pa)']
columnsname=['stage','frequency band name','vessel id','Oscillation amplitude (pc)','Oscillation frequency (Hz)','Effective diffusion coefficient','Enhancement factor R','Peak velocity (um/s)', 'Peak pressure (Pa)']


data[listvariables].to_excel(outputfolder+'table_'+length+diffusioncoef+'.xls', header=columnsname)


fig1,axs1 = plt.subplots(len(stages), len(bandnames)+1)


fig2=plt.figure()
gs=fig2.add_gridspec(len(stages), len(bandnames)+1, hspace=0, wspace=0)
axs2=gs.subplots(sharex='col', sharey='row')

theta = np.linspace(0, 2*np.pi, 100)



# bubble representation of the distributions
for i,stage in enumerate(stages) :
    for j, bandname in enumerate(bandnames) :
        filter=(data['bandname']==bandname)&(data['stage']==stage)
        
        
        Enhancement=data[variable][filter]
        
        axs1[i, j].hist(Enhancement)
        
        if lognorm :
            param=sp.stats.lognorm.fit(Enhancement,loc=0 ) # fit the sample data
        else :
            param=sp.stats.norm.fit(Enhancement) # fit the sample data

        #x=np.linspace(max(0,np.mean(Enhancement)-1*np.std(Enhancement)),np.mean(Enhancement)+1*np.std(Enhancement),100)
        x=np.linspace(0,escale*2,50)
        if lognorm :
            pdf_fitted = sp.stats.lognorm.pdf(x, param[0], loc=param[1], scale=param[2])# fitted distribution
        else:
            pdf_fitted = sp.stats.norm.pdf(x, param[0], param[1])# fitted distribution
        
        pdf_fitted=pdf_fitted-pdf_fitted.min()
        pdf_fitted=pdf_fitted/pdf_fitted.max() 
        
        p = np.linspace(0, 2*np.pi, 50)
        R, P = np.meshgrid(x, p)
        # Express the mesh in the cartesian system.
        X, Y = R*np.cos(P), R*np.sin(P)
        if lognorm :
            Z = sp.stats.lognorm.pdf(R, param[0], loc=param[1], scale=param[2])
        else:
            Z = sp.stats.norm.pdf(R, param[0], param[1])
        Z=Z/Z.max()
        
        #for e,level in zip(x,pdf_fitted) :
        #    axs2[i, j].plot( e*np.cos(theta), e*np.sin(theta), 'b',alpha=level,linewidth=1)
        
        
        axs2[i,j].contourf(X, Y, Z,50, zdir='z', offset=-1.5,cmap=plt.cm.Blues)
        
        #for e in Enhancement :
        #    axs2[i, j].plot( e*np.cos(theta), e*np.sin(theta), 'k',alpha=0.3,linewidth=1)
        
        emean=np.median(Enhancement)
        emin=np.min(Enhancement)
        emax=np.max(Enhancement)
        

        
        axs2[i, j].plot( emean*np.cos(theta), emean*np.sin(theta), 'k',linewidth=1)
        
        axs2[i, j].text( -0.5*escale, 0.6*escale, formatstr%(emean*factor)+unit,fontsize=9)
        axs2[i, j].text( -0.9*escale, -0.7*escale, formatminmaxN%((emin*factor,emax*factor,len(Enhancement))),fontsize=7)
        
        print(stage)
        print(bandname)
        print(formatstr%(emean*factor)+unit)
        print(formatminmax%((emin*factor,emax*factor)))
        print('\n')
        
        
        
        axs2[i, j].set_aspect(1)
        axs2[i, j].set_xlim([-escale,escale])
        axs2[i, j].set_ylim([-escale,escale])
        
        axs2[i, j].set_xlabel(bandname)
        axs2[i, j].set_ylabel(stage[5::])
        
        # make xaxis invisibel
        #axs2[i, j].xaxis.set_visible(False)
        # make spines (the box) invisible
        #plt.setp(axs2[i, j].spines.values(), visible=False)
        # remove ticks and labels for the left axis
        axs2[i, j].tick_params(left=False, labelleft=False)# remove ticks and labels for the left axis
        axs2[i, j].tick_params(bottom=False, labelbottom=False)
    
    if showtotal :
        # add the total
        Npoints=len(np.where((data['bandname']==bandname)&(data['stage']==stage))[0])-1
        Enhancement=[]
        
        vesselIDS=np.unique(data[(data['bandname']=='VLF')&(data['stage']==stage)]['vessel id'])
    
        
        for no in vesselIDS:
             #filter=(data['stage']==stage)&(data['job'].str.contains('pt'+str(no)))
             filter=(data['stage']==stage)&(data['job'].str.contains('id'+str(no)))
             filterfb=(data['bandname']==bandnames[0])
             for bandname in bandnames[1::]:
                 filterfb=filterfb|(data['bandname']==bandname)
             filter=filter&filterfb
             etot=data[variable][filter].sum()
             Enhancement.append(etot)
            
        axs1[i, len(bandnames)].hist(Enhancement)
            
        if lognorm :
            param=sp.stats.lognorm.fit(Enhancement,loc=0 ) # fit the sample data
        else :
            param=sp.stats.norm.fit(Enhancement)
    
        # #x=np.linspace(max(0,np.mean(Enhancement)-1*np.std(Enhancement)),np.mean(Enhancement)+1*np.std(Enhancement),100)
        x=np.linspace(0,escale*2,100)
        if lognorm :
            pdf_fitted = sp.stats.lognorm.pdf(x, param[0], loc=param[1], scale=param[2])# fitted distribution
        else:
            pdf_fitted = sp.stats.norm.pdf(x, param[0], param[1])# fitted distribution
        
        pdf_fitted=pdf_fitted-pdf_fitted.min()
        pdf_fitted=pdf_fitted/pdf_fitted.max()   
        
        if lognorm :
            Z = sp.stats.lognorm.pdf(R, param[0], loc=param[1], scale=param[2])
        else:
            Z = sp.stats.norm.pdf(R, param[0], param[1])
        Z=Z/Z.max()
        
        #for e,level in zip(x,pdf_fitted) :
        #     axs2[i, len(bandnames)].plot( e*np.cos(theta), e*np.sin(theta), 'b',alpha=level,linewidth=1)
        
        axs2[i, len(bandnames)].contourf(X, Y, Z,50, zdir='z', offset=-1.5,cmap=plt.cm.Blues)
        
        #for e in Enhancement :
        #     axs2[i, len(bandnames)].plot( e*np.cos(theta), e*np.sin(theta), 'k',alpha=0.3,linewidth=1)
            
        emean=np.median(Enhancement)
        axs2[i, len(bandnames)].plot( emean*np.cos(theta), emean*np.sin(theta), 'k',linewidth=1)
        
        emin=np.min(Enhancement)
        emax=np.max(Enhancement)
        

        
        axs2[i, len(bandnames)].text( -0.5*escale, 0.6*escale, formatstr%(emean*factor)+unit,fontsize=9)
        axs2[i, len(bandnames)].text( -0.9*escale, -0.7*escale, formatminmaxN%((emin*factor,emax*factor,len(Enhancement))),fontsize=7)

            
    axs2[i, len(bandnames)].set_aspect(1)
    axs2[i, len(bandnames)].set_xlim([-escale,escale])
    axs2[i, len(bandnames)].set_ylim([-escale,escale])
            

    axs2[i, len(bandnames)].set_xlabel('Total')
    axs2[i, len(bandnames)].set_ylabel(stage[5:])
            
    # make xaxis invisibel
    #axs2[i, len(bandnames)].xaxis.set_visible(False)
    # make spines (the box) invisible
    plt.setp(axs2[i, len(bandnames)].spines.values(), visible=False)
    # remove ticks and labels for the left axis
    axs2[i, len(bandnames)].tick_params(left=False, labelleft=False)# remove ticks and labels for the left axis
    axs2[i, len(bandnames)].tick_params(bottom=False, labelbottom=False)
    
        

for ax in axs2.flat:
    ax.label_outer()
    
    
    
plt.savefig(outputfolder+'bubbles'+variable+complementname+'.png') 
plt.savefig(outputfolder+'bubbles'+variable+complementname+'surf.pdf')





# figure with one line per vessel, in each FB + total we plot 4 linked dots showing the change with stage


def draw_bs_replicates(data,func,size):
    """creates a bootstrap sample, computes replicates and returns replicates array"""
    # Create an empty array to store replicates
    bs_replicates = np.empty(size)
    
    # Create bootstrap replicates as much as size
    for i in range(size):
        # Create a bootstrap sample
        bs_sample = np.random.choice(data,size=len(data))
        # Get bootstrap replicate and append to bs_replicates
        bs_replicates[i] = func(bs_sample)
    
    return bs_replicates


def bootstrap_simulation(sample_data, num_realizations):
    n = sample_data.shape[0]
    boot = []
    for i in range(num_realizations):
        real = np.random.choice(sample_data.values.flatten(), size=n)
        boot.append(real)
        
    columns = ['Real ' + str(i + 1) for i in range(num_realizations)]
    
    return pd.DataFrame(boot, index=columns).T

def calc_sum_stats(boot_df):
    sum_stats = boot_df.describe().T[['mean', 'std', 'min', 'max']]
    sum_stats['median'] = boot_df.median()
    sum_stats['skew'] = boot_df.skew()
    sum_stats['kurtosis'] = boot_df.kurtosis()
    sum_stats['IQR'] = boot_df.quantile(0.75) - boot_df.quantile(0.25)
    return sum_stats.T

def calc_bounds(conf_level):
    
    assert (conf_level < 1), "Confidence level must be smaller than 1"
    
    margin = (1 - conf_level) / 2
    upper = conf_level + margin
    lower = margin
    return margin, upper, lower

def calc_confidence_interval(df_sum_stats, conf_level): 
    
    margin, upper, lower = calc_bounds(conf_level)
    
    conf_int_df = df_sum_stats.T.describe(percentiles=[lower, 0.5, upper]).iloc[4:7, :].T
    conf_int_df.columns = ['P' + str(round(lower * 100, 1)), 'P50', 'P' + str(round(upper * 100, 1))]
    return conf_int_df 

def print_confidence_interval(conf_df, conf_level):
    print('By {}% chance, the following statistics will fall within the range of:\n'.format(round(conf_level * 100, 1)))
    
    margin, upper, lower = calc_bounds(conf_level)
    
    upper_str = 'P' + str(round(upper * 100, 1))
    lower_str = 'P' + str(round(lower * 100, 1))
    
    for stat in conf_df.T.columns:
        lower_bound = round(conf_df[lower_str].T[stat], 1)
        upper_bound = round(conf_df[upper_str].T[stat], 1)

        mean = round(conf_df['P50'].T[stat], 1)
        print("{0:<10}: {1:>10}  ~ {2:>10} , AVG = {3:>5}".format(stat, lower_bound, upper_bound, mean))


 
for j, bandname in enumerate(bandnames) :
    fig, ax = plt.subplots()
    plt.title(bandname)
    
    #get the vessels IDS present in all stages
    vesselIDSdict={}
    
    for stage in stages :
        vesselIDSdict[stage]=np.unique(data[(data['bandname']==bandname)&(data['stage']==stage)]['vessel id']) 
     
    vesselIDS=vesselIDSdict[stages[0]]
    
    for stage in stages[1::]:
        vesselIDS=[x for x in vesselIDS if x in vesselIDSdict[stage]]
        
    eFB=np.ones([len(stages),len(vesselIDS)])
    
    for j,no in enumerate(vesselIDS):
        
        
        for i,stage in enumerate(stages) :    
            filter=(data['bandname']==bandname)&(data['stage']==stage)&(data['job'].str.endswith('id'+str(no)))

            eFB[i,j]=data[variable][filter]
            

        
    median=[]
    quartileup=[]
    quartiledown=[]
    
    for i,stage in enumerate(stages) :    
        
         # test method 1
         bs_replicates = draw_bs_replicates(eFB[i,:]*factor,np.median,15000)
         q1,q2,q3=np.percentile( bs_replicates,[5,50,95],interpolation='linear')
         
         
         # test method 2 
         M = 1000                      # number of realizations - arbitrary
         df = pd.DataFrame(eFB[i,:]*factor, columns = [variable])
         boot_perm_data = bootstrap_simulation(df, M)
         boot_perm_sum_stats = calc_sum_stats(boot_perm_data)
         conf_int_perm = calc_confidence_interval(boot_perm_sum_stats, 0.90)
         
         conf_int_perm.round(1)
         
         #q1=conf_int_perm.round(1)['P5.0']['median']
         #q2=conf_int_perm.round(1)['P50']['median']
         #q3=conf_int_perm.round(1)['P95.0']['median']
         
         median.append(q2)
         quartileup.append(q3)
         quartiledown.append(q1)
         
    median=np.array(median)
    quartiledown=np.array(quartiledown)
    quartileup=np.array(quartileup)
         
    plt.plot(np.arange(len(stages)), median, 'b-',linewidth=3)
    plt.plot(np.arange(len(stages)), quartileup, 'b-',linewidth=1,alpha=0.5)
    plt.plot(np.arange(len(stages)), quartiledown, 'b-',linewidth=1,alpha=0.5)
    
    ax.fill_between(np.arange(len(stages)), quartiledown, quartileup,'b',alpha=0.5)
    
    for j,no in enumerate(vesselIDS):
        plt.plot(np.arange(len(stages)), eFB[:,j]*factor, 'kx-',alpha=0.3)

    
    plt.text(0,eFB.max()*0.9*factor,'N=%i'%len(vesselIDS))
        
    # set the ticks
    plt.xticks(np.arange(len(stagesname)),stages, rotation=45)
        
    plt.ylabel(variable+' ('+unit+')')

    plt.savefig(outputfolder+'lines_'+bandname+'_'+variable+complementname+'.pdf')
    plt.savefig(outputfolder+'lines_'+bandname+'_'+variable+complementname+'.png')
        
        
plt.figure()
plt.title('Total')
for no in vesselIDS:
    
    for stage in stages :
        vesselids=np.unique(data[(data['bandname']==bandnames[0])&(data['stage']==stage)]['vessel id']) 
        for bandname in bandnames[1::]:
            vesselidsnew=np.unique(data[(data['bandname']==bandname)&(data['stage']==stage)]['vessel id']) 
            vesselids=[x for x in vesselids if x in vesselidsnew]
            
        vesselIDSdict[stage]=vesselids
     
    vesselIDS=vesselIDSdict[stages[0]]
    
    for stage in stages[1::]:
        vesselIDS=[x for x in vesselIDS if x in vesselIDSdict[stage]]
        
        
    eFB=[]
        
    for i,stage in enumerate(stages) :    
        filter=(data['stage']==stage)&(data['job'].str.endswith('id'+str(no)))#&(data['bandname']!='card')
        filterfb=(data['bandname']==bandnames[0])
        for bandname in bandnames[1::]:
                filterfb=filterfb|(data['bandname']==bandname)
        filter=filter&filterfb
        eFB.append(data[variable][filter].sum())
            
    try :
        plt.plot(np.arange(len(stages)), np.array(eFB)*factor, 'o-')
    except :
        continue
        
    # set the ticks
    plt.xticks(np.arange(len(stagesname)),stages, rotation=45)
    plt.ylabel(variable+' ('+unit+')')
    
    
    
    
comparison_variable='stage'
variable='u max (um/s)'
for j, bandname in enumerate(bandnames) :        
    filter=(data['bandname']==bandname)
    dataplot=data[filter]
    plt.figure()
    plt.title(bandname)
    
    yposlist = (dataplot.groupby([comparison_variable])[variable].median()[stages]).tolist()
    Nlist = (dataplot.groupby([comparison_variable])[variable].size()[stages]).tolist()                
    maxlist = (dataplot.groupby([comparison_variable])[variable].max()[stages]).tolist()                
    xposlist = np.array(range(len(yposlist)))
    stringlist = ['%.2f, N=%i'%(m,s) for m,s in zip(yposlist,Nlist)]

    ax=sbn.violinplot(x=comparison_variable, y=variable, data=dataplot, order=stages,alpha=0.3, palette=my_pal, cut=0)  

    for i in range(len(stringlist)):
        ax.text(xposlist[i]-0.3, maxlist[i]*1.02, stringlist[i])
    plt.xlabel(variable)

variable='p max (Pa)'

for j, bandname in enumerate(bandnames) :        
    filter=(data['bandname']==bandname)
    dataplot=data[filter]
    plt.figure()
    plt.title(bandname)
    
    yposlist = (dataplot.groupby([comparison_variable])[variable].median()[stages]).tolist()
    Nlist = (dataplot.groupby([comparison_variable])[variable].size()[stages]).tolist()                
    maxlist = (dataplot.groupby([comparison_variable])[variable].max()[stages]).tolist()                
    xposlist = np.array(range(len(yposlist)))
    stringlist = ['%.2f, N=%i'%(m,s) for m,s in zip(yposlist,Nlist)]

    ax=sbn.violinplot(x=comparison_variable, y=variable, data=dataplot, order=stages,alpha=0.3, palette=my_pal, cut=0)  

    for i in range(len(stringlist)):
        ax.text(xposlist[i]-0.3, maxlist[i]*1.02, stringlist[i])
    plt.xlabel(variable)


variable='amp'

for j, bandname in enumerate(bandnames) :        
    filter=(data['bandname']==bandname)
    dataplot=data[filter]
    plt.figure()
    plt.title(bandname)
    
    yposlist = (dataplot.groupby([comparison_variable])[variable].median()[stages]).tolist()
    Nlist = (dataplot.groupby([comparison_variable])[variable].size()[stages]).tolist()                
    maxlist = (dataplot.groupby([comparison_variable])[variable].max()[stages]).tolist()                
    xposlist = np.array(range(len(yposlist)))
    stringlist = ['%.2f, N=%i'%(m,s) for m,s in zip(yposlist,Nlist)]

    ax=sbn.violinplot(x=comparison_variable, y=variable, data=dataplot, order=stages,alpha=0.3, palette=my_pal, cut=0)  

    for i in range(len(stringlist)):
        ax.text(xposlist[i]-0.3, maxlist[i]*1.02, stringlist[i])
    plt.xlabel(variable)
    
    
variable='Rfit'

for j, bafitndname in enumerate(bandnames) :        
    filter=(data['bandname']==bandname)
    dataplot=data[filter]
    plt.figure()
    plt.title(bandname)
    
    yposlist = (dataplot.groupby([comparison_variable])[variable].median()[stages]).tolist()
    Nlist = (dataplot.groupby([comparison_variable])[variable].size()[stages]).tolist()                
    maxlist = (dataplot.groupby([comparison_variable])[variable].max()[stages]).tolist()                
    xposlist = np.array(range(len(yposlist)))
    stringlist = ['%.2f, N=%i'%(m,s) for m,s in zip(yposlist,Nlist)]

    ax=sbn.violinplot(x=comparison_variable, y=variable, data=dataplot, order=stages,alpha=0.3, palette=my_pal, cut=0)  

    for i in range(len(stringlist)):
        ax.text(xposlist[i]-0.3, maxlist[i]*1.02, stringlist[i])
    plt.xlabel(variable)    