from shiny import App, render, reactive,ui

from shiny.ui import h2, tags
from data_process import univ_reg_dict,topic_qlist_dict,qlist_qcontent_dict
from data_process import univ_reg_display,qlist_qcontent_display
from data_process import lea_display,topic_display
from data_process import qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,qlist_qcontent_inverse_dict_sp
from data_process import edu_df,prn_df
from data_process_func import *
#from data_process_func import record_login
from encrypto_file import checkpassword
from data_process import lea_univ_dict
import pandas as pd
import io
import csv
import asyncio
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from data_process import get_v_counts
table_only = {'Q6','Q21','Q21_6_TEXT','Q139','Q139_6_TEXT','Q35','Q35_6_TEXT','Q219','Q219_6_TEXT','Q175','Q175_4_TEXT','Q218','Q218_4_TEXT','Q26','Q34','Q34_4_TEXT'}

total_status = {"login":-1,"authlevel":-1}
app_ui = ui.page_fluid(
    ui.panel_title("Login"),
    ui.row(
        ui.input_text("username","Username:",placeholder="username"),
        ui.input_password("password","Password:"),
        ui.input_action_button("submit","Log in/Log out",width='200px'),
        ui.output_text_verbatim("validate_pass",placeholder=True),
        ui.input_action_button("show_guide","Guideline",width='150px'),

    ),
    
    ui.panel_title("Main Page"),
    ui.row(
        
        ui.column(
            3,
            ui.panel_well(
                ui.output_text("out_text1"),
                ui.input_radio_buttons("role","role:",{"principal":"Principal","educator":"Educator"}),
            )
            
        ),
        ui.column(
            3,
            ui.panel_well(
                ui.output_text("out_text2"),
            )
            
        ),
        #ui.input_action_button("more_guide","Additional Guide",width='150px'),
        ui.column(
            3,
            ui.panel_well(
                ui.output_text("out_text3"),
                ui.input_select("cate","Topic:",topic_display),
                ui.input_select("question","Question:",[]),

            )
            
            
        ),
        ui.column(
            3,
            ui.panel_well(
                ui.output_text("out_text4"),
                ui.download_button("save_fig","Download LEA figure",width='150px',len ='150px'),
                ui.download_button("save_fig_st","Download State figure",width='150px',len ='150px'),
                ui.output_text("out_text5"),
                ui.download_button("save_result","Download LEA table",width='150px'),
                ui.download_button("save_result_st","Download State table",width='150px'),
            )
            
        )
        
    ),
    ui.row(
        ui.column(
            6,
            ui.panel_well(
                ui.panel_title("Selected LEA Result: "),
                ui.output_text("print_txt1"),
                ui.output_plot("plot_curr"),
                ui.output_text("print_txt2"),
                ui.output_table("print_table"),
            )
            
        ),
        ui.column(
            6,
            ui.panel_well(
                ui.panel_title("State Result: "),
                ui.output_text("print_txt3"),
                ui.output_plot("plot_curr_st"),
                ui.output_text("print_txt4"),
                ui.output_table("print_table_st"),
            )
            
        ),
    )
)


def server(input, output, session):
    login_status = -1
    log_role = "notset"
    correct_or_not = -1
    lea_region = "notselected"
    choices = [0,0,0,0]
    value_counts = 0
    # 0 means result of lea displayed
    # 1 means result of univ displayed
    lea_or_univ = 0 
    total_size = 0
    display_text = ""
    displayed_table = pd.DataFrame()
    curr_fig = 0 
    file_name = ""



    @output
    @render.text
    def out_text1():
        return "Choose Roles:"
    
    @output
    @render.text
    def out_text2():
        return "Choose University/LEA Region:"
    
    @output
    @render.text
    def out_text3():
        return "Choose Topic/Question:"

    @output
    @render.text
    def out_text4():
        return "Click here to download the selected LEA/district figure shown below!"

    @output
    @render.text
    def out_text5():
        return "Click here to download the selected LEA/district result table shown below!"

    @output
    @render.text
    def out_text6():
        return "Click here to download the state result figure shown below!"

    @output
    @render.text
    def out_text7():
        return "Click here to download the state result table shown below!"


    @output
    @render.text
    def validate_pass():
        try:
            role = input.role()
            univ_region = input.univ_region()
            topics =input.cate()
            lea = input.lea_region()
            qs = input.question()
        except:
            pass
        if total_status["authlevel"] == -1:
            txt = "Please Log in first!!!"
        if total_status["authlevel"] == 1:
            txt = "Welcome, admin!"
        if total_status["authlevel"] ==2 :
            try:
                curr_lea = input.lea_region()
            except:
                curr_lea = "N/A"
            
            txt  = "Welcome, LEA of "+ str(curr_lea) + " !"

        return txt

    @reactive.Effect
    @reactive.event(input.more_guide)
    def additional_guide():
        m_2 = ui.modal("Log in to see!!!",title = "Guide",easy_close=True,footer=None,)
        ui.modal_show(m_2)


    @reactive.Effect
    @reactive.event(input.show_guide)
    def showguide():
        m = ui.modal(
            "You need to login to see/save the figures and result tables. Once you logged out, you need to press 'F5' to refresh the page before login again!!! ",
            title="Brief guide",
            easy_close=True,
            footer=None,

        )
        ui.modal_show(m)
 

    @output
    @render.ui
    @reactive.Effect
    @reactive.event(input.submit)
    def submit():
        nonlocal login_status
        nonlocal log_role
        global correct_or_not
        nonlocal choices
        

        #print(login_status)
        
        #log in!
        if login_status==-1:
            username = input.username()
            password = str(input.password())
            correct_or_not = checkpassword(username,password)        
            if correct_or_not ==1 or correct_or_not==2:
                ui.remove_ui(selector="div:has(> #username)")
                ui.remove_ui(selector="div:has(> #password)")
                login_status=1
                log_role = username
                
                if correct_or_not ==1:
                    total_status["login"]=1
                    total_status["authlevel"]=1
                    
                    """
                    
                    ui.insert_ui( 
                        ui.input_radio_buttons("role_select","role:",{"principal":"Principal","educator":"Educator"}),                 
                        selector="#out_text1",
                        where="afterEnd"
                    )
                    """
                    ui.insert_ui(
                        ui.input_select("lea_region","",[]),             
                        selector="#out_text2",
                        where="afterEnd"
                    )
                    ui.insert_ui(
                        ui.input_select("univ_region","",univ_reg_display),
                        selector="#out_text2",
                        where="afterEnd"
                    )
                    """
                    
                    ui.insert_ui(                       
                        ui.input_select("question","question",[]),
                        selector="#out_text3",
                        where="afterEnd"
                    )
                    ui.insert_ui(                      
                        ui.input_select("cate","topic",topic_display),
                        #ui.input_select("question","question",[]),
                        selector="#out_text3",
                        where="afterEnd"
                    )
                    """
                if correct_or_not ==2:
                    total_status["authlevel"]=2
                    total_status["login"]=1
                    lea_info = input.username()

                    curr_univ_region = lea_univ_dict[lea_info]
                    try:
                        curr_univ_region = lea_univ_dict[lea_info]
                    except:
                        curr_univ_region = "Undefined!"
                    ui.insert_ui(
                        ui.input_select("lea_region","",{lea_info:lea_info}),             
                        selector="#out_text2",
                        where="afterEnd"
                    )
                    ui.insert_ui(
                        ui.input_select("univ_region","",{curr_univ_region:curr_univ_region}),
                        selector="#out_text2",
                        where="afterEnd"
                    )
                    """
                    
                    ui.insert_ui(                       
                        ui.input_select("question","question",[]),
                        selector="#out_text3",
                        where="afterEnd"
                    )
                    ui.insert_ui(                      
                        ui.input_select("cate","topic",topic_display),
                        #ui.input_select("question","question",[]),
                        selector="#out_text3",
                        where="afterEnd"
                    )
                    """


                    

                
                



        

        #log out!
        elif login_status ==1:
            
            ui.insert_ui(
                ui.input_text("username","Username:",placeholder="username"),
                selector="#submit",
                where="beforeBegin",
                
            )
            ui.insert_ui(
                ui.input_password("password","Password"),
                selector="#submit",
                where="beforeBegin",
            )
            #ui.remove_ui(selector="div:has(< #role_select)")
            ui.update_select(
                "lea_region",
                choices=[]
            )
            ui.update_select(
                "univ_region",
                choices=[]
            )
            


            ui.remove_ui(selector="div:has(> #univ_region)")
            ui.remove_ui(selector="div:has(> #lea_region)")
            #ui.remove_ui(selector="div:has(> #cate)")
            #ui.remove_ui(selector="div:has(> #question)")
            login_status = -1
            correct_or_not = -1
            username = "test1"
            password = "test1"
            log_role = "notset"
            for i in range(4):
                choices[i] = 0
            total_status["authlevel"] = -1
            total_status["login"] = -1
    
    
    @output
    @render.text
    def print_txt1():
        role = input.role()
        univ_region = input.univ_region()
        topics =input.cate()
        lea = input.lea_region()
        qs = input.question()
        return "Here is the result from "+str(univ_region)+" University Region and "+str(lea)+" LEA or district."
    
    @output
    @render.text
    def print_txt3():
        
        #topics =input.cate()
        
        #qs = input.question()
        return "Here is the result from all LEA/district in Utah."
    



    @output
    @render.text
    def print_txt2():
        role = input.role()
        univ_region = input.univ_region()
        topics =input.cate()
        lea = input.lea_region()
        qs = input.question()
        if correct_or_not ==2:
            lea = input.username()
            univ_region = lea_univ_dict[lea]

        if(role=="educator"):
            df_curr = edu_df.copy()
            reg_locator = "Q43"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
        elif(role=="principal"):
            df_curr = prn_df.copy()
            reg_locator = "Q7"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn
        
        
        try:
            df_region = df_curr[df_curr[reg_locator]==lea]
        except:
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"
        #df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
        sz1,sz2 = df_region.shape
        if sz1 ==0:
            display_text = "No result found in "+str(input.lea_region())+" LEA/district"
        if sz1>=10:
            display_text = "The result of "+str(input.lea_region())+" LEA/district is displayed."
        else:
            display_text ="Due to the privacy, the result of that LEA region will be hidden, instead, results of the "+str(input.univ_region())+" University Region will be displayed."
        return display_text

    @output
    @render.text
    def print_txt4():
        try:
            lea = input.lea_region()
        except:
            lea = " "
        
        try: 
            univ_region = input.univ_region()
        except:
            univ_region = " "


        
        role = input.role()
        topics =input.cate()
        
        qs = input.question()

        v_count_df,display_text,total_size =get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,"a")
        return display_text




    @reactive.Effect()
    def update_select():
        #print("After log in")
        global correct_or_not
        univ_region_chose = input.univ_region()
        curr_role = input.role()
        #print("Correct or not in LEA update is "+str(correct_or_not))
        #print(univ_region_chose)
        if correct_or_not ==1:
            try:
                lea_list_dict = list(univ_reg_dict[univ_region_chose])
                lea_display = list_display(lea_list_dict)
                ui.update_select(
                    "lea_region",
                    choices=lea_display
                    )
            except:
                pass
        elif correct_or_not ==2:
            lea = input.username()
            ui.update_select(
                "lea_region",
                choices={lea:lea}
            )





        
        
            
       
            
    
    
        
    
    
    @reactive.Effect()
    def update_select1():
        curr_role = input.role()
        curr_topic = input.cate()
        list1 = list(topic_qlist_dict[curr_role][curr_topic])

        display_list = get_qlist_by_cate(list1, qlist_qcontent_dict)
        ui.update_select(
            "question",
            choices= display_list
            )



    
    # need rework on this function
    @output
    @render.plot    
    def plot_curr_v1():
        global lea_or_univ
        global display_text
        #global login_status
        nonlocal total_size
        nonlocal value_counts
        nonlocal curr_fig
        nonlocal file_name
        nonlocal login_status
        try:
            role = input.role()
            univ_region = input.univ_region()
            topics =input.cate()
            lea = input.lea_region()
            qs = input.question()
            if correct_or_not ==2:
                lea = input.username()
                univ_region = lea_univ_dict[lea]

            if(role=="educator"):
                df_curr = edu_df.copy()
                reg_locator = "Q43"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
            elif(role=="principal"):
                df_curr = prn_df.copy()
                reg_locator = "Q7"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn

            if qlist_qcontent_inverse_dict[qs] in table_only:
                    
                fig,ax = plt.subplots()
                ax.set_title("Results will be shown in table only!")
                return fig

            
            df_region = df_curr[df_curr[reg_locator]==lea]
        
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            sz1,sz2 = df_region.shape
            if (sz1 >=10):
            
                display_text = "There is the result"
                lea_or_univ =0
                total_size = sz1
            if (sz1<= 10):
                lea_set = univ_reg_dict[univ_region]
                df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
                df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
                display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
                sz1,sz2 = df_region.shape
                lea_or_univ = 1 
                total_size = sz1
            v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
            v_labels = list(v_count_df.iloc[:,0])
            displayed_table = v_count_df
            #print(displayed_table)
            values = list(v_count_df.iloc[:,1])

            from matplotlib import pyplot as plt
            fig,ax = plt.subplots()
            ax.pie(values,labels = v_labels,autopct = '%2.2f%%')
            question_code = v_count_df.columns[1]
            q_details = qlist_qcontent_dict[question_code]
            ax.set_title("Question "+str(question_code)+": "+q_details+" .")
            file_name =input.role()+" "+input.lea_region()+" "+input.qs()+"_result.png"
            curr_fig = fig

            return fig
        except:
            from matplotlib import pyplot as plt
            
        try:
            region = input.lea_region()
        except:
            from matplotlib import pyplot as plt
            return 
        if login_status ==-1:
            return 
    


    @output
    @render.plot
    def plot_curr():
        #print("lea part, the current log in status is :" + str(total_status["authlevel"]))
        from matplotlib import pyplot as plt
        if total_status["authlevel"] == 1 or total_status["authlevel"] ==2:
            #print("The role of the current log in is :", total_status["authlevel"])
            role = input.role()
            univ_region = input.univ_region()
            topics =input.cate()
            lea = input.lea_region()
            qs = input.question()
            
            if correct_or_not ==2:
                lea = input.username()
                univ_region = lea_univ_dict[lea]
            if(role=="educator"):
                df_curr = edu_df.copy()
                reg_locator = "Q43"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
            elif(role=="principal"):
                df_curr = prn_df.copy()
                reg_locator = "Q7"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn

            if qlist_qcontent_inverse_dict[qs] in table_only:
                    
                fig,ax = plt.subplots()
                ax.set_title("Results will be shown in table only!")
                return fig
                
            df_region = df_curr[df_curr[reg_locator]==lea]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            sz1,sz2 = df_region.shape
            if (sz1 >=10):
                #lea_or_univ =0
                total_size = sz1
            if (sz1<= 10):
                lea_set = univ_reg_dict[univ_region]
                df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
                df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
                display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
                sz1,sz2 = df_region.shape
                total_size = sz1
            v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
            print(v_count_df)
            question_code = v_count_df.columns[0]
            values = list(v_count_df.iloc[:,1])
            total_counts = sum(values)
            percent_list = [round(x/total_counts*100,2) for x in values]
            new_title_1 = ["Each Response","Percentage"]
            v_count_df.columns = new_title_1
            v_count_df["Percentage"] = percent_list


            v_labels = list(v_count_df.iloc[:,0])
            fig,ax = plt.subplots()
            ax.pie(values,labels = v_labels,autopct = '%2.2f%%')

            q_details = qlist_qcontent_dict[question_code]
            #ax.set_title("Question "+str(question_code)+": "+q_details+" .")

            return fig
        else:
            #print("logged out")
            fig,ax = plt.subplots()
            ax.set_title("LEA results will be shown after logged in!!!")
            try:
                role = input.role()
                univ_region = input.univ_region()
                topics =input.cate()
                lea = input.lea_region()
                qs = input.question()
            except:
                pass
            return fig 






    @output
    @render.plot
    def plot_curr_st():
        #print("state part, the current log in status is :" + str(total_status["authlevel"]))
        from matplotlib import pyplot as plt
        global lea_or_univ
        nonlocal total_size
        nonlocal value_counts
        role = input.role()
        
        qs = input.question()
        try:
            univ_region = input.univ_region()
        except:
            univ_region = " "
        try:
            lea = input.lea_region()
        except:
            lea = " "

        if qlist_qcontent_inverse_dict_sp[input.role()][input.question()] in table_only:
            fig,ax = plt.subplots()
            ax.set_title("Results will be shown in table only!")
            return fig
        v_count_df,display_text,total_size =get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,"a")
        print(v_count_df)
        v_labels = list(v_count_df.iloc[:,0])
        values = list(v_count_df.iloc[:,1])
        displayed_table = v_count_df
        #print(v_count_df)
        
        fig,ax = plt.subplots()
        ax.pie(values,labels = v_labels,autopct = '%2.2f%%')
        question_code = v_count_df.columns[1]
        q_details = qlist_qcontent_dict[question_code]
        try:
            q_details = qlist_qcontent_dict[question_code]
        except:
            q_details = "Question is not listed"

        #ax.set_title("Question "+str(question_code)+": "+q_details+" .")
        #file_name =input.role()+" "+input.lea_region()+" "+input.qs()+"_result.png"
        return fig

        
    

    """
    """
    @output
    @render.table
    def print_table():
        global lea_or_univ
        nonlocal total_size
        nonlocal value_counts
        role = input.role()
        univ_region = input.univ_region()
        lea = input.lea_region()
        qs = input.question()
        if correct_or_not ==2:
            lea = input.username()
            univ_region = lea_univ_dict[lea]
        if(role=="educator"):
            df_curr = edu_df.copy()
            reg_locator = "Q43"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
        elif(role=="principal"):
            df_curr = prn_df.copy()
            reg_locator = "Q7"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn
            
        df_region = df_curr[df_curr[reg_locator]==lea]
        df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
        sz1,sz2 = df_region.shape
        if (sz1 >=10):
            #lea_or_univ =0
            total_size = sz1
        if (sz1<= 10):
            lea_set = univ_reg_dict[univ_region]
            df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
            sz1,sz2 = df_region.shape
            #lea_or_univ = 1 
            total_size = sz1
        v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
        question_code = v_count_df.columns[1]
        values = list(v_count_df.iloc[:,1])
        total_counts = sum(values)
        percent_list = [round(x/total_counts*100,2) for x in values]
        new_title_1 = ["Each Response","Percentage"]
        v_count_df.columns = new_title_1
        v_count_df["Percentage"] = percent_list
        
        #v_count_df.iloc[1,:] = percent_list
        
        #print(v_count_df)
        #v_count_df.columns = new_title
        #v_count_df["Percentage"] = percent_list
        return v_count_df

    @output
    @render.table
    def print_table_st():
        global lea_or_univ
        nonlocal total_size
        nonlocal value_counts
        role = input.role()
        topics =input.cate()
        qs = input.question()
        try:
            univ_region = input.univ_region()
        except:
            univ_region = " "
        try:
            lea = input.lea_region()
        except:
            lea = " "
        
        v_count_df,display_text,total_size =get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,"a")
        question_code = v_count_df.columns[1]
        #new_title = ["Answers","Question code: "+question_code]
        #v_count_df.columns = new_title
        values = list(v_count_df.iloc[:,1])
        total_counts = sum(values)
        percent_list = [round(x/total_counts*100,2) for x in values]
        new_title = ["Each Response","Counts"]
        
        v_count_df.columns = new_title
        v_count_df["Percentage"] = percent_list       
        return v_count_df
        







    @session.download(filename =lambda: f"{input.role()}_{input.lea_region()}_of question: {qlist_qcontent_inverse_dict_sp[input.role()][input.question()]}.png")
    def save_fig():

        if total_status["authlevel"] == 1 or total_status["authlevel"] ==2:
            #print("The role of the current log in is :", total_status["authlevel"])
            role = input.role()
            univ_region = input.univ_region()
            topics =input.cate()
            lea = input.lea_region()
            qs = input.question()
            
            if correct_or_not ==2:
                lea = input.username()
                univ_region = lea_univ_dict[lea]
            if(role=="educator"):
                df_curr = edu_df.copy()
                reg_locator = "Q43"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
            elif(role=="principal"):
                df_curr = prn_df.copy()
                reg_locator = "Q7"
                qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn

            if qlist_qcontent_inverse_dict[qs] in table_only:
                print("Dont save")
                return 
                
            df_region = df_curr[df_curr[reg_locator]==lea]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            sz1,sz2 = df_region.shape
            if (sz1 >=10):
                #lea_or_univ =0
                total_size = sz1
            if (sz1<= 10):
                lea_set = univ_reg_dict[univ_region]
                df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
                df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
                display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
                sz1,sz2 = df_region.shape
                total_size = sz1
            v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
            print(v_count_df)
            question_code = v_count_df.columns[0]
            values = list(v_count_df.iloc[:,1])
            total_counts = sum(values)
            percent_list = [round(x/total_counts*100,2) for x in values]
            new_title_1 = ["Each Response","Percentage"]
            v_count_df.columns = new_title_1
            v_count_df["Percentage"] = percent_list


            v_labels = list(v_count_df.iloc[:,0])
            fig,ax = plt.subplots()
            ax.pie(values,labels = v_labels,autopct = '%2.2f%%')

            q_details = qlist_qcontent_dict[question_code]
            #ax.set_title("Question "+str(question_code)+": "+q_details+" .")
        else:
            #print("logged out")
            fig,ax = plt.subplots()
            ax.set_title("LEA results will be shown after logged in!!!")
            try:
                role = input.role()
                univ_region = input.univ_region()
                topics =input.cate()
                lea = input.lea_region()
                qs = input.question()
            except:
                pass
      

        if login_status ==1:
            with io.BytesIO() as buf:
                fig.savefig(buf, format="png")
                yield buf.getvalue()
        
        
    @session.download(
        filename =lambda: f"{input.role()}_{input.lea_region()}_of question: {qlist_qcontent_inverse_dict_sp[input.role()][input.question()]}.csv"
    )

    async def save_result():
        global lea_or_univ
        nonlocal total_size
        nonlocal value_counts
        nonlocal login_status
        role = input.role()
        univ_region = input.univ_region()
        lea = input.lea_region()
        qs = input.question()
        if(role=="educator"):
            df_curr = edu_df.copy()
            reg_locator = "Q43"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_edu
        elif(role=="principal"):
            df_curr = prn_df.copy()
            reg_locator = "Q7"
            qlist_qcontent_inverse_dict = qlist_qcontent_inverse_dict_prn
            
        df_region = df_curr[df_curr[reg_locator]==lea]
        df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
        sz1,sz2 = df_region.shape
        if (sz1 >=10):
            lea_or_univ =0
            total_size = sz1
        if (sz1<= 10):
            lea_set = univ_reg_dict[univ_region]
            df_region = df_curr[df_curr[reg_locator].isin(lea_set)]
            df_region_qs = df_region[qlist_qcontent_inverse_dict[qs]]
            display_text = "Due to the privacy, the result of that LEA region will be hidden, instead, results of the University Region will be displayed"
            sz1,sz2 = df_region.shape
            lea_or_univ = 1 
            total_size = sz1
        v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()

        question_code = v_count_df.columns[1]
        values = list(v_count_df.iloc[:,1])
        total_counts = sum(values)
        percent_list = [round(x/total_counts*100,2) for x in values]
        new_title = ["Each Response","Percentage"]
        v_count_df.columns = new_title
        v_count_df["Percentage"] = percent_list

        
        
        
        
        #v_count_df.iloc[1,:] = percent_list
        #new_title_pre = ["Answers","Question code: "+question_code]
        #v_count_df.columns = new_title_pre
        #v_count_df["Percentage"] = percent_list
        
        new_title = v_count_df.columns
        firstline = ""
        secondline = ""
        for i in range(2):  # fix here 
            firstline += (new_title[i]+",")
            secondline+= (str(v_count_df.iloc[1,i])+",")
        firstline+="\n"
        secondline+="\n"
        sz_r1,sz_r2 = v_count_df.shape
        if login_status ==1:
            await asyncio.sleep(0.5)
            yield new_title[0]+",Percentage"+"\n"
            for i in range(sz_r1):
                yield str(v_count_df.iloc[i,0])+","+str(v_count_df.iloc[i,1])+"\n"
            

    @session.download(filename =lambda: f"Statewise_w/_{input.role()}_of question: {qlist_qcontent_inverse_dict_sp[input.role()][input.question()]}.png")
    def save_fig_st():

        role = input.role()
        univ_region = " "

        lea = " "
        qs = input.question()
        if qlist_qcontent_inverse_dict_sp[input.role()][input.question()] in table_only:
            print("Dont save")
            return 

        v_count_df,display_text,total_size =get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,"a")
        v_labels = list(v_count_df.iloc[:,0])
        values = list(v_count_df.iloc[:,1])
        displayed_table = v_count_df
        #print(displayed_table)
        from matplotlib import pyplot as plt
        fig,ax = plt.subplots()
        ax.pie(values,labels = v_labels,autopct = '%2.2f%%')
        question_code = v_count_df.columns[1]
        q_details = qlist_qcontent_dict[question_code]
        #ax.set_title("Question "+str(question_code)+": "+q_details+" .")

        
        with io.BytesIO() as buf:
            fig.savefig(buf, format="png")
            yield buf.getvalue()

    @session.download(
        filename =lambda: f"Statewise_w/_{input.role()}_of question: {qlist_qcontent_inverse_dict_sp[input.role()][input.question()]}.csv"
    )

    async def save_result_st():
        role = input.role()
        univ_region = " "
        lea =  " "
        qs = input.question()
        v_count_df,display_text,total_size =get_v_counts(role,univ_region,lea,qs,qlist_qcontent_inverse_dict_edu,qlist_qcontent_inverse_dict_prn,edu_df,prn_df,"a")
        #v_count_df = pd.DataFrame(df_region_qs.value_counts(sort=True)).reset_index()
        question_code = v_count_df.columns[1]
        values = list(v_count_df.iloc[:,1])
        total_counts = sum(values)
        percent_list = [round(x/total_counts*100,2) for x in values]
        new_title_pre = ["Response","Counts"]
        
        v_count_df.columns = new_title_pre
        v_count_df["Percentage"] = percent_list   
        new_title = v_count_df.columns
        firstline = ""
        secondline = ""
        for i in range(3):
            firstline += (new_title[i]+",")
            secondline+= (str(v_count_df.iloc[1,i])+",")
        firstline+="\n"
        secondline+="\n"
        """
        if login_status ==1:
            buffer = io.BytesIO()
            v_count_df.to_csv(buffer, sep=",", index=False, mode="wb", encoding="UTF-8")
               
        """
        #yield firstline
        #yield secondline
        sz_r1,sz_r2 = v_count_df.shape

        await asyncio.sleep(0.5)
        yield new_title[0]+","+new_title[1]+",Percentage"+"\n"
        for i in range(sz_r1):
            yield str(v_count_df.iloc[i,0])+","+str(v_count_df.iloc[i,1])+","+str(v_count_df.iloc[i,2])+"\n"


        

        
    
    
    
    
 
    
    
    
    


app = App(app_ui, server)
