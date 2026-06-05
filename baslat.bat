@echo off
echo =========================================
echo Job Scrater - Kariyer Zekasi Paneli
echo =========================================
echo.

echo Python yuklu mu kontrol ediliyor...
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo HATA: Bilgisayarinizda Python yuklu degil! Lutfen python.org adresinden Python 3.10 veya uzeri bir surum indirin.
    pause
    exit /b
)

IF NOT EXIST "venv" (
    echo Ilk kurulum yapiliyor, lutfen bekleyin -bu islem internet hiziniza bagli olarak 1-2 dakika surebilir-...
    python -m venv venv
    call venv\Scripts\activate
    echo Kutuphaneler yukleniyor...
    pip install -r requirements.txt
) ELSE (
    echo Ortam hazir, uygulama baslatiliyor...
    call venv\Scripts\activate
)

echo.
echo Eski oturumlar temizleniyor (Eger varsa port 8501 bosaltiliyor)...
FOR /F "tokens=5" %%T IN ('netstat -ano ^| findstr :8501 ^| findstr LISTENING') DO taskkill /F /PID %%T >nul 2>&1

echo.
echo =========================================
echo Tarayicinizda Job Scrater paneli aciliyor...
echo (Otomatik acilmazsa tarayicidan su adrese gidin: http://localhost:8501)
echo =========================================
streamlit run app.py
pause
