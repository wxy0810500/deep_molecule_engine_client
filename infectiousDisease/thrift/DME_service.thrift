# Interface definition of DME service
# coding = utf-8
# Created   :   1,  8, 2020
# Revised   :   4,  1, 2020  add 'aux_data' field in DME_input
# Author    :  David Leon (dawei.leng@ghddi.org)
# All rights reserved

# constants
const string __version__    = '1.0.1'

# server input
struct DME_input {
    1: required string sample_id,
    2: required string SMILES,
    3: required string task,           # service task {'LBVS' | 'SBVS'}
    4: required binary aux_data,       # auxiliary data, packed in binary format
}

# server return
struct DME_return {
    1: required string sample_id,
    2: required string result,         # '%s-%d-%0.4f' % (predicted_label, predicted_idx, predicted_score)
    3: required i64    err_code,
    4: required string version,        # '%s|%s|%s' % (DME_engine_version, model_file_md5, label_file_md5)
}

service DME {
    list<DME_return> DME_predict(1:list<DME_input> inputs),
}