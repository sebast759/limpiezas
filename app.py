import pandas as pd
import os
import re
from datetime import datetime

# Spanish + English date mappings
dias_semana = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles", "Thursday": "Jueves",
    "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
meses = {
    "January": "enero", "February": "febrero", "March": "marzo", "April": "abril",
    "May": "mayo", "June": "junio", "July": "julio", "August": "agosto",
    "September": "septiembre", "October": "octubre", "November": "noviembre", "December": "diciembre"
}
dias_en = {k: k for k in dias_semana}
meses_en = {k: k for k in meses}

# Detect language based on listing title
def detect_language(name):
    if any(word in name.lower() for word in ['cottage']):
        return 'en'
    return 'es'

# Find the latest reservation CSV
def get_latest_reservation_csv():
    files = [f for f in os.listdir() if f.lower().startswith("reservation") and f.lower().endswith(".csv")]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
    return files[0]

# Load and clean the reservation file
def load_reservations(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = [col.strip().lower() for col in df.columns]
        return df
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return None

# Run main logic
def main():
    file = get_latest_reservation_csv()
    if not file:
        print("❌ No 'reservation*.csv' file found.")
        input("\nPress Enter to exit...")
        return

    print(f"📄 Reading: {file}")
    df = load_reservations(file)
    if df is None:
        input("\nPress Enter to exit...")
        return

    required_cols = ["start date", "end date", "listing"]
    if not all(col in df.columns for col in required_cols):
        print(f"❌ Missing one or more required columns: {required_cols}")
        input("\nPress Enter to exit...")
        return

    # Parse and format
    data = []
    for _, row in df.iterrows():
        try:
            start = pd.to_datetime(row["start date"]).to_pydatetime()
            end = pd.to_datetime(row["end date"]).to_pydatetime()
            listing = str(row["listing"]).strip()
            data.append({"start": start, "end": end, "listing": listing})
        except:
            continue

    if not data:
        print("⚠️ No valid reservation data found.")
        input("\nPress Enter to exit...")
        return

    df_clean = pd.DataFrame(data)

    for listing_name, group in df_clean.groupby("listing"):
        lang = detect_language(listing_name)
        dias = dias_en if lang == 'en' else dias_semana
        meses_dict = meses_en if lang == 'en' else meses
        header = "🌟 **Upcoming Cleaning Schedule** 🌟" if lang == 'en' else "🌟 **Planificación de las próximas limpiezas** 🌟"
        early_text = "after **11:00 AM**" if lang == 'en' else "después de las **11.00 horas**"
        late_text = "after **2:30 PM**" if lang == 'en' else "después de las **14.30 horas**"
        same_day_text = "(same-day start date) 🔴" if lang == 'en' else "(start date el mismo día) 🔴"
        next_guest_text = "(next guest {d} days later)" if lang == 'en' else "(siguiente huésped {d} días después)"
        end_text = "(end of stays)" if lang == 'en' else "(fin de estancia)"

        mensaje = f"{header}\n"
        group = group.sort_values("start").reset_index(drop=True)

        for i in range(len(group)):
            out_date = group.loc[i, "end"]
            dia = dias[out_date.strftime("%A")]
            mes = meses_dict[out_date.strftime("%B")]
            fecha = f"{dia} {out_date.day} de {mes}"

            same_day = (i + 1 < len(group)) and (group.loc[i + 1, "start"].date() == out_date.date())
            if same_day:
                mensaje += f"- {fecha} {early_text} {same_day_text}\n"
            else:
                if i + 1 < len(group):
                    diff = (group.loc[i + 1, "start"].date() - out_date.date()).days
                    mensaje += f"- {fecha} {late_text} {next_guest_text.format(d=diff)}\n"
                else:
                    mensaje += f"- {fecha} {late_text} {end_text}\n"

        print(f"\n🏠 *{listing_name}*\n")
        print(mensaje)

    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()
