#! /bin/csh

###################
### Description ###
###################

### The arc frame needs to be reduced in the same way as the
### object image. This csh script performs arc image reduction.
### The end product is a series of files containing 
### the image slices of the arc image

### Upto two arc frames are reduced
### - the arc taken closest in time to file_name is always reduced
### - if the next closest arc was taken < 30min from file_name
###   it is also reduced

### The arcs are found by find_arc.py
### Then reduced using the standard bias_subtract.py
### And chopped using chop_image.py

### Note that they are chopped according to the same settings as 
### that of the object frame - this is important!

### Usage: reduce_arc.csh file_path file_name

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

### Find the Ne-Ar arc to be used for dispersion solution
echo Finding Ne-Ar arc lamp image
python find_arc.py $file_path $file_name

### set counter to the no of lines for file arcs_to_use
set counter=`wc -l $file_path/temp/arcs_to_use.txt | awk '{print $1}'` 

########################################################
### Begin loop through all the arc images to be used ###
########################################################
set i = 1

while ($i <= $counter)
### Set the ith arc from file imagelist
set arc_name = `gawk "NR==$i {print}" $file_path/temp/arcs_to_use.txt` 

echo Processing arc image $arc_name

set arc_name_short = `basename $arc_name .fits`

### Check if it has already been processed
ls {$file_path}/temp/out_ccdproc_{$arc_name} >& /dev/null
if ( $status == 0 ) then
    echo $arc_name has already been reduced
else    
    rm -f $file_path/temp/*$arc_name_short*
    rm -f $file_path/reduced/*$arc_name_short*
    rm -f $file_path/temp/database/*$arc_name_short*
    rm -f $file_path/reduced/database/*$arc_name_short*

    ### Run bias and flat correction
    ### Chop up the image into its image slices
    echo Running bias subtraction on the NeAr arc lamp $arc_name
    python bias_subtraction.py $file_path $arc_name
    python chop_image.py $file_path $arc_name
endif

@ i = $i + 1
end
