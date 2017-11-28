# coding: utf-8
import re


class CanonicalPhoneGenerationException(Exception):
    pass


def gen_canonical_phone(original_phone, first_number='7', check_code=True):
    # удалим все не цифровые символы
    phone = re.sub('\D', '', original_phone)

    if not (10 <= len(phone) <= 11):
        raise CanonicalPhoneGenerationException('Номер должен состоять из 10 или 11 цифр (%s)' % str(original_phone))

    # избавимся от ведущей цифры 11ти значного номера
    phone = phone[-10:]

    if check_code and phone[0] != '9':
        raise CanonicalPhoneGenerationException('Код города должен начинатся с 9 (%s)' % str(original_phone))

    # установим ведущую семерку
    phone = '%s%s' % (first_number, phone)

    return phone


def canonise_phone(phone):
    """
         пытается присти к каноническому виду.
         в случае не удачи, возвращает исходный номер
    """
    if phone:
        try:
            phone = gen_canonical_phone(phone)
        except CanonicalPhoneGenerationException:
            pass

    return phone


def prettify_phone(phone):
    import phonenumbers
    parsed_number = phonenumbers.parse(phone, 'RU')
    pretty_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
    return pretty_number
