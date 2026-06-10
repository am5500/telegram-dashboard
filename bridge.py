import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

# مسار ملف app.py الخاص بك (عدله حسب مكانه الحقيقي على جهازك)
STREAMLIT_SCRIPT_PATH = r"C:\Users\user\Desktop\N8n py\app.py"


@app.route("/run", methods=["GET", "POST"])
def run_dashboard():
    try:
        # تشغيل Streamlit في الخلفية بدون حجز الـ terminal
        subprocess.Popen(["streamlit", "run", STREAMLIT_SCRIPT_PATH])
        return (
            jsonify(
                {
                    "status": "success",
                    "message": "Streamlit dashboard is launching!",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # تشغيل السيرفر المحلي على بورت 5000
    app.run(host="0.0.0.0", port=5000)