import unittest
from ecommerce_alipay_sdk.api import AliPay


class TestStringMethods(unittest.TestCase):
    configuration = {
        "cancel_url": "https: // lab.yungoal.com / commerce / checkout / cancel /",
        "error_url": "https: // lab.yungoal.com / commerce / checkout / error /",
        "receipt_url": "https: // lab.yungoal.com / commerce / checkout / receipt /",
        "mode": "live",
        "app_id": "2017110209674781",
        "private_key": "MIIEogIBAAKCAQEAqIQiqiDfyZ44X2aL0DWX8964oWahlqQ49r6sVxgrxj4ErFr6ikEjxlCLJMT7ZyKVwJE+7RFnYZhUWtJ7YWkrXp4N4kkHOCMSz4YW7d+24mc+45sYnaTk7Hi3F8LN+cEUpL5jF+fhvdStd/UXG1/zG+cTFBJN5X8yjjq0mQlAMuVREGH4TBkMMS2TE0FOncBuiDxAf2fKg5d9BzkIGnq+9ihxwFomPd/FU9pqLgMHEyTjjjMIB7gU11TOi8DD+VXPinCOWQKyV6ZkMuPNWrs/H2RTtnCrfTTyyIlap2IFEagiRf9t+IvLdtBh3SaIqPdC3wghtgm66I0GS6GBaVWTbwIDAQABAoIBAE8QD6N6YQSbMx+vYRGC05Qbfsxa9p1S11cNBpamRINyPYcP+FQ9U6eLynyp3rn4xAHhI4DelX54lbs23aRKT4rI5QKx+K0h54VuB/v65jc68YqgDeCIqM85o82GHFV9fU399UgWBxelXO3XE8xILCt/MrhMDjgKgZGxgWH7sR8vLHmj1hvlFunwWq2Lmwv3QMQ6axEqGqjdEgq2cnCUaneuM+77WRfob16eNpVJ86XP7Z5HDJ1R7dq9q0ohQanyLqbNSivoHgwMxllbPSiifuy7/KTM/AzecbRJVPQINNtXpXtBz1f+hot8SGNQTPOu+WTgjOE3hcCzQ8dtMvQl4EECgYEA33sYGi8zktaB/kxNd9vi42imrfY2bp8tt5rCsuqWeNWktFVUn+EtIXj9ID7xZ6lVbHx1T1vQb1xpngW7iUSpqnqYqpWYGboMmBEYy29YVp7Ayz9OZdpyjCRCasWhQOjT5UL8DeoUV5vtv8ppEjGwXfsL0KHSp8TW8L0MhT1QjNcCgYEAwQmL8V0+kcX6gQvFT0jKOLxytcYgpG9J8VGdr/Ify1aPTJxqdy6gh30adNUOBKgGHrs/aZLoDYvft2b6PbWsPV1oDNlpHVOcgh1zTMCYS+sVjQ37maTNq1KxXPAQSU79decC4yfC5V4982+MvQBz2Bp8hMAfK/tOaHV/JtrrgykCgYBstsvVyQp0rwcTtvikiwIHkFwtGi4GiEbMH2wBb179ryhtVWlSUU8MDnhMnHIA9H4KxUyn60ktMy5p4e4F67IBrZvgt98C/N+thfui0yqNELNG7CfuImNAy07H9BXqppiV2Y0WE74LlF4Gw6dzY1qhjUOFHYOFe5r4B280zcwGhwKBgCKTrjB2rk14M+3HiPkxpZ9SCg4LRi+OC6WhI+ivKwjGIXbskZl1jaWXQBTrUM5+tlHs4mfru4spodH9LRe+ofJ/97JNgymQn3kjA1MdMGpw2nRgq8+SmJB2iHSIP7KR5o6m6Xp81ck1/0zKj2APY7Cy1dkFfM/o/NtzKGpyTjs5AoGAIGJba6k6gdekAQ0XpUy1jITtIosbBsAxyx/Hp+39ntQmUg6cWQIB848+4v+7wez9f4Bz3qUGEIJDen5iJ3qDydc+ekgO7cDSqrtznKRxZsM9fFYDvlnZzBb0Ot0xz8/+wt+QSfIURFSBJ1SCN7jSRtMdSShVWQ4wYhDY6SJO8Ng=",
        "alipay_public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzl8cjX9DuoCVnIQonN4lF2uO7wpC//4lehHyA7+Laz7DsYVkH36e8NFl51fDmiINf7l1A+4X/Gd/86UwiDwxXKu5OOKsWbWHIERtO5257bwDaeOlT7M99u/fhD9b3vaGdkJAD4WWnYUjhn/aF9tuSWXb9Rh4HmI4Wi+8VcR1Zy4Am6LAJvaVnDo7oZU0Ld48HojqkweU6k2paAMXuI8WNF9PxO5dvGsSTdIm1HHpO2wFL8RDvLf0lNsT7aDWjv+7+rIm/H91UifBdv4uey7bdX/2TBXWFQR4/4bWPHFqVRpIE1FiyTGqsrJxmGSuB1tBiDJNPRab62VYEIe+TkuPDwIDAQAB",
        "sign_type": "RSA2",
        "charset": "UTF - 8",
    }
    alipay_api = AliPay({
        'mode': configuration['mode'],
        'app_id': configuration['app_id'],
        'private_key': configuration['private_key'],
        'alipay_public_key': configuration['alipay_public_key'],
        'sign_type': configuration['sign_type'],
        'charset': configuration['charset'],
    })

    def test_api_alipay_trade_page_pay(self):
        order_string = self.alipay_api.api_alipay_trade_page_pay(
            out_trade_no=1,
            total_amount=0.01,
            subject="CCCCCCCC",
            return_url=None,
        )
        print order_string

    def test_api_alipay_trade_query(self):
        r = self.alipay_api.api_alipay_trade_query(out_trade_no='14a707b8e57e4bb292e7552e50225554')
        print(r[u'trade_status']==u'TRADE_SUCCESS')
        print(r)


if __name__ == '__main__':
    unittest.main()
