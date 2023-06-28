from operator import index
from matplotlib import markers
#from regex import I
import statsapi
import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

plt.rc('font', family='Malgun Gothic')

BASE_PATH = '.'

st.set_page_config(
    page_title="MLB data dashboard",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        
        'About': 'made by Ju',
    }
)

st.title(':baseball: MLB Dashboard')
st.markdown('---')


with st.sidebar:
    a = st.selectbox(
        'MENU', 
        (   
            'Dashboard Info',
            'Player stat data',
            'Charts_Rank',
            'Charts_player'
        )
    )
    
    st.markdown('---')

    st.markdown(
        '''
            <style>
                .css-1adrfps.e1fqkh3o2 {
                    width: 500px;
                }
                .css-1wf22gv.e1fqkh3o2 {
                    width: 500px;
                    margin-left: -500px;
                }
            </style>
        ''',
        unsafe_allow_html=True
    )

filter_options = st.sidebar.empty()

list_file = ['diabetes.csv', 'bodyfat.csv']



def get_stats(name,stat_type,time_type):
    player_id=statsapi.lookup_player(name)[0]['id']

    player_stats_list=[]
    index_list=[]

    if(time_type=='yearByYear'):
        stat=statsapi.player_stat_data(player_id,group=stat_type,type=time_type)
        
        for i in range(len(stat['stats'])):
            player_stats_list.append(stat['stats'][i]['stats'])
            index_list.append(stat['stats'][i]['season'])
        
        df=pd.DataFrame(player_stats_list)
        df['season']=index_list
        df.set_index(keys='season',inplace=True)
        float_list=['avg','slg','ops','obp']
        for i in float_list:
            df[i]=df[i].astype(float)
        return df

    else:
        stat=statsapi.player_stat_data(player_id,group=stat_type,type=time_type)['stats'][0]['stats']
        player_stats_list.append(stat)
        return pd.DataFrame(player_stats_list)

def get_stat_rank(stat,year):
    stat_leader=statsapi.league_leader_data(stat,season=year,limit=3)
    names=['Rank','Name','Team',stat]
    stat_frame=pd.DataFrame(stat_leader,columns=names)
    if stat in ['battingAverage','earnedRunAverage','inningsPitched']:
        stat_frame[stat]=stat_frame[stat].astype(float)
    else:
        stat_frame[stat]=stat_frame[stat].astype(int)
    
    stat_frame['year']=year
    return stat_frame



if a == 'Dashboard Info':
    st.markdown('''
        ## Info
        MLB API를 이용하여 메이저리그 선수들의 다양한 기록을 확인하고 시각화 할 수 있도록 만들어진 Dashboard  
        사용한 API "https://github.com/toddrob99/MLB-StatsAPI"
        1) player stat data
            -  선수의 기록을 이름으로 검색하여 원하는 스탯을 DataFrame으로 반환하고 표시하는 기능

        2) Charts_rank
            - 원하는 기간을 선택하면 해당하는 기간동안의 전체 리그의 특정 타이틀 홀더 3위까지를 barchart로 확인할 수 있는 기능
        
        3) charts_player
            - 선수 개인의 연도별 기록을 특정 스탯을 선택하여 barchart와 line graph 형태 중 하나로 확인할 수 있는 기능 
    ''')


if a == 'Player stat data':
    filter_options = st.sidebar.empty()

    list_file = ['hitting','fielding','pitching']

    filter_options.header("filter options")

    option = filter_options.selectbox(
        'stat type',
        list_file,
        key='filter_options'
    )


    player = st.text_input('Player name', 'Mike Trout')

    

    
    def draw_table(df):
        with st.spinner('Wait for it...'):
            st.dataframe(df)
    
  

    
    mode = st.sidebar.radio(
        "mode",
        ['Season', 'Career', 'Season By Season']
        # ['summary statistics', 'correlation', 'covariance']
    )

 
    submit = st.sidebar.button('Submit')
    
    
    if submit:
        if mode == 'Season':
            df = get_stats(player,option,'season')
        elif mode == 'Career':
            df = get_stats(player,option,'career')
        elif mode == 'Season By Season':
            df = get_stats(player,option,'yearByYear')
        draw_table(df)
    


if a == 'Charts_player':
    
    filter_options = st.sidebar.empty()

    list_file = ['hitting','pitching']

    filter_options.header("filter options")

    option = filter_options.radio(
        'stat type',
        list_file,
        key='filter_options'
    )

    chart_type=st.sidebar.radio(
            "chart type",
            ['bar','line']
        )

    player = st.text_input('Player name', 'Mike Trout')

    

    if option == 'hitting':
        stat_for_data = st.sidebar.selectbox(
            "Stat to draw",
            ('homeRuns', 'rbi', 'avg', 'obp', 'slg','ops'))

        df=get_stats(player,option,'yearByYear')

        
        if chart_type == 'line':
            
            fig=px.line(df,x=df.index,y=stat_for_data, title=player+' '+stat_for_data+' chart',markers=True)

        elif chart_type == 'bar':
            fig=px.bar(df,x=df.index,y=stat_for_data, title=player+' '+stat_for_data+' chart',color=stat_for_data)

        submit = st.sidebar.button('Submit')
        if submit:
            st.plotly_chart(fig, use_container_width=True, responsive=True)

        

        


    if option == 'pitching':
        stat_for_data = st.sidebar.selectbox(
            "Stat to draw",
            ('strikeOuts', 'era', 'whip', 'wins', 'saves','inningsPitched'))

        df=get_stats(player,option,'yearByYear')

        if chart_type == 'line':
            fig=px.line(df,x=df.index,y=stat_for_data, title=player+' '+stat_for_data+' chart',markers=True)

        elif chart_type == 'bar':
            fig=px.bar(df,x=df.index,y=stat_for_data, title=player+' '+stat_for_data+' chart',color=stat_for_data)

        submit = st.sidebar.button('Submit')
        if submit:
            st.plotly_chart(fig, use_container_width=True, responsive=True)


if a == 'Charts_Rank':
    title_list=['homeRuns','battingAverage','stolenBases','strikeOuts','wins','saves','inningsPitched','earnedRunAverage']

    range_row = filter_options.slider(
        "years",
        1,10,
        key='filter_options'
    )


    stat_title=st.sidebar.selectbox(
        "Stat title",
        title_list
    )

    submit = st.sidebar.button('Submit')

    if submit:

        df=get_stat_rank(stat_title,2022)
        if range_row>1:
            for i in range(range_row-1):
                k=get_stat_rank(stat_title,2021-i)
                df=pd.concat([df,k])

        
        df1=df.query("index==0")
        df2=df.query("index==1")
        df3=df.query("index==2")

        data1=go.Bar(x=df1['year'],y=df1[stat_title],text=df1['Name'],name='1st')
        data2=go.Bar(x=df2['year'],y=df2[stat_title],text=df2['Name'],name='2nd')
        data3=go.Bar(x=df3['year'],y=df3[stat_title],text=df3['Name'],name='3rd')

        fig = go.Figure(data=[data1, data2, data3])
        st.plotly_chart(fig, use_container_width=True, responsive=True)

        

    




   
