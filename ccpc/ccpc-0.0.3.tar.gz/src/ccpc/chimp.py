import asyncio
import click
import random
import ssl
from aiohttp import ClientSession, TCPConnector
from yarl import URL


async def get_pods(settings):
    async with settings['session'].get(settings['list_pods_url']) as resp:
            body = await resp.json()

    return [
        '{}{}'.format(settings['base_url'], pod['metadata']['selfLink'])
        for pod in body['items']
        if pod['metadata']['labels']['app'] != settings['own_name']
    ]


async def delete_pods(settings):
    # Get pods
    pods = await get_pods(settings)

    # Decide how many pods to bring down
    chaos_index = random.randint(0, len(pods))

    to_kill = []
    # Decide which pods to kill
    for _ in range(chaos_index):
        to_kill.append(pods.pop(random.randint(0, len(pods)-1)))

    tasks = []
    # Kill selected pods concurrently
    for kill in to_kill:
        tasks.append(settings['session'].delete(kill))
    res = await asyncio.gather(*tasks)


async def get_deployment_configs(settings):
    async with settings['session'].get(settings['list_dcs_url']) as resp:
        body = await resp.json()

    return {
        '{}{}/scale'.format(settings['base_url'], dc['metadata']['selfLink']):
        dc
        for dc in body['items']
        if dc['metadata']['labels']['app'] != settings['own_name']
    }


async def scale_deployment_configs(settings):
    # Get Deployment Configs
    dcs = await get_deployment_configs(settings)
    # Decide how many pods to bring down
    chaos_index = random.randint(0, len(dcs))

    to_scale = {}
    keys = list(dcs.keys())
    # Decide which pods to scale
    for _ in range(chaos_index):
        index = random.randint(0, len(keys)-1)
        to_scale[keys[index]] = dcs.pop(keys[index])
    tasks = []
    for ep, data in to_scale.items():
        replicas = data['spec']['replicas']
        replicas = replicas - 1 if replicas > 0 else replicas + 1
        body = {
            'kind': 'Scale',
            'apiVersion': 'extensions/v1beta1',
            'metadata': {
                'name': data['metadata']['name'],
                'namespace': data['metadata']['namespace']
            },
            'spec': {
                'replicas': replicas
            }
        }
        tasks.append(settings['session'].put(ep, json=body))
    res = await asyncio.gather(*tasks)


async def master(settings):
    # Decide action
    actions = [delete_pods, scale_deployment_configs]
    action = actions[random.randint(0, len(actions)-1)]
    # Create connections context
    ctx = {}
    if 'ca_path' in settings:
        ctx['ssl_context'] = ssl.create_default_context(
            cafile=settings['ca_path']
        )
    else:
        ctx['verify_ssl'] = settings['verify_ssl']
    conn = TCPConnector(**ctx)
    # Create auth headers
    headers = {
        'Authorization': 'Bearer {}'.format(settings['token'])
    }
    async with ClientSession(connector=conn, headers=headers) as session:
        settings['session'] = session
        await action(settings)


@click.command()
@click.option('--verify-ssl/--no-verify-ssl', 'verify_ssl', default=True,
              help='Verify the ssl cert of the Open Shift server')
@click.option('--ca-path', 'ca_path', help='Path to a ca certificate')
@click.option('-t', '--token', 'token', default='', multiple=False,
              help='Auth token for a service account with read/write to the project')
@click.option('-p', '--project', 'project', default='', multiple=False,
              help='The project to receive the chaos')
@click.option('--own-name', 'own_name', default='', multiple=False,
              help='CCPC\'s Open Shift container name')
@click.option('-b', '--base_url', 'base_url', default='', multiple=False,
              help='Open Shift\'s base url')
def main(verify_ssl, ca_path, token, project, own_name, base_url):
    # Make sure we've got https
    url = URL(base_url)
    if url.scheme != 'https':
        url = url.with_scheme('https')
    settings = {
        'verify_ssl': verify_ssl,
        'base_url': base_url,
        'token': token,
        'project': project,
        'own_name': own_name
    }
    if ca_path:
        settings.update({'ca_path': ca_path})
    settings['list_pods_url'] = '{}/api/v1/namespaces/{}/pods/'.format(
        settings['base_url'], settings['project']
    )
    settings['list_dcs_url'] = '{}/oapi/v1/namespaces/{}/deploymentconfigs/'.format(
        settings['base_url'], settings['project']
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(master(settings))


if __name__ == '__main__':
    main()
