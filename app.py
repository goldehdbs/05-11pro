import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="수면 건강 집중 분석 대시보드",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    # 카테고리 한글 변환
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
    
    # 결측치 처리 및 변환
    df['Sleep Disorder'] = df['Sleep Disorder'].fillna('없음')
    df['Sleep Disorder'] = df['Sleep Disorder'].replace({'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'})
    
    occ_map = {
        'Software Engineer': '엔지니어', 'Doctor': '의사', 'Sales Representative': '영업직', 
        'Teacher': '교사', 'Nurse': '간호사', 'Engineer': '엔지니어', 'Accountant': '회계사', 
        'Scientist': '과학자', 'Lawyer': '변호사', 'Salesperson': '영업직', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    return df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질', 
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애'
    })

@st.cache_data
def load_data_2():
    file_path = 'Sleep_Efficiency.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    df = df.fillna(0)
    
    df['Smoking status'] = df['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    
    return df.rename(columns={
        'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 
        'Deep sleep percentage': '깊은수면비율', 'Light sleep percentage': '얕은수면비율', 
        'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 'Exercise frequency': '운동빈도',
        'Smoking status': '흡연여부'
    })

try:
    df1 = load_data_1()
    df2 = load_data_2()
except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

# ==========================================
# 3. 사이드바 (깔끔하게 직업군 필터만 유지)
# ==========================================
st.sidebar.title("🎮 필터 조절")
st.sidebar.markdown("연령대 필터를 제거하고 깔끔하게 구성했습니다.")

if not df1.empty:
    all_occupations = df1['직업'].unique().tolist()
    selected_occ = st.sidebar.multiselect("분석 직업군 선택 (선택 해제 시 제외됨)", all_occupations, default=all_occupations)
    df1_filtered = df1[df1['직업'].isin(selected_occ)].copy()
else:
    df1_filtered = df1

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")

if df1.empty and df2.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다. CSV 파일 위치를 확인해 주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📉 수면시간 집중 분석", "💤 수면 효율 분석 (외부 요인)"])

# ------------------------------------------
# 탭 1: 요청하신 3가지 수면시간 분석
# ------------------------------------------
with tab1:
    if df1_filtered.empty:
        st.warning("조건에 맞는 데이터가 없습니다. 좌측 직업군 필터를 조절해 주세요.")
    else:
        # 상단 Metric 지표
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 수면 시간", f"{df1_filtered['수면시간'].mean():.1f}시간")
        c2.metric("평균 스트레스 지수", f"{df1_filtered['스트레스지수'].mean():.1f}점")
        c3.metric("평균 수면의 질", f"{df1_filtered['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        # 1. 직업군별 수면시간 (넓게 배치)
        st.subheader("👨‍💻 1. 직업군별 평균 수면 시간")
        avg_sleep_occ = df1_filtered.groupby('직업')['수면시간'].mean().reset_index().sort_values('수면시간', ascending=False)
        fig1 = px.bar(avg_sleep_occ, x='직업', y='수면시간', color='수면시간', text_auto='.1f', color_continuous_scale='Blues')
        fig1.update_layout(yaxis_title="수면 시간 (시간)", xaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")
        
        # 2. BMI별 / 3. 스트레스별 (좌우 나란히 배치)
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("⚖️ 2. 체중(BMI) 분류별 평균 수면 시간")
            avg_sleep_bmi = df1_filtered.groupby('BMI분류')['수면시간'].mean().reset_index().sort_values('수면시간', ascending=False)
            fig2 = px.bar(avg_sleep_bmi, x='BMI분류', y='수면시간', color='수면시간', text_auto='.1f', color_continuous_scale='Greens')
            fig2.update_layout(yaxis_title="수면 시간 (시간)", xaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)

        with col_right:
            st.subheader("🔥 3. 스트레스 지수별 평균 수면 시간")
            avg_sleep_stress = df1_filtered.groupby('스트레스지수')['수면시간'].mean().reset_index()
            # 스트레스 지수는 순서대로 정렬하고 글자로 변환하여 X축 정렬
            avg_sleep_stress = avg_sleep_stress.sort_values('스트레스지수')
            avg_sleep_stress['스트레스지수_str'] = avg_sleep_stress['스트레스지수'].astype(str) + "점"
            
            fig3 = px.bar(avg_sleep_stress, x='스트레스지수_str', y='수면시간', color='수면시간', text_auto='.1f', color_continuous_scale='Reds')
            fig3.update_layout(yaxis_title="수면 시간 (시간)", xaxis_title="")
            st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율 (기존 유지)
# ------------------------------------------
with tab2:
    if df2.empty:
        st.warning("`Sleep_Efficiency.csv` 파일이 없습니다.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
        c2.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
        c3.metric("평균 자다 깨는 횟수", f"{df2['각성횟수'].mean():.1f}회")

        st.markdown("---")

        col_eff1, col_eff2 = st.columns(2)
        with col_eff1:
            st.subheader("🍺 알코올 섭취량별 수면 효율")
            avg_eff = df2.groupby('알코올')['수면효율'].mean().reset_index()
            avg_eff['수면효율'] = (avg_eff['수면효율'] * 100).round(1)
            fig5 = px.line(avg_eff, x='알코올', y='수면효율', markers=True, text='수면효율',
                           labels={'알코올': '음주량', '수면효율': '수면 효율 (%)'})
            fig5.update_traces(textposition='top center', line_color='#a855f7', marker=dict(size=10))
            st.plotly_chart(fig5, use_container_width=True)

        with col_eff2:
            st.subheader("🛌 평균 수면 단계 구성")
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            fig6 = px.pie(stages, values='비중', names='단계', hole=0.4, color_discrete_sequence=['#10b981', '#38bdf8', '#64748b'])
            fig6.update_traces(textinfo='percent+label')
            st.plotly_chart(fig6, use_container_width=True)

        st.markdown("---")

        col_eff3, col_eff4 = st.columns(2)
        with col_eff3:
            st.subheader("🚬 흡연 여부와 각성 횟수")
            avg_awake = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
            fig7 = px.bar(avg_awake, x='흡연여부', y='각성횟수', color='흡연여부', text_auto='.1f')
            st.plotly_chart(fig7, use_container_width=True)

        with col_eff4:
            st.subheader("🏃 주당 운동 빈도와 깊은 수면")
            avg_deep = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            avg_deep['깊은수면비율'] = avg_deep['깊은수면비율'].round(1)
            fig8 = px.line(avg_deep, x='운동빈도', y='깊은수면비율', markers=True, text='깊은수면비율',
                           labels={'운동빈도': '주당 운동 횟수(회)', '깊은수면비율': '깊은 수면 비율 (%)'})
            fig8.update_traces(textposition='top center', line_color='#10b981', marker=dict(size=10))
            st.plotly_chart(fig8, use_container_width=True)
