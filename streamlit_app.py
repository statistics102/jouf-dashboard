import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# إعدادات الصفحة
st.set_page_config(
    page_title="الملخص التنفيذي - جامعة الجوف",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحسين دعم اللغة العربية في الواجهة
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    h1 { color: #0068c9; text-align: center; font-family: 'Arial', sans-serif; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# عنوان الصفحة
st.title("الملخص التنفيذي لمشروع جامعة الجوف ")

# دالة تحميل البيانات
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("DATA.xlsx")
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return None

df = load_data()

if df is not None:
    # حساب الإحصائيات العامة (KPIs)
    total_students = len(df)
    total_colleges = df['الكلية'].nunique()
    total_instructors = df['اسم المحاضر'].nunique()
    total_courses = df['اسم المقرر'].nunique()

    # عرض البطاقات العلوية
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="إجمالي عدد الطلبة", value=f"{total_students:,}")
    col2.metric(label="إجمالي عدد الكليات", value=f"{total_colleges}")
    col3.metric(label="إجمالي عدد المحاضرين", value=f"{total_instructors}")
    col4.metric(label="إجمالي عدد المقررات", value=f"{total_courses}")

    st.markdown("---")

    # --- الرسوم البيانية ---
    
    # إعداد شكل الرسم البياني المتداخل (Stacked Bar) كما طلبت سابقاً
    # نقوم بإنشاء قائمة بالمتغيرات التي نريد عرضها
    vars_to_show = ['الدرجة', 'الكلية', 'اسم المحاضر', 'اسم المقرر']
    
    # سنقوم بإنشاء رسم بياني واحد يجمع المتغيرات لتجنب الازدحام الشديد
    # حيث يمثل المحور X أسماء المتغيرات (الدرجة، الكلية..)
    # والمجموعات داخل كل عمود هي الفروع (بكالوريوس/دبلوم، أسماء الكليات، إلخ)
    
    # تحويل البيانات لتناسب الرسم المتداخل
    chart_data = pd.DataFrame()
    
    for var in vars_to_show:
        temp = df[var].value_counts().reset_index()
        temp.columns = ['Branch', 'Count']
        temp['Variable'] = var
        chart_data = pd.concat([chart_data, temp])

    # رسم الأعمدة المتداخلة
    fig = go.Figure()

    # إضافة التتبعات (Traces) لكل فرع
    # لتجنب تداخل النصوص في المحاضر والمقرر، سنقوم بإخفاء النص داخل العمود إذا كانت الفروع كثيرة
    branches = chart_data['Branch'].unique()
    
    # نستخدم الألوان بناءً على المتغير لتمييز المجموعات
    colors = {
        'الدرجة': ['#FFD700', '#87CEEB'], # ألوان افتراضية للبكالوريوس والدبلوم
        'الكلية': '#636EFA',
        'اسم المحاضر': '#EF553B',
        'اسم المقرر': '#00CC96'
    }

    # طريقة مبسطة للرسم: عرض كل متغير كعمود واحد متداخل
    # سنستخدم plotly express للتسهيل والجمالية
    fig = go.Figure()
    
    # سنقوم برسم كل متغير بشكل منفصل في شبكة (Grid) ليكون الشكل أوضح وأكثر احترافية للوحة العرض
    # لأن دمج كل شيء في عمود واحد سيجعل النسب غير منطقية (مجموع الكليات لا يساوي مجموع الدرجات)
    
    # المتغير 1: الدرجة (Pie Chart)
    fig1_data = df['الدرجة'].value_counts()
    fig1 = go.Figure(data=[go.Pie(labels=fig1_data.index, values=fig1_data.values, hole=.3, name="الدرجة")])
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    fig1.update_layout(title_text="توزيع الطلبة حسب الدرجة", height=400)

    # المتغير 2: الكلية (Bar Chart)
    fig2_data = df['الكلية'].value_counts()
    fig2 = go.Figure(data=[go.Bar(x=fig2_data.index, y=fig2_data.values, name="الكلية")])
    fig2.update_layout(title_text="توزيع الطلبة حسب الكلية", xaxis_tickangle=-45, height=400)

    # المتغير 3: المحاضر (Bar Chart - Top 10)
    fig3_data = df['اسم المحاضر'].value_counts().head(10)
    fig3 = go.Figure(data=[go.Bar(x=fig3_data.values, y=fig3_data.index, orientation='h', name="المحاضر")])
    fig3.update_layout(title_text="أكثر المحاضرين عدداً (أول 10)", height=400)

    # المتغير 4: المقرر (Bar Chart - Top 10)
    fig4_data = df['اسم المقرر'].value_counts().head(10)
    fig4 = go.Figure(data=[go.Bar(x=fig4_data.index, y=fig4_data.values, name="المقرر")])
    fig4.update_layout(title_text="أكثر المقررات دراسة (أول 10)", xaxis_tickangle=-45, height=400)

    # عرض الرسوم في الشبكة
    col_left, col_right = st.columns(2)
    with col_left:
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
    with col_right:
        st.plotly_chart(fig3, use_container_width=True)
        st.plotly_chart(fig4, use_container_width=True)

    # جدول البيانات التفصيلي (اختياري)
    with st.expander("عرض البيانات الخام"):
        st.dataframe(df)
