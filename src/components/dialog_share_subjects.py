import streamlit as st
from src.database.db import create_subject
import segno
import io


@st.dialog("Share class link")
def share_subject_dialog(name,code):
   app_domain="ai-attendancee.streamlit.app"
   join_url=f"{app_domain}/join=code={code}"

   st.header('Scan To Join')

   qr=segno.make(join_url)

   out=io.BytesIO()
   qr.save(out,kind='png',scale=10,border=1)

   col1,col2=st.columns(2)
   with col1:
      
      st.markdown('### Copy Link')
      st.code(join_url,language="text")
      st.code(code,language="text")
      st.info('Copy This link to share')
    
   with col2:
     st.markdown('### Scan To Join')
     st.image(out.getvalue(),caption="QRcode for class Joining")

     


