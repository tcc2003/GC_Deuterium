import os

##############################################################
'''

  Exporting Pipeline calibrated CASA MS to FITS files

  History.
    v0: 2023.Nov.04
    v1: 2023.Nov.29
    v2: 2023.Dec.05 (casa version 561)
'''
##### Define variables #######################################

# The CASA MS to export
all_ms = [
          'uid___A002_Xad93f4_X2f03.ms.split.cal.split',
          'uid___A002_Xaee04e_X2599.ms.split.cal.split',
          'uid___A002_Xaee04e_X2987.ms.split.cal.split',
          'uid___A002_Xaee04e_X2dc3.ms.split.cal.split',
          'uid___A002_Xb52d1b_X2341.ms.split.cal.split',
          'uid___A002_Xb54d65_X2e35.ms.split.cal.split',
          'uid___A002_Xb54d65_X3230.ms.split.cal.split',
          'uid___A002_Xb58564_Xcf.ms.split.cal.split',
          'uid___A002_Xb5a3ad_X1f3.ms.split.cal.split',
          'uid___A002_Xb5a3ad_X659.ms.split.cal.split',
          'uid___A002_Xb5a3ad_Xa3d.ms.split.cal.split',
          'uid___A002_Xb5aa7c_X3b08.ms.split.cal.split',
          'uid___A002_Xb5aa7c_X431a.ms.split.cal.split',
          'uid___A002_Xb5ee5a_Xa20.ms.split.cal.split',
          'uid___A002_Xb66ea7_X9c01.ms.split.cal.split',
          'uid___A002_Xb7a3f8_X9d67.ms.split.cal.split'
         ]
# The fields and spectral windows to export
all_fieldIDs = range(1,5)
all_spwIDs   = range(0,4)

# The head of the output FITS file name
outname_head = 'ACA7m'

# velocity gridding in the output
vel_start  = '-1230km/s'
vel_width  = '1.57km/s'
vel_nchan  = 1532

# rest frequencies
restfreq = {}
restfreq[0] = '217.238530GHz'
restfreq[1] = '215.700000GHz'
restfreq[2] = '223.900000GHz'
restfreq[3] = '232.694912GHz'

##############################################################


thesteps = []
step_title = {
              0: 'Output listobs files',
              1: 'Split individual target source fields in to MS files',
              2: 'Concat the MS for the observations on the same fileds',
              3: 'Export the observations on each field to FITS'
             }

try:
  print ('List of steps to be executed ...', mysteps)
  thesteps = mysteps
except:
  print ('global variable mysteps not set.')
if (thesteps==[]):
  thesteps = range(0,len(step_title))
  print ('Executing all steps: ', thesteps)


##### output lisobs file #####################################

mystep = 0
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print ('Step ', mystep, step_title[mystep])


  for vis in all_ms:

    listfile = vis + '.listobs'
    os.system('rm -rf ' + listfile)
    listobs(vis = vis, listfile = listfile)

##############################################################



##### Split individual target source fields in to MS files ###

mystep = 1
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print ('Step ', mystep, step_title[mystep])

  print('########################################\n')
  print('Exporting mosaic fields: ', all_fieldIDs)

  for visID in range(len(all_ms)):
    vis = all_ms[visID]

    for fieldID in all_fieldIDs:
      for spwID in all_spwIDs:

          splitms = outname_head + '_vis' + str(visID)  + '_spw' + str(spwID) + '_' + str(fieldID) + '.ms'
          os.system('rm -rf ' + splitms )
          split(
                vis = vis, datacolumn = 'data',
                outputvis = splitms,
                field = str(fieldID), spw = str(spwID),
               )

          cvelms = outname_head + '_vis' + str(visID)  + '_spw' + str(spwID) + '_' + str(fieldID) + '.cvel.ms'
          os.system('rm -rf ' + cvelms)
          cvel(
               vis = splitms,
               outputvis = cvelms,
               mode = 'velocity',
                 start = vel_start,
                 nchan = vel_nchan,
                 width = vel_width,
                 restfreq = restfreq[spwID],
               veltype = 'radio'
              )

##############################################################



##### Concat the MS for the observations on the same fields ##

mystep = 2
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print ('Step ', mystep, step_title[mystep])

  for fieldID in all_fieldIDs:
    for spwID in all_spwIDs:
      concatvis = outname_head + '_spw' + str(spwID) + '_' + str(fieldID) + '.cvel.ms'

      # organize the list of files to be concatenated.
      ms_list = []
      for visID in range(len(all_ms)):
        temp_msname = outname_head + '_vis' + str(visID)  + '_spw' + str(spwID) + '_' + str(fieldID) + '.cvel.ms'
        ms_list.append(temp_msname)

      # concatenate visibility files in a ms_list
      os.system('rm -rf ' + concatvis)
      concat(
             vis = ms_list,
             concatvis = concatvis
            )

##############################################################



##### Export the observations on each field to FITS ##########

mystep = 3
if(mystep in thesteps):
  casalog.post('Step '+str(mystep)+' '+step_title[mystep],'INFO')
  print ('Step ', mystep, step_title[mystep])

  for fieldID in all_fieldIDs:
    for spwID in all_spwIDs:


      filenamehead = outname_head + '_spw' + str(spwID) + '_' + str(fieldID) + '.cvel'
      concatvis = filenamehead + '.ms'
      fitsfile  = filenamehead + '.fits'

      os.system('rm -rf ' + fitsfile )
      exportuvfits(
                   vis = concatvis, datacolumn = 'data',
                   fitsfile = fitsfile,
                   multisource = False, combinespw = False
                   )

##############################################################

