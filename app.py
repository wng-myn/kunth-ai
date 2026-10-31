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
        st.sidebar.info("ยังไม่มีเรื่องนิยายในระบบ กรุณาสร้างเรื่องใหม่")

st.sidebar.markdown("---")
st.sidebar.header("🔑 ตั้งค่าระบบ")
api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="ใส่ API Key ฟรีที่ได้จาก Google AI Studio")

if current_novel_title:
    novel_data = load_novel(current_novel_title)
    st.subheader(f"📖 กำลังแต่งเรื่อง: :blue[{novel_data['title']}]")

    st.sidebar.markdown("---")
    st.sidebar.subheader("➕ เพิ่มตัวละคร")
    with st.sidebar.form("char_form"):
        c_name = st.text_input("ชื่อตัวละคร")
        c_role = st.selectbox("บทบาท", ["พระเอก", "นางเอก/นายเอก", "ตัวร้าย", "ตัวประกอบ 1", "ตัวประกอบ 2", "อื่นๆ"])
        c_personality_type = st.selectbox("ระบบจิตวิทยา", ["MBTI (16 Personalities)", "Enneagram (นพลักษณ์)"])
        
        if c_personality_type == "MBTI (16 Personalities)":
            c_trait = st.selectbox("เลือก MBTI", ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"])
        else:
            c_trait = st.selectbox("เลือกนพลักษณ์", ["Type 1 (นักปฏิรูป)", "Type 2 (ผู้ช่วยเหลือ)", "Type 3 (ผู้สำเร็จ)", "Type 4 (ศิลปิน/โรแมนติก)", "Type 5 (ผู้สังเกตการณ์)", "Type 6 (ผู้ภักดี)", "Type 7 (ผู้สร้างความสุข)", "Type 8 (ผู้ท้าทาย)", "Type 9 (ผู้ประสานงาน)"])
            
        c_backstory = st.text_area("ปมฝังใจ / แรงจูงใจ (ถ้ามี)")
        
        submitted = st.form_submit_button("บันทึกตัวละคร")
        if submitted and c_name:
            novel_data["characters"].append({
                "name": c_name, "role": c_role, "system": c_personality_type, "trait": c_trait, "backstory": c_backstory
            })
            save_novel(current_novel_title, novel_data)
            st.sidebar.success(f"เพิ่ม {c_name} สำเร็จ!")
            st.rerun()

    st.sidebar.subheader("👥 รายชื่อตัวละครในเรื่องนี้")
    if novel_data["characters"]:
        for idx, char in enumerate(novel_data["characters"]):
            st.sidebar.markdown(f"**{char['name']}** ({char['role']}) - `{char['trait']}`")
            if st.sidebar.button(f"ลบ {char['name']}", key=f"del_char_{idx}"):
                novel_data["characters"].pop(idx)
                save_novel(current_novel_title, novel_data)
                st.rerun()

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 1. ธีม & สำนวนการเขียน", 
        "🧩 2. ห้องวิเคราะห์ปมตัวละคร (AI Lab)", 
        "🎬 3. เขียนฉากรายตอน (AI)", 
        "📚 4. อ่านนิยายย้อนหลัง & Export"
    ])

    with tab1:
        st.markdown("### 🎭 1. ตั้งค่าธีมหลักของเรื่องนี้")
        theme_list = [
            "ยุโรปยุคขุนนาง/ราชวงศ์", "หลังวันสิ้นโลก/การแพร่ระบาดเชื้อไวรัส/ภัยพิบัติ", 
            "ย้อนเวลา (Time Travel)", "ทะลุมิติเข้าไปในนิยาย/เกม (Isekai)", 
            "แฟนตาซี/เวทมนตร์ (Fantasy)", "โรแมนติกแฟนตาซี (Romance Fantasy)", 
            "โรแมนติก/รักหวานซึ้ง", "สงคราม/การเมือง/การชิงอำนาจ", 
            "ผจญภัย/การเดินทาง (Adventure)", "เติบโตไปด้วยกัน (Coming of Age)", 
            "สืบสวนสอบสวน/ปริศนา", "กำลังภายใน/เทพเซียน", "ไซไฟ/เทคโนโลยีล้ำยุค (Sci-Fi)"
        ]
        
        saved_themes = novel_data.get("themes", ["โรแมนติกแฟนตาซี"])
        valid_default = [t for t in saved_themes if t in theme_list]
        selected_themes = st.multiselect("เลือกธีมหลัก:", theme_list, default=valid_default)
        custom_theme = st.text_input("ธีมเพิ่มเติม/ฉากหลังเฉพาะ:", value=novel_data.get("custom_theme", ""))
        
        style_preset = st.selectbox("เลือกสไตล์การเขียนสำเร็จรูป:", [
            "ภาษาสวยงาม สละสลวย ละเมียดละไม เน้นฉากและบรรยากาศ (หรูหรา/คลาสสิก)",
            "กระชับ ดิบ ดุดัน ตัดฉับไว เน้นการกระทำและสถานการณ์วิกฤต (แอ็กชัน/สิ้นโลก)",
            "คมคาย เปรียบเปรย ใช้ถ้อยคำลึกซึ้ง (แฟนตาซีโบราณ/กำลังภายใน)",
            "เน้นบรรยายภาษากาย ความรู้สึกภายใน และแรงดันทางอารมณ์ (ดราม่า/จิตวิทยา)",
            "เบาสบาย เข้าถึงง่าย ภาษา現代 (โรแมนติกคอมเมดี้/เติบโตไปด้วยกัน)"
        ])
        my_style_sample = st.text_area("📝 ตัวอย่างสำนวนการเขียนของคุณเอง:", value=novel_data.get("my_style_sample", ""))

        if st.button("💾 บันทึกตั้งค่าธีม & สำนวน"):
            novel_data["themes"] = selected_themes
            novel_data["custom_theme"] = custom_theme
            novel_data["prose_style"] = style_preset
            novel_data["my_style_sample"] = my_style_sample
            save_novel(current_novel_title, novel_data)
            st.success("บันทึกการตั้งค่าเรียบร้อย!")

        st.markdown("---")
        st.markdown("### 🔗 ผังความสัมพันธ์ระหว่างตัวละคร")
        if len(novel_data["characters"]) >= 2:
            char_names = [c["name"] for c in novel_data["characters"]]
            with st.form("rel_form"):
                c1, c2, c3 = st.columns(3)
                with c1: f_char = st.selectbox("ตัวละครต้นทาง", char_names, key="fc")
                with c2: r_type = st.selectbox("ความสัมพันธ์", ["พันธมิตร", "ศัตรู", "แอบชอบ", "ไม่ชอบ", "เฉยๆ", "พึ่งพา", "ผลประโยชน์", "ทรยศ/หักหลัง"])
                with c3: t_char = st.selectbox("ตัวละครปลายทาง", char_names, key="tc")
                if st.form_submit_button("บันทึกความสัมพันธ์") and f_char != t_char:
                    novel_data["relationships"].append({"from": f_char, "relation": r_type, "to": t_char})
                    save_novel(current_novel_title, novel_data)
                    st.rerun()

            for r_idx, r in enumerate(novel_data["relationships"]):
                col_a, col_b = st.columns([4, 1])
                with col_a: st.write(f"🔹 **{r['from']}** $\rightarrow$ *{r['relation']}* $\rightarrow$ **{r['to']}**")
                with col_b:
                    if st.button("ลบ", key=f"del_rel_{r_idx}"):
                        novel_data["relationships"].pop(r_idx)
                        save_novel(current_novel_title, novel_data)
                        st.rerun()

    with tab2:
        st.subheader("🧩 ห้องวิเคราะห์ปม จิตวิทยา และพฤติกรรมตัวละคร")
        char_idea = st.text_area("เล่าพล็อตเรื่องราว หรือพฤติกรรมสั้นๆ ของตัวละคร:")
        if st.button("🔍 ให้ AI ช่วยวิเคราะห์ปม นิสัย และแรงจูงใจ"):
            if not api_key: 
                st.error("กรุณากรอก Google Gemini API Key ที่แถบด้านซ้ายก่อนครับ")
            elif not char_idea: 
                st.error("กรุณากรอกข้อมูลตัวละครก่อน")
            else:
                with st.spinner("Gemini กำลังวิเคราะห์..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model="gemini-2.0-flash", 
                            contents=f"วิเคราะห์ตัวละคร: '{char_idea}' เสนอ MBTI, นพลักษณ์ และปมฝังใจ เป็นภาษาไทย"
                        )
                        st.markdown("### 💡 ผลการวิเคราะห์จาก AI:")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดจาก API: {e}")

    with tab3:
        st.subheader("✍️ กำหนดพล็อตตอนปัจจุบัน & ให้ Gemini บรรยายฉาก")
        ep_num = len(novel_data["episodes"]) + 1
        ep_title = st.text_input("ชื่อตอน / เลขตอน:", value=f"ตอนที่ {ep_num}")
        sel_chars = st.multiselect("เลือกตัวละครที่เข้าฉากนี้", [c["name"] for c in novel_data["characters"]])
        sc_plot = st.text_area("กรอกพล็อตสั้นๆ ในตอนนี้")
        sc_tone = st.selectbox("โทนอารมณ์", ["ดราม่าเข้มข้น", "ตื่นเต้นระทึกขวัญ", "โรแมนติกหวานซึ้ง", "ตลกขบขัน", "หักมุมลึกลับ", "อุ่นวาบในหัวใจ"])

        if st.button("🚀 สั่งให้ Gemini เขียนบรรยายฉากและบันทึกอัตโนมัติ"):
            if not api_key: 
                st.error("กรุณากรอก Google Gemini API Key ที่แถบด้านซ้ายก่อนครับ")
            elif not sc_plot or not sel_chars: 
                st.error("กรุณากรอกพล็อตและเลือกตัวละครอย่างน้อย 1 คน")
            else:
                with st.spinner("Gemini กำลังแต่งนิยาย..."):
                    c_det = [f"- {c['name']} ({c['role']}) | บุคลิก: {c['trait']}" for c in novel_data["characters"] if c["name"] in sel_chars]
                    r_det = [f"- {r['from']} มีความสัมพันธ์ '{r['relation']}' ต่อ {r['to']}" for r in novel_data["relationships"] if r['from'] in sel_chars and r['to'] in sel_chars]
                    th_all = ", ".join(novel_data.get("themes", []))
                    
                    prompt = f"""
                    คุณคือนักเขียนนิยายมืออาชีพ จงแต่งเนื้อหานิยายภาษาไทย:
                    [เรื่อง] {novel_data['title']} | [ตอน] {ep_title}
                    [ธีม] {th_all} | [สไตล์] {novel_data.get('prose_style')}
                    [ตัวละคร] {'\n'.join(c_det)}
                    [ความสัมพันธ์] {'\n'.join(r_det) if r_det else 'ไม่มี'}
                    [พล็อต] {sc_plot} | [โทน] {sc_tone}
                    แต่ง 2-4 ย่อหน้า และตอนท้ายให้เสนอทางเลือก (Choices) 3 ทาง
                    """
                    try:
                        client = genai.Client(api_key=api_key)
                        res = client.models.generate_content(
                            model="gemini-2.0-flash", 
                            contents=prompt
                        )
                        novel_data["episodes"].append({"ep_title": ep_title, "plot": sc_plot, "content": res.text})
                        save_novel(current_novel_title, novel_data)
                        st.success("บันทึกตอนเรียบร้อย!")
                        st.markdown(res.text)
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดจาก API: {e}")

    with tab4:
        st.subheader("📚 รายชื่อตอนทั้งหมด & ส่งออกไฟล์")
        if novel_data["episodes"]:
            for ep in novel_data["episodes"]:
                st.markdown(f"### 📌 {ep['ep_title']}")
                st.markdown(f"**พล็อต:** {ep['plot']}")
                st.markdown(ep['content'])
                st.markdown("---")
            
            st.download_button("📥 ดาวน์โหลดนิยายเป็นไฟล์ Word (.docx)", data=create_docx(novel_data), file_name=f"{novel_data['title']}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        else:
            st.info("ยังไม่มีตอนในเรื่องนี้")
else:
    st.info("👈 กรุณาเลือกเรื่องหรือสร้างเรื่องใหม่ที่แถบซ้ายมือ")
