# 1,0,80,1,2017,1,1,Posto 1,1,Fortaleza,1,Posto Flex,1,GAS
# 2,0,120,3,2017,1,2,Posto 2,2,Fortaleza,1,Posto Flex,1,GAS
# 3,0,1,2,2017,1,3,Posto 1,1,Fortaleza,1,Posto Flex,1,GAS
# 4,0,199,4,2017,1,4,Posto 2,2,Fortaleza,1,Posto Flex,1,GAS
# 5,49,0,0,2017,1,5,Posto 1,1,Fortaleza,1,Posto Flex,1,GAS
# 6,51,0,0,2017,1,6,Posto 2,2,Fortaleza,1,Posto Flex,1,GAS
# 7,200,0,0,2017,2,7,Posto 1,1,Fortaleza,1,Posto Flex,1,GAS
# 8,0,1600,40,2017,2,8,Posto 2,2,Fortaleza,1,Posto Flex,1,GAS
from datetime import datetime
from decimal import Decimal

from pointz.db.constants import GAS
from pointz.db.schema import Partner, Region, Subsidiary, Transaction
from pointz.db.session import Session


def populate_db():
    session = Session()
    posto_flex = Partner(name='Posto Flex', segment=GAS)
    session.add(posto_flex)
    session.commit()
    fortaleza = Region(name='Fortaleza', partner=posto_flex)
    session.add(fortaleza)
    session.commit()
    subsidiaries = [Subsidiary(name=f'Posto {i}', region=fortaleza) for i in range(1, 3)]
    session.add_all(subsidiaries)
    session.commit()
    transactions = [
        Transaction(
            subsidiary=subsidiaries[0],
            sale=Decimal('0.00'),
            pointz_sale=Decimal('0.80'),
            pointz=1,
            creation=datetime(2017, 1, 1, 1, 1)
        ),
        Transaction(
            subsidiary=subsidiaries[1],
            sale=Decimal('0.00'),
            pointz_sale=Decimal('1.20'),
            pointz=3,
            creation=datetime(2017, 1, 2, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[0],
            sale=Decimal('0.00'),
            pointz_sale=Decimal('0.01'),
            pointz=2,
            creation=datetime(2017, 1, 3, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[1],
            sale=Decimal('0.00'),
            pointz_sale=Decimal('1.99'),
            pointz=4,
            creation=datetime(2017, 1, 4, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[0],
            sale=Decimal('0.49'),
            pointz_sale=Decimal('0.00'),
            pointz=0,
            creation=datetime(2017, 1, 5, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[1],
            sale=Decimal('0.51'),
            pointz_sale=Decimal('0.00'),
            pointz=0,
            creation=datetime(2017, 1, 6, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[0],
            sale=Decimal('2.00'),
            pointz_sale=Decimal('0.00'),
            pointz=0,
            creation=datetime(2017, 2, 7, 3, 4)
        ),
        Transaction(
            subsidiary=subsidiaries[1],
            sale=Decimal('0.00'),
            pointz_sale=Decimal('16.00'),
            pointz=40,
            creation=datetime(2017, 2, 8, 3, 4)
        ),

    ]
    session.add_all(transactions)
    session.commit()
    session.close()


if __name__ == '__main__':
    populate_db()
