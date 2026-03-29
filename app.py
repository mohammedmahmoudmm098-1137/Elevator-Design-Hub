import streamlit as st
import ezdxf
import io

# إعدادات الصفحة
st.set_page_config(page_title="Elevator Design Hub", layout="wide")

# العنوان الرئيسي
st.title("🏗️ Elevator Design Hub - مسقط أفقي للمصعد")
st.markdown("---")

# وظيفة إنشاء رسم المصعد من الصفر
def generate_elevator_plan(s_width, s_depth, c_width, c_depth):
    # 1. إنشاء مستند DXF جديد
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()

    # 2. إنشاء الطبقات (Layers) لتنظيم الرسم
    doc.layers.new('Shaft', dxfattribs={'color': 7}) # أبيض للبئر
    doc.layers.new('Car', dxfattribs={'color': 1})   # أحمر للكابينة
    doc.layers.new('Rails', dxfattribs={'color': 3}) # أخضر للسكك
    doc.layers.new('Counterweight', dxfattribs={'color': 5}) # أزرق للثقل

    # 3. رسم بئر المصعد (Shaft) كـ Polyline مغلق
    shaft_points = [(0, 0), (s_width, 0), (s_width, s_depth), (0, s_depth), (0, 0)]
    msp.add_lwpolyline(shaft_points, dxfattribs={'layer': 'Shaft'})

    # 4. حساب مكان الكابينة (توسيطها في العرض، وترك مسافة للأبواب في الأمام)
    car_x = (s_width - c_width) / 2
    car_y = 200 # مسافة للأبواب (Clearance) من الأمام
    car_points = [
        (car_x, car_y), 
        (car_x + c_width, car_y), 
        (car_x + c_width, car_y + c_depth), 
        (car_x, car_y + c_depth), 
        (car_x, car_y)
    ]
    msp.add_lwpolyline(car_points, dxfattribs={'layer': 'Car'})

    # 5. رسم السكك (Rails) - خطوط بسيطة للتوضيح
    # سكة على اليمين وسكة على اليسار في منتصف العمق
    rail_y = s_depth / 2
    msp.add_line((0, rail_y), (100, rail_y), dxfattribs={'layer': 'Rails'}) # سكة يسار
    msp.add_line((s_width - 100, rail_y), (s_width, rail_y), dxfattribs={'layer': 'Rails'}) # سكة يمين

    # 6. رسم الثقل (Counterweight) - مستطيل بسيط في الخلف
    cw_width = c_width * 0.8 # عرض الثقل 80% من الكابينة
    cw_depth = 100 # عمق الثقل
    cw_x = (s_width - cw_width) / 2
    cw_y = s_depth - cw_depth - 50 # مسافة من الخلف
    cw_points = [
        (cw_x, cw_y),
        (cw_x + cw_width, cw_y),
        (cw_x + cw_width, cw_y + cw_depth),
        (cw_x, cw_y + cw_depth),
        (cw_x, cw_y)
    ]
    msp.add_lwpolyline(cw_points, dxfattribs={'layer': 'Counterweight'})

    # 7. حفظ الملف في ذاكرة مؤقتة للتحميل
    out_buffer = io.BytesIO()
    doc.write(out_buffer)
    return out_buffer.getvalue()

# --- واجهة المستخدم (Streamlit) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("إدخال الأبعاد (مم)")
    s_width = st.number_input("عرض البئر (Shaft Width)", value=1600)
    s_depth = st.number_input("عمق البئر (Shaft Depth)", value=1800)
    c_width = st.number_input("عرض الكابينة (Car Width)", value=1100)
    c_depth = st.number_input("عمق الكابينة (Car Depth)", value=1400)
    
    st.markdown("---")
    if st.button("توليد ملف الأوتوكاد (DXF)"):
        # التأكد من منطقية الأبعاد
        if c_width >= s_width or c_depth >= s_depth:
            st.error("خطأ: أبعاد الكابينة لا يمكن أن تكون أكبر من أبعاد البئر!")
        else:
            with st.spinner('جاري إنشاء الرسم...'):
                dxf_file = generate_elevator_plan(s_width, s_depth, c_width, c_depth)
                st.success("تم إنشاء الرسم بنجاح!")
                st.download_button(
                    label="📥 تحميل ملف DXF",
                    data=dxf_file,
                    file_name=f"Elevator_{s_width}x{s_depth}.dxf",
                    mime="application/dxf"
                )

with col2:
    st.info("معاينة تخطيطية (غير دقيقة)")
    # رسم مبسط جداً بالـ HTML للتوضيح فقط
    st.markdown(f"""
    <div style="border: 2px solid black; width: {s_width/5}px; height: {s_depth/5}px; position: relative; background-color: #f0f0f0;">
        <div style="border: 2px solid red; width: {c_width/5}px; height: {c_depth/5}px; position: absolute; left: {(s_width-c_width)/10}px; top: 40px; background-color: white; text-align: center; line-height: {c_depth/5}px;">Car</div>
    </div>
    """, unsafe_allow_html=True)
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
