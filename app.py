import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. 페이지 기본 설정 및 디자인
# ==========================================
st.set_page_config(
    page_title="수면 건강 분석 대시보드",
    layout="wide"
)

# 고급스러운 미니멀리즘 UI를 위한 CSS 적용
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 색상 조정 */
    .main {
        background-color: #f8fafc;
    }
    
    /* 탭 디자인 세련되게 변경 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 2px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 16px;
        padding-bottom: 16px;
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #0f172a;
        border-bottom: 2px solid #0f172a;
    }
    
    /* 메트릭 카드(상단 수치 박스) 디자인 고급화 */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {
        font-weight: 700;
        color: #0f172a;
    }
    
    /* 버튼 디자인 */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        background-color: #0f172a;
        color: #ffffff;
        font-weight: 500;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #334155;
        color: #ffffff;
    }
    
    /* 컨테이너 및 헤더 여백 정리 */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 로드 및 전처리
# ==========================================
def categorize_bp(bp_str):
    try:
        sys, dia = map(int, str(bp_str).split('/'))
        if sys < 120 and dia < 80: return '정상혈압'
        elif 120 <= sys < 130 and dia < 80: return '주의혈압'
        elif 130 <= sys < 140 or 80 <= dia < 90: return '고혈압 전단계'
        else: return '고혈압'
    except: return '기타'

@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path): return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['혈압상태'] = df['Blood Pressure'].apply(categorize_bp)
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
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 
        'Age': '나이', 'Blood Pressure': '혈압원문', 'Daily Steps': '일일걸음수'
    })

@st.cache_data
def load_data_2():
    file_path = 'Sleep_Efficiency.csv'
    if not os.path.exists(file_path): return pd.DataFrame()
    df = pd.read_csv(file_path)
    df = df.fillna(0)
    df['Smoking status'] = df['Smoking status'].replace({'Yes': '흡연', 'No': '비흡연'})
    return df.rename(columns={
        'Sleep efficiency': '수면효율', 'REM sleep percentage': 'REM비율', 
        'Deep sleep percentage': '깊은수면비율', 'Light sleep percentage': '얕은수면비율', 
        'Awakenings': '각성횟수', 'Alcohol consumption': '알코올', 'Exercise frequency': '운동빈도',
        'Smoking status': '흡연여부', 'Age': '나이'
    })

try:
    df1_raw = load_data_1()
    df2_raw = load_data_2()
except:
    df1_raw = pd.DataFrame()
    df2_raw = pd.DataFrame()

# ==========================================
# 3. 사이드바 필터
# ==========================================
st.sidebar.title("데이터 필터")

if not df1_raw.empty and not df2_raw.empty:
    min_age = int(min(df1_raw['나이'].min(), df2_raw['나이'].min()))
    max_age = int(max(df1_raw['나이'].max(), df2_raw['나이'].max()))
    age_range = st.sidebar.slider("연령대 설정", min_age, max_age, (min_age, max_age))
    all_occupations = sorted(df1_raw['직업'].unique().tolist())
    selected_occ = st.sidebar.multiselect("직업군 선택", all_occupations, default=all_occupations)

    df1 = df1_raw[(df1_raw['나이'] >= age_range[0]) & (df1_raw['나이'] <= age_range[1]) & (df1_raw['직업'].isin(selected_occ))].copy()
    df2 = df2_raw[(df2_raw['나이'] >= age_range[0]) & (df2_raw['나이'] <= age_range[1])].copy()
else:
    df1, df2 = df1_raw, df2_raw

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("수면 건강 통합 대시보드")
st.markdown("수면 데이터를 다각도로 분석하여 생활 습관과 수면의 질 사이의 상관관계를 도출합니다.")

if df1.empty and df2.empty:
    st.error("데이터를 불러오지 못했습니다. CSV 파일 위치를 확인해 주세요.")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "라이프스타일 분석", 
    "수면 효율 분석", 
    "심혈관 건강 분석",
    "수면 점수 진단",
    "최적 수면 골든타임"
])

# ------------------------------------------
# 탭 1: 라이프스타일 분석
# ------------------------------------------
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택된 모집단", f"{len(df1)}명", f"전체 {len(df1_raw)}명 대비")
    c2.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
    c3.metric("평균 스트레스 지수", f"{df1['스트레스지수'].mean():.1f}점")
    c4.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
    
    st.markdown("---")
    st.subheader("맞춤형 수면시간 및 수면의 질 분석")
    col_sel1, col_sel2 = st.columns([1, 3])
    with col_sel1:
        target_category = st.radio("분석 기준 선택", options=['직업', 'BMI분류', '스트레스지수', '혈압원문'], key='tab1_radio')
    with col_sel2:
        avg_dynamic = df1.groupby(target_category)[['수면시간', '수면의질']].mean().reset_index().sort_values('수면시간')
        # 고급스러운 단색 블루 스케일 적용
        fig_dyn = px.bar(avg_dynamic, x='수면시간', y=target_category, orientation='h', color='수면의질', text_auto='.1f', color_continuous_scale='Blues', title=f"[{target_category}]별 현황")
        fig_dyn.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_dyn, use_container_width=True)

    st.subheader("체중(BMI) 분류별 수면 장애 현황")
    bmi_data = df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
    # 차분하고 모던한 컬러맵 적용
    fig3 = px.bar(bmi_data, x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True, color_discrete_map={'없음': '#94a3b8', '불면증': '#fb923c', '수면 무호흡증': '#3b82f6'})
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율 분석
# ------------------------------------------
with tab2:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("선택된 모집단", f"{len(df2)}명", f"전체 {len(df2_raw)}명 대비")
    c2.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
    c3.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
    c4.metric("평균 각성 횟수", f"{df2['각성횟수'].mean():.1f}회")

    st.markdown("---")
    col_eff1, col_eff2 = st.columns([1, 2])
    with col_eff1:
        st.subheader("수면 단계 구성")
        stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
        # 프로페셔널한 색상 배열
        fig6 = px.pie(stages, values='비중', names='단계', hole=0.5, color_discrete_sequence=['#1e293b', '#64748b', '#cbd5e1'])
        fig6.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig6, use_container_width=True)
        
    with col_eff2:
        st.subheader("외부 요인별 영향도 분석")
        factor_choice = st.selectbox("분석 요인 선택", ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'])
        if '알코올' in factor_choice:
            avg_f = df2.groupby('알코올')['수면효율'].mean().reset_index()
            fig_f = px.line(avg_f, x='알코올', y='수면효율', markers=True, title="음주와 수면효율")
            fig_f.update_traces(line_color='#0f172a', marker=dict(size=8, color='#0f172a'))
        elif '운동' in factor_choice:
            avg_f = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
            fig_f = px.line(avg_f, x='운동빈도', y='깊은수면비율', markers=True, title="운동과 깊은 수면")
            fig_f.update_traces(line_color='#2563eb', marker=dict(size=8, color='#2563eb'))
        else:
            avg_f = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
            fig_f = px.bar(avg_f, x='흡연여부', y='각성횟수', color='흡연여부', text_auto='.1f', title="흡연과 각성 횟수", color_discrete_map={'비흡연': '#64748b', '흡연': '#ef4444'})
        fig_f.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_f, use_container_width=True)

# ------------------------------------------
# 탭 3: 심혈관 건강 분석
# ------------------------------------------
with tab3:
    st.header("수면의 질과 심혈관 건강(고혈압) 상관관계")
    st.markdown("수면 점수가 낮을수록 고혈압 위험이 어떻게 변하는지 분석합니다.")
    
    bp_data = df1.groupby('수면의질')['혈압상태'].value_counts(normalize=True).unstack().fillna(0) * 100
    
    if '고혈압' in bp_data.columns:
        hp_rate = bp_data[['고혈압']].reset_index()
        
        c_hp1, c_hp2 = st.columns([2, 1])
        with c_hp1:
            fig_hp = px.line(hp_rate, x='수면의질', y='고혈압', markers=True, title="수면의 질 점수에 따른 고혈압군 비율(%)")
            fig_hp.update_traces(line_color='#dc2626', marker=dict(size=8, color='#dc2626'))
            fig_hp.update_layout(xaxis_title="수면의 질 점수 (1-10점)", yaxis_title="고혈압군 비율 (%)", plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_hp, use_container_width=True)
            
        with c_hp2:
            st.markdown("#### 분석 인사이트")
            st.write("데이터 분석 결과, 수면의 질 점수가 낮아질수록 고혈압군에 속하는 인원의 비중이 증가하는 경향을 보입니다.")
            st.write("수면 부족은 자율신경계 불균형을 초래하여 혈압 상승의 직접적인 원인이 될 수 있음을 시사합니다.")
            
        st.markdown("---")
        st.subheader("스트레스 및 BMI와 혈압의 복합 관계")
        col_hp_sub1, col_hp_sub2 = st.columns(2)
        
        custom_bp_colors = {'정상혈압':'#94a3b8', '주의혈압':'#64748b', '고혈압 전단계':'#334155', '고혈압':'#0f172a'}
        with col_hp_sub1:
            fig_stress_bp = px.histogram(df1, x="스트레스지수", color="혈압상태", barmode="group", title="스트레스 지수별 혈압 상태 분포", color_discrete_map=custom_bp_colors)
            fig_stress_bp.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_stress_bp, use_container_width=True)
            
        with col_hp_sub2:
            fig_bmi_bp = px.histogram(df1, x="BMI분류", color="혈압상태", barmode="group", title="BMI 분류별 혈압 상태 분포", color_discrete_map=custom_bp_colors)
            fig_bmi_bp.update_layout(plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig_bmi_bp, use_container_width=True)
    else:
        st.warning("현재 선택된 데이터 범위 내에 고혈압 데이터가 부족합니다.")

# ------------------------------------------
# 탭 4: 나의 수면 점수 진단
# ------------------------------------------
with tab4:
    st.header("수면 건강 자가진단 서비스")
    st.markdown("신체 정보 및 생활 습관을 입력하여 데이터 기반 수면 점수를 산출합니다.")
    
    with st.container(border=True):
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            u_height = st.number_input("키 (cm)", 100.0, 250.0, 170.0)
            u_weight = st.number_input("몸무게 (kg)", 30.0, 200.0, 65.0)
            user_smoke = st.radio("흡연 여부", ["비흡연", "흡연"], horizontal=True)
        with col_in2:
            user_alc = st.number_input("일주일 평균 음주 횟수 (회)", 0, 7, 0)
            user_ex = st.slider("일주일 평균 운동 횟수 (회)", 0, 7, 3)
            user_sleep = st.number_input("일일 평균 수면 시간 (시간)", 0.0, 12.0, 7.0, step=0.5)

        bmi_val = u_weight / ((u_height / 100) ** 2)
        bmi_status = "정상" if bmi_val < 18.5 else "정상" if bmi_val < 25 else "과체중" if bmi_val < 30 else "비만"
        
        st.markdown(f"**산출된 BMI:** {bmi_val:.1f} ({bmi_status})")

        if st.button("수면 점수 분석 실행"):
            base_score = 90
            if bmi_status == "과체중": base_score -= 7
            elif bmi_status == "비만": base_score -= 18
            if user_smoke == "흡연": base_score -= 12
            base_score -= (user_alc * 4)
            base_score += (user_ex * 5)
            if 7 <= user_sleep <= 8.5: base_score += 10
            elif user_sleep < 6 or user_sleep > 10: base_score -= 10
            
            final_score = max(0, min(100, base_score))
            st.markdown("---")
            st.subheader(f"예상 수면 점수: {final_score}점 / 100점")
            
            if final_score >= 85:
                st.success("우수: 숙면 가능성이 매우 높은 이상적인 생활 습관을 유지하고 있습니다.")
            elif final_score >= 65:
                st.info("보통: 평균적인 수면 건강 상태입니다. 운동량 증가 등 일부 개선이 필요할 수 있습니다.")
            else:
                st.warning("주의: 수면 효율 저하 위험이 있습니다. 생활 습관 교정을 권장합니다.")

with st.expander("데이터 원본 조회"):
    st.dataframe(df1.head())

# ------------------------------------------
# 탭 5: 최적 수면 골든타임
# ------------------------------------------
with tab5:
    st.header("데이터 기반 수면 골든타임 계산기")
    st.markdown("기상 시간과 현재 신체 상태를 입력하여 최적의 취침 시간을 확인하세요.")

    with st.container(border=True):
        col_calc1, col_calc2 = st.columns(2)
        
        with col_calc1:
            st.subheader("일정 및 상태 입력")
            target_wakeup = st.time_input("내일 기상 목표 시간", value=pd.to_datetime("07:00").time())
            user_quality = st.slider("최근 평균 수면 만족도 (1-10점)", 1, 10, 7)
            today_steps = st.number_input("오늘 총 활동량 (걸음 수)", 0, 30000, 6000)
            
            c_col1, c_col2 = st.columns(2)
            with c_col1:
                has_coffee = st.checkbox("오늘 카페인 섭취 여부")
            with c_col2:
                is_smoking = st.checkbox("오늘 흡연(니코틴) 여부")

        with col_calc2:
            st.subheader("맞춤형 분석 결과")
            
            base_sleep_hr = df1[df1['수면의질'] >= 8]['수면시간'].mean() if not df1.empty else 7.5
            adjustment = 0.0
            
            if user_quality <= 4:
                adjustment += 1.0
                st.write("- 수면 만족도가 낮아 1시간의 보충 수면을 권장합니다.")
            elif user_quality <= 6:
                adjustment += 0.5
                st.write("- 수면 개선을 위해 30분 추가 수면을 권장합니다.")
            
            if today_steps >= 10000:
                adjustment += 0.5
                st.write("- 높은 신체 활동량으로 인해 회복 수면 시간 30분이 추가되었습니다.")
            
            if has_coffee:
                adjustment += 0.3
                st.write("- 카페인 섭취로 인한 수면 지연 패널티가 반영되었습니다 (+20분).")
            
            if is_smoking:
                adjustment += 0.4
                st.write("- 니코틴 각성 효과로 인한 수면 지연 패널티가 반영되었습니다 (+25분).")

            recommended_duration = base_sleep_hr + adjustment

        st.divider()
        
        from datetime import datetime, timedelta
        now = datetime.now()
        wakeup_dt = datetime.combine(now.date() + timedelta(days=1), target_wakeup)
        bedtime_dt = wakeup_dt - timedelta(hours=recommended_duration)
        
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.metric("권장 총 수면 시간", f"{recommended_duration:.1f}시간")
        
        with res_col2:
            st.subheader(f"최적 취침 시각: {bedtime_dt.strftime('%H시 %M분')}")
            
            if is_smoking or has_coffee:
                st.write("**전문가 팁:** 니코틴과 카페인은 깊은 수면 비중을 감소시킵니다. 평소보다 어두운 환경을 조성하는 것이 좋습니다.")
            
            if bedtime_dt.hour >= 1 and bedtime_dt.hour <= 4:
                st.write("**주의:** 데이터 분석상 새벽 1시 이후 취침은 수면 장애 위험률과 연관성이 높습니다.")
