#!/bin/bash
echo "========================================="
echo "Job Scrater - Kariyer Zekasi Paneli"
echo "========================================="

if ! command -v python3 &> /dev/null
then
    echo "HATA: Bilgisayarinizda Python3 yuklu degil!"
    exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "Ilk kurulum yapiliyor, lutfen bekleyin (bu islem 1-2 dakika surebilir)..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python3 -m spacy download en_core_web_sm
else
    echo "Ortam hazir, uygulama baslatiliyor..."
    source venv/bin/activate
fi

echo "Tarayicinizda pencere aciliyor..."
streamlit run app.py
