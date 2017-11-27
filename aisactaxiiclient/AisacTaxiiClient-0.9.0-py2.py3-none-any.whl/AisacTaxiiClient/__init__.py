import cabby
import dateutil
import hashlib
import os
import pytz
import re
import logging


class AisacClient(cabby.Client11):
    def __init__(self, *args, **kwargs):
        super(AisacClient, self).__init__(*args, **kwargs)
        self.log.warning('\n本軟體使用 A-ISAC Taxii Client SDK 開發, 僅限於與教育部 A-ISAC Taxii 伺服器連線使用\n')

    def push(self, content, content_binding='urn:stix.mitre.org:xml:1.2', collection_names=None,
             timestamp=None, uri=None):
        return super(AisacClient, self).push(
            content=content,
            content_binding=content_binding,
            collection_names=collection_names,
            timestamp=timestamp,
            uri=uri,
        )

    def pull(self,
             limit=None, begin=None, bindings=None, count_only=None, collection=None, subscription_id=None,
             path=None, end=None, dest_dir=None, as_raw=False, as_xml=True, xmltodict=True,
             ):
        def generate_filename(collection, content_block):

            collection_name = re.sub(r"[^\w]+", "-", collection) if collection else ""

            md5 = hashlib.md5()
            md5.update(content_block.raw.to_xml())

            filename = '%s_%s' % (collection_name, md5.hexdigest())

            return filename

        def save_to_dir(dest_dir, collection, content_block, as_raw):

            filename = generate_filename(collection, content_block)
            path = os.path.abspath(os.path.join(dest_dir, filename))

            with open(path, 'wb') as f:
                if as_raw:
                    content = content_block.raw.to_xml(pretty_print=True)
                else:
                    content = content_block.content

                f.write(
                    content if isinstance(content, bytes)
                    else content.encode('utf-8'))

            self.log.info("Content block saved to %s", path)

            return path

        if limit == 0:
            return

        if begin:
            begin = dateutil.parser.parse(begin)
            if not begin.tzinfo:
                begin = begin.replace(tzinfo=pytz.UTC)
        else:
            begin = None

        if end:
            end = dateutil.parser.parse(end)
            if not end.tzinfo:
                end = end.replace(tzinfo=pytz.UTC)
        else:
            end = None

        bindings = bindings.split(',') if bindings else None
        self.log.info("Polling using data binding: %s",
                 str(bindings) if bindings else "ALL")

        if count_only:
            count = self.get_content_count(
                collection_name=collection,
                begin_date=begin,
                end_date=end,
                subscription_id=subscription_id,
                uri=path,
                content_bindings=bindings,
            )
            if count:
                self.log.info("Content blocks count: %s, is partial: %s",
                         count.count, count.is_partial)
            else:
                self.log.warning("Count value was not returned")

            return

        blocks = self.client.poll(
            collection_name=collection,
            begin_date=begin,
            end_date=end,
            subscription_id=subscription_id,
            uri=path,
            content_bindings=bindings,
        )

        counter = 0
        data_list = list()

        for counter, block in enumerate(blocks, 1):
            if dest_dir:
                dest_dir = os.path.abspath(dest_dir)
                file_path = save_to_dir(dest_dir, collection, block, as_raw)
                data_list.append(file_path)
            else:
                if as_raw:
                    if as_xml:
                        value = block.raw.to_xml()
                        if xmltodict:
                            value = xmltodict.parse(value)
                    else:
                        value = block.raw.to_text()
                else:
                    value = block.content
                data_list.append(value.decode('utf-8'))

            if limit and counter >= limit:
                break

        self.log.info("%d blocks polled", counter)
        return data_list



def create_client(username, password,
                  host='taxii.aisac.tw', port=443, discovery_path='/services/discovery', use_https=True,
                  headers=None,
                  ):
    if username.lower() in ['tacert', 'ncc', 'nccst']:
        discovery_path = '/services/{}/discovery'.format(username.lower())

    params = dict(
        host=host,
        port=port,
        use_https=use_https,
        discovery_path=discovery_path,
        headers=headers)

    client = AisacClient(**params)

    client.set_auth(
        username=username,
        password=password,
    )

    return client


def submit(user_name, user_pass, filepath, iodef_type_id=None, client=None):
    try:
        from cabby.exceptions import UnsuccessfulStatusError
        logging.warning('Submit method is deprecated. Use create_client instead')

        if iodef_type_id:
            logging.warning('Type ID will be detected automatically. Parameter ignored.')

        if not client:
            client = create_client(username=user_name, password=user_pass)

        with open(filepath, 'r') as f:
            content = f.read()


        client.push(content=content)
        return {
            "success": True,
            "status": 201,
            "reason": "Created",
        }
    except UnsuccessfulStatusError as e:
        return {
            "success": False,
            "status": e.status,
            "reason": e.text,
        }
    except Exception as e:
        return {
            "success": False,
            "status": 400,
            "reason": e.__repr__(),
        }
