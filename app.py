import streamlit as st
from google import genai
import json
import os
from io import BytesIO
from docx import Document

st.set_page_config(page_title="AI Novel Writing Assistant (Pro & Docx)", layout="wide")

DATA_DIR = "my_novels"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_novel_list():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    return [f.replace('.json', '') for f in files]

def load_novel(title):
    filepath = os.path.join(DATA_DIR, f"{title}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_novel(title, data):
    filepath = os.path.join(DATA_DIR, f"{title}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_docx(novel_data):
    doc = Document()
    doc.add_heading(f"นิยายเรื่อง: {novel_data['title']}", level=0)
    doc.add_paragraph(f"ธีมหลัก: {', '.join(novel_data.get('themes', []))}")
    doc.add_paragraph("-" * 40)
    for ep in novel_data.get("episodes", []):
        doc.add_heading(ep['ep_title'], level=1)
        doc.add_paragraph(f"พล็อตตอน: {ep['plot']}")
        doc.add_paragraph(ep['content'])
        doc.add_paragraph("\n" + "="*30 + "\n")
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

st.title("✍️ AI Novel Writing Assistant (Pro Copilot + Docx Export)")

st.sidebar.header("📁 เลือก / สร้างเรื่องนิยาย")
novel_list = get_novel_list()
option = st.sidebar.radio("ตัวเลือกโปรเจกต์:", ["เลือกเรื่องที่มีอยู่", "➕ สร้างเรื่องใหม่"])

current_novel_title = None

if option == "➕ สร้างเรื่องใหม่":
    new_title = st.sidebar.text_input("ตั้งชื่อเรื่องใหม่:")
    if st.sidebar.button("สร้างโปรเจกต์นิยาย"):
        if new_title.strip():
            if new_title in novel_list:
                st.sidebar.error("มีนิยายชื่อนี้อยู่แล้ว!")
            else:
                initial_data = {
                    "title": new_title,
                    "themes": ["โรแมนติกแฟนตาซี", "ยุโรปยุคขุนนาง/ราชวงศ์"],
                    "custom_theme": "",
                    "prose_style": "กระชับ ฉับไว เน้นบรรยายอารมณ์ความรู้สึก",
                    "my_style_sample": "",
                    "characters": [],
                    "relationships": [],
                    "episodes": []
                }
                save_novel(new_title, initial_data)
                st.sidebar.success(f"สร้างเรื่อง '{new_title}' สำเร็จ!")
                st.rerun()
        else:
            st.sidebar.warning("กรุณากรอกชื่อเรื่อง")
else:
    if novel_list:
        current_novel_title = st.sidebar.selectbox("เลือกเรื่องที่ต้องการแต่ง:", novel_list)
    else:
        st.sidebar.info("ยังไม่มีเรื่อง
