
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[2]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[3]:


def trimstr(s,by):
    if by in s:
        return s[:s.index(by)].strip()
    return s


utowns_raw=pd.read_table('university_towns.txt',header=None)
utowns=pd.DataFrame(columns=['State','RegionName'])
    
current_state=None
current_indx=0
for indx,row in utowns_raw.iterrows():
    curstr=row[0]
    if curstr.endswith('[edit]'):
        current_state=trimstr(curstr,'[')
    else:
        current_town=trimstr(curstr,'(')
        utowns.loc[current_indx]=[current_state,current_town]
        current_indx+=1


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''   
    
    #return pd.DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ],columns=["State", "RegionName"]  )
    #return utowns[utowns['State']=='Michigan']
    return utowns

get_list_of_university_towns()


# In[4]:


GDP=(pd.read_excel('gdplev.xls',skiprows=4,header=1,usecols=[4,5,6])
     .dropna()
     .rename(columns={
         'Unnamed: 4':'Quarter',
         'GDP in billions of current dollars.1':'GDP1',
         'GDP in billions of chained 2009 dollars.1':'GDP2'})
     .set_index('Quarter')
     .loc['2000q1':]
    )

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''    
    
    diffGDP1=GDP.diff(-1)
    for i in range(len(diffGDP1-2)):
        if (diffGDP1.iloc[i]['GDP1']>0) and (diffGDP1.iloc[i+1]['GDP1']>0):
            return diffGDP1.iloc[i].name
    return ''

get_recession_start()


# In[5]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    diffGDP2=GDP.diff(1)
    for i in range(2,len(diffGDP2-2)):
        if (diffGDP2.iloc[i-2]['GDP1']<0) and (diffGDP2.iloc[i-1]['GDP1']<0)         and (diffGDP2.iloc[i]['GDP1']>0) and (diffGDP2.iloc[i+1]['GDP1']>0):
            return diffGDP2.iloc[i+1].name
    return ''

get_recession_end()
#diffGDP2.iloc[10:]


# In[6]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    rstart=get_recession_start()
    rend=get_recession_end()
    #return GDP.loc[rstart:rend]
    return GDP[GDP['GDP1']==np.min(GDP.loc[rstart:rend]['GDP1'])].index[-1]

get_recession_bottom()


# In[7]:


house_raw=pd.read_csv('City_Zhvi_AllHomes.csv').set_index('RegionID')
house_raw['State']=house_raw['State'].map(states)
house_raw=house_raw.sort_values('State').set_index(['State','RegionName'])
#print(list(GDP.index.values))
quarterlst=list(GDP.index.values)
quarterlst.append('2016q3')
start=48
for cq in quarterlst:
    house_raw[cq]=house_raw.iloc[:,start:start+3].mean(axis=1)
    start+=3
house=house_raw.iloc[:,-67:]

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    ''' 
    return house

convert_housing_data_to_quarters()


# In[8]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    rstart=get_recession_start()
    rend=get_recession_end()
    rbottom=get_recession_bottom()
    
    house_range=house.loc[:,rstart:rend].reset_index()
    
    #state_names=pd.unique(utowns['State'].values)
    #region_names=pd.unique(utowns['RegionName'].values)
    #sr_names=utowns.values
    
    utowns['isTown']=True
    house_range=pd.merge(house_range,utowns,how='left',left_on=['State','RegionName'],right_on=['State','RegionName'])
    house_range['decline']=house_range[rstart]-house_range[rbottom]
    
    #house_range=pd.merge(house,utowns,how='inner',left_index=True,right_on=['State','RegionName'])
    
    house_utown=house_range[house_range['isTown'] == True]['decline']
    house_other=house_range[house_range['isTown'] != True]['decline']
    
    t,p=ttest_ind(house_utown.dropna(),house_other.dropna())    
    different=p<0.01
    
    if house_utown.mean() < house_other.mean(): # lower price decline
        better="university town"
    else:
        better="non-university town"

    return different,p,better

run_ttest()


# In[ ]:




