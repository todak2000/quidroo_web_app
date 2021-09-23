import random
import string


def alphanumeric(stringLength=40):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.sample(lettersAndDigits, stringLength))

def alpha(stringLength=40):
    letters = string.ascii_lowercase
    return ''.join(random.sample(letters, stringLength))

def numeric(stringLength=40):
    Digits = string.digits
    return ''.join(random.sample(Digits, stringLength))

def memo(stringLength=40):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
# ''.join(random.choice('0123456789ABCDEF') for i in range(16))
# 'E2C6B2E19E4A7777'
