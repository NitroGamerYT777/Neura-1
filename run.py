from neura import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True rejimini yoqish orqali o'zgarishlarni darhol ko'rish va xatoliklarni osonroq topish mumkin.
    # production muhitida buni o'chirib qo'yish kerak.
    app.run(debug=True)