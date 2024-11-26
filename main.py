import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="자율/진로/개인/종합사항 초안", layout="wide")

# CSS - 최소한의 스타일만 적용
st.markdown("""
    <style>
    .section-header {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0;
    }
    .byte-count {
        color: #333;
        font-size: 14px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 메인 앱
st.title("자율/진로/개인/종합사항 초안")

# 데이터 로드
def get_google_credentials():
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
    return credentials

@st.cache_data
def load_sheet_data():
    try:
        credentials = get_google_credentials()
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key('1S-Q7oBziDDd9C_sSQdZrbt6cbR0GvMJ4v43NYVvWOb8').sheet1
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
        return None

def update_password(student_id, new_password):
    try:
        # Google Sheets 인증 및 접근
        credentials = get_google_credentials()
        gc = gspread.authorize(credentials)
        sheet = gc.open_by_key('1S-Q7oBziDDd9C_sSQdZrbt6cbR0GvMJ4v43NYVvWOb8').sheet1
        
        # 데이터 로드
        df = pd.DataFrame(sheet.get_all_records())
        data_index = df[df['ID'] == student_id].index[0]
        
        # 비밀번호 업데이트
        sheet.update_cell(data_index + 2, df.columns.get_loc('Password') + 1, new_password)
        
        # 캐시 무효화
        load_sheet_data.clear()
        
        # 데이터 재로드 (선택 사항)
        st.session_state.updated_df = pd.DataFrame(sheet.get_all_records())
        
        return True
    except Exception as e:
        st.error(f"비밀번호 업데이트 중 오류가 발생했습니다: {str(e)}")
        return False


def login(student_id, password, df):
    if df is None:
        return False
    student = df[(df['ID'] == student_id) & (df['Password'] == password)]
    if not student.empty:
        st.session_state.logged_in = True
        st.session_state.student_id = student_id
        return True
    return False

# 세션 상태 초기화
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.logged_in = False
    st.session_state.student_id = None
    st.session_state.show_password_change = False

df = load_sheet_data()

if df is None:
    st.error("데이터를 불러올 수 없습니다. 새로고침을 해보세요.")
    st.stop()

if not st.session_state.logged_in:
    # 로그인 폼
    with st.form("login_form"):
        student_id = st.text_input("학생 ID를 입력하세요:")
        password = st.text_input("비밀번호를 입력하세요:", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            if login(student_id, password, df):
                st.success("로그인 성공!")
                st.experimental_rerun()
            else:
                st.error("ID 또는 비밀번호가 잘못되었습니다.")

else:
    # 학생 정보 표시
    student = df[df['ID'] == st.session_state.student_id].iloc[0]
    
    st.header(f"학생 이름: {student['Name']}")

    # 자율활동
    st.subheader("🎯 자율활동")
    st.text(f"글자 수 제한: 한글 500자 / 1500byte")
    st.text_area("자율활동", value=student['A'], height=300, label_visibility="collapsed")
    st.text(f"현재 Byte 수: {student['B']}/1500")
    
    st.markdown("---")

    # 진로활동
    st.subheader("🎓 진로활동")
    st.text(f"글자 수 제한: 한글 700자 / 2100byte")
    st.text_area("진로활동", value=student['C'], height=400, label_visibility="collapsed")
    st.text(f"현재 Byte 수: {student['D']}/2100")
    
    st.markdown("---")

    # 개인별 세부사항
    st.subheader("👤 개인별 세부사항")
    st.text(f"글자 수 제한: 한글 500자 / 1500byte")
    st.text_area("개인특기사항", value=student['E'], height=300, label_visibility="collapsed")
    st.text(f"현재 Byte 수: {student['F']}/1500")
    
    st.markdown("---")

    # 종합평가
    st.subheader("📝 종합평가")
    st.text(f"글자 수 제한: 한글 500자 / 1500byte")
    st.text_area("종합평가", value=student['G'], height=300, label_visibility="collapsed")
    st.text(f"현재 Byte 수: {student['H']}/1500")
    
    st.markdown("---")
    
    # 하단 메뉴
    col1, col2, col3 = st.columns([1, 1, 8])
    
    with col1:
        if st.button("로그아웃"):
            st.session_state.logged_in = False
            st.session_state.student_id = None
            st.experimental_rerun()
    
    with col2:
        if st.button("비밀번호 변경"):
            st.session_state.show_password_change = not st.session_state.show_password_change
    
    # 비밀번호 변경 폼
    if st.session_state.show_password_change:
        with st.form("password_change_form"):
            st.write("비밀번호 변경")
            new_password = st.text_input("새 비밀번호:", type="password")
            confirm_password = st.text_input("새 비밀번호 확인:", type="password")
            change_button = st.form_submit_button("변경하기")
            
            if change_button:
                if new_password == confirm_password:
                    if update_password(st.session_state.student_id, new_password):
                        st.success("비밀번호가 변경되었습니다. 다시 로그인해주세요.")
                        st.session_state.logged_in = False
                        st.experimental_rerun()
                else:
                    st.error("새 비밀번호가 일치하지 않습니다.")
