import requests
import json
import pandas as pd
import smartsheet_dataframe as ssdf
import matplotlib.pyplot as plt
import itertools
import streamlit as st
import altair as alt
import time
import smartsheet


# Replace ACCESS_TOKEN with your Smartsheet API access token
ACCESS_TOKEN = 'r84vLFkD7bYJaE3eXaSB3Z8mWwD4wgTm3zucM'

# Replace SHEET_ID with the ID of the sheet you want to access
#SHEET_ID = "562741225252740"
today_sheet_id = '4988080772933508'
past_sheet_id = '562741225252740'
master_game_sheet_id = '7707037434963844'
contact_info_sheet_id = '4682115892701060'

today_column_map = {}
master_column_map = {}

master_column_map = {'Game Info': 7629695487371140,
 'Row ID': 1850723038193540,
 'Date': 2000195953158020,
 'Day of the Week': 6503795580528516,
 'League': 4251995766843268,
 'Client Team': 8755595394213764,
 'Home Team': 170608604538756,
 'Away Team': 4674208231909252,
 'TV Network': 2422408418224004,
 'BB City': 6926008045594500,
 'Operating Site': 1296508511381380,
 'Operator': 5800108138751876,
 'Start Time (Local)': 3548308325066628,
 'Call Time (Local)': 8051907952437124,
 'Event Notes Prior': 733558557960068,
 'Notes, Issues, Comments': 5237158185330564,
 'Game Result': 7488957999015812,
 'Inventory': 1859458464802692,
 'Rotation': 6363058092173188,
 'Art': 4111258278487940,
 'Art Made?': 8614857905858436,
 'Rotation Sent?': 452083581249412,
 'Start Time (EST)': 4955683208619908,
 'Cancelled/PPD/NO VIRTUAL': 2703883394934660,
 'BB Station': 8690528527116164,
 'Op Contact Info': 7207483022305156,
 'Are Client, Home, Away Team BLANK?2': 1577983488092036,
 'Things to Note Before Game': 6081583115462532,
 'Op Unavailability': 3829783301777284,
 'Channel': 8333382929147780,
 'Column40': 1015033534670724,
 'Column41': 5518633162041220,
 'Operating Site Call Times': 3266833348355972,
 'Call Time (local) 24hrs': 7770432975726468,
 'Call Time (Local) HOURS': 2140933441513348,
 'Call Time (Local) MINUTES': 6644533068883844,
 'Call Time (Local) 12am/pm format': 4392733255198596,
 'Time Zone': 8896332882569092,
 'Convert to 24hrs local': 100239860361092,
 '24hrs to 12ampm HOUR Conversion': 4603839487731588,
 '24hrs to 12ampm MINUTE Conversion': 2352039674046340,
 '12ampm hours+minutes': 6855639301416836,
 'Column31': 1226139767203716,
 '24hrs to eastern': 5729739394574212,
 '24hrs to 12ampm HOUR Conversion EASTERN': 3477939580888964,
 '24hrs to 12ampm MINUTE Conversion EASTERN': 7981539208259460,
 'Eastern Time': 663189813782404,
 'Billable': 1027035457972100,
 'Billed': 5530635085342596,
 'Op_Contact_Name_1': 3861738782779268,
 'Op_Contact_No_1': 1382705134364548,
 'Op_Contact_Email_1': 7172973884401540,
 'Op_Contact_Name_2': 8365338410149764,
 'Op_Contact_No_2': 5886304761735044,
 'Op_Contact_Email_2': 2669374257031044,
 'Op_Contact_Copy_2': 4921174070716292,
 'Op_Contact_Name_3': 1046989015672708,
 'Op_Contact_No_3': 3634504948049796,
 'Op_Contact_Email_3': 1543474350188420,
 'Op_Contact_Copy_3': 417574443345796,
 'Op_Contact_Name_4': 5550588643043204,
 'Op_Contact_No_4': 8138104575420292,
 'Op_Contact_Email_4': 6047073977558916,
 'Op_Contact_Copy_4': 1987058572519300}

#grab smartsheet data using smartsheet API#

smartsheet_client = smartsheet.Smartsheet('r84vLFkD7bYJaE3eXaSB3Z8mWwD4wgTm3zucM')

def get_smartsheet_api():

    global today_sheet_id,master_game_sheet_id,today_column_map,master_column_map

    today_sheet = smartsheet_client.Reports.get_report(today_sheet_id)
    today_sheet_save = "D:/Users/Santi/Documents/Brand Brigade/BB_Programs/today_report.json"

    master_sheet = smartsheet_client.Sheets.get_sheet(master_game_sheet_id)
    master_sheet_save = 'D:/Users/Santi/Documents/Brand Brigade/BB_Programs/master_sheet.json'

    with open(today_sheet_save, "w") as outfile:
        outfile.write(str(today_sheet))

    f_today = open(today_sheet_save)
    today_data = json.load(f_today)

    with open(master_sheet_save, "w") as outfile:
        outfile.write(str(master_sheet))

    f_master = open(master_sheet_save)
    master_data = json.load(f_master)

    #grab column ids
    
    for i in today_data['columns']:
        #print(i["virtualId"],i['title'])
        today_column_map[i["virtualId"]] = i['title']

    
    for i in master_data['columns']:
        #print(i["virtualId"],i['title'])
        master_column_map[i["title"]]= i['id']

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)


st.set_page_config(layout="wide")
#st.title("Nightwatch Game Rating",anchor='middle')
st.markdown("<h1 style='text-align: center'>Nightwatch Game Ratings</h1><br><br>", unsafe_allow_html=True)

# class MyDict(dict):
#     def __missing__(self, key):
#         return ""



df_past_games = ssdf.get_sheet_as_df(token=ACCESS_TOKEN, sheet_id=past_sheet_id)
#op_games = df_past_games.loc[df_past_games['Operator'] == 'santi@brandbrigade.com', 'Game Result'].squeeze("index")

df_today = ssdf.get_report_as_df(token=ACCESS_TOKEN, report_id=today_sheet_id)

# df_today = ssdf.get_report_as_df(token=ACCESS_TOKEN, report_id=today_sheet_id).set_index('row_id')
df_today["Op Contact Info"] = df_today["Op Contact Info"].astype('string')

df_master = ''
stdf = ''

today_ops = df_today["Operator"].drop_duplicates()
today_teams = df_today["Client Team"].drop_duplicates()
past_games_ops = df_past_games["Operator"].drop_duplicates()
past_game_dates = df_past_games["Date"].drop_duplicates() 

weighted_avg = [30,9,8,7,6,5,4,3]

op_scores = {}
team_scores = {}
games_done = {}
day_scores = {}
day_scores_range = {}
scores_df = {}
df_today_all = {}
col = []
day_scores_df = ""

date_chart_dates = []
date_chart_colors = []

def add_scores_to_today():
    global df_today, df_today_all

    df_today["Team Scores"] = df_today["Client Team"].map(team_scores).fillna('N\A')
    df_today["Op Scores"] = df_today["Operator"].map(op_scores).fillna('N\A')
    df_today_all = df_today
    df_today = df_today[['row_id','Cancelled/PPD/NO VIRTUAL','League','TV Network','Operating Site','Client Team','Team Scores','Home Team','Away Team','BB City','Start Time (EST)','Operator','Op Scores','Op Contact Info','Art','Event Notes Prior','Game Result','Notes, Issues, Comments']]

def op_game_score (x):
    game_list = []
    op_game = pd.Series(df_past_games.loc[df_past_games['Operator'] == x, 'Game Result'].squeeze())
    op_game_avg = op_game.reset_index(drop=True)
    op_game_avg = op_game.iloc[0:8]
    weighted_avg_len = len(op_game_avg)
    op_game_weighted_sum = sum(op_game_avg.multiply(weighted_avg[0:weighted_avg_len],fill_value=0))
    weighted_avg_sum = sum(weighted_avg[0:weighted_avg_len])
    if weighted_avg_sum == 0:
        return
    weighted_op_score = round(op_game_weighted_sum/weighted_avg_sum,2)
    op_scores[x] = weighted_op_score

def team_game_score (x):
    game_list = []
    op_game = pd.Series(df_past_games.loc[df_past_games['Client Team'] == x, 'Game Result'].squeeze())
    op_game_avg = op_game.reset_index(drop=True)
    op_game_avg = op_game.iloc[0:8]
    weighted_avg_len = len(op_game_avg)
    op_game_weighted_sum = sum(op_game_avg.multiply(weighted_avg[0:weighted_avg_len],fill_value=0))
    weighted_avg_sum = sum(weighted_avg[0:weighted_avg_len])
    if weighted_avg_sum == 0:
        return
    weighted_op_score = round(op_game_weighted_sum/weighted_avg_sum,2)
    team_scores[x] = weighted_op_score

def op_games_done (x):
    game_list = []
    op_game = pd.Series(df_past_games.loc[df_past_games['Operator'] == x, 'Game Result'].squeeze())
    op_game_avg = op_game.reset_index(drop=True)
    op_games_done = len(op_game_avg)
    games_done [x] = op_games_done

def remap_email_to_op(where_to_replace):
    df_contact = ssdf.get_sheet_as_df(token=ACCESS_TOKEN, sheet_id=contact_info_sheet_id)
    df_contact_dict = df_contact.to_dict()
    df_contact_dict_re = {}
    for i in df_contact_dict["Name"]:
        df_contact_dict_re[df_contact_dict["Email"][i]] = df_contact_dict["Name"][i]
    where_to_replace.__init__(where_to_replace.replace(df_contact_dict_re))

def day_game_score (x):
    game_list = []
    games_scores_by_day = pd.Series(df_past_games.loc[df_past_games['Date'] == x, 'Game Result'].squeeze())
    day_score_sum = sum(games_scores_by_day)
    day_score_len = len(games_scores_by_day)
    day_score_simple_avg = round(day_score_sum/day_score_len,2)
    day_scores[x] = day_score_simple_avg

def get_today_op_score():
    for i in today_ops:
        op_game_score(i)
    #return op_scores

def get_today_team_score():
    for i in today_teams:
        team_game_score(i)
    #return team_scores

def refresh():
    remap_email_to_op(df_past_games)
    get_today_op_score()
    get_today_team_score()

def get_op_games_done():
    remap_email_to_op(past_games_ops)
    for i in past_games_ops:
        op_games_done(i)
    #return games_done    

def get_day_game_score():
    global day_scores

    for i in past_game_dates:
        day_game_score(i)
        #day_scores = day_scores[0:8]
    day_scores = dict(list(day_scores.items())[-7:])
    # return day_scores

def make_7_day_score_graph():
    global day_scores, col
    
    # if not day_scores:
    #     get_day_game_score()
    
    day_scores = {k.replace(k,k[:-3]):v for k,v in day_scores.items()}
    day_scores_series = pd.Series(day_scores)

    for val in day_scores_series:
        if val > 3 and val < 6:
            col.append('yellow')
        elif val >= 6:
            col.append('green')
        else:
            col.append('red')
    
    day_graph = day_scores_series.plot.bar(width=1, color = col)
    plt.title("Past 7 Day Average")
    plt.xlabel("Date")
    plt.ylabel("Day Score")
    plt.xticks(rotation=0, horizontalalignment="center")
    day_graph.bar_label(day_graph.containers[0])
    #fig, ax = plt.subplots()
    #st.pyplot(fig)

def all_stats():
    refresh()
    get_op_games_done()
    get_day_game_score()
    add_scores_to_today()
    make_7_day_score_graph()
    # return df_today

def run_app():
    global df_today, day_scores

    all_stats()
    #day_scores = pd.DataFrame(day_scores,index=[1])
    
    #st.dataframe(df_today)
    #st.experimental_data_editor(df_today)
    
    # st.bar_chart(day_scores_df.style.apply(team_scores_colors,index=1),x="Date",y="Score")
    # #st.bar_chart(day_scores)

    
    

def team_scores_colors(val):
    if val == "N\A":
        val = 0
    else:
        val = float(val)
    if val > 3 and val < 6:
        color = 'yellow'
    elif val >= 6:
        color = 'green'
    elif val == 0:
        color = ''
    else:
        color = 'red'
    return f'background-color: {color}'

def day_score_dict_to_df():
    global day_scores, scores_df,day_scores_df

    scores_df_dates = []
    scores_df_scores = []
    for i in day_scores:
        scores_df_dates.append(str(i))
        scores_df_scores.append(float(day_scores[i]))
    scores_df["Date"] = scores_df_dates
    scores_df["Score"] = scores_df_scores
    
    day_scores_df = pd.DataFrame(scores_df)

run_app()

def make_7_day_score_graph_altair ():
    day_score_dict_to_df()
    dsdf = day_scores_df
    for idx,y in dsdf.Date.items():
        date_value = dsdf.Date[idx]
        score_value = dsdf.Score[idx]
        date_chart_dates.append(date_value)
        x = score_value
        if x > 3 and x < 6:
            #print(x,'yellow')
            date_chart_colors.append('yellow')
        elif x >= 6:
            #print(x,'green')
            date_chart_colors.append('green')
        elif x == 0:
            date_chart_colors.append('black')
            #print(x,'black')
        else:
            date_chart_colors.append('red')
            #print(x,'red')

    chart = (
        alt.Chart(day_scores_df)
        .mark_bar()
        .encode(
            alt.X("Date",axis=alt.Axis(labelAngle=0)),
            alt.Y("Score",scale=alt.Scale(domain=[0,8],nice=False)),
            alt.Color("Date",legend=None,scale=alt.Scale(domain=date_chart_dates,range=date_chart_colors)),
            alt.Tooltip(["Date", "Score"]),
            
        )
        #.interactive()
    )

    text = chart.mark_text(
        #align='center',
        #baseline='middle',
        dy= -10
        ).encode(text='Score')

    st.altair_chart((chart + text).properties(width=800,title="7 Day Average").configure_title(color='white',anchor='middle'))

def make_7_day_score_graph_altair ():
    print('')

#UNCOMMENT
def op_games_done_table():
    print('')
    # st.markdown("<h6>Op Overview</h6>", unsafe_allow_html=True)
    # st.experimental_data_editor(games_done)
#UNCOMMENT

def change_df():
    # st.write(df_today)
    print('tetting thia out')
def today_game_table():


    st.markdown("<h6 style='text-align: center'>Today's Games</h6>", unsafe_allow_html=True)

    global df_today,stdf
    df_today = df_today.astype(str)
    df_today["Game Result"] = pd.to_numeric(df_today['Game Result'], errors='coerce').astype('Int64')
    #stdf = st.experimental_data_editor(df_today.style.apply(team_scores_colors, subset=['Team Scores']),use_container_width=False,on_change=change_df()).style.apply_index({lambda x : '{:.4f}'.format(x)})
    stdf = st.experimental_data_editor(df_today)
    #st.write(df_today)




    # def updated_df():
    #     global stdf
    #     print(stdf)
    




make_7_day_score_graph_altair()
op_games_done_table()
today_game_table()
#st.write(date_chart_dates,date_chart_colors)
#st.write(type(df_today),type(games_done))
#st.write(df_today)



# df = pd.DataFrame(
#     [
#        {"command": "st.selectbox", "rating": 4, "is_widget": True},
#        {"command": "st.balloons", "rating": 5, "is_widget": False},
#        {"command": "st.time_input", "rating": 3, "is_widget": True},
#    ]
# )
# edited_df = st.experimental_data_editor(df)

@st.cache_data
def load_master():
    global df_master

    df_master = ssdf.get_sheet_as_df(token=ACCESS_TOKEN,sheet_id=master_game_sheet_id).set_index('row_id')


edited_df = stdf
df_diff = pd.DataFrame()
df_merge = stdf.merge(df_today,how='outer')
df_diff = pd.concat([df_merge,df_today]).drop_duplicates(keep=False)
try:
    favorite_command = edited_df.loc[edited_df["Game Result"].idxmax()]["Client Team"]
    #st.write(df_diff)
except Exception:
    pass
#st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

# print(type(stdf))
# print(
#     df_today.compare(stdf)
#     )
print('\n')
print(current_time,'\n')

# print(df_today.index)
# print(stdf.index)

#print(df_today['Game Result'])
print('\n')
#print(stdf['Game Result'])
print('\n')
print(current_time)

#print(df_today.compare(stdf, align_axis=1, keep_shape=False, keep_equal=False))

# merged_data = df_today.merge(stdf,how='inner',indicator=True)
# merged_data = merged_data.set_index(stdf.index,inplace=True)
# data_12_diff = merged_data.loc[lambda x : x['_merge'] != 'both']
# print(data_12_diff)

# diff = df_today["Game Result"].isin(df_today['Client Team'])
# df_diff = stdf.drop(stdf[diff].index,inplace=True)
# #print(df_diff)
# st.markdown(df_diff)

# df1 = stdf
# df2 = df_today
#df1 = df1.merge(df2, how="outer", left_index=True, right_index=True)

# st.markdown('merge')
# st.write(df_merge)
# st.markdown('merge')


def update_smartsheet_go (x,y):
    global smartsheet_client

    new_cell = smartsheet.models.Cell()
    new_cell.column_id = 7488957999015812
    new_cell.value = y
    new_cell.strict = False

    # Build the row to update
    new_row = smartsheet.models.Row()
    new_row.id = x
    new_row.cells.append(new_cell)

    # Update rows
    updated_row = smartsheet_client.Sheets.update_rows(
    master_game_sheet_id,      # sheet_id
    [new_row])

def update_smartsheet():
    #st.write('Currently Updating Smartsheet')
    for idx in df_diff.index:
        #st.write(f"Updating {df_diff['Client Team'][idx]} Score")

        diff_row_id = int(df_diff['row_id'][idx])
        diff_game_result = int(df_diff['Game Result'][idx])
        #print(type(diff_row_id),type(diff_game_result))
        update_smartsheet_go(diff_row_id,diff_game_result)
        #print(df_diff['row_id'][idx],df_diff['Game Result'][idx])
    st.markdown("Done Updating")
    

#st.write(df_today)

#st.markdown('Merged Datasets')
#st.write(df_merge)
#st.markdown('Merged Datasets 2')

# result = stdf[stdf["Game Result"] != df_today["Game Result"]]
# st.write(result)

# df1 = df1.merge(df2, indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
# st.write(df1)

#st.button('Update Smartsheet',on_click=update_smartsheet())

def smart_button():
    if st.button('Update Smartsheet'):
        update_smartsheet()

col1, col2, col3 , col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    center_button = smart_button()