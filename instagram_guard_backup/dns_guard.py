#!/usr/bin/env python3
"""
DNS Settings Guard
يمنع الدخول لصفحة الاتصال والمشاركة في إعدادات الهاتف
تشغيل: python3 dns_guard.py
"""

import subprocess
import time
import sys

# ═══════════════════════════════════════════════
#              الإعدادات
# ═══════════════════════════════════════════════

# الكلمات التي إذا وُجدت في عنوان الصفحة → أخرج فوراً
BLOCKED_TITLES = [
    "الاتصال والمشاركة",
    "نظام أسماء النطاقات الخاص",
    "DNS الخاص",
]

# حزمة الإعدادات
SETTINGS_PACKAGE = "com.android.settings"

# سرعة الفحص
CHECK_INTERVAL = 1.0

# ═══════════════════════════════════════════════

def adb(cmd: list, timeout=5) -> str:
    result = subprocess.run(["adb"] + cmd, capture_output=True, timeout=timeout)
    return result.stdout.decode(errors="ignore")

def check_adb():
    out = adb(["devices"])
    lines = [l for l in out.strip().splitlines() if "device" in l and "List" not in l]
    if not lines:
        print("❌  لا يوجد جهاز متصل!")
        sys.exit(1)
    print(f"✅  جهاز متصل: {lines[0].split()[0]}")

def is_settings_open() -> bool:
    out = adb(["shell", "dumpsys", "window"])
    lines = [l for l in out.splitlines() if "mCurrentFocus" in l]
    if not lines:
        return False
    return SETTINGS_PACKAGE in lines[0]

def get_current_title() -> str:
    """قراءة عنوان الصفحة الحالية عبر uiautomator"""
    adb(["shell", "uiautomator", "dump", "/sdcard/ui.xml"], timeout=4)
    xml = adb(["shell", "cat", "/sdcard/ui.xml"], timeout=3)
    # نبحث عن عنوان الصفحة في action_bar_title
    import re
    matches = re.findall(r'action_bar_title[^>]*text="([^"]+)"', xml)
    if matches:
        return matches[0]
    # بديل: أول text في action_bar
    matches2 = re.findall(r'action_bar[^>]*text="([^"]+)"', xml)
    if matches2:
        return matches2[0]
    return ""

def is_blocked_page() -> tuple:
    """هل الصفحة الحالية محظورة؟"""
    try:
        # طريقة سريعة: نقرأ الـ XML مباشرة بدون dump جديد
        adb(["shell", "uiautomator", "dump", "/sdcard/ui.xml"], timeout=4)
        xml = adb(["shell", "cat", "/sdcard/ui.xml"], timeout=3)

        for title in BLOCKED_TITLES:
            if title in xml:
                return True, title
        return False, ""
    except Exception:
        return False, ""

def go_back():
    adb(["shell", "input", "keyevent", "KEYCODE_BACK"])

# ═══════════════════════════════════════════════

def main():
    print("=" * 50)
    print("    🔒  DNS Settings Guard  🔒")
    print("=" * 50)

    check_adb()

    print(f"\n الصفحات المحظورة:")
    for t in BLOCKED_TITLES:
        print(f"   🚫 {t}")
    print(f"\n🚀  بدأ المراقبة... Ctrl+C للإيقاف\n")

    count = 0

    try:
        while True:
            t0 = time.time()

            if is_settings_open():
                blocked, title = is_blocked_page()
                count += 1

                if blocked:
                    print(f"\n🚫  صفحة محظورة: {title} → رجوع!")
                    go_back()
                    time.sleep(0.5)
                else:
                    sys.stdout.write(f"\r✅  إعدادات آمنة | #{count}   ")
                    sys.stdout.flush()
            else:
                sys.stdout.write(f"\r💤  الإعدادات مغلقة | #{count}   ")
                sys.stdout.flush()

            time.sleep(max(0, CHECK_INTERVAL - (time.time() - t0)))

    except KeyboardInterrupt:
        print(f"\n\n⏹️  توقفت. فحوصات: {count}")

if __name__ == "__main__":
    main()
