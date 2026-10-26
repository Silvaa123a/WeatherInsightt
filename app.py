import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import hashlib

st.set_page_config(
    page_title="WeatherInsight Pro",
    page_icon="🌤️",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #5c5346 0%, #383129 100%);
        color: #ffffff;
    }
    .weather-card {
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.08);
    }
    .city-header {
        font-size: 32px;
        font-weight: 600;
        text-align: right;
        margin-bottom: 0px;
        color: #ffffff;
    }
    .big-temp {
        font-size: 80px !important;
        font-weight: 200;
        line-height: 1;
        text-align: right;
        margin: 5px 0;
        color: #ffffff;
    }
    .sub-info {
        text-align: right;
        color: #d0c0b0;
        font-size: 16px;
        margin-bottom: 20px;
    }
    .card-title {
        color: #c0b0a0;
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: right;
    }
    .card-value {
        font-size: 26px;
        font-weight: bold;
        color: #ffffff;
        text-align: right;
    }
    .card-desc {
        color: #b0a090;
        font-size: 12px;
        margin-top: 5px;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_weather_data(city_name):
    city_hash = int(hashlib.md5(city_name.strip().encode('utf-8')).hexdigest(), 16) % 10000
    np.random.seed(city_hash)
    
    dates = pd.date_range(start="2026-10-25 12:00:00", periods=24, freq='h')
    humidity = np.random.uniform(25, 60, 24)
    wind_speed = np.random.uniform(5, 25, 24)
    pressure = np.random.uniform(1010, 1020, 24)
    rain_chance = np.random.uniform(0, 85, 24)
    temperature = 31 - (humidity * 0.05) + np.random.normal(0, 1, 24)
    
    formatted_hours = dates.strftime('%H:00')
    
    return pd.DataFrame({
        'Hour': formatted_hours,
        'Datetime': dates,
        'Temperature': temperature,
        'Humidity': humidity,
        'WindSpeed': wind_speed,
        'Pressure': pressure,
        'RainChance': rain_chance
    })

# إدارة المدن والمواقع
if 'saved_cities' not in st.session_state:
    st.session_state.saved_cities = ["حمص"]

if 'current_selected_city' not in st.session_state:
    st.session_state.current_selected_city = "حمص"

st.sidebar.markdown("## 🏢 إدارة المدن")

new_city = st.sidebar.text_input("🔍 ادخل الموقع / ابحث عن مدينة:", placeholder="مثلاً: حماة، اللاذقية...")
btn_add = st.sidebar.button("➕ إضافة وتحديد الموقع")

if (btn_add or new_city) and new_city.strip():
    city_name = new_city.strip()
    if city_name not in st.session_state.saved_cities:
        st.session_state.saved_cities.append(city_name)
    st.session_state.current_selected_city = city_name

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 المواقع المضافة")

target_city = st.sidebar.radio(
    "اختر المدينة لعرض الطقس:",
    st.session_state.saved_cities,
    index=st.session_state.saved_cities.index(st.session_state.current_selected_city) if st.session_state.current_selected_city in st.session_state.saved_cities else 0
)

st.session_state.current_selected_city = target_city

df = load_weather_data(target_city)

# حساب المتغيرات ديناميكياً
max_temp = df['Temperature'].max()
min_temp = df['Temperature'].min()
current_temp = df['Temperature'].iloc[0]
air_quality = 70 + (int(hashlib.md5(target_city.encode('utf-8')).hexdigest(), 16) % 25)

# تدريب النموذج
X = df[['Humidity', 'WindSpeed', 'Pressure']]
y = df['Temperature']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
# الواجهة الرئيسية
st.markdown(f"""
    <div>
        <div class="city-header">{target_city} 📍</div>
        <div class="sub-info">جارٍ التحديث • طقس مستقر</div>
        <div class="big-temp">{current_temp:.0f}°</div>
        <div class="sub-info">{max_temp:.0f}° / {min_temp:.0f}° &nbsp;|&nbsp; جودة الهواء: {air_quality} 🌿</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="weather-card">
        <div class="card-title">⏰ توقعات 24 ساعة القادمة</div>
    </div>
""", unsafe_allow_html=True)

chart_data = df.set_index('Hour')[['Temperature']].round(0)
st.line_chart(chart_data, height=150)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
        <div class="weather-card">
            <div class="card-title">🌧️ احتمال الأمطار / الهطول</div>
            <div class="card-value">{df['RainChance'].iloc[0]:.0f}%</div>
            <div class="card-desc">فرصة هطول معتدلة اليوم</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="weather-card">
            <div class="card-title">💧 الرطوبة</div>
            <div class="card-value">{df['Humidity'].iloc[0]:.0f}%</div>
            <div class="card-desc">معدل طبيعي ومريح</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="weather-card">
            <div class="card-title">🧭 الرياح (شمالي)</div>
            <div class="card-value">{df['WindSpeed'].iloc[0]:.1f} <span style="font-size:14px;">كم/س</span></div>
            <div class="card-desc">حركة هادئة وثابتة</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="weather-card">
            <div class="card-title">☀️ أشعة فوق بنفسجية</div>
            <div class="card-value">4 <span style="font-size:16px;">(متوسط)</span></div>
            <div class="card-desc">مستوى آمن للخروج</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="weather-card">
            <div class="card-title-item card-title">🌡️ الشعور الحقيقي</div>
            <div class="card-value">{current_temp + 1:.0f}°</div>
            <div class="card-desc">مطابق لدرجة الحرارة الفعلية</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="weather-card">
            <div class="card-title">📈 الضغط الجوي</div>
            <div class="card-value">{df['Pressure'].iloc[0]:.0f} <span style="font-size:14px;">mbar</span></div>
            <div class="card-desc">استقرار تام في الضغط</div>
        </div>
    """, unsafe_allow_html=True)

if st.checkbox("عرض جدول توقعات الطقس المفصل للأيام القادمة"):
    display_df = df.head(7).copy()
    display_df['Date'] = pd.date_range(start="2026-10-25", periods=7).strftime('%Y-%m-%d')
    display_df['Temperature'] = display_df['Temperature'].round(1).astype(str) + ' °C'
    display_df['RainChance'] = display_df['RainChance'].round(0).astype(str) + ' %'
    display_df['Humidity'] = display_df['Humidity'].round(1).astype(str) + '%'
    display_df['WindSpeed'] = display_df['WindSpeed'].round(1).astype(str) + ' km/h'
    display_df = display_df[['Date', 'Temperature', 'RainChance', 'Humidity', 'WindSpeed']]
    display_df.columns = ['التاريخ', 'درجة الحرارة', 'احتمال الأمطار', 'الرطوبة', 'سرعة الرياح']
    st.dataframe(display_df, use_container_width=True)
