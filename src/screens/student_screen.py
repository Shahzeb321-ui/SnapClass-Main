import streamlit as st
from src.components.header import header_dashboard
from src.ui.base_layout import style_base_dashboard,style_base_Layout
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card
import numpy as np
from PIL import Image
from src.pipelines.face_pipeline import predict_attendence,get_face_embeddings,train_classifier
from src.pipelines.voice_pipleline import get_voice_embeddings
from src.database.db import get_all_students,create_student,get_student_subjects,get_student_attendance,unenroll_student_to_subject
import time

def student_dashboard():
    student_data=st.session_state.student_data
    student_id=student_data['student_id']
    c1,c2=st.columns(2,vertical_alignment="center",gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']}""")
        if st.button("Log Out",key="loginbackbtn",shortcut="control+backspace"):
            st.session_state['is_logged_in']=False
            del st.session_state.student_data

    st.rerun()

    st.space()
    c1,c2=st.columns(2)
    with c1:
        st.header('Your Enrolled Subjects')
    with c2:
        if st.button("Enroll in subjects",type='primary',width="stretch"):
            enroll_dialog()

    st.divider()

    with st.spinner("Loading your subjects"):
        subjects=get_student_subjects(student_id)
        logs=get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button():
                if st.button("Unenroll from tihs course", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f'Unenrolled from {sub['name']} successfully!')
                    st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )

    footer_dashboard()


   



def student_screen():
    style_base_dashboard()
    style_base_Layout() 

    if "student_data" in st.session_state:
        student_dashboard()
        return
    
    c1,c2=st.columns(2,vertical_alignment="center",gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go Back To Home",key="loginbackbtn",shortcut="control+backspace"):
            st.session_state['login_type']=None
            st.rerun()
    st.header("Login Using FaceID",text_alignment='center')
    st.space()
    st.space()
    show_registration=False

    photo_source=st.camera_input("Position your face in the center")

    if photo_source:
        img=np.array(Image.open(photo_source))

        with st.spinner('Ai is scanning...'):
            detected,all_ids,num_faces=predict_attendence(img)

            if num_faces==0:
                st.warning('Face not found')
            elif num_faces>1:
                st.warning('Multiple Faces Found')
            else:
                if detected:
                    student_id=list(detected.keys())[0]
                    all_students=get_all_students()
                    student=next((s for s in all_students if s['student_id']==student_id ), None)

                    if student:
                        st.session_state.is_logged_in =True
                        st.session_state.user_role= 'student'
                        st.session_state.student_data=student
                        st.toast(f'Welcome back! {student['name']}')
                        time.sleep(2)
                        st.rerun()
                else:
                    st.info("Face Not Recognized! You might be a new student")
                    show_registration=True

    if show_registration:
        with st.container(border=True):
            st.header('Register New Profile')
            new_name=st.text_input("Enter Your Name", placeholder="E.g Shahzeb Sheraz")

            st.subheader('Optional: Voice Enrollment')
            st.info("Enroll your for voice only attendance")

            audio_data=None

            try:
                audio_data=st.audio_input('Record a short phrase like I am Present, My Name is Your Name')
            except Exception:
                st.error('Audio data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile...'):
                        img = np.array(Image.open(photo_source))
                        embeddings=get_face_embeddings(img)
                        if embeddings:
                            face_emb=embeddings[0].tolist()

                            voice_emb=None
                            if audio_data:
                                voice_emb=get_voice_embeddings(audio_data.read())

                            response_data=create_student(new_name,face_embeddings=face_emb,voice_embeddings=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in =True
                                st.session_state.user_role= 'student'
                                st.session_state.student_data=student
                                st.toast(f'Profile Created! Hi {new_name}')
                                time.sleep(2)
                                st.rerun()
                        else:
                            st.error('Couldnt Cpature your facial heaftures for regitration')
                else:
                    st.warning('Please enter your name')

                        

    footer_dashboard()
