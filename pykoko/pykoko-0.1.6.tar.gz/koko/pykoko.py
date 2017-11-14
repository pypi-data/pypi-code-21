"""
Copyright 2017 Recruit Institute of Technology

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import logging
from .query_processor import QueryProcessor


def run(query_file, doc_parser="koko", output_format="text", log_level="info", target_lang='en', embedding_file="../input/embedding.txt"):
    # Set up logging
    logging_level_dict = {'info': logging.INFO,
                          'warning': logging.WARNING,
                          'error': logging.ERROR}
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging_level_dict[log_level])
    formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    with open(query_file, 'r') as qfile:
        query = qfile.read()

    # Process the KOKO query

    processor = QueryProcessor(doc_parser, target_lang)
    response = processor.ProcessQuery(query, embedding_path=embedding_file)

    # Print the results
    if output_format == 'text':
        print("\nResults:\n")
        #print("%s %s" % ("{:<50}".format("Entity name"), "Entity score"))
        print("%s %s %s" % ("{:<30}".format("Entity name"), "{:<20}".format("Entity count"), "Entity score"))        
        #print("===============================================================")
        print("="*70)
        for entity in response.entities:
            #print("%s %f" % ("{:<50}".format(entity.name), entity.score))
            print("%s %s %f" % ("{:<30}".format(entity.name), "{:<20}".format(str(len(entity.mentions))), entity.score))
    else:
        import json
        import jsonpickle
        pickled = jsonpickle.encode(response, unpicklable=False)
        json_result = json.loads(pickled)
        print(json.dumps(json_result, sort_keys=False, indent=2))
        with open('json_result.txt', 'w') as ofile:
            json.dump(json_result, ofile)
