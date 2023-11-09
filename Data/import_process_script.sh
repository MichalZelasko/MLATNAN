#!/bin/bash
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-70086/dwi/sub-70086_dwi.bval?versionId=eZJYZu2Wf9Vn26caaX68LZdNeJ_VVYW5 -o sub-10171/dwi/sub-10171_dwi.bval
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-70052/dwi/sub-70052_dwi.bvec?versionId=QnLEzLmVhJ4l3lSIbnw8EVMM9Ih3htOK -o sub-10171/dwi/sub-10171_dwi.bvec
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-10171/dwi/sub-10171_dwi.json?versionId=g1x9gpdPMjnCNgOdSlifNrXOub61f8oc -o sub-10171/dwi/sub-10171_dwi.json
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-10171/dwi/sub-10171_dwi.nii.gz?versionId=sF.q2FFvJVIbE6xqNn8Qwdlu3ZgeTK6t -o sub-10171/dwi/sub-10171_dwi.nii.gz
export FSLOUTPUTTYPE=NIFTI_GZ
export PATH="/usr/local/fsl/bin$PATH"
export FSLDIR="/usr/local/fsl"
bet ./sub-10171/dwi/sub-10171_dwi.nii.gz ./sub-10171/dwi/sub-10171_dwimask.nii.gz
