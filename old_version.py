import matplotlib.pylab as plt
import os
import numpy as np
from scipy.ndimage import binary_dilation

from dipy.tracking.utils import length 
import nibabel as nib
from dipy.data import get_sphere
from dipy.tracking import utils
from dipy.core.gradients import gradient_table
from dipy.io.gradients import read_bvals_bvecs
from dipy.io.image import load_nifti_data, load_nifti
from dipy.direction import peaks
from dipy.reconst import shm
from dipy.reconst.dti import TensorModel
from dipy.reconst.dti import fractional_anisotropy
from dipy.reconst.dti import color_fa
from dipy.reconst.shm import CsaOdfModel
from dipy.segment.mask import median_otsu
from dipy.tracking import utils
from dipy.tracking.local_tracking import LocalTracking
from dipy.tracking.stopping_criterion import BinaryStoppingCriterion
from dipy.tracking.streamline import Streamlines
from dipy.direction import peaks
from dipy.reconst.eudx_direction_getter import EuDXDirectionGetter

from dipy.io.stateful_tractogram import Space, StatefulTractogram
from dipy.io.streamline import save_trk


def process_to_streamlines(filename = None, number = 10159, do_draw = False):
    # load data
    if filename == None:
        data, affine, load_img = load_nifti(f"./sub-{number}/dwi/sub-{number}_dwi.nii.gz", return_img=True)
        bvals, bvecs = read_bvals_bvecs(f"./sub-{number}/dwi/sub-{number}_dwi.bval", f"./sub-{number}/dwi/sub-{number}_dwi.bvec")
        gtab = gradient_table(bvals, bvecs)
        mask, S0_mask = median_otsu(data[:, :, :, 0])
        print("File read!")
    else:
        data, affine, load_img = load_nifti(filename, return_img=True)
        bvals, bvecs = read_bvals_bvecs(f"./sub-{number}/dwi/sub-{number}_dwi.bval", f"./sub-{number}/dwi/sub-{number}_dwi.bvec")
        gtab = gradient_table(bvals, bvecs)
        mask, S0_mask = median_otsu(data[:, :, :, 0])
        print("File read!")

    # choosing part of the brain
    # white_matter = binary_dilation((labels == 1) | (labels == 2)) 
    # it probably doesn't work this way, white_matter mask may look different in this files
    #build diffusion model
    gtab = gradient_table(bvals, bvecs)
    ten_model = TensorModel(gtab)
    ten_fit = ten_model.fit(data, mask)
    print("Tensor model!")

    fa = fractional_anisotropy(ten_fit.evals)
    cfa = color_fa(fa, ten_fit.evecs)
    csamodel = CsaOdfModel(gtab, 6)
    sphere = get_sphere('symmetric724')
    print("CSA Model!")

    pmd = peaks.peaks_from_model(model=csamodel,
                        data=data,
                        sphere=sphere,
                        relative_peak_threshold=.5,
                        min_separation_angle=25,
                        mask=mask,
                        return_odf=False)
    
    print("Peaks")

    #Run deterministic tractography 
    eu = EuDXDirectionGetter(a=fa, ind=pmd.peak_indices[..., 0], seeds=2000000, odf_vertices=sphere.vertices, a_low=0.01)
    affine = eu.affine
    csd_streamlines= list(eu)
    print("EuDX")

    #Remove tracts shorter than 30mm
    #print np.shape(csd_streamlines)
    csd_streamlines=[t for t in csd_streamlines if length(t)>30]
    print("Streamlines")
    
    #Save trackvis
    hdr = nib.trackvis.empty_header()
    hdr['voxel_size'] = load_img.get_header().get_zooms()[:3]
    hdr['voxel_order'] = 'LAS'
    hdr['dim'] = fa.shape
    tensor_streamlines_trk = ((sl, None, None) for sl in csd_streamlines)
    ten_sl_fname = 'cc_streamlines.trk'
    nib.trackvis.write(ten_sl_fname, tensor_streamlines_trk, hdr, points_space='voxel')
    print("Trakcvis")
    
    atlas = nib.load('atlas_reg.nii.gz')
    labels = atlas.get_data()
    labelsint = labels.astype(int)
    print("Atlas")
    
    #M, grouping = utils.connectivity_matrix(csd_streamlines, labelsint, affine=affine,    return_mapping=True,  mapping_as_streamlines=True)
    M = utils.connectivity_matrix(csd_streamlines, labelsint, affine=affine)
    print("Connectivity matrix")

    # plot cennectivity matrix
    if do_draw:
        plt.imshow(np.log1p(M), interpolation='nearest')
        plt.savefig(f"connectivity-{number}.png")
    # except:
    #     print(f"File = {filename}, number = {number}: Error while processing data")
    #     M = None

    return M   

def process_to_streamlines(filename = None, number = 10159, do_draw = False):
    # load data
    if filename == None:
        data, affine, load_img = load_nifti(f"./sub-{number}/dwi/sub-{number}_dwi.nii.gz", return_img=True) #f"./sub-{number}/anat/sub-10159_T1w.nii.gz"
        bvals, bvecs = read_bvals_bvecs(f"./sub-{number}/dwi/sub-{number}_dwi.bval", f"./sub-{number}/dwi/sub-{number}_dwi.bvec")
        gtab = gradient_table(bvals, bvecs)
        labels = load_nifti_data(f"./sub-{number}/dwi/sub-{number}_dwimask.nii.gz")
        # labels = load_nifti_data(f"./sub-{number}/dwi/sub-{number}_dwi_seg.nii.gz")
    else:
        data, affine, load_img = load_nifti(filename, return_img=True) #f"./sub-{number}/anat/sub-10159_T1w.nii.gz"
        bvals, bvecs = read_bvals_bvecs(f"./sub-{number}/dwi/sub-{number}_dwi.bval", f"./sub-{number}/dwi/sub-{number}_dwi.bvec")
        gtab = gradient_table(bvals, bvecs)
        labels = load_nifti_data(filename[:-7] + "mask.nii.gz")
        # labels = load_nifti_data(f"./sub-{number}/dwi/sub-{number}_dwi_seg.nii.gz")

    # choosing part of the brain
    # white_matter = binary_dilation((labels == 1) | (labels == 2)) 
    # it probably doesn't work this way, white_matter mask may look different in this files
    try:
        # print(labels.shape, labels)
        white_matter = binary_dilation((labels == 1) | (labels == 2)) 
        csamodel = shm.CsaOdfModel(gtab, 6)
        # print(white_matter.shape, data.shape)
        csapeaks = peaks.peaks_from_model(model=csamodel,
                                        data=data,
                                        sphere=peaks.default_sphere,
                                        relative_peak_threshold=.8,
                                        min_separation_angle=45)

        affine = np.eye(4)
        seeds = utils.seeds_from_mask(white_matter, affine, density=1)
        stopping_criterion = BinaryStoppingCriterion(white_matter)

        # choosing tracks model
        streamline_generator = LocalTracking(csapeaks, stopping_criterion, seeds,
                                            affine=affine, step_size=0.5) # we can change stopping criterion here
        streamlines = Streamlines(streamline_generator)

        # choosing proper brain slice (verify if it is necessary)
        cc_slice = labels == 2
        cc_streamlines = utils.target(streamlines, affine, cc_slice)
        cc_streamlines = Streamlines(cc_streamlines)

        # save streamlines
        sft = StatefulTractogram(cc_streamlines, load_img, Space.VOX)
        save_trk(sft, "cc_streamlines.trk")

        # create connectivity matrix
        # print(cc_streamlines)
        M, _ = utils.connectivity_matrix(cc_streamlines, affine,
                                            labels.astype(np.uint8),
                                            return_mapping=True,
                                            mapping_as_streamlines=True)
        M[:3, :] = 0
        M[:, :3] = 0

        # plot cennectivity matrix
        if do_draw:
            plt.imshow(np.log1p(M), interpolation='nearest')
            plt.savefig(f"connectivity-{number}.png")
    except:
        print(f"File = {filename}, number = {number}: Error while processing data")
        M = None

    return M   