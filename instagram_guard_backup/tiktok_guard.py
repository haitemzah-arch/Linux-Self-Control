#!/usr/bin/env python3
"""
TikTok Messages Guard - النسخة النهائية
تشغيل: python3 tiktok_guard.py
"""

import subprocess
import time
import sys
import os
import io
import numpy as np
from PIL import Image

# ═══════════════════════════════════════════════
#              الإعدادات
# ═══════════════════════════════════════════════

# زر الرسائل - عند فتح التطبيق
MSG_BTN_X = 755
MSG_BTN_Y = 2188

# منطقة زر البيت
HOME_X1, HOME_Y1 = 52,  2148
HOME_X2, HOME_Y2 = 162, 2260

# منطقة رمز @
ICON_X1, ICON_Y1 = 938, 2165
ICON_X2, ICON_Y2 = 1016, 2240

# حد التشابه
THRESHOLD = 0.90

CHECK_INTERVAL = 0.6
TIKTOK_PACKAGE = "com.zhiliaoapp.musically"

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
REF_HOME    = os.path.join(SCRIPT_DIR, "tt_ref_home.png")
REF_ICON    = os.path.join(SCRIPT_DIR, "tt_ref_new.png")

# ═══════════════════════════════════════════════

def adb(cmd: list, timeout=5) -> bytes:
    result = subprocess.run(["adb"] + cmd, capture_output=True, timeout=timeout)
    return result.stdout

def check_adb():
    out = adb(["devices"]).decode()
    lines = [l for l in out.strip().splitlines() if "device" in l and "List" not in l]
    if not lines:
        print("❌  لا يوجد جهاز متصل!")
        sys.exit(1)
    print(f"✅  جهاز متصل: {lines[0].split()[0]}")

def is_tiktok_open() -> bool:
    out = adb(["shell", "dumpsys", "window"]).decode(errors="ignore")
    lines = [l for l in out.splitlines() if "mCurrentFocus" in l]
    return bool(lines) and TIKTOK_PACKAGE in lines[0]

def take_screenshot() -> Image.Image:
    raw = adb(["exec-out", "screencap", "-p"], timeout=5)
    return Image.open(io.BytesIO(raw)).convert("RGB")

def tap(x, y):
    adb(["shell", "input", "tap", str(x), str(y)])

def go_home():
    adb(["shell", "input", "keyevent", "KEYCODE_HOME"])

# ═══════════════════════════════════════════════

TARGET_SIZE = (50, 50)

def prepare(img: Image.Image) -> np.ndarray:
    arr = np.array(img.resize(TARGET_SIZE, Image.LANCZOS), dtype=np.float32).flatten()
    arr -= arr.mean()
    return arr

def similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def is_forbidden(screen: Image.Image, ref_home: np.ndarray, ref_icon: np.ndarray) -> tuple:
    # فحص زر البيت
    home_region = screen.crop((HOME_X1, HOME_Y1, HOME_X2, HOME_Y2))
    home_score = similarity(prepare(home_region), ref_home)
    if home_score >= THRESHOLD:
        return True, "زر البيت", home_score

    # فحص رمز @
    icon_region = screen.crop((ICON_X1, ICON_Y1, ICON_X2, ICON_Y2))
    icon_score = similarity(prepare(icon_region), ref_icon)
    if icon_score >= THRESHOLD:
        return True, "رمز @", icon_score

    return False, "", max(home_score, icon_score)

# ═══════════════════════════════════════════════

def main():
    print("=" * 50)
    print("    📵  TikTok Messages Guard  📵")
    print("=" * 50)

    check_adb()

    for path in [REF_HOME, REF_ICON]:
        if not os.path.exists(path):
            print(f"❌  ملف غير موجود: {path}")
            sys.exit(1)

    ref_home = prepare(Image.open(REF_HOME).convert("RGB"))
    ref_icon = prepare(Image.open(REF_ICON).convert("RGB"))
    print(f"✅  مرجع محمّل: زر البيت")
    print(f"✅  مرجع محمّل: رمز @")
    print(f"\n🚀  بدأ المراقبة... Ctrl+C للإيقاف\n")

    was_open = False
    count = 0

    try:
        while True:
            t0 = time.time()
            is_open = is_tiktok_open()

            if is_open and not was_open:
                print("📱  تيك توك فُتح → الانتقال للرسائل...")
                time.sleep(1.5)
                tap(MSG_BTN_X, MSG_BTN_Y)
                time.sleep(1.2)

            was_open = is_open

            if is_open:
                try:
                    screen = take_screenshot()
                    forbidden, reason, score = is_forbidden(screen, ref_home, ref_icon)
                    count += 1

                    if forbidden:
                        print(f"\n🚫  {reason} ({score:.2%}) → خروج")
                        go_home()
                        time.sleep(0.5)
                    else:
                        sys.stdout.write(f"\r✅  آمن | {score:.2%} | #{count}   ")
                        sys.stdout.flush()

                except Exception as e:
                    print(f"⚠️  {e}")

            time.sleep(max(0, CHECK_INTERVAL - (time.time() - t0)))

    except KeyboardInterrupt:
        print(f"\n\n⏹️  توقفت. فحوصات: {count}")

if __name__ == "__main__":
    main()
