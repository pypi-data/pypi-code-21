#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

def push(secret, **meta):
    push_url = 'http://zf.omgm4j.com/api/v1/%s/send' % (secret)

    theme = meta.get('theme', 'miss theme')
    title = meta.get('title', 'miss title')
    summary = meta.get('summary', 'miss summary')
    content = meta.get('content', '')

    payload = {'theme': theme, 'title': title, 'summary': summary}

    if content:
      payload['content'] = content

    resp = requests.post(push_url, params = payload)
    ret = resp.json()

    return ret['ok'] == 0


def push_batch(secrets = [], **meta):
    theme = meta.get('theme', 'miss theme')
    title = meta.get('title', 'miss title')
    summary = meta.get('summary', 'miss summary')
    content = meta.get('content', '')

    errors = []
    for secret in secrets:
      push_url = 'http://zf.omgm4j.com/api/v1/%s/send' % (secret)

      payload = {
        'theme': theme,
        'title': title,
        'summary': summary
      }

      if content:
        payload['content'] = content

      resp = requests.post(push_url, params = payload)
      ret = resp.json()

      errors.append(ret['ok'] == 0)

    results = set(errors)
    if len(results) > 1:
      return False
    else:
      return results.pop() == True    


if __name__ == '__main__':
    pass
