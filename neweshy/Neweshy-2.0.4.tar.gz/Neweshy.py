__author__ = 'Haytham Mahmoud'

def nagwaRound(value, decimal_places=0):
    if float(value)%1==0: case=0; return round(value)
    else:
        from math import copysign
        # from math import copysign
        # This function is used for the following cases:
        # 1- To fix rounding issues in the python itself (ex. round(1.25,1)1.2 & nagwaRound(1.25,1)=1.3)
        # 2- Considering rounding process in case "if necessary" is mentioned (ex. round(3.0201,3)=3.02 & nagwaRound(3.0201,3)=3.020)

        # Steps:

        # convert the string to float if found
        value = float(value)
        # decimal_places can't be negative, if it is decimal will be rounded to the floor, and if it's 0 will be rounded to integer
        if not (decimal_places%1==0 and decimal_places in range(0,15)):
            raise ValueError("number of decimal places must be integer >= 0")

        # set the precision of the python to 14 decimal places
        prec = 15

        if decimal_places > prec: decimal_places = prec

        # take the sign of the value
        sign = copysign(1, value)
        abs_value = abs(value)

        # decimals_length: length of decimals of the value

        # decimals = str(abs_value).split(".")[1]

        if "e-" in str(abs_value):
            decimals = (('{0:.%df}'%(prec)).format(abs_value).split(".")[1])

        else:
            decimals = str(abs_value).split(".")[1]

        # to solve precision issue
        redn = 6    # number of repeated value
        for x in [redn * "9", redn * "0"]:
            if x in decimals:
                value = round(value, decimals.index(x))
        abs_value = abs(value)


        if "e-" in str(abs_value):
            decimals_length = (int(str(abs_value).split("e-")[1])) + int(len(str(abs_value).split("e-")[0]) - 1)
            if "." in str(abs_value): decimals_length = decimals_length - 1
        else:
            decimals_length = len(str(abs_value).split(".")[1])

        # if the value is integer return the value
        if round(value, prec) % 1 == 0:
            value = round(value)
            case = "1"

        # compare decimals_length with the decimal_places required
        else:
            if decimals_length <= decimal_places:

                value = ("{0:.%df}" % (decimals_length)).format(sign * (abs_value))
                case = "2"
            else:
                # adding precision ( prec ) to overcome rounding up issue
                prec = prec - (len(str(abs_value).split(".")[0]))
                value = ("{0:.%df}" % (decimal_places)).format(sign * (abs_value+1*10**(-prec)))
                case = "3"
                # -0.0 to be 0.0
                if eval(str(value)) == 0:  value = str(value).replace("-", "");  case = "4"
        return value