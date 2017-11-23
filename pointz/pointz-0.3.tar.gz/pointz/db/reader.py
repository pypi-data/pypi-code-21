from sqlalchemy.orm import joinedload

from pointz.db.schema import Transaction, Subsidiary, Region
from pointz.db.session import Session


def get_transactions_ordered_by_id(id, limit=100):
    session = Session()
    query = session.query(Transaction)
    query = query.options(joinedload(
        Transaction.subsidiary).joinedload(Subsidiary.region).joinedload(Region.partner))
    query = query.filter(Transaction.id > id)
    query = query.order_by(Transaction.id)
    query = query.limit(limit)
    transactions = query.all()
    session.close()
    return transactions


if __name__ == '__main__':
    for transaction in get_transactions_ordered_by_id(0,2):
        print(transaction.id,transaction.sale, transaction.subsidiary.name, transaction.subsidiary.region.name)
