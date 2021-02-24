from typing import Tuple, List

from prediction.forms import StructureModelInputForm
from smiles.searchService import searchDrugReferenceByInputRequest
import os
from utils.fileUtils import handleUploadedFile
from prediction.predictionTask import processTasks, StructureModelTypeAndPortDict, \
    PREDICTION_TASK_TYPE_SBVS, PredictionTaskRet
import numpy as np
from typing import Sequence, List, Dict

DB_FILE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')


def __getCleanedSmilesInfoListFromInputForm(request, inputForm) -> Tuple[List[dict], List[str]]:
    drugRefDF, invalidInputList = searchDrugReferenceByInputRequest(request, inputForm)
    if drugRefDF.size == 0:
        return None, invalidInputList
    return drugRefDF[['input', 'drug_name', 'cleaned_smiles']].to_dict(orient='records'), invalidInputList


def __distanceMatrix(pts1, pts2):
    # pts.shape = k, 3
    sumsq1 = (pts1 ** 2).sum(axis=1)
    sumsq2 = (pts2 ** 2).sum(axis=1)
    k2 = pts2.shape[0]
    dis_cor = sumsq1 + sumsq2.reshape(k2, 1) - 2 * pts2.dot(pts1.T)
    return dis_cor[0]


def __getPocket(rawPDBContent, cxyz: tuple, cutoff_r=15):
    lns = rawPDBContent.splitlines()

    xyz = []
    valid_lns = []
    for ln in lns:
        if ln.startswith('ATOM'):
            x = float(ln[30:38])
            y = float(ln[38:46])
            z = float(ln[46:54])
            xyz.append([x, y, z])
            valid_lns.append(ln)
    xyz = np.array(xyz)

    cxyz = np.array(cxyz).reshape(1, 3)

    d = __distanceMatrix(xyz, cxyz)
    pocket_idx = np.where(d < (cutoff_r ** 2))[0]
    pocketList = [valid_lns[i] for i in pocket_idx]
    return '\n'.join(pocketList)


def predictSBVS(modelTypes: Sequence, smilesInfoList: List, pdbContent: str) -> List[Dict[str, PredictionTaskRet]]:
    return processTasks(StructureModelTypeAndPortDict, modelTypes, smilesInfoList, PREDICTION_TASK_TYPE_SBVS,
                        pdbContent)


def processSBVS(request, inputForm: StructureModelInputForm):
    smilesInfoList, invalidInputList = __getCleanedSmilesInfoListFromInputForm(request, inputForm)
    if smilesInfoList:
        # get pdbFile
        pdbContent = handleUploadedFile(request.FILES['uploadPDBFile'])
        pdbFileType = inputForm.cleaned_data['pdbFileType']
        if StructureModelInputForm.PDB_FILE_TYPE_POCKET == pdbFileType:
            pdbContent = __getPocket(pdbContent, (inputForm.cleaned_data['cx'],
                                                  inputForm.cleaned_data['cy'],
                                                  inputForm.cleaned_data['cz']))
        modelTypes = inputForm.cleaned_data['modelTypes']
        preRetList, allSmilesDict = predictSBVS(modelTypes, smilesInfoList, pdbContent)
    else:
        preRetList = None
    return preRetList, invalidInputList
