import os
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="한눈에 보는 수면 건강 리포트",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. 데이터 로드 및 전처리 (안전성 강화 및 에러 수정)
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

# 예외 처리를 통해 에러 발생 시 앱이 죽지 않도록 방지
try:
    df1 = load_data_1()
    df2 = load_data_2()
except Exception as e:
    st.error(f"데이터를 읽는 중 내부 오류가 발생했습니다: {e}")
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

# ==========================================
# 3. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")
st.markdown("복잡한 산점도 대신 **막대/라인 그래프**를 사용하여 주요 수치를 직관적으로 비교합니다.")

# CSV 파일이 둘 다 없을 경우 경고 표시 후 정지
if df1.empty and df2.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다. `app.py` 파일이 있는 위치에 2개의 CSV 파일이 있는지 파일명을 다시 확인해 주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석 (생활 습관)", "💤 수면 효율 분석 (외부 요인)"])

# ------------------------------------------
# 탭 1: 생활 습관 (직업, 스트레스, 체중)
# ------------------------------------------
with tab1:
    if df1.empty:
        st.warning("`Sleep_health_and_lifestyle_dataset.csv` 파일이 없어 해당 탭을 표시할 수 없습니다.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
        c2.metric("평균 스트레스 지수", f"{df1['스트레스지수'].mean():.1f}점")
        c3.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("👨‍💻 직업별 평균 수면 시간")
            avg_sleep = df1.groupby('직업')['수면시간'].mean().reset_index().sort_values('수면시간')
            fig1 = px.bar(avg_sleep, x='수면시간', y='직업', orientation='h', color='수면시간', text_auto='.1f', color_continuous_scale='Blues')
            st.plotly_chart(fig1, use_container_width=True)

        with col_right:
            st.subheader("🔥 직업별 평균 스트레스")
            avg_stress = df1.groupby('직업')['스트레스지수'].mean().reset_index().sort_values('스트레스지수')
            fig2 = px.bar(avg_stress, x='스트레스지수', y='직업', orientation='h', color='스트레스지수', text_auto='.1f', color_continuous_scale='Reds')
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        
        col_low1, col_low2 = st.columns(2)
        with col_low1:
            st.subheader("⚖️ 체중분류별 수면 장애 현황")
            fig3 = px.bar(df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수'), x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True)
            st.plotly_chart(fig3, use_container_width=True)
            
        with col_low2:
            st.subheader("🌙 수면 장애별 수면의 질 점수")
            avg_qual = df1.groupby('수면장애')['수면의질'].mean().reset_index()
            fig4 = px.bar(avg_qual, x='수면장애', y='수면의질', color='수면장애', text_auto='.1f')
            st.plotly_chart(fig4, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율 (알코올, 운동, 수면단계)
# ------------------------------------------
with tab2:
    if df2.empty:
        st.warning("`Sleep_Efficiency.csv` 파일이 없어 해당 탭을 표시할 수 없습니다.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
        c2.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
        c3.metric("평균 자다 깨는 횟수", f"{df2['각성횟수'].mean():.1f}회")

        st.markdown("---")

        col_eff1, col_eff2 = st.columns(2)
        
        with col_eff1:
            st.subheader("🍺 알코올 섭취량별 수면 효율")
            # 라인 그래프로 변경
            avg_eff = df2.groupby('알코올')['수면효율'].mean().reset_index()
            avg_eff['수면효율'] = (avg_eff['수면효율'] * 100).round(1)
            
            fig5 = px.line(avg_eff, x='알코올', y='수면효율', markers=True, text='수면효율',
                           labels={'알코올': '음주량', '수면효율': '수면 효율 (%)'})
            fig5.update_traces(textposition="top center", line_color="#8b5cf6", marker=dict(size=10)) # 보라색 라인 테마
            fig5.update_yaxes(range=[avg_eff['수면효율'].min() - 5, avg_eff['수면효율'].max() + 5]) # Y축 범위 넉넉하게 설정
            st.plotly_chart(fig5, use_container_width=True)

        with col_eff2:
            st.subheader("🛌 평균 수면 단계 구성")
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            fig6 = px.pie(stages, values='비중', names='단계', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
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
            # 라인 그래프로 변경
            avg_deep = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            avg_deep['깊은수면비율'] = avg_deep['깊은수면비율'].round(1)
            
            fig8 = px.line(avg_deep, x='운동빈도', y='깊은수면비율', markers=True, text='깊은수면비율',
                           labels={'운동빈도': '주당 운동 횟수(회)', '깊은수면비율': '깊은 수면 비율 (%)'})
            fig8.update_traces(textposition="top center", line_color="#10b981", marker=dict(size=10)) # 초록색 라인 테마
            fig8.update_yaxes(range=[avg_deep['깊은수면비율'].min() - 5, avg_deep['깊은수면비율'].max() + 5]) # Y축 범위 설정
            st.plotly_chart(fig8, use_container_width=True)
