import os,sys,functions,string,mysql_query


RV_cmd =  "select distinct SPECobject from SPEC where SPECtype = \"RV\" and not (SPECcomment = \"SpecPhot\" or SPECcomment = \"RV Standard\")" 
output = mysql_query.query_hsmso(RV_cmd)

RV_list = []
for cand in output:
    cand = cand[0]
    print cand
    cand_cmd =  "select SPEChjd from SPEC where SPECobject = \""+cand+"\" and SPECtype = \"RV\"" 
    cand_rv = mysql_query.query_hsmso(cand_cmd)

    if len(cand_rv) > 2:
        RV_list.append(cand)

print "RV",len(RV_list)



spectype_cmd = "select distinct SPECobject from SPEC where SPECtype = \"ST\" and not (SPECcomment = \"SpecPhot\" or SPECcomment = \"RV Standard\")" 

output = mysql_query.query_hsmso(spectype_cmd)
print "Spectral typing ",len(output)
