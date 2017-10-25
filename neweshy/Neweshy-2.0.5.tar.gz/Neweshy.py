def nagwaRound(value, decimal_places=0):
    # This function is used for the following cases:
    # 1- To fix rounding issues in the python itself (ex. round(1.25,1)1.2 & nagwaRound(1.25,1)=1.3)
    # 2- Considering rounding process in case "if necessary" is mentioned (ex. round(3.0201,3)=3.02 & nagwaRound(3.0201,3)=3.020)
    # 3- The maximum decimal length that can be displayed is 15
    # 4- We have 4 output forms covered in 5 cases from 0 to 4:
    #   Case 0:    the input value is a whole number >> the output is the integer of the value
    #   Case 1:    the input value supposed to be a whole number but it has calculations error from python >> the output is the integer of the value
    #   Case 2:    the decimal length of the value is less than the required decimal places >> the output is a float number (accurate) without extra zeros
    #   Case 3:    the decimal length of the value is greater than the required decimal places >> the output is a float number rounded to the required decimal places.
    #   Case 4:    the rounded value equals zero >> the output is 0 without the negative sign.

    # Steps:
    # If the value is a whole number, the output will be the integer of the value
    if float(value)%1==0: case=0; return round(value)
    else:
        from math import copysign

        # convert the string to float if found
        value = float(value)
        # decimal_places must be an integer between 0 and 15
        if not (decimal_places%1==0 and decimal_places in range(0,15)):
            raise ValueError("number of decimal places must be integer between 0 and 15")

        # maximum length displayed for decimals in python is 18 [the negative sign not included] including the decimal point and the integer part
        # python has calculation's issues appear in the last digit in the displayed value
        # the highest precision we can use is 15
        prec = 15

        # take the sign of the value
        sign = copysign(1, value)
        abs_value = abs(value)

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

        # if the value is integer return the value
        if round(value, prec) % 1 == 0:
            value = round(value)
            case = "1"

        else:
            if "e-" in str(abs_value):
                decimals_length = (int(str(abs_value).split("e-")[1])) + int(len(str(abs_value).split("e-")[0]) - 1)
                if "." in str(abs_value): decimals_length = decimals_length - 1
            else:
                decimals_length = len(str(abs_value).split(".")[1])

            # compare decimals_length with the required decimal_places
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
