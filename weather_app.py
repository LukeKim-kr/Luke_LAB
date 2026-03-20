import streamlit as st
import requests
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="날씨 앱",
    page_icon="⛅",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .weather-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        border-radius: 20px;
        padding: 30px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    .temp-display {
        font-size: 72px;
        font-weight: bold;
        line-height: 1;
    }
    .weather-desc {
        font-size: 22px;
        text-transform: capitalize;
        opacity: 0.9;
    }
    .city-name {
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .metric-box {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }
    .forecast-card {
        background: linear-gradient(135deg, #2c3e50, #3498db);
        border-radius: 12px;
        padding: 15px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("⛅ 날씨 앱")

# API Key input
with st.sidebar:
    st.header("설정")
    api_key = st.text_input(
        "OpenWeatherMap API Key",
        type="password",
        help="https://openweathermap.org/api 에서 무료 API 키를 발급받으세요."
    )
    st.markdown("---")
    st.markdown("### 사용 방법")
    st.markdown("1. [OpenWeatherMap](https://openweathermap.org/api) 가입")
    st.markdown("2. 무료 API 키 발급")
    st.markdown("3. 위에 API 키 입력")
    st.markdown("4. 도시명 검색")

WEATHER_ICONS = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "🌧️",
    "Drizzle": "🌦️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}

def get_weather_icon(condition):
    return WEATHER_ICONS.get(condition, "🌡️")

def get_current_weather(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "kr"
    }
    response = requests.get(url, params=params, timeout=10)
    return response

def get_forecast(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "kr",
        "cnt": 40
    }
    response = requests.get(url, params=params, timeout=10)
    return response

# Search bar
col_input, col_btn = st.columns([4, 1])
with col_input:
    city = st.text_input("도시명 입력", placeholder="예: Seoul, Tokyo, New York", label_visibility="collapsed")
with col_btn:
    search = st.button("검색", use_container_width=True, type="primary")

# Demo mode without API key
if not api_key:
    st.info("사이드바에 OpenWeatherMap API 키를 입력하면 실시간 날씨를 확인할 수 있습니다.")
    st.markdown("---")
    st.markdown("#### 앱 미리보기")

    # Sample UI preview
    st.markdown("""
    <div class="weather-card">
        <div class="city-name">📍 Seoul, KR</div>
        <div style="opacity:0.8; margin-bottom:10px;">2026-03-20 12:00</div>
        <div style="font-size:60px;">☀️</div>
        <div class="temp-display">15°C</div>
        <div class="weather-desc">맑음</div>
        <div style="opacity:0.8; margin-top:8px;">체감 온도: 13°C</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("💧 습도", "60%"),
        ("💨 풍속", "3.2 m/s"),
        ("👁️ 가시거리", "10 km"),
        ("🌡️ 기압", "1013 hPa"),
    ]
    for col, (label, val) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.metric(label, val)

elif city and (search or city):
    with st.spinner("날씨 정보를 불러오는 중..."):
        try:
            # Current weather
            weather_resp = get_current_weather(city, api_key)

            if weather_resp.status_code == 401:
                st.error("유효하지 않은 API 키입니다. API 키를 확인해주세요.")
            elif weather_resp.status_code == 404:
                st.error(f"'{city}' 도시를 찾을 수 없습니다. 영문 도시명을 입력해주세요.")
            elif weather_resp.status_code == 200:
                data = weather_resp.json()
                condition = data["weather"][0]["main"]
                icon = get_weather_icon(condition)
                desc = data["weather"][0]["description"]
                temp = round(data["main"]["temp"])
                feels_like = round(data["main"]["feels_like"])
                temp_min = round(data["main"]["temp_min"])
                temp_max = round(data["main"]["temp_max"])
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                visibility = data.get("visibility", 0) // 1000
                pressure = data["main"]["pressure"]
                country = data["sys"]["country"]
                city_name = data["name"]
                sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
                sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

                # Main weather card
                st.markdown(f"""
                <div class="weather-card">
                    <div class="city-name">📍 {city_name}, {country}</div>
                    <div style="opacity:0.8; margin-bottom:10px;">{now_str}</div>
                    <div style="font-size:60px;">{icon}</div>
                    <div class="temp-display">{temp}°C</div>
                    <div class="weather-desc">{desc}</div>
                    <div style="opacity:0.8; margin-top:8px;">체감 온도: {feels_like}°C &nbsp;|&nbsp; 최저: {temp_min}°C &nbsp;|&nbsp; 최고: {temp_max}°C</div>
                </div>
                """, unsafe_allow_html=True)

                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💧 습도", f"{humidity}%")
                with col2:
                    st.metric("💨 풍속", f"{wind_speed} m/s")
                with col3:
                    st.metric("👁️ 가시거리", f"{visibility} km")
                with col4:
                    st.metric("🌡️ 기압", f"{pressure} hPa")

                col5, col6 = st.columns(2)
                with col5:
                    st.metric("🌅 일출", sunrise)
                with col6:
                    st.metric("🌇 일몰", sunset)

                # 5-day forecast
                st.markdown("---")
                st.subheader("📅 5일 예보")

                forecast_resp = get_forecast(city, api_key)
                if forecast_resp.status_code == 200:
                    forecast_data = forecast_resp.json()
                    daily = {}
                    for item in forecast_data["list"]:
                        date = datetime.fromtimestamp(item["dt"]).strftime("%m/%d")
                        if date not in daily:
                            daily[date] = {
                                "temps": [],
                                "icons": [],
                                "descs": []
                            }
                        daily[date]["temps"].append(item["main"]["temp"])
                        daily[date]["icons"].append(item["weather"][0]["main"])
                        daily[date]["descs"].append(item["weather"][0]["description"])

                    days = list(daily.keys())[:5]
                    cols = st.columns(len(days))
                    for col, day in zip(cols, days):
                        info = daily[day]
                        avg_temp = round(sum(info["temps"]) / len(info["temps"]))
                        max_temp = round(max(info["temps"]))
                        min_temp = round(min(info["temps"]))
                        # Most frequent icon
                        main_icon = get_weather_icon(max(set(info["icons"]), key=info["icons"].count))
                        with col:
                            st.markdown(f"""
                            <div class="forecast-card">
                                <div style="font-weight:bold; font-size:16px;">{day}</div>
                                <div style="font-size:30px; margin:8px 0;">{main_icon}</div>
                                <div style="font-size:18px; font-weight:bold;">{avg_temp}°C</div>
                                <div style="font-size:12px; opacity:0.8;">{min_temp}° / {max_temp}°</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.error(f"날씨 정보를 불러오지 못했습니다. (상태 코드: {weather_resp.status_code})")

        except requests.exceptions.ConnectionError:
            st.error("인터넷 연결을 확인해주세요.")
        except requests.exceptions.Timeout:
            st.error("서버 응답이 없습니다. 잠시 후 다시 시도해주세요.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

elif api_key and not city:
    st.info("도시명을 입력하고 검색 버튼을 눌러주세요.")
