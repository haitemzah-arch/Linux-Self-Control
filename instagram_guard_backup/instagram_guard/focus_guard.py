#!/usr/bin/env python3
"""
Instagram Messages Guard - النسخة النهائية الكاملة
تشغيل: python3 focus_guard.py
"""

import subprocess
import time
import sys
import os
import io
import numpy as np
from PIL import Image, ImageDraw

# ═══════════════════════════════════════════════
#              الإعدادات
# ═══════════════════════════════════════════════

# إحداثيات الـ Toolbar (بدون أيقونة البروفايل)
TOOLBAR_X1 = 216
TOOLBAR_Y1 = 2175
TOOLBAR_X2 = 1080
TOOLBAR_Y2 = 2285

# منطقة النقطة الحمراء - نسوّدها دائماً قبل المقارنة
DOT_REL_X1 = 471 - TOOLBAR_X1
DOT_REL_Y1 = 2196 - TOOLBAR_Y1
DOT_REL_X2 = 540 - TOOLBAR_X1
DOT_REL_Y2 = 2254 - TOOLBAR_Y1

# إحداثيات العنوان العلوي (لكشف صفحة الإعدادات)
HEADER_X1 = 552
HEADER_Y1 = 142
HEADER_X2 = 882
HEADER_Y2 = 208

# منطقة أيقونة الريلز المرسل (تظهر عند فتح ريلز من محادثة)
REEL_ICON_X1, REEL_ICON_Y1 = 56,  164
REEL_ICON_X2, REEL_ICON_Y2 = 119, 202
REEL_THRESHOLD = 0.90

# زر الرسائل
MSG_BTN_X = 540
MSG_BTN_Y = 2230

# ─── حدود التشابه ───────────────────────────
# فوق 88%        → مسموح ✅ (رسائل أو بروفايل)
# بين 50% و 88%  → ممنوع 🚫 (ريلز، فييد، إكسبلورر)
# أقل من 50%     → مسموح ✅ (داخل محادثة أو إعدادات)
IN_MESSAGES_MIN    = 0.88
TOOLBAR_HIDDEN_MAX = 0.50
HEADER_MATCH_MIN   = 0.85

CHECK_INTERVAL = 0.6
INSTAGRAM_PACKAGE = "com.instagram.android"

SCRIPT_DIR          = os.path.dirname(os.path.abspath(__file__))
REF_TOOLBAR         = os.path.join(SCRIPT_DIR, "ref_no_dot.jpg")
REF_SETTINGS_HEADER = os.path.join(SCRIPT_DIR, "ref_settings_header.png")
REF_REEL_ICON       = os.path.join(SCRIPT_DIR, "tg_ref_icon.png")

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

def is_instagram_open() -> bool:
    out = adb(["shell", "dumpsys", "window"]).decode(errors="ignore")
    lines = [l for l in out.splitlines() if "mCurrentFocus" in l]
    if not lines:
        return False
    return INSTAGRAM_PACKAGE in lines[0]

def take_screenshot() -> Image.Image:
    raw = adb(["exec-out", "screencap", "-p"], timeout=5)
    return Image.open(io.BytesIO(raw)).convert("RGB")

def mask_dot(img: Image.Image) -> Image.Image:
    img = img.copy()
    draw = ImageDraw.Draw(img)
    draw.rectangle([DOT_REL_X1, DOT_REL_Y1, DOT_REL_X2, DOT_REL_Y2], fill=(0, 0, 0))
    return img

def go_home():
    adb(["shell", "input", "keyevent", "KEYCODE_HOME"])

def tap(x, y):
    adb(["shell", "input", "tap", str(x), str(y)])

# ═══════════════════════════════════════════════

def prepare(img: Image.Image, size=(300, 30)) -> np.ndarray:
    arr = np.array(img.resize(size, Image.LANCZOS), dtype=np.float32).flatten()
    arr -= arr.mean()
    return arr

def similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)

def check_toolbar(screen: Image.Image, toolbar_ref: np.ndarray) -> tuple:
    toolbar = mask_dot(screen.crop((TOOLBAR_X1, TOOLBAR_Y1, TOOLBAR_X2, TOOLBAR_Y2)))
    score = similarity(prepare(toolbar), toolbar_ref)
    if score >= IN_MESSAGES_MIN:
        return "allowed", score
    elif score <= TOOLBAR_HIDDEN_MAX:
        return "hidden", score
    else:
        return "blocked", score

def check_header(screen: Image.Image, header_ref: np.ndarray) -> tuple:
    header = screen.crop((HEADER_X1, HEADER_Y1, HEADER_X2, HEADER_Y2))
    score = similarity(prepare(header, size=(200, 25)), header_ref)
    return score >= HEADER_MATCH_MIN, score

def check_reel_icon(screen: Image.Image, reel_ref: np.ndarray) -> tuple:
    region = screen.crop((REEL_ICON_X1, REEL_ICON_Y1, REEL_ICON_X2, REEL_ICON_Y2))
    score = similarity(prepare(region, size=(50, 30)), reel_ref)
    return score >= REEL_THRESHOLD, score

# ═══════════════════════════════════════════════

def main():
    print("=" * 50)
    print("    📵  Instagram Messages Guard  📵")
    print("=" * 50)

    check_adb()

    # تحميل صورة مرجع الـ Toolbar
    if not os.path.exists(REF_TOOLBAR):
        print(f"❌  ملف غير موجود: {REF_TOOLBAR}")
        sys.exit(1)
    toolbar_ref = prepare(mask_dot(Image.open(REF_TOOLBAR).convert("RGB")))
    print(f"✅  مرجع الـ Toolbar محمّل")

    # تحميل صورة مرجع الإعدادات
    header_ref = None
    if os.path.exists(REF_SETTINGS_HEADER):
        header_ref = prepare(Image.open(REF_SETTINGS_HEADER).convert("RGB"), size=(200, 25))
        print(f"🔒  صفحة الإعدادات محظورة")
    else:
        print(f"⚠️   ملف غير موجود: {REF_SETTINGS_HEADER}")

    # تحميل صورة مرجع أيقونة الريلز
    reel_ref = None
    if os.path.exists(REF_REEL_ICON):
        reel_ref = prepare(Image.open(REF_REEL_ICON).convert("RGB"), size=(50, 30))
        print(f"🔒  أيقونة الريلز المرسل محظورة")
    else:
        print(f"⚠️   ملف غير موجود: {REF_REEL_ICON}")

    print(f"\n المنطق:")
    print(f"   فوق 88%        → رسائل/بروفايل ✅")
    print(f"   بين 50% و 88%  → ريلز/فييد/إكسبلورر 🚫 يُخرجك")
    print(f"   أقل من 50%     → داخل محادثة/إعدادات ✅")
    print(f"   صفحة الإعدادات → يُخرجك فوراً 🔒")
    print(f"   أيقونة الريلز  → يُخرجك فوراً 🔒")
    print(f"\n🚀  بدأ المراقبة... Ctrl+C للإيقاف\n")

    was_open = False
    count = 0

    try:
        while True:
            t0 = time.time()
            is_open = is_instagram_open()

            if is_open and not was_open:
                print("📱  انستقرام فُتح → الانتقال للرسائل...")
                time.sleep(1.5)
                tap(MSG_BTN_X, MSG_BTN_Y)
                time.sleep(1.2)

            was_open = is_open

            if is_open:
                try:
                    screen = take_screenshot()
                    count += 1

                    # فحص صفحة الإعدادات أولاً
                    if header_ref is not None:
                        blocked_page, hscore = check_header(screen, header_ref)
                        if blocked_page:
                            print(f"\n🔒  إعدادات محظورة! ({hscore:.2%}) → خروج")
                            go_home()
                            time.sleep(0.5)
                            continue

                    # فحص أيقونة الريلز المرسل
                    if reel_ref is not None:
                        reel_open, rscore = check_reel_icon(screen, reel_ref)
                        if reel_open:
                            print(f"\n🔒  ريلز مفتوح! ({rscore:.2%}) → خروج")
                            go_home()
                            time.sleep(0.5)
                            continue

                    # فحص الـ Toolbar
                    status, score = check_toolbar(screen, toolbar_ref)

                    if status == "allowed":
                        sys.stdout.write(f"\r✅  مسموح          | {score:.2%} | #{count}   ")
                        sys.stdout.flush()
                    elif status == "hidden":
                        sys.stdout.write(f"\r💬  محادثة/إعدادات | {score:.2%} | #{count}   ")
                        sys.stdout.flush()
                    else:
                        print(f"\n🚫  ممنوع! ({score:.2%}) → خروج")
                        go_home()
                        time.sleep(0.5)

                except Exception as e:
                    print(f"⚠️  {e}")

            time.sleep(max(0, CHECK_INTERVAL - (time.time() - t0)))

    except KeyboardInterrupt:
        print(f"\n\n⏹️  توقفت. فحوصات: {count}")

if __name__ == "__main__":
    main()
