PATH_FILE='/Users/vitorsilva/Documents/PhD/GiovinazziLagomarsino/loss-map.xml'
PATH_LOG='/Users/vitorsilva/Documents/PhD/GiovinazziLagomarsino/loss-map.txt'

import math

def isodd(num):
    return num & 1 and True or False

def parse_values(path):
    
    values=[]
    file=open(path)
    lines=file.readlines()
    
    return lines
    
    
def compute_map(lines):
    
    no = len(lines)
    Latitude = []
    Longitude =[]
    Values = []
    no_assets = 0
    out_file = open(PATH_LOG,"w")

    for i in range(no):
        if lines[i].strip()[:7] == '<LMNode':
            j=1
            subValue = 0.0
            while lines[i+j].strip()[:8] != '</LMNode':
                
                if lines[i+j].strip()[:9] == '<gml:pos>':
                    coordinates = lines[i+j].strip().replace('<gml:pos>','').replace('</gml:pos>','').split()                                
                
                if lines[i+j].strip()[:6] == '<mean>':
                    subValue = subValue + float(lines[i+j].strip().replace('<mean>','').replace('</mean>',''))
                    no_assets = no_assets+1
                j=j+1
            
            Latitude.append(coordinates[1])
            Longitude.append(coordinates[0])
            Values.append(subValue)
    
    out_file.write('x,y,value\n')
    for i in range(len(Values)):
        out_file.write(Longitude[i]+','+Latitude[i]+','+str(Values[i])+'\n')
    out_file.close()
    
    print no_assets        
    print len(Values)

lines = parse_values(PATH_FILE)

compute_map(lines)