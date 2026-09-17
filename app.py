import streamlit as st
import requests
import datetime
import re

# ==========================
# 기본 설정
# ==========================

st.set_page_config(
    page_title="급식 알레르기 확인",
    page_icon="🍽️",
    layout="centered"
)

# ==========================
# 학교 정보 설정
# ==========================

API_KEY = st.secrets["API_KEY"]

ATPT_OFCDC_SC_CODE = st.secrets["ATPT_OFCDC_SC_CODE"]

SD_SCHUL_CODE = st.secrets["SD_SCHUL_CODE"]


# ==========================
# 급식 가져오기
# ==========================

def get_meal(date):

    url = (
        "https://open.neis.go.kr/hub/mealServiceDietInfo?"
        f"KEY={API_KEY}"
        "&Type=json"
        f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
        f"&SD_SCHUL_CODE={SD_SCHUL_CODE}"
        f"&MLSV_YMD={date}"
    )

    response = requests.get(url)
    try:
        data = response.json()
        meals = data["mealServiceDietInfo"][1]["row"]
        result = []
        for meal in meals:
            menus = (
                meal["DDISH_NM"]
                .replace("<br/>","\n")
                .split("\n")
            )
            result.append(
                {
                    "type": meal["MMEAL_SC_NM"],
                    "menus": menus
                }
            )
        return result
    except:
        return []

# ==========================
# 급식 출력
# ==========================

def display_meal(meals, allergy_list):
    danger = False
    number = 1
    for meal in meals:
        st.subheader(
            "🍴 " + meal["type"]
        )
        for menu in meal["menus"]:
            menu = menu.strip()
            if menu == "":
                continue
            # 알레르기 번호 제거
            clean_menu = re.sub(
                r"\([0-9.,]+\)",
                "",
                menu
            )
            warning = False
            if allergy_list:
                for allergy in allergy_list:
                    if allergy in clean_menu:
                        warning = True
                        danger = True

            # 위험 음식 표시
            if warning:
                st.markdown(
                    f"""
                    <div style="
                    background:#ffcccc;
                    padding:12px;
                    border-radius:10px;
                    margin:5px;">
                    ⚠️ {number}. {clean_menu}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                    background:#eaf4ff;
                    padding:12px;
                    border-radius:10px;
                    margin:5px;">
                    🍚 {number}. {clean_menu}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            number += 1
    return danger

# ==========================
# 제목
# ==========================

st.markdown(
    """
    <h2 style="text-align:center;">
    🍽️ 송곡여고자고등학교
    </h2>
    """,
    unsafe_allow_html=True
)



# ==========================
# 오늘 날짜 급식
# ==========================

today = datetime.date.today()
today_code = today.strftime("%Y%m%d")
meal_data = get_meal(today_code)

# 세션 저장
if "checked" not in st.session_state:
    st.session_state.checked = False
if "allergy" not in st.session_state:
    st.session_state.allergy = []

# ==========================
# 오늘 급식 출력
# ==========================

st.divider()
st.header(
    f"📅 오늘 급식 ({today})"
)

if meal_data:
    danger = display_meal(
        meal_data,
        st.session_state.allergy
    )
else:
    st.warning(
        "오늘 급식 정보가 없습니다."
    )


st.divider()
st.caption(
    "송곡여자고등학교 공공데이터 기반 급식 알레르기 지원 프로그램"
)
