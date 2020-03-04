# coding:utf-8
"""
DME client interface, built upon thrift
Created   :   1, 10, 2020
Revised   :
All rights reserved
"""
__author__ = 'dawei.leng'
__version__ = '1.0.0'

import time, os
import thriftpy2 as thriftpy
from thriftpy2.rpc import make_client

here = os.path.abspath(os.path.dirname(__file__))
thrift_file = os.path.join(here, 'DME_service.thrift')
# thrift_file = 'DME_service.thrift'

class DME_client:
    def __init__(self,
                 thrift_file=thrift_file,
                 ):
        self.thrift_file = thrift_file
        self.thriftdef   = thriftpy.load(self.thrift_file, module_name="DME_thrift")

    def make_worker(self, server_host, server_port, time_out=3):
        """
        :param server_host:
        :param server_port:
        :param time_out: seconds
        :return:
        """
        client_worker = make_client(self.thriftdef.DME, server_host, server_port, timeout=time_out*1000)
        return client_worker

    def do_task(self, client_worker, SMILES_list):
        """
        :param client_worker: a client worker instance returned by self.make_client
        :param SMILES_list:
        :return: results,  list of string, predicted results, can be labeled or just numeric
                 err_codes, list of int
                 task_time, time cost for the task
                 server_info, server information, string
        """
        server_inputs = []
        task = 'classification'
        for i, SMILES in enumerate(SMILES_list):
            sample_id = 'sample_%d' % i
            one_input = self.thriftdef.DME_input(sample_id, SMILES, task)
            server_inputs.append(one_input)

        time0 = time.time()
        predicted_results = client_worker.DME_predict(server_inputs)
        task_time = time.time() - time0

        #--- restore the order ---#
        results, err_codes = [], []
        result_dict = {}
        for record in predicted_results:
            result_dict[record.sample_id] = [record.result, record.err_code, record.version]
        for record in server_inputs:
            results.append(result_dict[record.sample_id][0])
            err_codes.append(result_dict[record.sample_id][1])
        server_info = predicted_results[0].version

        return results, err_codes, task_time, server_info

