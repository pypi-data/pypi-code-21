from pointz.db.reader import get_transactions_ordered_by_id


def sql_transaction_to_bigquery_row(transaction):
    return (
        transaction.id,
        int(100 * transaction.sale),
        int(100 * transaction.pointz_sale),
        transaction.pointz,
        transaction.creation.year,
        transaction.creation.month,
        transaction.creation.day,
        transaction.subsidiary.name,
        transaction.subsidiary.id,
        transaction.subsidiary.region.name,
        transaction.subsidiary.region.id,
        transaction.subsidiary.region.partner.name,
        transaction.subsidiary.region.partner.id,
        transaction.subsidiary.region.partner.segment
    )

def get_transaction_batches(id=None, limit=100):
    if id is None:
        id=0 # tem que buscar o maior id do BigQuery
    transactions=get_transactions_ordered_by_id(id, limit)
    while len(transactions) > 0:
        yield transactions
        transactions = get_transactions_ordered_by_id(transactions[-1].id, limit)

