#! /bin/csh

###################
### Description ###
###################

### Applies main.csh to all object images in the file_path
### Accepts all settings from config_file and param_file

### Usage: ./main_all.csh

########################
### Load config_file ###
########################

### Define file_path
set file_path = `grep FILE_PATH config_file | awk '{print $2}'`

########################
### Start of program ###
########################

### Go to file_path and create a list of all fits files
set program_dir = `pwd`
./generage_imagetype_lists.py $file_path

set image_list = $file_path/image_list

### find the no of lines for file "image_list"
set counter=`wc -l $image_list | awk '{print $1}'` 

### Get rid of everything
rm -rf $file_path/temp/*
rm -rf $file_path/reduced/*

##################
### Begin loop ###
##################

set i = 1
while ($i <= $counter)
### finds the ith image from file imagelist
set file_name = `gawk "NR==$i {print}" $image_list` 

echo "---------------- *** --------------------"

echo Reducing $file_name - task $i out of $counter

./main.csh $file_path $file_name

@ i = $i + 1
end
