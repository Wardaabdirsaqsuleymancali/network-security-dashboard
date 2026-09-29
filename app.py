from datetime import datetime
import json
import os
from fpdf import FPDF
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.ensemble import IsolationForest

# Page Configuration
st.set_page_config(
    page_title="Network Anomaly Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
)

USERS_FILE = "users.json"
HISTORY_FILE = "history.json"


# --- TRANSLATIONS DICTIONARY ---
TRANSLATIONS = {
    "English": {
        "title": "Network Security Platform",
        "subtitle": "Please select your language and login or sign up",
        "login_tab": "🔑 Login",
        "signup_tab": "📝 Sign Up",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "login_btn": "Login",
        "signup_btn": "Sign Up",
        "success_login": "Successfully logged in!",
        "error_login": "Incorrect username or password!",
        "success_signup": "Account successfully created!",
        "welcome": "Welcome",
        "logout": "Logout",
        "data_source": "📁 Where to get data?",
        "default_files": "Project Files (Default)",
        "upload_file": "Upload New File (CSV/TXT)",
        "upload_label": "Upload your data file (CSV or TXT)",
        "select_dataset": "Select Dataset File:",
        "main_title": (
            "Advanced Network Traffic Security & Anomaly Analyzer"
        ),
        "main_desc": (
            "This advanced dashboard allows you to monitor network"
            " threats, time-series analysis, test new data, and save your"
            " history."
        ),
        "total_traffic": "Total Traffic",
        "normal_traffic": "Normal Traffic",
        "anomalies": "Anomalies / Threats",
        "risk_percentage": "Risk Percentage (%)",
        "tab1": "📊 Dashboard & Time-Series Trend",
        "tab2": "⚡ Live Predict",
        "tab3": "📥 Download Reports (PDF/CSV)",
        "tab4": "📜 Saved History",
        "security_distribution": "Security Distribution",
        "normal": "Normal",
        "anomaly": "Anomalies",
        "trend_chart": "Trend Line Chart",
        "security_events": "Security Events List",
        "filter_status": "Filter by status:",
        "all": "All",
        "open_alert": "Open (Alert)",
        "live_checker": "Live Packet Anomaly Checker",
        "duration": "Duration",
        "wrong_fragment": "Wrong Fragment",
        "src_bytes": "Source Bytes",
        "urgent": "Urgent Packets",
        "dst_bytes": "Destination Bytes",
        "hot": "Hot Indicators",
        "check_btn": "Check Anomaly",
        "alert_msg": "WARNING: This packet is an ANOMALY (Potential Attack)!",
        "safe_msg": "SAFE: This packet is normal traffic.",
        "saved_msg": "Saved to your account history successfully!",
        "pdf_btn": "Download PDF Report",
        "csv_btn": "Download CSV List",
        "history_title": "Your Search History",
        "history_desc": "Here you can see all your past tests.",
        "clear_history": "Clear History",
        "history_cleared": "History cleared!",
        "no_history": "No history found yet.",
        "lang_label": "Choose Language / Dooro Luqadda / اختر اللغة",
    },
    "Soomaali": {
        "title": "Madasha Amniga Shabakadda",
        "subtitle": "Fadlan dooro luqadaada oo soo gal ama sameyso akoon",
        "login_tab": "🔑 Gal (Login)",
        "signup_tab": "📝 Akoon Cusub (Sign Up)",
        "username": "Magaca isticmaalaha (Username)",
        "password": "Erayga sirta ah (Password)",
        "confirm_password": "Xaqiiji erayga sirta ah",
        "login_btn": "Gal (Login)",
        "signup_btn": "Sameyso Akoon",
        "success_login": "Si guul leh ayaad u gashay!",
        "error_login": "Magaca ama erayga sirta ah waa qalad!",
        "success_signup": "Akoonkaaga waa la sameeyay oo waa la kaydiyay!",
        "welcome": "Ku soo dhowow",
        "logout": "Ka bax (Logout)",
        "data_source": "📁 Xogta halkee laga keenayaa?",
        "default_files": "Faylasha Mashruuca (Default)",
        "upload_file": "Soo Geli Fayl Cusub (Upload CSV/TXT)",
        "upload_label": "Soo geli faylkaaga xogta (CSV ama TXT)",
        "select_dataset": "Dooro Faylka Xogta:",
        "main_title": (
            "Advanced Network Traffic Security & Anomaly Analyzer"
        ),
        "main_desc": (
            "Dashboard-kan heerka sare ah wuxuu kuu sahlayaa inaad la socoto"
            " halista shabakadda, falanqaynta waqtiga, tijaabiso xog cusub, oo aad"
            " keydiso taariikhdaada."
        ),
        "total_traffic": "Wadarta Taraafikada",
        "normal_traffic": "Taraafikada Caadiga ah",
        "anomalies": "Cilladaha / Halista",
        "risk_percentage": "Heerka Halista (%)",
        "tab1": "📊 Dashboard & Time-Series Trend",
        "tab2": "⚡ Foomka Baarista Tooska ah (Live Predict)",
        "tab3": "📥 Soo Dejinta Warbixinta (PDF / CSV)",
        "tab4": "📜 Taariikhdayda (Saved History)",
        "security_distribution": "Qeybsanaanta Amniga",
        "normal": "Caadi (Normal)",
        "anomaly": "Halis (Anomalies)",
        "trend_chart": "Isbeddelka Waqtiga (Trend Line Chart)",
        "security_events": "Liiska Dhacdooyinka Amniga (Security Events)",
        "filter_status": "Kala sooc heerka:",
        "all": "Dhammaan",
        "open_alert": "Open (Alert)",
        "live_checker": "Ku Tijaabi Baakidh Cusub (Live Packet Checker)",
        "duration": "Duration (Mugga Waqtiga)",
        "wrong_fragment": "Wrong Fragment",
        "src_bytes": "Source Bytes (Byte-ka ka yimid)",
        "urgent": "Urgent Packets",
        "dst_bytes": "Destination Bytes (Byte-ka tagay)",
        "hot": "Hot Indicators",
        "check_btn": "Baaro Baakidhkan (Check Anomaly)",
        "alert_msg": "🚨 DIGNIIN: Baakidhkani waa HALIS (Anomaly / Potential Attack)!",
        "safe_msg": "✅ WAA AMMAAN: Baakidhkani waa mid caadi ah (Normal Traffic).",
        "saved_msg": "💾 Taariikhda baaritaankaan waxaa si guul leh loogu keydiyay akoonkaaga!",
        "pdf_btn": "📄 Soo Degso Warbixinta PDF",
        "csv_btn": "📥 Soo Degso Liiska CSV",
        "history_title": "Taariikhda Baaritaannada",
        "history_desc": "Halkan waxaad ku arkeysaa dhammaan tijaabooyinkii aad horey u samaysay.",
        "clear_history": "🗑️ Masax Taariikhdaada",
        "history_cleared": "Taariikhdaada waa la tirtiray!",
        "no_history": "Weli ma jiro wax taariikh ah oo ku keydsan akoonkaaga.",
        "lang_label": "Dooro Luqadda",
    },
    "العربية": {
        "title": "منصة أمن شبكات الحاسوب",
        "subtitle": "يرجى اختيار اللغة وتسجيل الدخول أو إنشاء حساب",
        "login_tab": "🔑 تسجيل الدخول",
        "signup_tab": "📝 إنشاء حساب جديد",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "confirm_password": "تأكيد كلمة المرور",
        "login_btn": "دخول",
        "signup_btn": "إنشاء حساب",
        "success_login": "تم تسجيل الدخول بنجاح!",
        "error_login": "اسم المستخدم أو كلمة المرور غير صحيحة!",
        "success_signup": "تم إنشاء الحساب بنجاح وحفظه!",
        "welcome": "أهلاً بك",
        "logout": "تسجيل الخروج",
        "data_source": "📁 من أين تحصل على البيانات؟",
        "default_files": "ملفات المشروع (افتراضي)",
        "upload_file": "رفع ملف جديد (CSV/TXT)",
        "upload_label": "قم برفع ملف البيانات الخاص بك (CSV أو TXT)",
        "select_dataset": "اختر ملف البيانات:",
        "main_title": (
            "Advanced Network Traffic Security & Anomaly Analyzer"
        ),
        "main_desc": (
            "تتيح لك لوحة التحكم هذه مراقبة تهديدات الشبكة، تحليل السلاسل"
            " الزمنية، واختبار بيانات جديدة وحفظ السجل."
        ),
        "total_traffic": "إجمالي حركة المرور",
        "normal_traffic": "حركة المرور العادية",
        "anomalies": "التهديدات / الشذوذ",
        "risk_percentage": "نسبة الخطر (%)",
        "tab1": "📊 لوحة التحكم واتجاه السلسلة الزمنية",
        "tab2": "⚡ الفحص المباشر للحزم",
        "tab3": "📥 تنزيل التقارير (PDF / CSV)",
        "tab4": "📜 السجل المحفوظ",
        "security_distribution": "توزيع الأمان",
        "normal": "عادي (Normal)",
        "anomaly": "تهديد (Anomalies)",
        "trend_chart": "مخطط الاتجاه الزمني",
        "security_events": "قائمة أحداث الأمان",
        "filter_status": "تصفية حسب الحالة:",
        "all": "الكل",
        "open_alert": "تنبيه مفتوح",
        "live_checker": "فاحص الحزم المباشر",
        "duration": "المدة الزمنية",
        "wrong_fragment": "الجزئية الخاطئة",
        "src_bytes": "بايت المصدر",
        "urgent": "الحزم العاجلة",
        "dst_bytes": "بايت الوجهة",
        "hot": "مؤشرات ساخنة",
        "check_btn": "فحص الحزمة",
        "alert_msg": "🚨 تحذير: هذه الحزمة تشكل خطراً / هجوم محتمل!",
        "safe_msg": "✅ آمن: هذه الحزمة طبيعية.",
        "saved_msg": "💾 تم حفظ نتيجة الفحص في سجل حسابك بنجاح!",
        "pdf_btn": "📄 تنزيل تقرير PDF",
        "csv_btn": "📥 تنزيل قائمة CSV",
        "history_title": "سجل عمليات البحث",
        "history_desc": "هنا يمكنك رؤية جميع اختباراتك السابقة.",
        "clear_history": "🗑️ مسح السجل",
        "history_cleared": "تم مسح السجل بنجاح!",
        "no_history": "لا توجد أي سجلات محفوظة في حسابك حتى الآن.",
        "lang_label": "اختر اللغة",
    },
}


def load_users():
  if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {"admin": "admin123"}
  return {"admin": "admin123"}


def save_users(users_dict):
  with open(USERS_FILE, "w") as f:
    json.dump(users_dict, f)


def load_history():
  if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
      try:
        return json.load(f)
      except json.JSONDecodeError:
        return {}
  return {}


def save_history(history_dict):
  with open(HISTORY_FILE, "w") as f:
    json.dump(history_dict, f)


# Session State
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
if "users" not in st.session_state:
  st.session_state.users = load_users()
if "username" not in st.session_state:
  st.session_state.username = ""
if "language" not in st.session_state:
  st.session_state.language = "Soomaali"

# Active Language Dictionary
t = TRANSLATIONS[st.session_state.language]

# --- LOGIN & SIGNUP SCREEN ---
if not st.session_state.logged_in:
  col_lang1, col_lang2, col_lang3 = st.columns([1, 2, 1])
  with col_lang2:
    selected_lang = st.selectbox(
        t["lang_label"],
        ["Soomaali", "English", "العربية"],
        index=["Soomaali", "English", "العربية"].index(
            st.session_state.language
        ),
    )
    if selected_lang != st.session_state.language:
      st.session_state.language = selected_lang
      st.rerun()

  t = TRANSLATIONS[st.session_state.language]

  st.markdown(
      f"<h1 style='text-align: center; color: #2c3e50;'>🛡️ {t['title']}</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      f"<h4 style='text-align: center; color: #7f8c8d;'>{t['subtitle']}</h4>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1.5, 1])

  with col2:
    tab1, tab2 = st.tabs([t["login_tab"], t["signup_tab"]])

    with tab1:
      login_user = st.text_input(t["username"], key="login_user")
      login_pass = st.text_input(
          t["password"], type="password", key="login_pass"
      )

      if st.button(t["login_btn"], use_container_width=True):
        users_db = load_users()
        if login_user in users_db and users_db[login_user] == login_pass:
          st.session_state.logged_in = True
          st.session_state.username = login_user
          st.success(t["success_login"])
          st.rerun()
        else:
          st.error(t["error_login"])

    with tab2:
      new_user = st.text_input(t["username"], key="new_user")
      new_pass = st.text_input(
          t["password"], type="password", key="new_pass"
      )
      confirm_pass = st.text_input(
          t["confirm_password"], type="password", key="confirm_pass"
      )

      if st.button(t["signup_btn"], use_container_width=True):
        users_db = load_users()
        if not new_user or not new_pass:
          st.warning("Fadlan buuxi dhammaan meelaha banaan!")
        elif new_user in users_db:
          st.error("Magacaan isticmaalaha waa la qaatay.")
        elif new_pass != confirm_pass:
          st.error("Erayada sirta ah isku mid ma aha!")
        else:
          users_db[new_user] = new_pass
          save_users(users_db)
          st.session_state.users = users_db
          st.success(t["success_signup"])

# --- MAIN ADVANCED DASHBOARD ---
else:
  st.sidebar.title(
      f"👋 {t['welcome']}, {st.session_state.username} ({st.session_state.language})"
  )
  st.sidebar.markdown("---")

  upload_option = st.sidebar.radio(
      t["data_source"], [t["default_files"], t["upload_file"]]
  )

  uploaded_file = None
  dataset_choice = "KDDTrain+.txt"

  if upload_option == t["upload_file"]:
    uploaded_file = st.sidebar.file_uploader(
        t["upload_label"], type=["txt", "csv"]
    )
  else:
    dataset_choice = st.sidebar.selectbox(
        t["select_dataset"], ["KDDTrain+.txt", "KDDTest+.txt"]
    )

  st.sidebar.markdown("---")
  if st.sidebar.button(t["logout"], type="primary"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

  st.title(f"🛡️ {t['main_title']}")
  st.markdown(t["main_desc"])


  @st.cache_data
  def load_and_process_data(file_path_or_buffer, is_uploaded=False):
    columns = [
        "duration",
        "protocol_type",
        "service",
        "flag",
        "src_bytes",
        "dst_bytes",
        "land",
        "wrong_fragment",
        "urgent",
        "hot",
        "num_failed_logins",
        "logged_in",
        "num_compromised",
        "root_shell",
        "su_attempted",
        "num_root",
        "num_file_creations",
        "num_shells",
        "num_access_files",
        "num_outbound_cmds",
        "is_host_login",
        "is_guest_login",
        "count",
        "srv_count",
        "serror_rate",
        "srv_serror_rate",
        "rerror_rate",
        "srv_rerror_rate",
        "same_srv_rate",
        "diff_srv_rate",
        "srv_diff_host_rate",
        "dst_host_count",
        "dst_host_srv_count",
        "dst_host_same_srv_rate",
        "dst_host_diff_srv_rate",
        "dst_host_same_src_port_rate",
        "dst_host_srv_diff_host_rate",
        "dst_host_serror_rate",
        "dst_host_srv_serror_rate",
        "dst_host_rerror_rate",
        "dst_host_srv_rerror_rate",
        "class",
    ]

    if is_uploaded:
      if file_path_or_buffer is not None:
        df = pd.read_csv(file_path_or_buffer, names=columns, low_memory=False)
      else:
        return None
    else:
      if not os.path.exists(file_path_or_buffer):
        return None
      df = pd.read_csv(file_path_or_buffer, names=columns, low_memory=False)

    numeric_features = [
        "duration",
        "src_bytes",
        "dst_bytes",
        "wrong_fragment",
        "urgent",
        "hot",
    ]
    for col in numeric_features:
      df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    X = df[numeric_features]
    model = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly_score"] = model.fit_predict(X)
    df["Status"] = df["anomaly_score"].apply(
        lambda x: "Open (Alert)" if x == -1 else "Normal"
    )
    df["Packet_Index"] = range(1, len(df) + 1)
    return df


  if upload_option == t["upload_file"] and uploaded_file is None:
    st.warning("⚠️ Fadlan soo geli faylkaaga xogta.")
    df = None
  else:
    if upload_option == t["upload_file"]:
      with st.spinner("Fadlan sug..."):
        df = load_and_process_data(uploaded_file, is_uploaded=True)
    else:
      with st.spinner("Fadlan sug..."):
        df = load_and_process_data(dataset_choice, is_uploaded=False)

  if df is not None:
    total_traffic = len(df)
    anomalies = df[df["anomaly_score"] == -1]
    normal_traffic = df[df["anomaly_score"] == 1]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t["total_traffic"], f"{total_traffic:,}")
    col2.metric(t["normal_traffic"], f"{len(normal_traffic):,}")
    col3.metric(t["anomalies"], f"{len(anomalies):,}", delta_color="inverse")
    col4.metric(
        t["risk_percentage"],
        f"{(len(anomalies)/total_traffic)*100:.2f}%" if total_traffic > 0 else "0%",
        delta_color="off",
    )

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [t["tab1"], t["tab2"], t["tab3"], t["tab4"]]
    )

    with tab1:
      chart_col, table_col = st.columns([1.2, 1.8])

      with chart_col:
        st.subheader(t["security_distribution"])
        fig = px.pie(
            values=[len(normal_traffic), len(anomalies)],
            names=[t["normal"], t["anomaly"]],
            hole=0.6,
            color_discrete_sequence=["#2ecc71", "#e74c3c"],
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(t["trend_chart"])
        trend_fig = px.scatter(
            df.head(1000),
            x="Packet_Index",
            y="src_bytes",
            color="Status",
            color_discrete_map={"Normal": "#2ecc71", "Open (Alert)": "#e74c3c"},
        )
        trend_fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=250)
        st.plotly_chart(trend_fig, use_container_width=True)

      with table_col:
        st.subheader(t["security_events"])
        status_filter = st.selectbox(
            t["filter_status"], [t["all"], t["open_alert"]]
        )
        display_df = (
            anomalies if status_filter == t["open_alert"] else df
        )

        st.dataframe(
            display_df[
                [
                    "protocol_type",
                    "service",
                    "flag",
                    "src_bytes",
                    "dst_bytes",
                    "Status",
                ]
            ].head(50),
            use_container_width=True,
            height=500,
        )

    with tab2:
      st.subheader(t["live_checker"])
      numeric_features = [
          "duration",
          "src_bytes",
          "dst_bytes",
          "wrong_fragment",
          "urgent",
          "hot",
      ]
      model_live = IsolationForest(contamination=0.05, random_state=42)
      model_live.fit(df[numeric_features])

      with st.form("prediction_form"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
          duration = st.number_input(t["duration"], min_value=0.0, value=0.0)
          wrong_fragment = st.number_input(
              t["wrong_fragment"], min_value=0, value=0
          )
        with f_col2:
          src_bytes = st.number_input(
              t["src_bytes"], min_value=0, value=100
          )
          urgent = st.number_input(t["urgent"], min_value=0, value=0)
        with f_col3:
          dst_bytes = st.number_input(
              t["dst_bytes"], min_value=0, value=0
          )
          hot = st.number_input(t["hot"], min_value=0, value=0)

        submit_btn = st.form_submit_button(t["check_btn"])

        if submit_btn:
          input_data = pd.DataFrame(
              [[duration, src_bytes, dst_bytes, wrong_fragment, urgent, hot]],
              columns=numeric_features,
          )
          prediction = model_live.predict(input_data)
          result_str = (
              "🚨 HALIS (Anomaly)"
              if prediction[0] == -1
              else "✅ AMMAAN (Normal)"
          )

          all_history = load_history()
          user_history = all_history.get(st.session_state.username, [])
          current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          user_history.insert(
              0,
              {
                  "Time": current_time,
                  "Duration": duration,
                  "Src_Bytes": src_bytes,
                  "Dst_Bytes": dst_bytes,
                  "Result": result_str,
              },
          )
          all_history[st.session_state.username] = user_history
          save_history(all_history)

          if prediction[0] == -1:
            st.error(t["alert_msg"])
          else:
            st.success(t["safe_msg"])
          st.info(t["saved_msg"])

    with tab3:
      st.subheader("📥 Download Reports")


      def create_pdf_report(anomalies_df):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(
            200, 10, txt="Network Security Anomaly Report", ln=True, align="C"
        )
        pdf.set_font("Arial", "", 12)
        pdf.cell(
            200,
            10,
            txt=f"Total Anomalies Detected: {len(anomalies_df)}",
            ln=True,
            align="C",
        )
        pdf.ln(10)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(30, 10, "Protocol", 1)
        pdf.cell(40, 10, "Service", 1)
        pdf.cell(30, 10, "Flag", 1)
        pdf.cell(40, 10, "Src Bytes", 1)
        pdf.cell(40, 10, "Dst Bytes", 1)
        pdf.ln()
        pdf.set_font("Arial", "", 9)
        for index, row in anomalies_df.head(30).iterrows():
          pdf.cell(30, 10, str(row["protocol_type"]), 1)
          pdf.cell(40, 10, str(row["service"]), 1)
          pdf.cell(30, 10, str(row["flag"]), 1)
          pdf.cell(40, 10, str(row["src_bytes"]), 1)
          pdf.cell(40, 10, str(row["dst_bytes"]), 1)
          pdf.ln()
        return pdf.output(dest="S").encode("latin1")

      pdf_data = create_pdf_report(anomalies)

      col_dl1, col_dl2 = st.columns(2)
      with col_dl1:
        st.download_button(
            label=t["pdf_btn"],
            data=pdf_data,
            file_name="network_security_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
      with col_dl2:
        csv_data = anomalies.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=t["csv_btn"],
            data=csv_data,
            file_name="network_anomalies_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with tab4:
      st.subheader(t["history_title"])
      st.markdown(t["history_desc"])

      all_history = load_history()
      user_history = all_history.get(st.session_state.username, [])

      if user_history:
        history_df = pd.DataFrame(user_history)
        st.dataframe(history_df, use_container_width=True)

        if st.button(t["clear_history"]):
          all_history[st.session_state.username] = []
          save_history(all_history)
          st.success(t["history_cleared"])
          st.rerun()
      else:
        st.info(t["no_history"])
