#! /bin/csh

###################
### Description ###
###################

### Applies flux calibration to object image

### Find, reduce any flux standards available in the file_path
### Only reduce those that have not yet been reduced

### Then apply flux_calibration.py to find sensitivity function according to those flux standards
### Apply sensfunc and calibration to object spectrum for calibration

### Usage: ./spectype.csh file_path file_name

#####################
### Load settings ###
#####################

### Define file_path
set file_path = $1

### Define file_name
set file_name = $2

########################
### Start of program ###
########################

### Find SpecPhot standards
echo Compiling list of flux standards
python find_specphot.py $file_path

### Reduce those flux standards
echo Finding and reducing flux standard images

set SpecPhot_list = $file_path/temp/SpecPhot_list

set test = `python check_SpecPhot_list.py $SpecPhot_list`

if ($test == "True") then
    echo Reducing flux standard exposures

    echo False > $file_path/temp/new_data_test

    set counter=`wc -l $SpecPhot_list | awk '{print $1}'` 

    ### Loop over all the images found
    set i = 1
    while ($i <= $counter)
    ### finds the ith image from file SpecPhot_list
    set SP_i = `gawk "NR==$i {print}" $SpecPhot_list` 

    ls $file_path/temp/smoothdiv_*{$SP_i}* >& /dev/null
    if ( $status == 0 ) then
        echo $SP_i has already been reduced
    else
        echo Reducing $SP_i
        ./reduce_image.csh $file_path {$SP_i}.fits
	echo True > $file_path/temp/new_data_test
    endif
    @ i = $i + 1
    end

else
    echo ERROR no flux standards exist
endif

################################################
### Apply flux calibration and normalisation ###
################################################

python flux_calibration.py $file_path $file_name

### Do the rest of the spectral typing processes?
set ONLY_FLUX = `grep ONLY_FLUX param_file | awk '{print $2}'`
if ($ONLY_FLUX == false) then 
    python normalise_for_spectype.py $file_path $file_name

    ### Create a series of dereddened spectra from the object spectrum
    python deredden.py $file_path $file_name
endif

###############################
### Perform spectral typing ###
###############################
set PERFORM_SPEC_MATCH = `grep PERFORM_SPEC_MATCH config_file | awk '{print $2}'`
if ($PERFORM_SPEC_MATCH == true) then
    python spectype_main.py $file_path $file_name
    
    set write_to_database = `grep WRITE_TO_DATABASE config_file | awk '{print $2}'`
    if ($write_to_database == true) then
	### Log spectype into database
	python update_spectype.py $file_path $file_name
    endif

endif
