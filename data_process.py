import pandas as pd

import os
from data_process_func import *
univ_region_file_directory = r"Univ_region.xlsx"
topic_qlist_directory = r"cate_qlist.xlsx"
qlist_qcontent_directory = r"2023_BTS_Survey_Questions_N_Number.xlsx"
univ_region_df = pd.read_excel(univ_region_file_directory )
topic_qlist_df = pd.read_excel(topic_qlist_directory)
qlist_qcontent_df = pd.read_excel(qlist_qcontent_directory,header = None)

univ_reg_dict = df_to_dict_univ_region(univ_region_df)
lea_univ_dict = get_univreg_by_school_dict(univ_region_df)
topic_qlist_dict = df_to_dict_topic_qlist(topic_qlist_df)
tsz1,tsz2 = topic_qlist_df.shape
qlist_qcontent_dict = df_to_dict_qlist(qlist_qcontent_df)

univ_reg_display = display_dict(univ_reg_dict)
qlist_qcontent_display = display_dict(qlist_qcontent_dict)
lea_display = {}
topic_display ={}
for i in range(tsz1):
    topic_display[topic_qlist_df.iloc[i,0]]=topic_qlist_df.iloc[i,0]

lea_v_count = univ_region_df["LEA"].value_counts().to_dict()


for k,_ in lea_v_count.items():
    lea_display[k] = k

#inverse dict
qlist_qcontent_inverse_dict_sp = {}
qlist_qcontent_inverse_dict_prn = {}
qlist_qcontent_inverse_dict_edu = {}
qlist_qcontent_inverse_dict_sp['educator']= qlist_qcontent_inverse_dict_edu
qlist_qcontent_inverse_dict_sp['principal']=qlist_qcontent_inverse_dict_prn
qsz1,qsz2 = qlist_qcontent_df.shape
"""

for i in range(qsz1):
    # need to seperate into 2 dict to avoid duplicate 
    qlist_qcontent_inverse_dict[qlist_qcontent_df.iloc[i,1]]= qlist_qcontent_df.iloc[i,0]
"""
for i in range(44):
    qlist_qcontent_inverse_dict_prn[qlist_qcontent_df.iloc[i,1]]=qlist_qcontent_df.iloc[i,0]
    
for i in range(44,90):
    qlist_qcontent_inverse_dict_edu[qlist_qcontent_df.iloc[i,1]]=qlist_qcontent_df.iloc[i,0]
    
for i in range(323,330):
    qlist_qcontent_inverse_dict_edu[qlist_qcontent_df.iloc[i,1]]=qlist_qcontent_df.iloc[i,0]

edu_result_directory = r"educator_raw.xlsx"
prn_result_directory = r"principal_raw.xlsx"

edu_df = pd.read_excel(edu_result_directory)
prn_df = pd.read_excel(prn_result_directory)

def get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,p_or_a):
    if(role=="educator"):
        df_curr = edu_df.copy()
        reg_locator = "Q43"
        qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
    elif(role=="principal"):
        df_curr = prn_df.copy()
        reg_locator = "Q7"
        qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn
    if p_or_a == "p":
        
        try:
            df_region = df_curr[df_curr[reg_locator]==lea]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            
        except:
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"

        sz1,sz2 = df_region.shape

        if (sz1 >=10):
            display_text = "There is the statewise result"
            #lea_or_univ =0
            total_size = sz1
        elif (sz1<= 10):
            try:
                lea_set = univ_reg_dict[univ_region]
            except:
                pass
            df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
            sz1,sz2 = df_region.shape
            #lea_or_univ = 1 
            total_size = sz1
        elif sz1 ==0:
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"
        
        v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
        sz1,sz2 = v_count_df.shape
        if sz1 ==1 and v_count_df.iloc[0,1]==0:
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"
        if sz1 == 0 :
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"

    elif p_or_a =="a":
        print("The question is: "+ str(qs))
        df_all = pd.DataFrame(df_curr[qlist_qcontent_inverse_dict[qs]])
        v_count_df = pd.DataFrame(df_all.value_counts(sort=True)).reset_index()
        #new_title = ["Answers","Question code: "+str(qlist_qcontent_inverse_dict[qs])]
        new_title = ["Answers",str(qlist_qcontent_inverse_dict[qs])]
        v_count_df.columns = new_title
        total_size,sz2 = df_all.shape
        display_text ="Result from all responses in Utah."
        

    return v_count_df,display_text,total_size