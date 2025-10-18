# Neura - AI Chat Ilovasi

Neura - bu Flask-da qurilgan oddiy veb-chat ilovasi bo'lib, foydalanuvchilarga sun'iy intellekt bilan suhbatlashish imkonini beradi.

## Asosiy funksiyalar

-   Foydalanuvchilarni ro'yxatdan o'tkazish va tizimga kiritish
-   Har bir foydalanuvchi uchun alohida chat tarixini saqlash
-   Suhbatlarni nomlash va o'chirish
-   Markdown formatidagi AI javoblarini qo'llab-quvvatlash

## O'rnatish va Ishga Tushirish

Ushbu loyihani o'z kompyuteringizda ishga tushirish uchun quyidagi amallarni bajaring:

### 1. Talablar

-   Python 3.8+
-   `pip` paket menejeri

### 2. Loyihani yuklab olish va o'rnatish

1.  **Loyiha nusxasini oling:**
    ```bash
    git clone <repository_url>
    cd Neura-1
    ```

2.  **Virtual muhit yaratish va faollashtirish (Tavsiya etiladi):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS uchun
    # venv\\Scripts\\activate  # Windows uchun
    ```

3.  **Kerakli paketlarni o'rnating:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Ma'lumotlar bazasini sozlash

Dasturni birinchi marta ishga tushirishdan oldin ma'lumotlar bazasini yaratishingiz kerak. Buning uchun `flask` buyrug'idan foydalaniladi:

```bash
export FLASK_APP=neura  # Linux/macOS uchun
# set FLASK_APP=neura    # Windows uchun

flask init-db
```
Bu buyruq `instance` papkasida `database.sqlite` faylini yaratadi.

### 4. Dasturni ishga tushirish

Dasturni ishga tushirishning eng oson yo'li - bu `run.py` skriptidan foydalanish:

```bash
python run.py
```

Shundan so'ng, dastur `http://127.0.0.1:5000/` manzilida ishlay boshlaydi. Brauzeringizda ushbu manzilni oching. Dastur sizni avtomatik ravishda ro'yxatdan o'tish/kirish sahifasiga yo'naltiradi.

**Izoh:** `run.py` fayli dasturni `debug=True` rejimida ishga tushiradi. Bu ishlab chiqish uchun qulay, ammo production muhitida `debug` rejimini o'chirib qo'yish tavsiya etiladi.