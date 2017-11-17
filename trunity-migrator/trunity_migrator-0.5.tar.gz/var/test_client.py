


if __name__ == "__main__":

    client = Client('VicHunting2', 'jjj3030jja')
    # client = Client('VicHunting', 'trn2323&&&83')

    # joins = client.get_topic_joins(site_id=9806, topic_id='536be57a0cf226e0bdbfe461')
    joins = client.get_topic_joins(site_id=9806, topic_id='52446d0b0cf264abcd85e90a')
    print(joins)

    # topic = client.get_a_topic(site_id=9806, topic_id='52446d0b0cf264abcd85e90a')
    # print(topic)

    # content = client.get_content(9806, '52446db30cf2ea76e5daa686')
    # print(content)