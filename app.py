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
def categorize_bp(bp_str):
    try:
        sys, dia = map(int, str(bp_str).split('/'))
        if sys < 120 and dia < 80:
            return '정상혈압'
        elif 120 <= sys < 130 and dia < 80:
            return '주의혈압'
        elif 130 <= sys < 140 or 80 <= dia < 90:
            return '고혈압 전단계'
        else:
            return '고혈압'
    except:
        return '기타'

@st.cache_data
def load_data_1():
    file_path = 'Sleep_health_and_lifestyle_dataset.csv'
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    df['Blood Pressure'] = df['Blood Pressure'].apply(categorize_bp)
    df['BMI Category'] = df['BMI Category'].replace({'Normal Weight': '정상', 'Normal': '정상', 'Overweight': '과체중', 'Obese': '비만'})
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
        'Stress Level': '스트레스지수', 'BMI Category': 'BMI분류', 'Sleep Disorder': '수면장애', 
        'Age': '나이', 'Blood Pressure': '혈압'
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
        'Smoking status': '흡연여부', 'Age': '나이'
    })

try:
    df1_raw = load_data_1()
    df2_raw = load_data_2()
except Exception as e:
    st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
    df1_raw = pd.DataFrame()
    df2_raw = pd.DataFrame()

# ==========================================
# 3. 사이드바 동적 필터
# ==========================================
st.sidebar.title("🎮 동적 필터 조절")

if not df1_raw.empty and not df2_raw.empty:
    min_age = int(min(df1_raw['나이'].min(), df2_raw['나이'].min()))
    max_age = int(max(df1_raw['나이'].max(), df2_raw['나이'].max()))
    age_range = st.sidebar.slider("분석 연령대 설정", min_age, max_age, (min_age, max_age))

    all_occupations = sorted(df1_raw['직업'].unique().tolist())
    selected_occ = st.sidebar.multiselect("분석 직업군 선택", all_occupations, default=all_occupations)

    df1 = df1_raw[(df1_raw['나이'] >= age_range[0]) & (df1_raw['나이'] <= age_range[1]) & (df1_raw['직업'].isin(selected_occ))].copy()
    df2 = df2_raw[(df2_raw['나이'] >= age_range[0]) & (df2_raw['나이'] <= age_range[1])].copy()
else:
    df1 = df1_raw
    df2 = df2_raw

# ==========================================
# 4. 메인 UI 구성
# ==========================================
st.title("📊 수면 건강 핵심 데이터 대시보드")

if df1.empty and df2.empty:
    st.error("⚠️ 데이터를 불러오지 못했습니다. CSV 파일 위치를 확인해 주세요.")
    st.stop()

tab1, tab2 = st.tabs(["📉 라이프스타일 분석 (생활 습관)", "💤 수면 효율 분석 (외부 요인)"])

# ------------------------------------------
# 탭 1: 생활 습관
# ------------------------------------------
with tab1:
    if df1.empty:
        st.warning("조건에 맞는 데이터가 없습니다. 좌측 필터를 조절해 주세요.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("선택된 모집단", f"{len(df1)}명", f"전체 {len(df1_raw)}명 기준", delta_color="off")
        c2.metric("평균 수면 시간", f"{df1['수면시간'].mean():.1f}시간")
        c3.metric("평균 스트레스 지수", f"{df1['스트레스지수'].mean():.1f}점")
        c4.metric("평균 수면의 질", f"{df1['수면의질'].mean():.1f}점")
        
        st.markdown("---")
        
        st.subheader("🎯 맞춤형 수면시간 & 수면의 질 분석")
        
        col_sel1, col_sel2 = st.columns([1, 3])
        with col_sel1:
            target_category = st.radio(
                "어떤 기준으로 분석할까요?",
                options=['직업', 'BMI분류', '스트레스지수', '혈압'],
                index=0
            )
        
        with col_sel2:
            avg_dynamic = df1.groupby(target_category)[['수면시간', '수면의질']].mean().reset_index()
            
            if target_category == '스트레스지수':
                avg_dynamic = avg_dynamic.sort_values(target_category, ascending=False)
                avg_dynamic[target_category] = avg_dynamic[target_category].astype(str) + "점"
            else:
                avg_dynamic = avg_dynamic.sort_values('수면시간', ascending=True)

            fig_dyn = px.bar(avg_dynamic, x='수면시간', y=target_category, orientation='h',
                             color='수면의질', text_auto='.1f', color_continuous_scale='Turbo',
                             title=f"[{target_category}]에 따른 평균 수면 시간 (색상: 수면의 질)")
            fig_dyn.update_layout(xaxis_title="평균 수면 시간 (h)", yaxis_title="")
            st.plotly_chart(fig_dyn, use_container_width=True)

        st.markdown("---")
        
        st.subheader("⚖️ 체중(BMI) 분류별 수면 장애 현황")
        bmi_data = df1.groupby(['BMI분류', '수면장애']).size().reset_index(name='인원수')
        
        fig3 = px.bar(bmi_data, x='BMI분류', y='인원수', color='수면장애', barmode='group', text_auto=True,
                      color_discrete_map={'없음': '#22c55e', '불면증': '#eab308', '수면 무호흡증': '#ef4444'})
        st.plotly_chart(fig3, use_container_width=True)

# ------------------------------------------
# 탭 2: 수면 효율
# ------------------------------------------
with tab2:
    if df2.empty:
        st.warning("해당 조건의 데이터가 없습니다.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("선택된 모집단", f"{len(df2)}명", f"전체 {len(df2_raw)}명 기준", delta_color="off")
        c2.metric("평균 수면 효율", f"{df2['수면효율'].mean()*100:.1f}%")
        c3.metric("깊은 수면 비중", f"{df2['깊은수면비율'].mean():.1f}%")
        c4.metric("평균 각성 횟수", f"{df2['각성횟수'].mean():.1f}회")

        st.markdown("---")

        col_eff1, col_eff2 = st.columns([1, 2])
        
        with col_eff1:
            st.subheader("🛌 평균 수면 단계 구성")
            stages = pd.DataFrame({'단계': ['깊은 수면', 'REM 수면', '얕은 수면'], '비중': [df2['깊은수면비율'].mean(), df2['REM비율'].mean(), df2['얕은수면비율'].mean()]})
            
            fig6 = px.pie(stages, values='비중', names='단계', hole=0.4, 
                          color_discrete_sequence=['#3b82f6', '#8b5cf6', '#f59e0b'])
            fig6.update_traces(textinfo='percent+label', textfont_size=14)
            st.plotly_chart(fig6, use_container_width=True)
            
        with col_eff2:
            st.subheader("⚡ 외부 요인별 수면 지표 분석")
            
            # [수정됨] 3가지 옵션을 모두 통합한 셀렉트 박스
            factor_choice = st.selectbox(
                "분석할 외부 요인을 선택하세요:", 
                ['알코올 섭취량 (수면 효율)', '운동 빈도 (깊은 수면 비중)', '흡연 여부 (각성 횟수)'], 
                index=0
            )
            
            # 1. 알코올 선택 시
            if '알코올' in factor_choice:
                avg_factor = df2.groupby('알코올')['수면효율'].mean().reset_index()
                avg_factor['수면효율'] = (avg_factor['수면효율'] * 100).round(1)
                
                fig_factor = px.line(avg_factor, x='알코올', y='수면효율', markers=True, text='수면효율')
                fig_factor.update_traces(textposition='top center', line_color='#ec4899', marker=dict(size=12, color='#ec4899'), textfont_size=14)
                fig_factor.update_layout(yaxis_title="수면 효율 (%)", xaxis_title="알코올 (잔/회)")
                
                # Y축 여백 설정
                min_y = avg_factor['수면효율'].min() - 3
                max_y = avg_factor['수면효율'].max() + 3
                fig_factor.update_layout(yaxis=dict(range=[min_y, max_y]))

            # 2. 운동빈도 선택 시
            elif '운동' in factor_choice:
                avg_factor = df2.groupby('운동빈도')['깊은수면비율'].mean().reset_index()
                avg_factor['깊은수면비율'] = avg_factor['깊은수면비율'].round(1)
                
                fig_factor = px.line(avg_factor, x='운동빈도', y='깊은수면비율', markers=True, text='깊은수면비율')
                fig_factor.update_traces(textposition='top center', line_color='#10b981', marker=dict(size=12, color='#10b981'), textfont_size=14)
                fig_factor.update_layout(yaxis_title="깊은 수면 비중 (%)", xaxis_title="운동빈도 (회/주)")
                
                min_y = avg_factor['깊은수면비율'].min() - 3
                max_y = avg_factor['깊은수면비율'].max() + 3
                fig_factor.update_layout(yaxis=dict(range=[min_y, max_y]))

            # 3. 흡연여부 선택 시
            else:
                avg_factor = df2.groupby('흡연여부')['각성횟수'].mean().reset_index()
                avg_factor['각성횟수'] = avg_factor['각성횟수'].round(1)
                
                # 흡연/비흡연은 텍스트 형태이므로 보기 편한 막대(Bar) 그래프 사용
                fig_factor = px.bar(avg_factor, x='흡연여부', y='각성횟수', text_auto='.1f',
                                    color='흡연여부', color_discrete_map={'비흡연': '#38bdf8', '흡연': '#ef4444'})
                fig_factor.update_traces(textfont_size=16)
                fig_factor.update_layout(yaxis_title="평균 각성 횟수 (회)", xaxis_title="흡연여부 (흡연/비흡연)")

            st.plotly_chart(fig_factor, use_container_width=True)
