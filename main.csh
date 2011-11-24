#! /bin/csh

###################
### Description ###
###################
### RUN THIS SCRIPT FOR REDUCING ONE IMAGE
###
### runs sub csh routines to command individual processes (eg, reduce_image,
### radial_velocity, spectype etc)

### usage: ./main.csh

#############
### To Do ###
#############

########################
### Load config_file ###
########################

### Define file_path
set file_path = `grep FILE_PATH config_file | awk '{print $2}'`

### Define file_name
set file_name = `grep FILE_NAME config_file | awk '{print $2}'`

####################
### Setup folder ###
####################

### Remove previously reduced files - if DELETE_ALL is turned on
set delete_all = `grep DELETE_ALL config_file | awk '{print $2}'`
if ($delete_all == true) then 
    rm -rf $file_path/temp/*
    rm -rf $file_path/reduced/*
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
