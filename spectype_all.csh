#! /bin/csh

###################
### Description ###
###################

### Spectral types everything in this folder

### ./spectype_all.csh $file_path

########################
### Load config_file ###
########################

### Define file_path
set file_path = $1

########################
### Start of program ###
########################

### Go to file_path and create a list of all fits files
set program_dir = `pwd`
cd $file_path 
ls *.fits > image_list
cd $program_dir

### Modify image_list to remove calibration files
python mod_imagelist.py $file_path image_list

set image_list = $file_path/image_list

### find the no of lines for file "image_list"
set counter=`wc -l $image_list | awk '{print $1}'` 

##################
### Begin loop ###
##################

set i = 1
while ($i <= $counter)
### finds the ith image from file imagelist
set file_name = `gawk "NR==$i {print}" $image_list` 

echo "---------------- *** --------------------"

echo Spectral typing $file_name - task $i out of $counter

python deredden.py $file_path $file_name
python spectype_main.py $file_path $file_name
python update_spectype.py $file_path $file_name

@ i = $i + 1
end
