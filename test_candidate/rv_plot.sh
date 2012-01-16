#!/bin/sh

##########################################
# Script to plot RVs and fit e=0 variation
# Daniel Bayliss; March 2011
# version2.0 (29 March 2011)
# Requires file called $cand.txt which contains RV in format:
# col_1 HJD
# col_2 RV (km/s)
# col_3 RV error (km/s)
#########################################

#usage ./rv_plot.sh candidate period
#Argument is candidate name
cand=$1

#Error Statements
if [ $# -ne 1 ]
then
  echo "Usage: ./rv_plot.sh candidate_name"
  exit
fi

if [ ! -f candidates.txt ]
then
    echo "No candidates.txt file found"
    exit
fi

if [ ! -f $cand.txt ]
then
    echo "No RV $cand.txt file found"
    exit
fi

flag=`grep -i $cand candidates.txt | wc -l`
if [ $flag != "1" ]
then
    echo "Candidate not found in candidates.txt file or multiple entry found"
    exit
fi

########

#Getting candidate parameters from candidates.txt file
t1=`grep -i $cand candidates.txt | awk '{print$6}'`
period=`grep -i $cand candidates.txt | awk '{print$7}'`
q=`grep -i $cand candidates.txt | awk '{print$8}'`

#Fitting e=0 to RVs
gnuplot <<EOF
reset
!rm $cand.log
set fit logfile "$cand.log"
cand='$cand' # Candidate    
period= $period # period (in days)            
q=$q # (fractional duration of transit)
t1=$t1 # in hjd (time of first contact)
K=1 #Best guess RV amplitude           
R0=1 #Best guess RV offset             
set yrange [-500 to 500] # Enter RV range 
#########################################
phase=0
tc=t1+(q*0.5*period) #calculating transit center
candfile=cand.".txt" #name of input RV file
f(x)=-sin(2*pi*(x-floor(x/period)-phase))*abs(K)+R0
fit f(x) candfile using \
(((\$1-tc)/period)-(floor((\$1-tc)/period))):2 via K,R0
EOF

K=`grep "K" $cand.log | grep "=" | tail -1 | awk '{print$3}'`
R0=`grep "R0" $cand.log | grep "=" | tail -1 | awk '{print$3}'`

#Plotting RV
gnuplot <<EOF
reset
cand='$cand' # Candidate    
period=$period # period (in days)            
q=$q # (fractional duration of transit)
t1=$t1 # in hjd (time of first contact)
set title\
"K=$K km/s, \
R_0=$R0 km/s" 
K=$K 
R0=$R0 
set yrange [R0-K-5 to R0+K+5] # Enter RV range 
#########################################

tc=t1+(q*0.5*period) #calculating transit center
candplot=cand.".ps" #naming output plot file
candfile=cand.".txt" #name of input RV file
set term x11
set term postscript enhanced color
set output candplot
set xlabel "Phase"
set ylabel "RV (km/s)"
set xrange [0 to 1]
set key at graph 0.95,0.95
set size square
set tics scale 1.5
set mytics 5
set mxtics 2
set xtics 0.2
phase=0
f(x)=-sin(2*pi*(x-floor(x/period)-phase))*abs(K)+R0
set style line 1 lt 1 lc 1
set style line 2 pt 0 lc 3 lt 1

plot candfile using\
     (((\$1-tc)/period)-(floor((\$1-tc)/period))):2:3\
     with yerrorbars pt 7 lc 3 ps 0.5 t cand,\
     f(x)  with lines ls 1 t \
     'e=0 fit'

EOF

ps2pdf $cand.ps $cand.pdf
#xpdf $cand.pdf
