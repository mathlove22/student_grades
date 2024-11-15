import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Google Sheets와 연결
google_secrets = st.secrets["google"]
credentials_info = {
    "type": google_secrets["type"],
    "project_id": google_secrets["project_id"],
    "private_key_id": google_secrets["private_key_id"],
    "private_key": google_secrets["private_key"].replace("\\n", "\n"),
    "client_email": google_secrets["client_email"],
    "client_id": google_secrets["client_id"],
    "auth_uri": google_secrets["auth_uri"],
    "token_uri": google_secrets["token_uri"],
    "auth_provider_x509_cert_url": google_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": google_secrets["client_x509_cert_url"],
    "universe_domain": google_secrets["universe_domain"]
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
gc = gspread.authorize(credentials)

# Google Sheets에서 데이터 가져오기
sheet = gc.open_by_key('1S-Q7oBziDDd9C_sSQdZrbt6cbR0GvMJ4v43NYVvWOb8').sheet1
df = pd.DataFrame(sheet.get_all_records())

# Streamlit 사용자 인터페이스 설정
st.title("자율/진로/개인/종합사항 초안")

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_id = None

# 로그인 함수
def login(student_id, password):
    student = df[(df['ID'] == student_id) & (df['Password'] == password)]
    if not student.empty:
        st.session_state.logged_in = True
        st.session_state.student_id = student_id
        return student
    return None

# 비밀번호 변경 함수
def change_password(student_id, new_password):
    global df
    data_index = df[df['ID'] == student_id].index[0]
    df.loc[data_index, 'Password'] = new_password
    sheet.update_cell(data_index + 2, df.columns.get_loc('Password') + 1, new_password)  # Adjust cell index as needed
    st.success("비밀번호가 성공적으로 변경되었습니다!")

if not st.session_state.logged_in:
    # 로그인 폼
    with st.form("login_form"):
        student_id = st.text_input("학생 ID를 입력하세요:")
        password = st.text_input("비밀번호를 입력하세요:", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            student = login(student_id, password)
            if student is not None:
                st.success("로그인 성공!")
                st.experimental_rerun()  # 즉시 페이지 새로고침
            else:
                st.error("ID 또는 비밀번호가 잘못되었습니다.")
else:
    # 학생 정보 및 비밀번호 변경 섹션
    student = df[df['ID'] == st.session_state.student_id].iloc[0]
    st.write(f"학생 이름 : {student['Name']}")
    st.write(f"자율활동기록: {student['A']}")
    st.write(f"자율활동Byte(1500): {student['B']}")
    st.write(f"진로활동기록: {student['C']}")
    st.write(f"진로활동Byte(2100): {student['D']}")
    st.write(f"개인특기기록: {student['E']}")
    st.write(f"개인특기Byte(1500): {student['F']}")
    st.write(f"종합평가기록: {student['G']}")
    st.write(f"종합평가Byte(1500): {student['H']}")
    
    st.subheader("비밀번호 변경")
    with st.form("password_change_form"):
        new_password = st.text_input("새 비밀번호를 입력하세요:", type="password")
        confirm_password = st.text_input("새 비밀번호를 다시 입력하세요:", type="password")
        change_button = st.form_submit_button("비밀번호 변경")
        
        if change_button:
            if new_password == confirm_password:
                change_password(st.session_state.student_id, new_password)
            else:
                st.error("새 비밀번호가 일치하지 않습니다. 다시 확인해주세요.")
    
    if st.button("로그아웃"):
        st.session_state.logged_in = False
        st.session_state.student_id = None
        st.experimental_rerun()  # 페이지 새로고침
