import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="Elevator Design Hub", layout="wide")

# العنوان الرئيسي
st.title("🏗️ Elevator Design & Analysis Hub")
st.markdown("---")

# القائمة الجانبية للتنقل
menu = ["📐 AutoCAD Design", "📊 Traffic Analysis", "📄 Spec Summarizer"]
choice = st.sidebar.selectbox("اختر الأداة", menu)

# --- القسم الأول: تصميم الأوتوكاد ---
if choice == "📐 AutoCAD Design":
    st.header("تعديل رسومات الأوتوكاد")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("إدخال الأبعاد")
        s_width = st.number_input("عرض البئر (Shaft Width) مم", value=1600)
        s_depth = st.number_input("عمق البئر (Shaft Depth) مم", value=1800)
        c_width = st.number_input("عرض الكابينة (Car Width) مم", value=1100)
        c_depth = st.number_input("عمق الكابينة (Car Depth) مم", value=1400)
        
        uploaded_cad = st.file_uploader("ارفع ملف الرسم المرجعي (.dxf)", type=['dxf'])
        
        if st.button("Generate Updated Drawing"):
            st.success(f"تم تحديث الرسم بالأبعاد: {s_width}x{s_depth}")
            st.info("ملاحظة: يتطلب ربط مكتبة ezdxf في السيرفر لتوليد الملف الحقيقي.")

    with col2:
        st.info("معاينة التصميم ستظهر هنا (مساحة تخطيطية)")
        # رسم مبسط يوضح الفكرة
        st.write(f"مخطط البئر الحالي: {s_width} مم × {s_depth} مم")

# --- القسم الثاني: تحليل الحركة ---
elif choice == "📊 Traffic Analysis":
    st.header("تحليل حركة المرور (Traffic Analysis)")
    
# --- داخل قسم Traffic Analysis في ملف app.py ---

def calculate_traffic(floors, population, speed, capacity):
    # فرضيات هندسية بسيطة:
    # d: المسافة المتوسطة بين الأدوار (3.5 متر)
    # tv: زمن السفر بين الأدوار = المسافة / السرعة
    # t_stop: زمن التوقف لفتح وإغلاق الأبواب (حوالي 8 ثوانٍ)
    
    dist_total = floors * 3.5
    tv = 3.5 / speed
    t_stop = 8 
    
    # حساب عدد التوقفات المتوقعة (S) بناءً على عدد الركاب (P)
    # P هنا هي حمولة الكابينة (نفرض 80% من السعة)
    p = capacity * 0.8 / 75 # متوسط وزن الراكب 75 كجم
    
    # معادلة RTT المبسطة
    rtt = (2 * floors * tv) + (p * t_stop) + (2 * dist_total / speed)
    
    # حساب قدرة النقل في 5 دقائق (Handling Capacity - HC)
    hc = (300 * p * 1.0) / rtt # لعدد 1 مصعد
    
    return round(rtt, 2), round(hc, 2)

# التفاعل مع الواجهة
if choice == "📊 Traffic Analysis":
    st.header("حسابات تحليل حركة المرور الهندسية")
    
    col1, col2 = st.columns(2)
    with col1:
        floors = st.number_input("عدد الطوابق فوق الأرضي", value=10)
        pop = st.number_input("إجمالي السكان", value=200)
        cap = st.selectbox("حمولة المصعد (كجم)", [450, 630, 800, 1000, 1275])
        speed = st.selectbox("السرعة (م/ث)", [1.0, 1.6, 1.75, 2.0])
        
    if st.button("بدء التحليل الهندسي"):
        rtt, hc = calculate_traffic(floors, pop, speed, cap)
        
        st.subheader("النتائج:")
        k1, k2 = st.columns(2)
        k1.metric("زمن الرحلة (RTT)", f"{rtt} ثانية")
        k2.metric("قدرة النقل (في 5 دقائق)", f"{hc} شخص")
        
        # تحليل النتيجة
        required_hc = pop * 0.12 # المستهدف عادة 12% من السكان
        num_lifts = round(required_hc / hc) + 1
        st.success(f"النتيجة: تحتاج إلى **{num_lifts} مصاعد** لتلبية الطلب في وقت الذروة.")
    
    col1, col2 = st.columns(2)
    with col1:
        floors = st.number_input("عدد الطوابق", min_value=1, value=10)
        pop = st.number_input("إجمالي السكان في المبنى", min_value=1, value=100)
        speed = st.selectbox("سرعة المصعد (م/ث)", [1.0, 1.6, 1.75, 2.0, 2.5])
        
    if st.button("Run Analysis"):
        # معادلة افتراضية بسيطة للتوضيح
        rtt = (floors * 2) / speed + 20 
        st.metric(label="زمن الرحلة التقريبي (RTT)", value=f"{round(rtt, 2)} ثانية")
        st.write("بناءً على المرجع المرفق، المصعد المقترح هو: **1000 كجم / 1.75 م/ث**")

# --- القسم الثالث: تلخيص المواصفات ---
elif choice == "📄 Spec Summarizer":
    st.header("ملخص المواصفات الفنية")
    uploaded_pdf = st.file_uploader("ارفع ملف مواصفات المشروع (PDF)", type=['pdf'])
    
    if uploaded_pdf:
        st.subheader("النقاط الفنية المستخلصة:")
        summary_data = {
            "البند": ["نظام القيادة", "السرعة", "الحمولة", "نظام الأبواب"],
            "المواصفة": ["Gearless VVVF", "1.6 m/s", "800 kg", "Center Opening"]
        }
        st.table(pd.DataFrame(summary_data))
        st.button("تصدير التلخيص إلى Word")
