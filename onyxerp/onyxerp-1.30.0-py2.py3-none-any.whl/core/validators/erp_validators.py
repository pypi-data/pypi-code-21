from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

status_choices = (("A", "A"), ("D", "D"), ("I", "I"))
sim_nao_choices = (("S", "S"), ("N", "N"))


def validate_cpf(value):
    value = str(value).zfill(11)
    if len(value) == 11 and value.isdigit():
        digito = dict()
        digito[0] = 0
        digito[1] = 0
        a = 10
        total = 0
        for c in range(0, 2):
            for i in range(0, (8 + c + 1)):
                total = total + int(value[i]) * a
                a = a - 1
            digito[c] = int(11 - (total % 11))
            a = 11
            total = 0
        if int(value[9]) == int(digito[0]) and int(value[10]) == int(digito[1]):
            return True
    raise ValidationError(
        _('%(value)s não é um CPF válido!'),
        params={'value': value},
    )
