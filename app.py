import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="수면 건강 핵심 데이터 대시보드",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 데이터 처리 함수
# ==========================================
# 혈압 수치를 의학적 기준 4단계로 분류
def categorize_bp(bp_str):
    try:
        sys, dia = map(int, str(bp_str).split('/'))
        if sys < 120 and dia < 80: return '정상혈압'
        elif 120 <= sys < 130 and dia < 80: return '주의혈압'
        elif 130 <= sys < 140 or 80 <= dia < 90: return '고혈압 전단계'
        else: return '고혈압'
    except: return '기타'

@st.cache_data
def load_data():
    # 데이터셋 1 로드
    df1 = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    df1['Blood Pressure'] = df1['Blood Pressure'].apply(categorize_bp)
    df1['BMI Category'] = df1['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    df1['Sleep Disorder'] = df1['Sleep Disorder'].fillna('없음').replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    
    occ_map = {'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 'Teacher': '교사', 
               'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 'Scientist': '과학자', 
               'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'}
    df1['Occupation'] = df1['Occupation'].map(occ_map).fillna(df1['Occupation'])
    
    df1 = df1.rename(columns={'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
                              'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 'Blood Pressure': '혈압'})

    # 데이터셋 2 로드
    df2 = pd.read_csv('Sleep_Efficiency.csv').fillna(0)
    df2['Smoking status'] = df2['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    df2 = df2.rename(columns={'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 'Deep sleep percentage': '깊은수면비율', 
                              'Light sleep percentage': '얕은수면비율', 'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 
                              'Exercise frequency': '운동빈도', 'Smoking status': '흡연여부'})
    return df1, df2

try:
    df1, df2 = load_data()
except Exception as e:
    st.error(f"파일을 읽는 중 오류가 발생했습니다. 파일명을 확인해 주세요: {e}")
    st.stop()

# ==========================================
# 3. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")

tab1, tab2 = st.tabs(["📉 라이프스타일 분석 (생활 습관)", "💤 수면 효율 분석 (외부 요인)"])

# ------------------------------------------
# 탭 1: 생활 습관 (직업, BMI, 스트레스, 혈압)
# ------------------------------------------
with tab1:
    # 핵심 지표 요약
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 인원수", f"{len(df1)}명")
    c2.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
    c3.metric("평균 스트레스", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
    
    st.markdown("---")
    
    # [동적 요소] 라디오 버튼으로 그래프 기준 선택
    st.subheader("🎯 카테고리별 수면 지표 분석")
    col_sel, col_chart = st.columns([1, 3])
    
    with col_sel:
        target = st.radio("분석 기준을 선택하세요:", ['직업', 'BMI분류', '스트레스지수', '혈압'], index=0)
    
    with col_chart:
        avg_df = df1.groupby(target)[['수면시간', '수면의질']].mean().reset_index()
        avg_df = avg_df.sort_values('수면시간', ascending=True) # 가로 막대는 True가 보기 편함
        
        # 가로 막대 그래프 (옆으로 눕힘)
        fig = px.bar(avg_df, x='수면시간', y=target, orientation='h',
                     color='수면의질', text_auto='.1f', color_continuous_scale='Turbo',
                     title=f"[{target}]별 평균 수면 시간 및 질")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("⚖️ 체중(BMI)별 수면 장애 발생 현황")
    bmi_disorder = df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
    fig2 = px.bar(bmi_disorder, x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True,
                  color_discrete_map={'없음': '#22c55e', '불면증': '#eab308', '수면 무호흡증': '#ef4444'})
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율 (알코올, 운동, 흡연)
# ------------------------------------------
with tab2:
    c1, c2, c3 = st.columns(3)
    c1.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
    c2.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
    c3.metric("평균 각성 횟수", f"{df2['각성횟수'].mean():.1f}회")

    st.markdown("---")
    
    st.subheader("⚡ 외부 요인별 수면 영향도 분석")
    col_sel2, col_chart2 = st.columns([1, 2])
    
    with col_sel2:
        factor = st.selectbox("분석할 요인을 선택하세요:", 
                              ['알코올 (잔/회)', '운동빈도 (회/주)', '흡연여부 (흡연/비흡연)'], index=0)
    
    with col_chart2:
        if '알코올' in factor:
            data = df2.groupby('알코올')['수면효율'].mean().reset_index()
            data['수면효율'] *= 100
            fig3 = px.line(data, x='알코올', y='수면효율', markers=True, text=data['수면효율'].round(1), title="음주량에 따른 수면 효율")
            fig3.update_traces(line_color='#ec4899', textposition='top center')
        elif '운동' in factor:
            data = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            fig3 = px.line(data, x='운동빈도', y='깊은수면비율', markers=True, text=data['깊은수면비율'].round(1), title="운동 빈도에 따른 깊은 수면 비중")
            fig3.update_traces(line_color='#10b981', textposition='top center')
        else: # 흡연
            data = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
            fig3 = px.bar(data, x='흡연여부', y='각성횟수', color='흡연여부', text_auto='.1f', title="흡연 여부와 평균 각성(깸) 횟수",
                          color_discrete_map={'비흡연': '#38bdf8', '흡연': '#ef4444'})
        
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.subheader("🛌 수면 단계별 평균 구성 비율")
    stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], 
                           '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
    fig4 = px.pie(stages, values='비중', names='단계', hole=0.4, color_discrete_sequence=['#3b82f6', '#8b5cf6', '#f59e0b'])
    st.plotly_chart(fig4, use_container_width=True)
