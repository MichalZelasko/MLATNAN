#!/bin/bash
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-70086/dwi/sub-70086_dwi.bval?versionId=eZJYZu2Wf9Vn26caaX68LZdNeJ_VVYW5 -o sub-10159/dwi/sub-10159_dwi.bval
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-70052/dwi/sub-70052_dwi.bvec?versionId=QnLEzLmVhJ4l3lSIbnw8EVMM9Ih3htOK -o sub-10159/dwi/sub-10159_dwi.bvec
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-10159/dwi/sub-10159_dwi.json?versionId=iW6eXaBlR4WuP5bbMJR0.q8GROtogRLf -o sub-10159/dwi/sub-10159_dwi.json
curl --create-dirs https://s3.amazonaws.com/openneuro.org/ds000030/sub-10159/dwi/sub-10159_dwi.nii.gz?versionId=L3wsoqPBy1MZqPDW4.Oss1WLBILEsfNj -o sub-10159/dwi/sub-10159_dwi.nii.gz
export FSLOUTPUTTYPE=NIFTI_GZ
export PATH="/usr/local/fsl/bin$PATH"
export FSLDIR="/usr/local/fsl"
eddy_correct ./sub-10159/dwi/sub-10159_dwi.nii.gz  ./sub-10159/dwi/sub-10159_dwi_eddycorrected.nii.gz -interp trilinear
3drefit -deoblique ./sub-10159/dwi/sub-10159_dwi.nii.gz
3dresample -orient RPI -inset sub-10159/dwi/sub-10159_dwi.nii.gz -prefix ./sub-10159/dwi/sub-10159_dwi_ro.nii.gz
bet ./sub-10159/dwi/sub-10159_dwi_ro.nii.gz brain.nii.gz -m -R -f 0.4
fslmaths ./sub-10159/dwi/sub-10159_dwi_eddycorrected.nii.gz ./sub-10159/dwi/sub-10159_dwi_bet.nii.gz
flirt -ref ./sub-10159/dwi/sub-10159_dwi_bet.nii.gz -in  ./atlas/MNI152lin_T1_1mm_brain.nii.gz -omat ./atlas/my_mat.mat
flirt -ref ./sub-10159/dwi/sub-10159_dwi_bet.nii.gz -in  ./atlas/aal.nii -applyxfm -init my_mat.mat -out ./atlas/atlas_reg.nii.gz -interp nearestneighbour
