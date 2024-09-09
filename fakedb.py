
import faker as fk
import tinydb as tdb


faker = fk.Faker()


def generate_person() -> dict[str, str]:
    return {
        "uuid": faker.uuid4(),
        "gender": (gender := "M" if faker.boolean() else "F"),
        "first_name": (fname := faker.first_name_male() if gender == "M" else faker.first_name_female()),
        "last_name": (lname := faker.last_name()),
        "middle_name": (mname := faker.last_name() if faker.boolean() else ""),
        "full_name": f"{fname} {mname[0] + '. ' if mname else ''}{lname}",
        "address": faker.address(),
        "username": (uname := f"{fname.lower()[0]}.{lname.lower()}{faker.random_int(0, 9999)}"),
        "email": f"{uname}@{faker.domain_name()}",
        "password_hash": faker.sha256(0),
        "phone": faker.phone_number(),
        "birthdate": faker.date(),
        'blood_type': faker.random_element(elements=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]),
        "job": faker.job(),
        "company": faker.company(),
        "credit_card_number": faker.credit_card_number(),
        "bank_account_number": faker.iban(),
        "ssn": faker.ssn(),
        "passport": faker.passport_number(),
        "vehicle_license_plate": faker.license_plate() if faker.boolean() else "",
        "ipv4": faker.ipv4(),
        "user_agent": faker.user_agent(),
        "mac_address": faker.mac_address(),
    }


if __name__ == "__main__":
    people = tdb.TinyDB("people.json", indent=2)

    for _ in range(10):
        people.insert(generate_person())