import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime

# Translations
dias_es = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves",
    "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
meses_es = {
    "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
    "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
    "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"
}
dias_en = {k: k for k in dias_es}
meses_en = {k: k for k in meses_es}

def detect_language(listing):
    if any(word in listing.lower() for word in ['cottage', 'studio']):
        return 'en'
    return 'es'

def generate_message(df):
    output = ""
    for listing, group in df.groupby("listing"):
        lang = detect_language(listing)
        dias = dias_en if lang == 'en' else dias_es
        meses = meses_en if lang == 'en' else meses_es
        header = "🌟 **Upcoming Cleaning Schedule** 🌟" if lang == 'en' else "🌟 **Planificación de las próximas limpiezas** 🌟"
        early = "after **11:00 AM**" if lang == 'en' else "después de las **11.00 horas**"
        late = "after **2:30 PM**" if lang == 'en' else "después de las **14.30 horas**"
        same = "(same-day checkin) 🔴" if lang == 'en' else "(checkin el mismo día) 🔴"
        next_guest = "(next guest {d} days later)" if lang == 'en' else "(siguiente huésped {d} días después)"
        end = "(end of stays)" if lang == 'en' else "(fin de estancia)"

        group = group.sort_values("start").reset_index(drop=True)
        mensaje = f"{header}\n"
        for i in range(len(group)):
            out_date = group.loc[i, "end"]
            dia = dias[out_date.strftime("%A")]
            mes = meses[out_date.strftime("%B")]
            fecha = f"{dia} {out_date.day} de {mes}"

            same_day = (i + 1 < len(group)) and (group.loc[i + 1, "start"].date() == out_date.date())
            if same_day:
                mensaje += f"- {fecha} {early} {same}\n"
            else:
                if i + 1 < len(group):
                    diff = (group.loc[i + 1, "start"].date() - out_date.date()).days
                    mensaje += f"- {fecha} {late} {next_guest.format(d=diff)}\n"
                else:
                    mensaje += f"- {fecha} {late} {end}\n"

        output += f"\n🏠 *{listing}*\n\n{mensaje}\n"
    return output

from PIL import Image
import streamlit as st

st.title("🧼 Limpiezas Message Generator")
st.markdown("Upload your Airbnb **reservation CSV**, and get a WhatsApp-ready cleaning message!")

# 📋 How to Use
st.markdown("## 📋 How to Use")

left, right = st.columns([1, 1.5])  # Wider left side for text
    
with left:
    st.markdown("""
    1. Go to 👉 [Airbnb Reservations](https://www.airbnb.com/hosting/reservations)  
    2. Click **Export > Download CSV file**  
    3. Upload the file to the app  
    """)

with right:
    st.image("image.png", caption="Example CSV download", width=500)

# Upload CSV
uploaded_file = st.file_uploader("📥 Upload your reservation CSV", type=["csv"])
st.markdown("""
4. **Copy the generated message and share it via <img src="https://img.icons8.com/color/48/000000/whatsapp.png" width="24" style="vertical-align: middle;"> WhatsApp!**
""", unsafe_allow_html=True)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        if not all(col in df.columns for col in ["start date", "end date", "listing"]):
            st.error("⚠️ Your CSV must include: start date, end date, listing")
        else:
            df["start"] = pd.to_datetime(df["start date"])
            df["end"] = pd.to_datetime(df["end date"])
            df["listing"] = df["listing"].astype(str)
            message = generate_message(df)
            st.success("✅ Message ready!")
            st.code(message, language="markdown")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

