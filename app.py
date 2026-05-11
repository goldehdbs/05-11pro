import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 기본 설정
# ==========================================
st.set_page_config(
    page_title="수면 & 라이프스타일 대시보드",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. 실제 데이터 로드 및 전처리
# ==========================================
@st.cache_data
def load_data():
    # 사용자가 업로드한 실제 CSV 파일 로드
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    
    # 영문 카테고리를 한글로 변환 (UI 가독성 향상)
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
    
    # 컬럼명을 한글로 변경하여 코딩 및 시각화 편의성 증대
    df = df.rename(columns={
        'Occupation': '직업',
        'Sleep Duration': '수면시간',
        'Quality of Sleep': '수면의질',
        'Daily Steps': '일일걸음수',
        'Stress Level': '스트레스지수',
        'BMI Category': 'BMI분류',
        'Sleep Disorder': '수면장애',
        'Age': '나이',
        'Gender': '성별'
    })
    
    return df

df = load_data()

# ==========================================
# 3. 사이드바 (데이터 필터)
# ==========================================
st.sidebar.title("설정 및 필터")
st.sidebar.markdown("Kaggle `Sleep Health and Lifestyle Dataset` 분석 대시보드입니다.")

st.sidebar.markdown("---")
st.sidebar.subheader("데이터 필터링")

# 직업 필터
selected_occ = st.sidebar.multiselect(
    "직업군 선택", 
    options=df['직업'].unique(), 
    default=df['직업'].unique()
)

# 성별 필터
selected_gender = st.sidebar.multiselect(
    "성별 선택",
    options=df['성별'].unique(),
    default=df['성별'].unique()
)

# 필터 적용
filtered_df = df[(df['직업'].isin(selected_occ)) & (df['성별'].isin(selected_gender))]

# ==========================================
# 4. 메인 화면 구성
# ==========================================
st.title("🌙 현대인 생활 습관 및 수면 질 분석")
st.markdown("수면 시간, 신체 활동량(걸음 수), 스트레스 및 체중이 건강에 미치는 영향을 탐색합니다.")

# 주요 지표 (KPI) 표시
col1, col2, col3, col4 = st.columns(4)
if not filtered_df.empty:
    col1.metric("총 응답자 수", f"{len(filtered_df)} 명")
    col2.metric("평균 수면 시간", f"{filtered_df['수면시간'].mean():.1f} 시간")
    col3.metric("평균 스트레스 지수", f"{filtered_df['스트레스지수'].mean():.1f} / 10")
    col4.metric("평균 일일 걸음 수", f"{int(filtered_df['일일걸음수'].mean()):,} 보")
else:
    st.warning("선택된 조건에 맞는 데이터가 없습니다.")

st.markdown("---")

# 레이아웃 나누기 (2x2 그리드)
row1_col1, row1_col2 = st.columns(2)

# [차트 1] 직업군별 평균 수면 시간
with row1_col1:
    st.subheader("📊 직업군별 평균 수면 시간")
    if not filtered_df.empty:
        occ_sleep = filtered_df.groupby('직업', as_index=False)['수면시간'].mean().sort_values('수면시간', ascending=True)
        fig1 = px.bar(occ_sleep, x='수면시간', y='직업', orientation='h', 
                      color='수면시간', color_continuous_scale='Blues',
                      text_auto='.1f', title="직업에 따른 평균 수면 시간 비교")
        fig1.update_layout(xaxis_range=[5, 9]) # 수면 시간 축 범위 조정
        st.plotly_chart(fig1, use_container_width=True)

# [차트 2] 걸음 수와 스트레스 지수의 상관관계
with row1_col2:
    st.subheader("🏃 일일 걸음 수 vs 스트레스 지수")
    if not filtered_df.empty:
        fig2 = px.scatter(filtered_df, x='일일걸음수', y='스트레스지수', color='직업',
                          trendline="ols", opacity=0.7,
                          title="걸음 수가 많을수록 스트레스가 감소하는가?")
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

# [차트 3] 수면 장애 여부와 수면의 질 (실제 데이터 반영)
with row2_col1:
    st.subheader("🛌 수면 장애 유무에 따른 수면의 질")
    if not filtered_df.empty:
        fig3 = px.box(filtered_df, x='수면장애', y='수면의질', color='수면장애',
                      color_discrete_sequence=['#38bdf8', '#ef4444', '#f59e0b'],
                      title="수면 장애(무호흡증, 불면증)와 수면의 질 분포")
        st.plotly_chart(fig3, use_container_width=True)

# [차트 4] BMI 분류별 수면 장애 발생 빈도
with row2_col2:
    st.subheader("⚖️ 체중(BMI)에 따른 수면 장애 비율")
    if not filtered_df.empty:
        bmi_disorder = filtered_df.groupby(['BMI분류', '수면장애']).size().reset_index(name='count')
        fig4 = px.bar(bmi_disorder, x='BMI분류', y='count', color='수면장애', barmode='group',
                      color_discrete_sequence=['#334155', '#ef4444', '#f59e0b'],
                      title="BMI 카테고리별 수면 장애 발생 현황")
        st.plotly_chart(fig4, use_container_width=True)

# ==========================================
# 5. 원본 데이터 확인 탭
# ==========================================
with st.expander("원본 데이터 테이블 보기"):
    st.dataframe(df, use_container_width=True)