import subprocess
import time

def run_adb(command):
    result = subprocess.run(
        f"adb shell {command}",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def is_split_screen():
    # طريقة 1: تحقق من windowing mode
    output = run_adb("dumpsys activity activities | grep -i 'windowingMode=3'")
    if output:
        return True
    
    # طريقة 2: تحقق من multi window state
    output = run_adb("dumpsys window | grep -i 'splitscreen'")
    if output:
        return True
    
    # طريقة 3: تحقق من MIUI freeform
    output = run_adb("dumpsys activity activities | grep -i 'inSplitScreenWindow'")
    if output:
        return True

    return False

def exit_split_screen():
    print("⚠️  تم اكتشاف Split Screen! جاري الإغلاق...")
    
    # طريقة 1: اضغط زر الرجوع مرتين
    run_adb("input keyevent KEYCODE_BACK")
    time.sleep(0.3)
    run_adb("input keyevent KEYCODE_BACK")
    
    # طريقة 2: اذهب للهوم
    run_adb("input keyevent KEYCODE_HOME")
    
    # طريقة 3: اخرج من multi window عبر recents
    run_adb("am broadcast -a com.miui.freeform.DISABLE 2>/dev/null || true")
    
    print("✅ تم الخروج من Split Screen")

def main():
    print("🔍 بدأ مراقبة Split Screen...")
    print("اضغط Ctrl+C للإيقاف\n")
    
    while True:
        try:
            if is_split_screen():
                exit_split_screen()
            time.sleep(1)  # فحص كل ثانية
        except KeyboardInterrupt:
            print("\n⛔ تم إيقاف المراقبة")
            break
        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()

