import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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

# Streamlit 사용자 인터페이스 설정
st.title("성적 확인 시스템")

user_id = st.text_input("아이디를 입력하세요")
password = st.text_input("비밀번호를 입력하세요", type="password")

if st.button("성적 조회"):
    # 아이디와 비밀번호로 데이터 필터링
    records = sheet.get_all_records()
    for record in records:
        if record['ID'] == user_id and record['Password'] == password:
            st.write(f"학생 성적: {record['Grade']}")
            break
    else:
        st.write("아이디 또는 비밀번호가 잘못되었습니다.")
