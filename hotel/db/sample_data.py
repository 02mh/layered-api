from hotel.db.models import DBCustomer, DBRoom

customers = [
    DBCustomer(
        first_name="John",
        last_name="Smith",
        email_address="email@email.com",
    ),
    DBCustomer(
        first_name="Jane",
        last_name="Doe",
        email_address="jane@hotmail.com",
    ),
    DBCustomer(
        first_name="Jack",
        last_name="Black",
        email_address="jack@black.com",
    ),
    DBCustomer(
        first_name="Jill",
        last_name="White",
        email_address="jill@gmail.com",
    ),
    DBCustomer(
        first_name="Arjan",
        last_name="Codes",
        email_address="hi@arjancodes.com",
    ),
]

rooms = [
    DBRoom(number="101", size=10, price=150_00),
    DBRoom(number="102", size=10, price=150_00),
    DBRoom(number="103", size=20, price=250_00),
    DBRoom(number="104", size=20, price=250_00),
    DBRoom(number="105", size=30, price=350_00),
]
