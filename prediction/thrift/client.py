# coding:utf-8
"""
DME client interface, built upon thrift
Created   :   1, 10, 2020
Revised   :
All rights reserved
"""
__author__ = 'dawei.leng'
__version__ = '1.0.0'

import os
import time

import thriftpy2 as thriftpy
from thriftpy2.rpc import make_client
from typing import Mapping

here = os.path.abspath(os.path.dirname(__file__))
thrift_file = os.path.join(here, 'DME_service.thrift')


# thrift_file = 'DME_service.thrift'

class DMEClient:

    def __init__(self,
                 thriftFile=thrift_file,
                 ):
        self.thriftFile = thriftFile
        self.thriftDef = thriftpy.load(self.thriftFile, module_name="DME_thrift")

    def make_worker(self, server_host, server_port, time_out=3):
        """
        :param server_host:
        :param server_port:
        :param time_out: seconds
        :return:
        """
        client_worker = make_client(self.thriftDef.DME, server_host, server_port, timeout=time_out * 1000)
        return client_worker

    def do_task(self, client_worker, task: str, SMILES_dict: Mapping, aux_data: bytes):
        """
        :param client_worker: a client worker instance returned by self.make_client
        :param SMILES_dict: {sample_id:{'smiles':SMILES}}:
        :@param task: lbvs, sbvs
        :return: results,  list of string, predicted results, can be labeled or just numeric
                 err_codes, list of int
                 task_time, time cost for the task
                 server_info, server information, string
        """
        server_inputs = []
        for smilesIndex, smilesInfo in SMILES_dict.items():
            sample_id = str(smilesIndex)
            one_input = self.thriftDef.DME_input(sample_id, smilesInfo['cleaned_smiles'], task, aux_data)
            server_inputs.append(one_input)

        time0 = time.time()
        predicted_results = client_worker.DME_predict(server_inputs)
        task_time = time.time() - time0

        # --- restore the order ---#
        predicted_results.sort(key=lambda retRecord: retRecord.sample_id)
        server_info = predicted_results[0].version
        # print(predicted_results)
        # predicted_results: List[
        #       {string sample_id,
        #        string result,
        #        i64 err_code,
        #        string version}]
        #
        # | Errcode      | Explanation  | Action   |
        # | -----------  | ------------ | -------- |
        # | 1            | Exception raised when input queue if full |  Try later |
        # | 2            | Exception raised when invalid SMILES encountered | Check input |
        # | 3            | Exception raised when maximum time reached for the infectiousDisease task | Reduce the input size |
        # | 1000         | Exception raised when unknown error raised | Report to algorithm developers |
        # results 格式
        # errcode为0时：
        # "active" 是服务返回的标签；//用户关心
        # “1”     是模型返回的类别；
        # ”0.6089“是模型返回的预测打分 //用户关心

        return task_time, server_info, predicted_results
