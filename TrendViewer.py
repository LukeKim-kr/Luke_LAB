#from readline import set_startup_hook
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 웹 앱 제목
st.title("호선 Trend Viewer")

# CSV 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    
    # CSV 파일 읽기
    df = pd.read_csv(uploaded_file, index_col=None)
   
    # ture/false값 삭제(항목 선택 쉽게 하기위해 잠깐 넣었습니다)
    # 필요없는 코드
    df=df.loc[:,df.dtypes != 'bool']
    

   
   
    # 데이터 확인 및 인덱스 컬럼 추가
    #st.write("데이터 보기:")
    #st.dataframe(df)
    
    # 인덱스를 컬럼으로 추가
    #df.reset_index(inplace=True)
    #st.write("데이터 미리보기 (인덱스 추가):")
    #st.dataframe(df.head())

    # 피처 선택 및 그래프 작성
    feature_columns = df.columns.tolist()

    x_axis = st.selectbox("x축으로 사용할 Feature를 선택하세요:", feature_columns)
    y_axis = st.multiselect("y축으로 사용할 Feature를 선택하세요:", feature_columns)
       
    # 시간 객체 변환
    df[x_axis] = pd.to_datetime(df[x_axis])

    if x_axis and y_axis:
        # 오토스케일 여부를 결정하는 체크박스 추가
        auto_scale = st.checkbox("Auto scale(입력 데이터 전체 표시)")
        y_min=[]
        y_max=[]
            
        if auto_scale:
            for i in range(len(y_axis)):
            #x_min = df[x_axis].min()
            #x_max = df[x_axis].max()
                y_min.append(df[y_axis[i]].min())
                y_max.append(df[y_axis[i]].max())
        else:
            # x축, y축의 최소값 및 최대값 설정

            # 시작 시간 선택
            start_time=st.slider(
                "시작 시간 선택", 
                min_value=df[x_axis].min().to_pydatetime(),
                max_value=df[x_axis].max().to_pydatetime(),
                value=df[x_axis].min().to_pydatetime(),
                format = 'YYYY-MM-DD HH:mm:ss'
                )
           
            time_options = [5,10,15,30,60] # 선택 분 단위
            time_range=st.selectbox("표시할 시간 범위(분)",time_options, index=1) # 시간 범위 선택

            # 선택 시간 범위 내 데이터만 선택
            df[x_axis] = pd.to_datetime(df[x_axis])
            end_time=start_time + pd.Timedelta(minutes=time_range)
            df = df[(df[x_axis]>=start_time) & (df[x_axis]<=end_time)]

            # y축 범위 각각 지정
            for i in range(len(y_axis)):
                y_min.append(st.number_input(f"{y_axis[i]} range min 조정", value = float(df[y_axis[i]].min()), step=0.1, key=f"y_min_{y_axis[i]}"))
                y_max.append(st.number_input(f"{y_axis[i]} range max 조정", value = float(df[y_axis[i]].max()), step=0.1, key=f"y_max_{y_axis[i]}"))
            
       

        st.write("선택한 Feature들의 시각화 미리보기:")
        fig = go.Figure()

        colors = px.colors.qualitative.Plotly  # Plotly의 기본 색상 팔레트

        for i,col in enumerate(y_axis):
            fig.add_trace(go.Scatter(
                x=df[x_axis], y=df[col], name=col, yaxis=f"y{i+1}", line=dict(color=colors[i])
                ))
        
        
        # x축 데이터 및 y축 feature 처리
        x_data = df[x_axis]
        if x_data.isnull().any():
            st.warning("x축 컬럼에 유효하지 않은 값이 있어 제외됩니다.")
            x_data = x_data.dropna()

#======================= 범주가 중복으로 나와 주석처리 함.======================

        # plotted = False
        # for i, feature in enumerate(y_axis):
        #     y_data = df[feature]
        #     if y_data.dropna().empty:
        #         st.warning(f"{feature} 컬럼에 유효한 데이터가 없습니다.")
        #         continue
#===============================================================================

            # 유효한 데이터를 나란히 정렬
            valid_mask = pd.notnull(x_data) & pd.notnull(y_data)
            fig.add_trace(go.Scatter(x=x_data[valid_mask], y=y_data[valid_mask], mode='lines', name=feature))
            plotted = True

#======================= 범주가 중복으로 나와 주석처리 함.======================

        # if not plotted:
        #     st.error("유효한 데이터가 있는 Feature가 없습니다.")
#==============================================================================

        else:
            layout={
                "xaxis":{"title":x_axis, "domain":[0.12,1]} # x축의 시작과 끝 위치를 설정하여 그래프를 오른쪽으로 이동
                #"yaxis":{"linecolor":px.colors.qualitative.Plotly}
                }

            fig.update_yaxes(showline=True, linewidth=2, color=colors[0]) # 첫번째 데이터 축 표시 따로 해주기

            for i in range(1,len(y_axis)):
                layout[f"yaxis{i+1}"]={
                    "overlaying":"y",
                    "side":"left",
                    "position": 0.115-(i*0.03), # 첫번째 축 표시 되면서 좁아져 간격 조정했습니다
                    "showline": True,# 선 그리기
                    "linewidth":2, # 선 두께 지정
                    "linecolor": colors[i],  # 데이터 선 색과 동일한 색상 설정                    
                    "range" : [y_min[i],y_max[i]]
                }   
            

            # 그래프 여백 설정        
            fig.update_layout(layout,margin=dict(l=150, r=0, t=0, b=0), ) # 왼쪽 여백을 넉넉하게 설정
            fig.update_layout(hovermode='x unified')
            
            # fig.update_layout(
            #     #title=f"{x_axis} 에 따른 변화량",
            #     title=f"Trend",
            #     xaxis=dict(title=x_axis, range=[x_min, x_max]),
            #     yaxis=dict(title="Value", range=[y_min, y_max])
            # )
            
            st.plotly_chart(fig)
    else:
        st.info("x축과 하나 이상의 y축 Feature를 선택하세요.")
else:
    st.info("CSV 파일을 업로드하면 데이터를 시각화할 수 있습니다.")