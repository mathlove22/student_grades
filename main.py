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
st.title("성적 확인 및 비밀번호 변경 시스템")

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
    sheet.update('C2:C', df['Password'].tolist())  # 비밀번호 열의 위치에 맞게 수정
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
                st.rerun()  # 즉시 페이지 새로고침
            else:
                st.error("ID 또는 비밀번호가 잘못되었습니다.")
else:
    # 학생 정보 및 비밀번호 변경 섹션
    student = df[df['ID'] == st.session_state.student_id].iloc[0]
    st.write(f"학생 이름 : {student['Name']}")
    st.write(f"성적: {student['Grade']}")
    
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
        st.rerun()  # st.experimental_rerun() 대신 st.rerun() 사용
