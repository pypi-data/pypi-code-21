import aiofiles
import aiohttp
import asyncio
import async_timeout
import os
import numpy as np
import pandas as pd

async def download_coroutine(session, url, group, sample, source, evalue=5, identity=60, length=15):
    with async_timeout.timeout(None):
        async with session.get(url, params = {'source': source,'evalue': evalue, 'identity': identity, 'length': length, 'type': 'all'}) as response:
            filename = '%(group)s_%(sample)s.tsv' % \
                {"group": group, "sample": sample}

            async with aiofiles.open(filename, 'wb') as fd:
                while True:
                    chunk = await response.content.read(10240)
                    if not chunk:
                        break
                    await fd.write(chunk)
            return await response.release()


async def download_geneonly_coroutine(session, url, study, idList, source, evalue=5, identity=60, length=15):
    with async_timeout.timeout(None):
        params_ids = {'id': mgID for mgID in idList}
        params_other =  {'source': source,'evalue': evalue, 'identity': identity, 'length': length}
        params = params_ids.copy()
        params.update(params_other)
        async with session.get(url, params = params) as response:
            filename = '%(study)s_function_counts.biom' % \
                {"study": study}

            async with aiofiles.open(filename, 'wb') as fd:
                while True:
                    chunk = await response.content.read(10240)
                    if not chunk:
                        break
                    await fd.write(chunk)
            return await response.release()
'''
async def main(loop, study, metagenomeGroupDict, source, evalue, identity, length):
    metagenomeGroupDF = pd.DataFrame({'metagenome ID' : list(metagenomeGroupDict.keys()),'group' : list(metagenomeGroupDict.values())})
    metagenomeGroupDF['sample'] = metagenomeGroupDF.groupby('group').cumcount()+1

    urls = ["http://api.metagenomics.anl.gov/annotation/similarity/" + str(id) for id in metagenomeGroupDF['metagenome ID']]
    geneOnlySeries = pd.Series(['all', 'gene-only', 'counts-all'], index=['metagenome ID','group','sample'])
    #metagenomeGroupDF.append(geneOnlySeries, ignore_index=True)
    geneOnlyURL = 'http://api.metagenomics.anl.gov/matrix/function'# + ''.join()id=mgm4447943.3&id=mgm4447192.3&id=mgm4447102.3  

    async with aiohttp.ClientSession(loop=loop) as session:
'''
       # for i in range(len(metagenomeGroupDF)):
           #await download_coroutine(session, urls[i], metagenomeGroupDF['group'][i], metagenomeGroupDF['sample'][i], source, evalue, identity, length)
        #await download_geneonly_coroutine(session, geneOnlyURL, study, metagenomeGroupDF['metagenome ID'], source, evalue, identity, length)
'''
    tasks = [asyncio.ensure_future(download_coroutine(session, urls[i], metagenomeGroupDF['group'][i], metagenomeGroupDF['sample'][i], source, evalue, identity, length)) for i in range(len(metagenomeGroupDF))]
'''

def ensure_all_futures(loop, study, metagenomeGroupDict, source, evalue, identity, length):
   metagenomeGroupDF = pd.DataFrame({'metagenome ID' : list(metagenomeGroupDict.keys()),'group' : list(metagenomeGroupDict.values())})
   metagenomeGroupDF['sample'] = metagenomeGroupDF.groupby('group').cumcount()+1
   urls = ["http://api.metagenomics.anl.gov/annotation/similarity/" + str(id) for id in metagenomeGroupDF['metagenome ID']]
   geneOnlyURL = 'http://api.metagenomics.anl.gov/matrix/function'# + ''.join()id=mgm4447943.3&id=mgm4447192.3&id=mgm4447102.3  

   with aiohttp.ClientSession(loop=loop) as session:
      tasks = [asyncio.ensure_future(download_coroutine(session, urls[i], metagenomeGroupDF['group'][i], metagenomeGroupDF['sample'][i], source, evalue, identity, length)) for i in range(len(metagenomeGroupDF))]
      tasks.append(asyncio.ensure_future(download_geneonly_coroutine(session, geneOnlyURL, study, metagenomeGroupDF['metagenome ID'], source, evalue, identity, length)))
      return tasks

def download_study_data(study, metagenomeGroupDict, source, evalue, identity, length):
#if __name__ == '__main__':
    metagenomeGroupDF = pd.DataFrame({'metagenome ID' : list(metagenomeGroupDict.keys()),'group' : list(metagenomeGroupDict.values())})
    metagenomeGroupDF['sample'] = metagenomeGroupDF.groupby('group').cumcount()+1
    loop = asyncio.get_event_loop()
#   async with aiohttp.ClientSession(loop=loop) as session:
#       tasks = [asyncio.ensure_future(download_coroutine(session, urls[i], metagenomeGroupDF['group'][i], metagenomeGroupDF['sample'][i], source, evalue, identity, length)) for i in range(len(metagenomeGroupDF))]
#       tasks.append(asyncio.ensure_future(download_geneonly_coroutine(session, geneOnlyURL, study, metagenomeGroupDF['metagenome ID'], source, evalue, identity, length)))
    #loop.run_until_complete(main(loop, study, metagenomeGroupDict, source, evalue, identity, length))
    loop.run_until_complete(asyncio.wait(ensure_all_futures(loop, study, metagenomeGroupDict, source, evalue, identity, length)))


