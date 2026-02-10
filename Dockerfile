# 1. الصورة الأساسية التي تحتوي على Python
FROM python:3.12-slim

# 2. تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# 3. نسخ ملفات المشروع
COPY requirements.txt .
COPY bot.py .

# 4. تثبيت المكتبات المطلوبة
RUN pip install --no-cache-dir -r requirements.txt

# 5. الأمر الذي يشغل البوت
CMD ["python", "bot.py"]
