# Interface definition of DME service
# coding = utf-8
# Created   :   1,  8, 2020
# Revised   :   
# Author    :  David Leon (dawei.leng@ghddi.org)
# All rights reserved

# constants
const string __version__    = '1.0.0'

# server input
struct DME_input {
    1: required string sample_id,
    2: required string SMILES,
    3: required string task,      # service task
}

# server return
struct DME_return {
    1: required string sample_id,
    2: required string result,
    3: required i64    err_code,
    4: required string version,
}

service DME {
    list<DME_return> DME_predict(1:list<DME_input> inputs),
}