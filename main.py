import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
import tarfile
from colorama import init, Fore, Style
import tkinter as tk
from tkinter import messagebox

init()

BASE_URL = "https://mcskill.net/McSkill.jar"
INSTALL_DIR = os.path.join(os.path.expanduser("~"), "McSkill")
JAR_PATH = os.path.join(INSTALL_DIR, "McSkill.jar")
JDK_DIR = os.path.join(INSTALL_DIR, "jdk")

def print_status(message, symbol="🔄", color=Fore.CYAN):
    print(color + f"{symbol} {message}" + Style.RESET_ALL)

def print_success(message):
    print_status(message, symbol="✅", color=Fore.GREEN)

def print_error(message):
    print_status(message, symbol="❌", color=Fore.RED)

def get_jdk_url():
    system = platform.system()
    arch = platform.machine()

    suffix = {"x86_64": "x64", "AMD64": "x64", "aarch64": "aarch64", "arm64": "aarch64"}.get(arch)
    if not suffix:
        raise RuntimeError(f"Unsupported architecture: {arch}")

    if system == "Windows":
        return f"https://cdn.azul.com/zulu/bin/zulu8.74.0.17-ca-fx-jdk8.0.392-win_{suffix}.zip"
    elif system == "Linux":
        return f"https://cdn.azul.com/zulu/bin/zulu8.74.0.17-ca-fx-jdk8.0.392-linux_{suffix}.tar.gz"
    elif system == "Darwin":
        return f"https://cdn.azul.com/zulu/bin/zulu8.74.0.17-ca-fx-jdk8.0.392-macosx_{suffix}.tar.gz"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

def download_file(url, dest):
    print_status(f"Скачивание: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(dest, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    print_success(f"Скачано: {os.path.basename(dest)}")

def extract_archive(archive_path, extract_to):
    print_status(f"Распаковка: {archive_path}")
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        raise RuntimeError("Неизвестный формат архива: " + archive_path)
    print_success("Распаковка завершена")

def show_message(title, text, error=False):
    root = tk.Tk()
    root.withdraw()
    if error:
        messagebox.showerror(title, text)
    else:
        messagebox.showinfo(title, text)

def main():
    try:
        os.makedirs(INSTALL_DIR, exist_ok=True)

        print_status("Скачивание McSkill.jar...")
        download_file(BASE_URL, JAR_PATH)

        if not os.path.exists(JDK_DIR):
            url = get_jdk_url()
            ext = ".zip" if url.endswith(".zip") else ".tar.gz"
            archive_name = os.path.join(INSTALL_DIR, "jdk_archive" + ext)
            download_file(url, archive_name)
            extract_archive(archive_name, INSTALL_DIR)
            for item in os.listdir(INSTALL_DIR):
                if item.lower().startswith("zulu") and os.path.isdir(os.path.join(INSTALL_DIR, item)):
                    os.rename(os.path.join(INSTALL_DIR, item), JDK_DIR)
                    break
            os.remove(archive_name)
        else:
            print_success("JDK уже установлен")

        java_bin = os.path.join(JDK_DIR, "bin", "java.exe" if platform.system() == "Windows" else "java")
        if not os.path.exists(java_bin):
            raise RuntimeError("Не найден исполняемый файл Java")

        print_status("Запуск McSkill.jar...")
        subprocess.run([java_bin, "-jar", JAR_PATH])
        show_message("Успех", "McSkill.jar успешно запущен!")

    except Exception as e:
        print_error(str(e))
        show_message("Ошибка", str(e), error=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
