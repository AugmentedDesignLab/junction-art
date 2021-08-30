from z3 import *
class ValueConverter:

    @staticmethod
    def z3RealToFloat(r):
        return float(r.numerator_as_long()) / float(r.denominator_as_long())

    @staticmethod
    def z3AnyToFloat(r, precision=4):

        strNum = r.as_decimal(precision)
        if isinstance(r, AlgebraicNumRef):
            strNum = strNum[0:-1]
        return float(strNum)