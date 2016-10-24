# -*- coding: utf-8 -*-

"""

Created on Mon Sep  2 11:59:50 2013



Calculates dose metrics using dose to structure from DicomManipulation.py



@author: Jamie Dean

"""



from __future__ import division

import numpy as np

np.set_printoptions(threshold=np.nan)

import matplotlib.pyplot as plt

from scipy import ndimage

from mayavi import mlab

import glob

import dicom

import pandas as pd





class DoseMetrics(object):



    

    def __init__(self, patientID, structureName):

        

        self.patientID = patientID

        self.structureName = structureName



        

    def load_oar_dose_distribution(self, ctSliceThickness, alphaBetaRatio, addChemoBED, chemoBED, noConChemo):

        """Loads the OAR dose distributions and dose cube coordinates generated by DicomManipulation.py"""

        

        print 'Running load_oar_dose_distribution() ...'

        

        if self.structureName != 'OMPM' and self.structureName != 'OMpartialPM' and self.structureName != 'OM2PM' and self.structureName != 'OM2partialPM' and self.structureName != 'SCMCIC':

	    #oarDoseDistFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

	    oarDoseDistFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'totalPhysicalDoseDistribution.npy'

	    oarDoseDist = np.load(oarDoseDistFile)

        

        elif self.structureName == 'OMPM':

            oarDoseDistFileOM = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistOM = np.load(oarDoseDistFileOM)

            oarDoseDistPM = np.load(oarDoseDistFilePM)

            # Use sets to find the voxels that are included in both structures

            nonzeroOM = set(np.nonzero(oarDoseDistOM.flatten())[0])

            nonzeroPM = set(np.nonzero(oarDoseDistPM.flatten())[0])

            # NB. need to list elements in set

            overlap = list(nonzeroOM & nonzeroPM)

            # When structure dose distributions are summed voxels included in both structures are counted twice

            oarDoseDist = oarDoseDistOM + oarDoseDistPM

            oarDoseDistFlat = oarDoseDist.flatten()

            # Divide by 2 to reverse summing the dose in voxels that are included in both structures

            oarDoseDistFlat[overlap] = oarDoseDistFlat[overlap]/2.0

            oarDoseDist = oarDoseDistFlat.reshape(oarDoseDistOM.shape)

        

        elif self.structureName == 'OMpartialPM':

            oarDoseDistFileOM = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM' + 'doseDistPhysical.npy'

            oarDoseDistFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'doseDistPhysical.npy'

            oarDoseDistOM = np.load(oarDoseDistFileOM)

            oarDoseDistPM = np.load(oarDoseDistFilePM)

            

            structCoordsFileOM = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM' + 'structureCoords.npy'

            structCoordsFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'structureCoords.npy'

            structCoordsOM = np.load(structCoordsFileOM)

            structCoordsPM = np.load(structCoordsFilePM)

            print np.min(structCoordsOM[2]), np.max(structCoordsOM[2])

            numSlicesOM = (np.max(structCoordsOM[2]) - np.min(structCoordsOM[2]))/ctSliceThickness

            print np.min(structCoordsPM[2]), np.max(structCoordsPM[2])

            numSlicesPM = (np.max(structCoordsPM[2]) - np.min(structCoordsPM[2]))/ctSliceThickness

            

            resampledDoseCubeCoordsOMFile = 'OutputData/' + self.patientID + '/' + self.patientID + 'resampledDoseCubeCoords.npy'

            resampledDoseCubeCoordsOM = np.load(resampledDoseCubeCoordsOMFile)

            resampledDoseCubeCoordsPMFile = 'OutputData/' + self.patientID + '/' + self.patientID + 'resampledDoseCubeCoords.npy'

            resampledDoseCubeCoordsPM = np.load(resampledDoseCubeCoordsPMFile)

            print np.min(resampledDoseCubeCoordsOM[2]), np.max(resampledDoseCubeCoordsOM[2])

            print np.min(resampledDoseCubeCoordsPM[2]), np.max(resampledDoseCubeCoordsPM[2])

            

            partialPMsuperiorBorder = np.argwhere(np.array(resampledDoseCubeCoordsPM[2]) == np.min(structCoordsOM[2]))

            partialPMinferiorBorder = np.argwhere(np.array(resampledDoseCubeCoordsPM[2]) == np.max(structCoordsOM[2]))

            print partialPMsuperiorBorder, partialPMinferiorBorder

            

            print resampledDoseCubeCoordsPM[0].shape, resampledDoseCubeCoordsPM[1].shape, resampledDoseCubeCoordsPM[2].shape

            print oarDoseDistPM.shape

            

            oarDoseDistPartialPM = oarDoseDistPM

            print np.min(oarDoseDistPartialPM), np.max(oarDoseDistPartialPM)

            oarDoseDistPartialPM[:, :, :(numSlicesPM - numSlicesOM)] = 0

            oarDoseDistPartialPM[:, :, numSlicesPM:] = 0

            print np.min(oarDoseDistOM), np.max(oarDoseDistOM)

            print np.min(oarDoseDistPartialPM), np.max(oarDoseDistPartialPM)

            oarDoseDistShiftedOM = np.roll(oarDoseDistOM, shift = int((np.min(structCoordsOM[2]) - np.min(resampledDoseCubeCoordsOM[2]))/ctSliceThickness), axis = 2)

            oarDoseDistShiftedPartialPM = np.roll(oarDoseDistPartialPM, shift = int((np.min(structCoordsPM[2]) - np.min(resampledDoseCubeCoordsPM[2]))/ctSliceThickness), axis = 2)

            

            # Use sets to find the voxels that are included in both structures

            nonzeroOM = set(np.nonzero(oarDoseDistShiftedOM.flatten())[0])

            nonzeroPartialPM = set(np.nonzero(oarDoseDistShiftedPartialPM.flatten())[0])

            

            # NB. need to list elements in set

            overlap = list(nonzeroOM & nonzeroPartialPM)

            # When structure dose distributions are summed voxels included in both structures are counted twice

            oarDoseDist = oarDoseDistShiftedOM + oarDoseDistShiftedPartialPM

            oarDoseDistFlat = oarDoseDist.flatten()

            # Divide by 2 to reverse summing the dose in voxels that are included in both structures

            oarDoseDistFlat[overlap] = oarDoseDistFlat[overlap]/2.0

            oarDoseDist = oarDoseDistFlat.reshape(oarDoseDistOM.shape)

        

        elif self.structureName == 'OM2PM':

            oarDoseDistFileOM2 = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM2' + 'doseDistPhysical.npy'

            #oarDoseDistFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'doseDistPhysical.npy'

            oarDoseDistOM2 = np.load(oarDoseDistFileOM2)

            oarDoseDistPM = np.load(oarDoseDistFilePM)

            # Use sets to find the voxels that are included in both structures

            nonzeroOM2 = set(np.nonzero(oarDoseDistOM2.flatten())[0])

            nonzeroPM = set(np.nonzero(oarDoseDistPM.flatten())[0])

            # NB. need to list elements in set

            overlap = list(nonzeroOM2 & nonzeroPM)

            # When structure dose distributions are summed voxels included in both structures are counted twice

            oarDoseDist = oarDoseDistOM2 + oarDoseDistPM

            oarDoseDistFlat = oarDoseDist.flatten()

            # Divide by 2 to reverse summing the dose in voxels that are included in both structures

            oarDoseDistFlat[overlap] = oarDoseDistFlat[overlap]/2.0

            oarDoseDist = oarDoseDistFlat.reshape(oarDoseDistOM2.shape)

            

        elif self.structureName == 'OM2partialPM':

            oarDoseDistFileOM2 = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM2' + 'doseDistPhysical.npy'

            oarDoseDistFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'doseDistPhysical.npy'

            oarDoseDistOM2 = np.load(oarDoseDistFileOM2)

            oarDoseDistPM = np.load(oarDoseDistFilePM)

            

            structCoordsFileOM2 = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM2' + 'structureCoords.npy'

            structCoordsFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'structureCoords.npy'

            structCoordsOM2 = np.load(structCoordsFileOM2)

            structCoordsPM = np.load(structCoordsFilePM)

            print np.min(structCoordsOM2[2]), np.max(structCoordsOM2[2])

            numSlicesOM2 = (np.max(structCoordsOM2[2]) - np.min(structCoordsOM2[2]))/ctSliceThickness

            print np.min(structCoordsPM[2]), np.max(structCoordsPM[2])

            numSlicesPM = (np.max(structCoordsPM[2]) - np.min(structCoordsPM[2]))/ctSliceThickness

            

            resampledDoseCubeCoordsOM2File = 'OutputData/' + self.patientID + '/' + self.patientID + 'resampledDoseCubeCoords.npy'

            resampledDoseCubeCoordsOM2 = np.load(resampledDoseCubeCoordsOM2File)

            resampledDoseCubeCoordsPMFile = 'OutputData/' + self.patientID + '/' + self.patientID + 'resampledDoseCubeCoords.npy'

            resampledDoseCubeCoordsPM = np.load(resampledDoseCubeCoordsPMFile)

            print np.min(resampledDoseCubeCoordsOM2[2]), np.max(resampledDoseCubeCoordsOM2[2])

            print np.min(resampledDoseCubeCoordsPM[2]), np.max(resampledDoseCubeCoordsPM[2])

            

            partialPMsuperiorBorder = np.argwhere(np.array(resampledDoseCubeCoordsPM[2]) == np.min(structCoordsOM2[2]))

            partialPMinferiorBorder = np.argwhere(np.array(resampledDoseCubeCoordsPM[2]) == np.max(structCoordsOM2[2]))

            print partialPMsuperiorBorder, partialPMinferiorBorder

            

            print resampledDoseCubeCoordsPM[0].shape, resampledDoseCubeCoordsPM[1].shape, resampledDoseCubeCoordsPM[2].shape

            print oarDoseDistPM.shape

            

            oarDoseDistPartialPM = oarDoseDistPM

            print np.min(oarDoseDistPartialPM), np.max(oarDoseDistPartialPM)

            oarDoseDistPartialPM[:, :, :(numSlicesPM - numSlicesOM2)] = 0

            oarDoseDistPartialPM[:, :, numSlicesPM:] = 0

            print np.min(oarDoseDistOM2), np.max(oarDoseDistOM2)

            print np.min(oarDoseDistPartialPM), np.max(oarDoseDistPartialPM)

            oarDoseDistShiftedOM2 = np.roll(oarDoseDistOM2, shift = int((np.min(structCoordsOM2[2]) - np.min(resampledDoseCubeCoordsOM2[2]))/ctSliceThickness), axis = 2)

            oarDoseDistShiftedPartialPM = np.roll(oarDoseDistPartialPM, shift = int((np.min(structCoordsPM[2]) - np.min(resampledDoseCubeCoordsPM[2]))/ctSliceThickness), axis = 2)

            

            # Use sets to find the voxels that are included in both structures

            nonzeroOM2 = set(np.nonzero(oarDoseDistShiftedOM2.flatten())[0])

            nonzeroPartialPM = set(np.nonzero(oarDoseDistShiftedPartialPM.flatten())[0])

            

            # NB. need to list elements in set

            overlap = list(nonzeroOM2 & nonzeroPartialPM)

            # When structure dose distributions are summed voxels included in both structures are counted twice

            oarDoseDist = oarDoseDistShiftedOM2 + oarDoseDistShiftedPartialPM

            oarDoseDistFlat = oarDoseDist.flatten()

            # Divide by 2 to reverse summing the dose in voxels that are included in both structures

            oarDoseDistFlat[overlap] = oarDoseDistFlat[overlap]/2.0

            oarDoseDist = oarDoseDistFlat.reshape(oarDoseDistOM2.shape)    

                    

        elif self.structureName == 'SCMCIC':

            oarDoseDistFileSC = 'OutputData/' + self.patientID + '/' + self.patientID + 'SC' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistFileMC = 'OutputData/' + self.patientID + '/' + self.patientID + 'MC' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistFileIC = 'OutputData/' + self.patientID + '/' + self.patientID + 'IC' + 'doseDistBED' + str(alphaBetaRatio) + '.npy'

            oarDoseDistSC = np.load(oarDoseDistFileSC)

            oarDoseDistMC = np.load(oarDoseDistFileMC)

            oarDoseDistIC = np.load(oarDoseDistFileIC)

            # Use sets to find the voxels that are included in multiple structures

            nonzeroSC = set(np.nonzero(oarDoseDistSC.flatten())[0])

            nonzeroMC = set(np.nonzero(oarDoseDistMC.flatten())[0])

            nonzeroIC = set(np.nonzero(oarDoseDistIC.flatten())[0])

            # NB. need to list elements in set

            overlap2 = list(nonzeroSC & nonzeroMC) + list(nonzeroMC & nonzeroIC) + list(nonzeroSC & nonzeroIC)

            overlap3 = list(nonzeroSC & nonzeroMC & nonzeroIC)

            # When structure dose distributions are summed voxels included in multiple structures are counted multiple times

            oarDoseDist = oarDoseDistSC + oarDoseDistMC + oarDoseDistIC

            oarDoseDistFlat = oarDoseDist.flatten()

            # Divide by 2 to reverse summing the dose in voxels that are included in 2 of the structures

            oarDoseDistFlat[overlap2] = oarDoseDistFlat[overlap2]/2.0

            # Divide by 3 to reverse summing the dose in voxels that are included in all 3 structures

            oarDoseDistFlat[overlap3] = oarDoseDistFlat[overlap3]/3.0

            oarDoseDist = oarDoseDistFlat.reshape(oarDoseDistSC.shape)

        

        #print np.min(oarDoseDist), np.max(oarDoseDist)

        oarDoseDistMaskedZeroes = np.ma.masked_less_equal(oarDoseDist, 0)

        

        # Add BED for concurrent chemotherapy

        if addChemoBED == True and noConChemo == False:

            oarDoseDistMaskedZeroes = oarDoseDistMaskedZeroes + chemoBED

        

        oarArgs = np.argwhere(oarDoseDistMaskedZeroes > 0)

        

        #print 'oarDoseDist.size', oarDoseDist.size

        #print 'total size', oarDoseDistMaskedZeroes.size

        #print 'zeroes size', np.size(np.where(oarDoseDistMaskedZeroes == 0))

        #print 'non-zeroes size', np.size(np.where(oarDoseDistMaskedZeroes > 0))

        

        # Note: ndimage.measurements.center_of_mass returns the arguments of the centre of mass as opposed to the value

        # Note: '~' is logical not function to used get reverse of mask

        centreOfMassArgs = ndimage.measurements.center_of_mass(~oarDoseDistMaskedZeroes.mask)

        resampledDoseCubeCoordsFile = 'OutputData/' + self.patientID + '/' + self.patientID + 'resampledDoseCubeCoords.npy'

        resampledDoseCubeCoords = np.load(resampledDoseCubeCoordsFile)



        doseCubeXCoords = np.zeros(resampledDoseCubeCoords[0].size)

        doseCubeYCoords = np.zeros(resampledDoseCubeCoords[1].size)

        doseCubeZCoords = np.zeros(resampledDoseCubeCoords[2].size)



        for n, x in enumerate (resampledDoseCubeCoords[0]):

            doseCubeXCoords[n] = x

        for n, y in enumerate (resampledDoseCubeCoords[1]):

            doseCubeYCoords[n] = y

        for n, z in enumerate (resampledDoseCubeCoords[2]):

            doseCubeZCoords[n] = z

        

        oarCoM = np.array((doseCubeXCoords[int(round(centreOfMassArgs[0]))],

                            doseCubeYCoords[int(round(centreOfMassArgs[1]))],

                            doseCubeZCoords[int(round(centreOfMassArgs[2]))]))

        

        #print 'min, mean, max = ', np.min(oarDoseDist), np.mean(oarDoseDist), np.max(oarDoseDist)

        #print 'min, mean, max = ', np.min(oarDoseDistMaskedZeroes), np.mean(oarDoseDistMaskedZeroes), np.max(oarDoseDistMaskedZeroes)

        

        #oarDoseDistMaskedZeroes = oarDoseDist

        

        return (oarDoseDist, oarDoseDistMaskedZeroes, resampledDoseCubeCoords, oarArgs, oarCoM)



    

    def fractional_dose_distribution(self, clinicalDataSet, oarDoseDistMaskedZeroes):

        """Calculates the physical dose/fraction distribution for acute toxicity analysis"""

        

        print 'Running fractional_dose_distribution() ...'

        

        df = pd.read_csv('clinicalData' + clinicalDataSet + '.csv').set_index('patientID')

        df.index = df.index.map(str)

        numFractions = df.loc[self.patientID]['numFractions']

        fractionalDoseDist = oarDoseDistMaskedZeroes/numFractions

        

        return fractionalDoseDist



    

    def total_physical_dose_distribution(self, oarDoseDistMaskedZeroes):

        

        totalPhysicalDoseDistribution = oarDoseDistMaskedZeroes

        

        return totalPhysicalDoseDistribution

    

    

    def total_biologically_effective_dose(self, oarDoseDistMaskedZeroes, alphaBetaRatio, alpha, Ttreat, Tk, Tp, numberOfFractions):

        """Corrects the total physical dose to total biological effective dose"""

    

        print 'Running total_biological_effective_dose() ...'

    

        totalBedDoseDistribution = oarDoseDistMaskedZeroes*(1 + (oarDoseDistMaskedZeroes/numberOfFractions)/alphaBetaRatio) - (np.log(2)/alpha)*((Ttreat - Tk)/Tp)

        # Do not allow negative dose

        totalBedDoseDistribution = totalBedDoseDistribution.clip(min = 0)

    

        return totalBedDoseDistribution

    

    

    def total_equivalent_dose_in_2Gy_fractions(self, oarDoseDistMaskedZeroes, alphaBetaRatio, alpha, Ttreat, Tk, Tp, numberOfFractions):

        """Corrects the total physical dose to total equivalent dose in 2 Gy fractions"""

        

        print 'Running total_equivalent_dose_in_2Gy_fractions() ...'

        

        totalEqd2DoseDistribution = DoseMetrics.total_biologically_effective_dose(oarDoseDistMaskedZeroes, alphaBetaRatio, alpha, Ttreat, Tk, Tp, numberOfFractions)/(1 + (2/alphaBetaRatio))

        

        return totalEqd2DoseDistribution

    

    def accumulated_biologically_effective_dose(self, oarDoseDistMaskedZeroes, alphaBetaRatio, alpha, Tk, Tp, toxicity, onset3, trialName):

        """Corrects the total physical dose to biological effective dose at the time of toxicity onset"""

        

        print 'Running accumulated_biological_effective_dose() ...'

    

        if trialName != 'doseEscalation':

            if onset3 < 7:

                numFractionsToxOnset = (onset3 - 1)*5

                numFractionsTotal = 30

                T = (onset3 - 1)*7 - 1

            else:

                numFractionsToxOnset = 30

                numFractionsTotal = 30

                T = 39

        else:

            if onset3 < 7:

                numFractionsToxOnset = (onset3 - 1)*5

                numFractionsTotal = 28

                T = (onset3 - 1)*7 - 1                

            else:

                numFractionsToxOnset = 28

                numFractionsTotal = 28

                T = 37

        

        oarBedDist = oarDoseDistMaskedZeroes*numFractionsToxOnset/numFractionsTotal*(1 + (oarDoseDistMaskedZeroes/numFractionsTotal)/alphaBetaRatio) - (np.log(2)/alpha)*((T - Tk)/Tp)

        # Do not allow negative dose

        oarBedDist = oarBedDist.clip(min = 0)

        

        return oarBedDist



    

    def display_3d_dose_distribution(self, doseDistribution):

        """Plots the 3D dose distribution"""

        

        print 'Running display_3d_dose_distribution() ...'

        

        if self.structureName != 'OMPM' and self.structureName != 'OMpartialPM' and self.structureName != 'OM2PM' and self.structureName != 'OM2partialPM' and self.structureName != 'SCMCIC':

            structureCoordsFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'structureCoords.npy'

            structureCoords = np.load(structureCoordsFile)

        

        elif self.structureName == 'OMPM' or self.structureName == 'OMpartialPM':

            structCoordsFileOM = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM' + 'structureCoords.npy'

            structCoordsFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'structureCoords.npy'

            structCoordsOM = np.load(structCoordsFileOM)

            structCoordsPM = np.load(structCoordsFilePM)

            structureCoords = np.concatenate((structCoordsOM, structCoordsPM), axis = 1)

        

        elif self.structureName == 'OM2PM' or self.structureName == 'OM2partialPM':

            structCoordsFileOM2 = 'OutputData/' + self.patientID + '/' + self.patientID + 'OM2' + 'structureCoords.npy'

            structCoordsFilePM = 'OutputData/' + self.patientID + '/' + self.patientID + 'PM' + 'structureCoords.npy'

            structCoordsOM2 = np.load(structCoordsFileOM2)

            structCoordsPM = np.load(structCoordsFilePM)

            structureCoords = np.concatenate((structCoordsOM2, structCoordsPM), axis = 1)

        

        elif self.structureName == 'SCMCIC':

            structCoordsFileSC = 'OutputData/' + self.patientID + '/' + self.patientID + 'SC' + 'structureCoords.npy'

            structCoordsFileMC = 'OutputData/' + self.patientID + '/' + self.patientID + 'MC' + 'structureCoords.npy'

            structCoordsFileIC = 'OutputData/' + self.patientID + '/' + self.patientID + 'IC' + 'structureCoords.npy'

            structCoordsSC = np.load(structCoordsFileSC)

            structCoordsMC = np.load(structCoordsFileMC)

            structCoordsIC = np.load(structCoordsFileIC)

            structureCoords = np.concatenate((structCoordsSC, structCoordsMC, structCoordsIC), axis = 1)

        

        # Might need to change the order of the coordinates - mayavi expects (z, y, x) not (x, y, z)

        #mlab.plot3d(structureCoords[0], structureCoords[1], structureCoords[2], representation = 'wireframe') 

        mlab.contour3d(doseDistribution, contours = 10,#[10, 20, 30, 40, 50, 60, 70, 80],

                       opacity = 0.2,

                       extent = [np.amin(structureCoords[0]), np.amax(structureCoords[0]),

                       np.amin(structureCoords[1]), np.amax(structureCoords[1]),

                       np.amin(structureCoords[2]), np.amax(structureCoords[2])]

                       )

        mlab.scalarbar(title = "Dose (Gy)", orientation = 'vertical')

        mlab.show()

    

    def dose_volume_histogram(self, doseDistribution, doseLimit, dvhBins, filename):

        """Computes the dose-volume histogram"""

        

        print 'Running dose_volume_histogram() ...'

        

        organDose = np.ma.compressed(doseDistribution)

        # Cumulative DVH

        hist, binEdges = np.histogram(organDose, range = (0, doseLimit), bins = dvhBins, density = True)

        doseVolumeHistogram = dvhBins/doseLimit - np.cumsum(hist)

        plt.plot(doseVolumeHistogram)

        plt.show()

        print doseVolumeHistogram[10]

        # Non-cumulative DVH

        '''hist, binEdges = np.histogram(organDose, range = (0, 80), bins = 80, density = True)

        doseVolumeHistogram = hist

        #plt.plot(doseVolumeHistogram)

        #plt.show()'''

        

        # Write doseVolumeHistogram to file

        outputFile = filename

        #outputFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName +'doseVolHistNonCum.npy'

        np.save(outputFile, doseVolumeHistogram)



        

    def load_ct_data(self):

        """Extracts the CT slice thickness and pixel spacing"""



        #ctFileNames = 'InputData/' + self.patientID + '/CT*'

        #filenames = glob.glob(ctFilenames)



        dicomFileNames = glob.glob('InputData/' + self.patientID + '//*')



        ctFileNames = []

        for fileNumber in range(0, len(dicomFileNames)):

            dicomFile = dicom.read_file(dicomFileNames[fileNumber])

            if dicomFile.Modality == 'CT':

                ctFileNames.append(dicomFileNames[fileNumber])



        ctAppended = []



        #for n in range (0, len(filenames)):

        #    ctFile = filenames[n]

        for n in range(0, len(ctFileNames)):

            ctFile = ctFileNames[n]

            ctFile = dicom.read_file(ctFile, force = True)

            ct = ctFile.pixel_array

            ctFlattened = ct.flatten()

            ctAppended = np.append(ctAppended, ctFlattened)

            

            # Use slice locations to calculate the CT slice thickness when this is not explicitly given

            if n == 0 and ctFile.SliceThickness == '':

                firstSliceLocation = ctFile.SliceLocation

            elif n == 1 and ctFile.SliceThickness == '':

                secondSliceLocation = ctFile.SliceLocation

        

        if not ctFile.SliceThickness == '':

            ctSliceThickness = ctFile.SliceThickness

        else:

            ctSliceThickness = np.fabs(firstSliceLocation - secondSliceLocation)

            

        ctPixelSpacing = ctFile.PixelSpacing

        

        return ctSliceThickness, ctPixelSpacing



        

    def long_extent_hist_abs(self, doseType, doseDistribution, ctSliceThickness, absDLHfilename):

        """Dose-absolute longitudinal extent histogram"""

        

        print 'Running long_extent_hist_abs() ...'

        



        if doseType == 'fractionalPhysical':

            maxDose = 2.7

            doseIncrement = 0.2

            longExtent = np.zeros((14))

        else:

            maxDose = 81

            doseIncrement = 5

            longExtent = np.zeros((17))



        loopCounter = 0

        doseLevels = np.arange(0, maxDose, doseIncrement)



        for doseLevel in doseLevels:

            zHeight = np.zeros((doseDistribution.shape[2]))

            

            for z in range (0, doseDistribution.shape[2]):

                if doseDistribution[:, :, z].max() > doseLevel:

                #if np.ma.median(oarDoseDistMaskedZeroes[:, :, z]) > doseLevel:

                #if oarDoseDistMaskedZeroes[:, :, z].min() > doseLevel:

                    zHeight[z] = 1.0

                else:

                    zHeight[z] = 0.0



            longExtent[loopCounter] = zHeight.sum()

            loopCounter += 1



        #doseLevel = np.arange(0, maxDose, doseIncrement)

        # Absolute longitudinal extent in cm

        absLongExtent = longExtent*ctSliceThickness/10.0

        

        # Write data to file

        outputFile = absDLHfilename

        #outputFile = 'OutputData/'+ self.patientID + '/' + self.patientID + self.structureName + 'medianDoseAbsLongExtHist.npy'

        #outputFile = 'OutputData/'+ self.patientID + '/' + self.patientID + self.structureName + 'minDoseAbsLongExtHist.npy'

        np.save(outputFile, absLongExtent)

        

        return (doseLevels, longExtent)





    def long_extent_hist_norm(self, longExtent, normDLHfilename):

        """Dose-normalised longitudinal extent histogram"""

        

        print 'Running long_extent_hist_norm() ...'

        

        normLongExtent = longExtent/longExtent[0]*100.0

        print normLongExtent

        

        # Write data to file

        outputFile = normDLHfilename

        #outputFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'medianDoseNormLongExtHist.npy'

        #outputFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'minDoseNormLongExtHist.npy'

        np.save(outputFile, normLongExtent)



    

    def circ_extent_hist(self, doseType, doseDistribution, resampledDoseCubeCoords, oarArgs, DCHfilename):

        """Dose-circumferential extent histogram"""

        

        print 'Running circ_extent_hist() ...'



        x = resampledDoseCubeCoords[0]

        y = resampledDoseCubeCoords[1]

        z = resampledDoseCubeCoords[2]



        doseCubeXCoords = np.zeros(resampledDoseCubeCoords[0].size)

        doseCubeYCoords = np.zeros(resampledDoseCubeCoords[1].size)

        doseCubeZCoords = np.zeros(resampledDoseCubeCoords[2].size)

        centreOfMassArgs = np.zeros((np.unique(oarArgs.T[2]).size, 2))

        oarCoM = np.zeros((np.unique(oarArgs.T[2]).size, 2))

        xDispFromCoM = np.zeros((np.unique(oarArgs.T[2]).size, doseCubeXCoords.size))

        yDispFromCoM = np.zeros((np.unique(oarArgs.T[2]).size, doseCubeYCoords.size))

        r = np.zeros((doseCubeXCoords.size, doseCubeYCoords.size, doseCubeZCoords.size))

        phi = np.zeros((doseCubeXCoords.size, doseCubeYCoords.size, doseCubeZCoords.size))

        

        for n, x in enumerate (resampledDoseCubeCoords[0]):

            doseCubeXCoords[n] = x

        for n, y in enumerate (resampledDoseCubeCoords[1]):

            doseCubeYCoords[n] = y

        for n, z in enumerate (resampledDoseCubeCoords[2]):

            doseCubeZCoords[n] = z

        

       # for z in range (0, np.unique(oarArgs.T[2]).size):

       #     print np.sum(~doseDistribution.mask[:, :, z])

            

        for z in range (0, np.unique(oarArgs.T[2]).size):

            # Note: ndimage.measurements.center_of_mass returns the arguments of the centre of mass as opposed to the value

            # Note: '~' is logical not function to used get reverse of mask

            centreOfMassArgs[z] = ndimage.center_of_mass(~doseDistribution.mask[:, :, z])

            #print z, centreOfMassArgs[z]

            oarCoM[z, 0] = doseCubeXCoords[int(round(centreOfMassArgs[z, 0]))]

            oarCoM[z, 1] = doseCubeYCoords[int(round(centreOfMassArgs[z, 1]))]    



            xDispFromCoM[z] = doseCubeXCoords - oarCoM[z, 0]

            yDispFromCoM[z] = doseCubeYCoords - oarCoM[z, 1]

            

            # Transform from cartesian to cylindrical coordinates

            for x in range (0, xDispFromCoM[z].size):

                for y in range (0, yDispFromCoM[z].size):

                    r[x, y, z] = np.sqrt(xDispFromCoM[z, x]**2 + yDispFromCoM[z, y]**2)

                    phi[x, y, z] = np.arctan2(xDispFromCoM[z, x], yDispFromCoM[z, y])

        

        #print 'max dose = ', np.max(oarDoseDistMaskedZeroes)

        #doseLevelMask = ~np.ma.masked_less(oarDoseDistMaskedZeroes, 75.0).mask

        #print 'doseLevelMask.sum() = ', doseLevelMask.sum()



        if doseType == 'fractionalPhysical':

            maxDose = 2.61

            doseIncrement = 0.20

            normPhiExtent = np.zeros((14))

        else:

            maxDose = 81

            doseIncrement = 5

            normPhiExtent = np.zeros((17))



        loopCounter = 0

        doseLevels = np.arange(0, maxDose, doseIncrement)

            

        for doseLevel in doseLevels:

            doseLevelMask = ~np.ma.masked_less(doseDistribution, doseLevel).mask

            #print 'doseLevelMask.sum() = ', doseLevelMask.sum()

            phiDoseMask = phi*doseLevelMask

            normPhiExtent[loopCounter] = (np.max(phiDoseMask) - np.min(phiDoseMask))/(2*np.pi)*100.0

            loopCounter += 1



        print 'normPhiExtent = ', normPhiExtent

              

        # Write data to file

        outputFile = DCHfilename

        np.save(outputFile, normPhiExtent)



                

    def cluster_analysis(self, oarDoseDist, ctSliceThickness, ctPixelSpacing, minClusterVolume):

        

        print 'Running cluster_analysis() ...'

        

        maxClusterSize = np.zeros((17))

        maxHoleSize = np.zeros((17))

        numClusters = np.zeros((17))

        numClustersAboveThreshold = np.zeros((17))

        numHoles = np.zeros((17))

        

        # Downsample the oarDoseDist

        oarDoseDist = np.round(ndimage.interpolation.zoom(oarDoseDist, (ctPixelSpacing[1]/2.5, ctPixelSpacing[0]/2.5, ctSliceThickness/2.5)), 1)

        print 'oarDoseDist.size = ', oarDoseDist.size

        #voxelVolume = ctPixelSpacing[0]*ctPixelSpacing[1]*ctSliceThickness

        voxelVolume = 2.5**3

        

        loopIter = 0



        for doseLevel in range(0, 81, 5):

            clustersBinaryMask = np.ma.masked_greater(oarDoseDist, doseLevel).mask

            # Generates a structuring element that considers features connected even if they touch diagonally

            if clustersBinaryMask.ndim == 3:

                s = ndimage.morphology.generate_binary_structure(3, 2)

            else:

                # Need to set the structure to None when there is no mask

                s = None

            labeled_array, num_features = ndimage.measurements.label(clustersBinaryMask, structure = s)

            clusterSize = np.zeros(num_features + 1)

            

            # Determine the size of each of the clusters

            for clusterNumber in range (1, num_features + 1):

                clusterSize[clusterNumber - 1] = (labeled_array == clusterNumber).sum()*voxelVolume



            numClusters[loopIter] = num_features

            sortedClusterSize = np.sort(clusterSize)

            # Reverse sort order

            sortedClusterSize = sortedClusterSize[::-1]

            numClustersAboveThreshold[loopIter] = np.argwhere(sortedClusterSize > minClusterVolume).size

            maxClusterSize[loopIter] = sortedClusterSize[0]



            holesBinaryMask = np.ma.masked_less(oarDoseDist, doseLevel).mask

            if holesBinaryMask.ndim == 3:

                s = ndimage.morphology.generate_binary_structure(3, 2)

            else:

                # Need to set the structure to None when there is no mask

                s = None

            # structure considers diagonally adjacent voxels as adjacent

            labeled_array, num_features = ndimage.measurements.label(holesBinaryMask, structure = s)

            holeSize = np.zeros((num_features + 1))

            # Determine the size of each of the holes

            for holeNumber in range (0, num_features + 1):

                holeSize[holeNumber] = (labeled_array == holeNumber).sum()*voxelVolume



            numHoles[loopIter] = num_features

            sortedHoleSize = np.sort(holeSize)

            # Reverse sort order

            sortedHoleSize = sortedHoleSize[::-1]

            maxHoleSize[loopIter] = sortedHoleSize[0]

            

            loopIter += 1



        print 'numClusters = ', numClusters

        print 'numClustersAboveThreshold = ', numClustersAboveThreshold      

        print 'maxClusterSize = ', maxClusterSize

        #print 'numHoles = ', numHoles

        #print 'maxHoleSize = ', maxHoleSize



        # Write data to file

        outputFile1 = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'numClusters.npy'

        np.save(outputFile1, numClustersAboveThreshold)

        outputFile2 = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + 'maxClusterSize.npy'

        np.save(outputFile2, maxClusterSize)



        

    def statistical_moments(self, doseType, oarDoseDistMaskedZeroes, resampledDoseCubeCoords, oarArgs, oarCoM):

        """Computes 3D statistical moments of the organ-at-risk dose distribution"""

        

        print 'Running statistical_moments() ...'

        

        x = resampledDoseCubeCoords[0]

        y = resampledDoseCubeCoords[1]

        z = resampledDoseCubeCoords[2]

        

        # Overcome the symmetry issue by taking the absolute value, |x[i] - xCentreOfMass|

        xDispFromCoM = abs(x - oarCoM[0])

        yDispFromCoM = y - oarCoM[1]

        zDispFromCoM = z - oarCoM[2]

        

        momentOrders = np.array([(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 1 ,1), (1, 1, 0), (1, 0, 1), (1, 1, 1), (2, 0, 0), (0, 0, 2), (0, 2, 0),

            (3, 0, 0), (0, 0, 3), (0, 3, 0)])

        mu = np.zeros((14))

        eta = np.zeros((14))

        for n in range (0, 14):

            momentOrder = momentOrders[n]

            mu[n] = 0

            p = momentOrder[0]

            q = momentOrder[1]

            r = momentOrder[2]



            for arg in oarArgs:

                muCurrentIteration = xDispFromCoM[arg[0]]**p * yDispFromCoM[arg[1]]**q * zDispFromCoM[arg[2]]**r * oarDoseDistMaskedZeroes[arg[0], arg[1], arg[2]]

                mu[n] = mu[n] + muCurrentIteration

            

            if n == 0:

                eta[n] = mu[n]

            else:

                eta[n] = mu[n] / mu[0]**((p + q + r) / 3 + 1)

        

        print 'eta = ', eta

            

        # Write data to file

        outputFile = 'OutputData/' + self.patientID + '/' + self.patientID + self.structureName + doseType + 'StatisticalMoments.npy'

        np.save(outputFile, eta)