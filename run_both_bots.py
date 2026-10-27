import os
import sys
import time
import subprocess

def run_both():
    print("=" * 60)
    print("🚀 IKKALA TELEGRAM BOTNI BIRGALIKDA 24/7 ISHGA TUSHIRISH")
    print("1. Universal Super Saver Bot")
    print("2. Ish Topish va Ish Berish Boti (@ish_topish_teambot)")
    print("=" * 60)

    p_job = subprocess.Popen([sys.executable, "ish_topish_bot.py"])
    print(f"✅ Ish topish boti yoqildi (PID: {p_job.pid})")

    p_uni = None
    if os.path.exists("universal_save_bot.py"):
        p_uni = subprocess.Popen([sys.executable, "universal_save_bot.py"])
        print(f"✅ Universal Save bot yoqildi (PID: {p_uni.pid})")

    while True:
        time.sleep(15)
        if p_job.poll() is not None:
            print("⚠️ Ish topish boti to'xtadi. Qayta yoqilmoqda...")
            time.sleep(3)
            p_job = subprocess.Popen([sys.executable, "ish_topish_bot.py"])

        if p_uni and p_uni.poll() is not None:
            print("⚠️ Universal bot to'xtadi. Qayta yoqilmoqda...")
            time.sleep(3)
            p_uni = subprocess.Popen([sys.executable, "universal_save_bot.py"])

if __name__ == "__main__":
    run_both()
