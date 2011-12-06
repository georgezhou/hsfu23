#! /bin/csh

###################
### Description ###
###################

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

### Find RV Standards
python find_rv.py $file_path

### Reduce these RV Standard images
echo Finding and reducing RV standard images

set RV_Standard_list = $file_path/temp/RV_Standard_list

set test = `python check_RV_list.py $RV_Standard_list`

if ($test == "True") then
    echo Reducing RV standard exposures

    set counter=`wc -l $RV_Standard_list | awk '{print $1}'` 

    ### Loop over all the images found
    set i = 1
    while ($i <= $counter)
    ### finds the ith image from file RV_Standard_list
    set RV_i = `gawk "NR==$i {print}" $RV_Standard_list` 

    ls $file_path/reduced/n_d_{$RV_i}* >& /dev/null
    if ( $status == 0 ) then
        echo $RV_i has already been reduced
    else
        echo Reducing $RV_i
        ./reduce_image.csh $file_path {$RV_i}.fits
    endif
    @ i = $i + 1
    end

    ### Apply fxcor
    echo Applying iraf.fxcor
    python fxcor.py $file_path $file_name

    # ### Write output of fxcor to reduced/RV_out.dat
    # python RV_tabulate.py $file_path $file_name

    # ### Write output to candidate_path
    # set record_rv = `grep RECORD_RV config_file | awk '{print $2}'`
    # if ($record_rv == true) then 
    #   python RV_distribute_2.py $file_path $file_name $candidate_path $display
    # endif

else
    echo ERROR No RV standards exist
endif
