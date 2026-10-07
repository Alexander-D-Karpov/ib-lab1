from app.models import Crystal, User, db


def seed_data():
    if User.query.first() is None:
        admin = User(username="admin", balance=5000)
        admin.set_password("CorrectHorse42!")
        db.session.add(admin)

    if Crystal.query.first() is None:
        defaults = [
            ("red", 100, 50),
            ("green", 120, 40),
            ("blue", 150, 30),
            ("violet", 300, 10),
        ]
        for color, price, stock in defaults:
            db.session.add(Crystal(color=color, price=price, stock=stock))

    db.session.commit()
