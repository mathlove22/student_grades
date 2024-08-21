import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets와 연결
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file(r'C:\Users\방송반\Documents\project02\indiviualsevice-fb746425b125.json', scopes=scope)
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
