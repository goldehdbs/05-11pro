import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="현대인 수면 & 라이프스타일 분석",
    page_icon="🌙",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .main { background-color: #0f172a; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 전처리 (안전성 대폭 강화)
# ==========================================
@st.cache_data
def load_data_1():
    file = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file): 
        return pd.DataFrame()
    
    df = pd.read_csv(file)
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음').replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 'Age': '나이'
    })

@st.cache_data
def load_data_2():
    file = 'Sleep_Efficiency.csv'
    if not os.path.exists(file): 
        return pd.DataFrame()
    
    df = pd.read_csv(file)
    df = df.fillna(0) # 결측치 안전하게 0으로 처리
    df['Smoking status'] = df['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    
    return df.rename(columns={
        'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 
        'Deep sleep percentage': '깊은수면비율', 'Light sleep percentage': '얕은수면비율', 
        'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 'Exercise frequency': '운동빈도', 
        'Smoking status': '흡연여부', 'Age': '나이'
    })

df1 = load_data_1()
df2 = load_data_2()

if df1.empty and df2.empty:
    st.error("⚠️ 데이터를 불러올 수 없습니다. 동일한 폴더에 CSV 파일 2개가 있는지 확인해 주세요.")
    st.stop()

# ==========================================
# 3. 사이드바 인터랙티브 필터
# ==========================================
st.sidebar.title("🎮 동적 필터 조절")
st.sidebar.markdown("조작 시 우측 그래프가 실시간으로 반응합니다.")

# 나이 범위 설정 (데이터의 최소/최대값 기반으로 안전하게 설정)
min_age = int(min(df1['나이'].min(), df2['나이'].min())) if not df1.empty and not df2.empty else 10
max_age = int(max(df1['나이'].max(), df2['나이'].max())) if not df1.empty and not df2.empty else 80
age_range = st.sidebar.slider("분석 연령대 설정", min_age, max_age, (min_age, max_age))

# 직업군 필터
all_occupations = df1['직업'].unique().tolist() if not df1.empty else []
selected_occ = st.sidebar.multiselect("분석 직업군 선택", all_occupations, default=all_occupations)

# [안전성 추가] 필터링된 데이터프레임 복사
df1_filtered = df1[(df1['나이'] >= age_range[0]) & (df1['나이'] <= age_range[1]) & (df1['직업'].isin(selected_occ))].copy() if not df1.empty else pd.DataFrame()
df2_filtered = df2[(df2['나이'] >= age_range[0]) & (df2['나이'] <= age_range[1])].copy() if not df2.empty else pd.DataFrame()

# ==========================================
# 4. 메인 화면 구성
# ==========================================
st.title("🌙 현대인 수면 건강 & 라이프스타일 인터랙티브 분석")
st.markdown("마우스를 올려 상세 데이터를 확인하거나 하단의 슬라이더로 범위를 좁혀보세요.")

tab1, tab2 = st.tabs(["📊 파트 1: 생활 습관 & 직업", "⚡ 파트 2: 수면 효율 & 외부 요인"])

# ------------------------------------------
# 탭 1: 직업, 스트레스, BMI
# ------------------------------------------
with tab1:
    if df1_filtered.empty:
        st.warning("조건에 맞는 데이터가 없습니다. 사이드바 필터 조건을 넓혀주세요.")
    else:
        # 상단 동적 KPI
        k1, k2, k3 = st.columns(3)
        k1.metric("선택된 인원", f"{len(df1_filtered)}명")
        k2.metric("평균 수면 시간", f"{df1_filtered['수면시간'].mean():.1f}h")
        k3.metric("평균 스트레스", f"{df1_filtered['스트레스지수'].mean():.1f}/10")

        st.markdown("---")
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("👨‍💻 직업별 수면 시간 vs 스트레스 (버블 차트)")
            bubble_data = df1_filtered.groupby('직업').agg({'수면시간': 'mean', '스트레스지수': 'mean', '나이': 'count'}).reset_index()
            # 원 크기는 해당 직업의 인원수(나이 컬럼 카운트 활용)
            fig1 = px.scatter(bubble_data, x='수면시간', y='스트레스지수', size='나이', color='직업',
                             hover_name='직업', text='직업', size_max=60)
            fig1.update_traces(textposition='top center')
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            st.subheader("⚖️ BMI 분류별 수면 장애 비중 (누적 막대)")
            bmi_data = df1_filtered.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
            fig2 = px.bar(bmi_data, x='BMI분류', y='인원수', color='수면장애', 
                         barmode='stack', text_auto=True,
                         color_discrete_map={'없음': '#38bdf8', '불면증': '#fb923c', '수면 무호흡증': '#f87171'})
            fig2.update_layout(hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------
# 탭 2: 알코올, 운동, 수면구조
# ------------------------------------------
with tab2:
    if df2_filtered.empty:
        st.warning("조건에 맞는 데이터가 없습니다. 사이드바 필터 조건을 넓혀주세요.")
    else:
        # 상단 동적 KPI
        k4, k5, k6 = st.columns(3)
        k4.metric("평균 수면 효율", f"{df2_filtered['수면효율'].mean()*100:.1f}%")
        k5.metric("깊은 수면 비중", f"{df2_filtered['깊은수면비율'].mean():.1f}%")
        k6.metric("평균 각성 횟수", f"{df2_filtered['각성횟수'].mean():.1f}회")

        st.markdown("---")
        c3, c4 = st.columns(2)

        with c3:
            st.subheader("🍷 알코올 섭취량별 수면 효율 (동적 라인)")
            alc_eff = df2_filtered.groupby('알코올')['수면효율'].mean().reset_index()
            alc_eff['수면효율'] = (alc_eff['수면효율'] * 100).round(1)
            
            fig3 = px.line(alc_eff, x='알코올', y='수면효율', markers=True, text='수면효율')
            fig3.update_traces(textposition="top center", line_color='#a855f7', marker=dict(size=12))
            # 하단에 스크롤로 범위를 조절할 수 있는 레인지 슬라이더 활성화
            fig3.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="linear"), yaxis_title="수면 효율 (%)")
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            st.subheader("🛌 수면 단계별 평균 비중 (도넛 차트)")
            stages = pd.DataFrame({
                '단계': ['깊은 수면', 'REM 수면', '얕은 수면'],
                '비중': [df2_filtered['깊은수면비율'].mean(), df2_filtered['REM비율'].mean(), df2_filtered['얕은수면비율'].mean()]
            })
            # 안전하게 파이 차트 생성 (데이터가 NaN일 경우 대비)
            stages = stages.fillna(0) 
            fig4 = go.Figure(data=[go.Pie(labels=stages['단계'], values=stages['비중'], hole=.5)])
            fig4.update_traces(textinfo='percent+label', pull=[0.1, 0, 0], marker=dict(colors=['#10b981', '#38bdf8', '#64748b']))
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        c5, c6 = st.columns(2)

        with c5:
            st.subheader("🏃 운동 빈도와 깊은 수면 (영역 차트)")
            ex_deep = df2_filtered.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            fig5 = px.area(ex_deep, x='운동빈도', y='깊은수면비율', color_discrete_sequence=['#10b981'])
            fig5.update_layout(hovermode="x unified", yaxis_title="깊은 수면 비율 (%)")
            st.plotly_chart(fig5, use_container_width=True)

        with c6:
            st.subheader("🚬 흡연 여부와 수면 중 각성 (박스 플롯)")
            # 각 그룹별 분포도를 볼 수 있도록 모든 점(points="all") 시각화
            fig6 = px.box(df2_filtered, x='흡연여부', y='각성횟수', color='흡연여부',
                         points="all", color_discrete_map={'비흡연': '#38bdf8', '흡연': '#f87171'})
            st.plotly_chart(fig6, use_container_width=True)
