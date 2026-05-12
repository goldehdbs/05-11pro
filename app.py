import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="수면 & 라이프스타일 종합 대시보드",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_lifestyle_data():
    """데이터셋 1: Sleep Health and Lifestyle"""
    try:
        df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    except Exception as e:
        st.error(f"첫 번째 파일 로드 에러: {e}")
        return pd.DataFrame()

    # 한글화 매핑
    bmi_map = {'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'}
    df['BMI Category'] = df['BMI Category'].map(bmi_map).fillna(df['BMI Category'])
    
    disorder_map = {'None': '없음', 'Sleep Apnea': '수면 무호흡증', 'Insomnia': '불면증'}
    df['Sleep Disorder'] = df['Sleep Disorder'].map(disorder_map).fillna('없음')
    
    occ_map = {
        'Software Engineer': '소프트웨어 엔지니어', 'Doctor': '의사', 
        'Sales Representative': '영업 대표', 'Teacher': '교사', 
        'Nurse': '간호사', 'Engineer': '엔지니어', 
        'Accountant': '회계사', 'Scientist': '과학자', 
        'Lawyer': '변호사', 'Salesperson': '영업 사원', 'Manager': '관리자'
    }
    df['Occupation'] = df['Occupation'].map(occ_map).fillna(df['Occupation'])
    
    # 컬럼명 변경
    df = df.rename(columns={
        'Occupation': '직업', 'Sleep Duration': '수면시간', 'Quality of Sleep': '수면의질',
        'Daily Steps': '일일걸음수', 'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류',
        'Sleep Disorder': '수면장애', 'Age': '나이', 'Gender': '성별'
    })
    return df

@st.cache_data
def load_efficiency_data():
    """데이터셋 2: Sleep Efficiency"""
    try:
        # 요청하신 파일명 정확히 반영
        df = pd.read_csv('Sleep_Efficiency.csv')
    except Exception as e:
        st.error(f"두 번째 파일 로드 에러: {e}")
        return pd.DataFrame()
    
    # 결측치 처리 (0으로 대체)
    df.fillna({'Caffeine consumption': 0, 'Alcohol consumption': 0, 'Exercise frequency': 0}, inplace=True)
    
    # 한글화
    df['Smoking status'] = df['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    df['Gender'] = df['Gender'].replace({'Male': '남성', 'Female': '여성'})
    
    # 컬럼명 변경
    df = df.rename(columns={
        'Age': '나이', 'Gender': '성별', 'Sleep duration': '수면시간', 
        'Sleep efficiency': '수면효율', 'REM sleep percentage': '렘수면_비율',
        'Deep sleep percentage': '깊은수면_비율', 'Light sleep percentage': '얕은수면_비율',
        'Awakenings': '각성횟수', 'Caffeine consumption': '카페인소비량',
        'Alcohol consumption': '알코올소비량', 'Smoking status': '흡연여부',
        'Exercise frequency': '운동빈도'
    })
    return df

# 데이터 불러오기
df_life = load_lifestyle_data()
df_eff = load_efficiency_data()

# ==========================================
# 3. 사이드바 구성
# ==========================================
st.sidebar.title("🌙 수면 분석 대시보드")
st.sidebar.markdown("두 가지 데이터셋을 바탕으로 현대인의 수면 건강을 다각도에서 분석합니다.")

st.sidebar.markdown("---")
st.sidebar.info(
    "**사용된 파일:**\n\n"
    "1. `Sleep_health_and_lifestyle_dataset.csv`\n"
    "2. `Sleep_Efficiency.csv`"
)

# ==========================================
# 4. 메인 화면 구성 (탭 활용)
# ==========================================
st.title("🌙 현대인 수면 건강 및 효율 심층 분석")

# 탭 생성
tab1, tab2 = st.tabs(["📊 파트 1: 생활 습관 및 수면 장애", "🛌 파트 2: 수면 효율 및 외부 요인"])

# ------------------------------------------
# 탭 1: 기존 데이터 (Lifestyle)
# ------------------------------------------
with tab1:
    st.markdown("### 직업, 스트레스, 체중이 수면의 질에 미치는 영향")
    
    if df_life.empty:
        st.warning("`Sleep_health_and_lifestyle_dataset.csv` 파일 데이터를 불러올 수 없습니다. 파일 위치를 확인해주세요.")
    else:
        # KPI
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("총 응답자 수", f"{len(df_life)} 명")
        c2.metric("평균 수면 시간", f"{df_life['수면시간'].mean():.1f} 시간")
        c3.metric("평균 스트레스 지수", f"{df_life['스트레스지수'].mean():.1f} / 10")
        c4.metric("평균 일일 걸음 수", f"{int(df_life['일일걸음수'].mean()):,} 보")
        
        st.markdown("---")
        
        r1_c1, r1_c2 = st.columns(2)
        with r1_c1:
            occ_sleep = df_life.groupby('직업', as_index=False)['수면시간'].mean().sort_values('수면시간', ascending=True)
            fig1 = px.bar(occ_sleep, x='수면시간', y='직업', orientation='h', color='수면시간', text_auto='.1f', title="직업군별 평균 수면 시간")
            fig1.update_layout(xaxis_range=[5, 9])
            st.plotly_chart(fig1, use_container_width=True)
            
        with r1_c2:
            fig2 = px.scatter(df_life, x='일일걸음수', y='스트레스지수', color='직업', opacity=0.7, title="일일 걸음 수와 스트레스의 상관관계")
            st.plotly_chart(fig2, use_container_width=True)
            
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            fig3 = px.box(df_life, x='수면장애', y='수면의질', color='수면장애', title="수면 장애 유무에 따른 수면의 질")
            st.plotly_chart(fig3, use_container_width=True)
            
        with r2_c2:
            bmi_disorder = df_life.groupby(['BMI분류', '수면장애']).size().reset_index(name='count')
            fig4 = px.bar(bmi_disorder, x='BMI분류', y='count', color='수면장애', barmode='group', title="체중(BMI) 분류별 수면 장애 발생 현황")
            st.plotly_chart(fig4, use_container_width=True)

# ------------------------------------------
# 탭 2: 신규 데이터 (Sleep Efficiency)
# ------------------------------------------
with tab2:
    st.markdown("### 알코올, 카페인, 운동 등 수면 구조(REM/Deep)에 미치는 요인")
    
    if df_eff.empty:
        st.warning("`Sleep_Efficiency.csv` 파일 데이터를 불러올 수 없습니다. 파일 위치를 확인해주세요.")
    else:
        # KPI
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("수면 효율 평균", f"{df_eff['수면효율'].mean() * 100:.1f} %")
        c2.metric("깊은 수면(Deep Sleep) 평균", f"{df_eff['깊은수면_비율'].mean():.1f} %")
        c3.metric("평균 중간 각성 횟수", f"{df_eff['각성횟수'].mean():.1f} 회")
        c4.metric("주당 평균 운동 빈도", f"{df_eff['운동빈도'].mean():.1f} 회")
        
        st.markdown("---")
        
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            # 알코올 소비량과 수면 효율
            fig5 = px.box(df_eff, x='알코올소비량', y='수면효율', color='알코올소비량', 
                          title="알코올 섭취량과 수면 효율의 관계",
                          labels={'알코올소비량': '알코올 섭취량 (단위)'})
            st.plotly_chart(fig5, use_container_width=True)
            
        with r3_c2:
            # 수면 단계 비율 (도넛 차트)
            avg_rem = df_eff['렘수면_비율'].mean()
            avg_deep = df_eff['깊은수면_비율'].mean()
            avg_light = df_eff['얕은수면_비율'].mean()
            
            fig6 = go.Figure(data=[go.Pie(labels=['REM 수면', '깊은 수면(Deep)', '얕은 수면(Light)'], 
                                          values=[avg_rem, avg_deep, avg_light], hole=.4)])
            fig6.update_layout(title_text="전체 응답자 평균 수면 단계 비율")
            st.plotly_chart(fig6, use_container_width=True)

        r4_c1, r4_c2 = st.columns(2)
        with r4_c1:
            # 흡연 여부와 중간 깸(각성) 횟수
            fig7 = px.histogram(df_eff, x='각성횟수', color='흡연여부', barmode='group',
                                title="흡연 여부에 따른 수면 중 각성(깸) 횟수 분포")
            st.plotly_chart(fig7, use_container_width=True)
            
        with r4_c2:
            # 운동 빈도와 깊은 수면 비율
            fig8 = px.scatter(df_eff, x='운동빈도', y='깊은수면_비율', 
                              color='수면효율', color_continuous_scale='Viridis',
                              title="주당 운동 빈도가 깊은 수면(Deep Sleep)에 미치는 영향")
            st.plotly_chart(fig8, use_container_width=True)

# ==========================================
# 5. 원본 데이터 확인 (하단 토글)
# ==========================================
st.markdown("---")
with st.expander("📁 원본 데이터 테이블 보기"):
    st.markdown("**1. Lifestyle 데이터셋 (`Sleep_health_and_lifestyle_dataset.csv`)**")
    if not df_life.empty:
        st.dataframe(df_life, use_container_width=True)
    
    st.markdown("**2. Sleep Efficiency 데이터셋 (`Sleep_Efficiency.csv`)**")
    if not df_eff.empty:
        st.dataframe(df_eff, use_container_width=True)
