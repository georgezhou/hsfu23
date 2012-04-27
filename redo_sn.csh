#! /bin/csh

###################
### Description ###
###################
### Reduces the WiFeS raw data
### Performs:
### bias subtraction, flat fielding, cosmic ray detection
### spectral extraction (line straightening, background removal etc)
### Produces an end spectrum

### For spectral typing - produces 1 spectrum by adding individual image
### slices
### For RV - produces n spectra according to the number of image slices
### extracted

### Usage: ./reduce_image.csh file_path file_name

########################
### Load config_file ###
########################

### Define file_path
set file_path = $1

### Define file_name
set file_name = $2

########################
### Start of program ###
########################

### Run bias subtraction and flat fielding on the object file
echo Running bias subtraction on the object file $file_name
python bias_subtraction.py $file_path $file_name

### Find the image slices and chop each image slice into separate files
python define_image_slices.py $file_path
python chop_image.py $file_path $file_name

### Reconstruct the spatial image
### and find which image slices to extract stellar signal
python reconstruct_image.py $file_path $file_name

### Analyse image signal-to-noise
python analyse_spectrum.py $file_path $file_name

python update_sn.py $file_path $file_name


### Remove temporary files
set clean_up = `grep CLEAN_UP config_file | awk '{print $2}'`
if ($clean_up == true) then
    python cleanup.py $file_path
endif
