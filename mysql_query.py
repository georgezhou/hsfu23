import string
import os
import functions
import MySQLdb

### Performs query of HSCAND database on princeton computer
### Only works if you run this from program_dir
def query_hscand(query_entry):
    ### Write the mysql query csh script
    command = "mysql --defaults-file=/home/gzhou/hscand.cfg HSCAND -e \"" + query_entry + "\" > /home/gzhou/query_result.txt"
    mysql_query = open("mysql_query.csh","w")
    mysql_query.write("#! /bin/csh \n")
    mysql_query.write(command + "\n")
    mysql_query.close()

    ### Copy the required scripts to hatsouth@princeton
    os.system("chmod a+x mysql_query.csh")
    print "copying files to hatsouth@princeton"
    os.system("scp hscand.cfg gzhou@hatsouth.astro.princeton.edu:/home/gzhou/")
    os.system("scp mysql_query.csh gzhou@hatsouth.astro.princeton.edu:/home/gzhou/")

    ### Execute the program and copy the results over
    print "Executing .csh files on princeton via ssh"
    os.system("ssh gzhou@hatsouth.astro.princeton.edu '/home/gzhou/mysql_query.csh'")
    os.system("scp gzhou@hatsouth.astro.princeton.edu:/home/gzhou/query_result.txt .")

    ### Read query_result.txt in as a list
    query_result = functions.read_ascii("query_result.txt")
    query_result = functions.read_table(query_result)

    os.system("rm query_result.txt")
    os.system("rm mysql_query.csh")
    return query_result

### For example:
### query_hscand("select HATSmagV, HATSmagJ, HATSmagK from HATS where HATSname='HATS551-002'")
### Returns [['HATSmagV', 'HATSmagJ', 'HATSmagK'], [13.487, 11.967, 11.461]]

### Query from HSMSO on marble
def query_hsmso(query_entry):
    db=MySQLdb.connect(host="mutant.anu.edu.au",user="daniel",passwd="h@ts0uthDB",db="daniel1")
    c = db.cursor()
    c.execute(query_entry)
    result = c.fetchall()
    return result
