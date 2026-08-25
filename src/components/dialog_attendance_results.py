import streamlit as st
from src.database.db import create_subject,enroll_student_to_subject,create_attendance
from src.database.config import supabase
from PIL import Image
import time

@st.dialog("Attendance Report")
def attendance_result_dialog(df,logs):

    st.write("Please review attendance before confirming.")
    st.dataframe(df,hide_index=True , width='stretch')

    col1,col2 = st.columns(2)

    with col1:
        if st.button('Discard', width='stretch'):
            st.session_state.attendance_images=[]
            st.session_state.voice_attendance_results=None
            st.rerun()
    
    with col2:
        if st.button('Confirm and Save', width='primary'):
            try:
                create_attendance(logs)
                st.toast("Attendance taken")
                st.session_state.attendance_images=[]
                st.session_state.voice_attendance_results=None
                st.rerun()
            except Exception as e:
                st.error('Sync Failed')

def show_attendance_result(df_results, logs):
    attendance_result_dialog(df_results,logs)
    

