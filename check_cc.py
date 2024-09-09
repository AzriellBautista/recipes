def is_valid_credit_card(card_number: str) -> bool:
    """Checks if a number is a valid Visa credit card (16 digits) using Luhn."""
    if not isinstance(card_number, str):
        raise TypeError("Card number must be a string.")
    else:
        if not card_number.isdigit() or len(card_number) != 16:
            raise ValueError("Card number must be a 16-digit number.")

    digits = (int(d) for d in card_number)
    total = 0
    for pos, digit in enumerate(digits):
        if digit < 0 or digit > 9:
            return False
        total += digit if pos % 2 else digit * 2 // 10 + digit * 2 % 10
    return total % 10 == 0


if __name__ == "__main__":
    from string import digits
    from random import choice

    while True:
        cc_number = "".join(choice(digits) for _ in range(16))
        if is_valid_credit_card(cc_number):
            print(cc_number)