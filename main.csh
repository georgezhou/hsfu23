#! /bin/csh

###################
### Description ###
###################
### RUN THIS SCRIPT FOR REDUCING ONE IMAGE
###
### runs sub csh routines to command individual processes (eg, reduce_image,
### radial_velocity, spectype etc)

### usage: ./main.csh [file_path file_name]

#############
### To Do ###
#############

########################
### Load config_file ###
########################


### Define file_path and file_name
if $1 == "" then
    set file_path = `grep FILE_PATH config_file | awk '{print $2}'`
    set file_name = `grep FILE_NAME config_file | awk '{print $2}'`
else
    set file_path = $1
    set file_name = $2
endif

echo Beginning reduction of $file_name

####################
### Setup folder ###
####################

### Remove previously reduced files - if DELETE_ALL is turned on
set delete_all = `grep DELETE_ALL config_file | awk '{print $2}'`
if ($delete_all == true) then
    if ($1 == "") then
    echo Deleting all previous reductions
    rm -rf $file_path/temp/*
    rm -rf $file_path/reduced/*
    endif
endif

### Remove previous reductions of FILE_NAME
set file_name_short = `basename $file_name .fits`
rm -f $file_path/temp/*$file_name_short*
rm -f $file_path/reduced/*$file_name_short*
rm -f $file_path/temp/database/*$file_name_short*
rm -f $file_path/reduced/database/*$file_name_short*

#######################
### Begin reduction ###
#######################

### Apply reduce_image.csh to object image
./reduce_image.csh $file_path $file_name

### Measure RV - if task is RV
set task = `grep TASK config_file | awk '{print $2}'`
if ($task == RV) then 
    ./radial_velocity.csh $file_path $file_name
endif

### Spectral typing
set task = `grep TASK config_file | awk '{print $2}'`
if ($task == SPECTYPE) then 
    ./spectype.csh $file_path $file_name
endif

### Remove the iraf log file it stores in this folder.
rm logfile
rm tmp*.fits

rm -f $file_path/temp/*
