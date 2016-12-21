import xml.etree.cElementTree as ET
import pprint
import re
import datetime
from collections import defaultdict
import csv
import codecs
import cerberus

street_type_re = re.compile(r'\#?\b\S+\.?\s?$', re.IGNORECASE)

phone_number_re = re.compile('\d{3}\d{3}\d{4}')
find_number_re = re.compile('\({0}\d{3}\){0}\)?[-.\s\)]{0,}\d{3}[-.\s\)]{0,}\d{4}')
modify_number_re = re.compile('\s|\.|-|\)')

good_code_re = re.compile('V[A-Z0-9]{2}\s?[A-Z0-9]{3}')

expected = re.compile('\d{4}-\d{0,2}-\d{0,2}')
month = re.compile('[a-zA-Z]+')
check = re.compile(r"(?P<other>\b\d{0,4}[-./\s]?\d{1,2})[-./\s](?P<year>\d{4})")




convert = re.compile('\d\.?\d?')
bad_height = re.compile('[a-zA-Z]+')

    
is_in_re = re.compile(r'[A-Z]{0,2}[-]?[A-Z]{2}')


isin_exp = ["British Columbia", "Canada","North America"]

isin_map = {"BC": "British Columbia",
            "CA": "Canada",
            "NA": "North America",
            "UBC": "UBC",
            "CA-BC":"British Columbia,Canada"}



mon_map = {"January" : "1",
           "Febrary" : "2",
           "March"   : "3",
           "April"   : "4",
           "May"     : "5",
           "June"    : "6",
           "July"    : "7",
           "August"  : "8",
           "October" : "9",
           "September": "10",
           "November": "11",
           "December": "12"}


str_exp = ["Street", "Avenue", "Boulevard","Broughton", "Drive", "Court", "Place", "Square", "Lane", "Road","Walk",
            "Drive", "South","Court","Alley","Esplanade","Jarvis","Jervis",'Connector',"Terminal","Nanaimo",
            "Trail", "Parkway", "Commons","East","Mews","Kingsway","West","Mall","Crescent","Way","Highway","Broadway"]

    # UPDATE THIS VARIABLE
str_map = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            "Blvd" : "Boulevard",
            "E" : "East",
            "W" : "West",
            "Steet" : "Street",
            "Venue" : "Avenue",
          "Denmanstreet" : "Denman Street",
          "Vancouver" : "",
          "2nd" : "2nd Avenue",
           "street" : "Street"
          }


    
pro_exp = ["British Columbia","Ontario"]



# UPDATE THIS VARIABLE
pro_map = {"BC" : "British Columbia",
           "B.C.": "British Columbia",
          "British-Columbia": "British Columbia",
          "ON" : "Ontario",
          "bc" : "British Columbia"}



def key_type(element, keys):
    lower = re.compile(r'^([a-z]|_)*$')
    lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    if element.tag == "tag":
        
        l = lower.search(element.attrib['k'])
        lc= lower_colon.search(element.attrib['k'])
        pc= problemchars.search(element.attrib['k'])
        
        if l :
            keys['lower'] += 1
        elif lc :
            keys['lower_colon'] += 1
        elif pc :
            keys['problemchars'] += 1
        else :
            keys['other'] += 1
        
        
    return keys



def process_map(filename):
    osm_file = open(filename, "r")
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    osm_file.close()
    return keys



def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

            


def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename, events=('start', 'end')):
        if elem.tag in tags.keys() and event == 'start':
            tags[elem.tag] += 1
        elif event == 'start':
            tags[elem.tag] = 1
        if event == 'end':
            elem.clear()
    return tags




def is_tag(elem) :
    return elem.tag == 'tag'

def audit_tag(filename, update) :
    tag_list = set()
    for event, elem in ET.iterparse(filename):
        if is_tag(elem) :
            if elem.attrib['k'][0].isupper():
                tag_list.add(elem.attrib['k'])
            else :
                pass
            if update == True :
                update_tag(elem.attrib['k'])
    pprint.pprint(tag_list)
    return tag_list


def update_tag(key) :
    if not key.islower() and ":" not in key:
        new_key = key.lower()
        print key,"=>",new_key
        return new_key
    else : 
        return key



    
    


def count_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()

        street_types[street_type] += 1

def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print ("%s: %d" % (k, v)) 

def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")

def count_street(filename):
    
    street_type_re = re.compile(r'\#?\b\S+\.?\s?$', re.IGNORECASE)
    street_types = defaultdict(int)
    
    for event, elem in ET.iterparse(filename):
        if is_street_name(elem):
            count_street_type(street_types, elem.attrib['v'])    
    print_sorted_dict(street_types)

    return
 

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in str_exp:
            street_types[street_type].add(street_name)
        else :
            return
    else :
        return


def audit_street(filename):
    
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types, str_map


def update_street(name, mapping):
    m = street_type_re.search(name)
    if m :
        st_type = m.group().rstrip()
        if st_type not in str_exp :
            
            if '#' in st_type :
                name = update_street(name.replace(st_type,""),mapping)
                return name
            else :
                name = name.replace(st_type,mapping[st_type])
                return update_street(name,mapping)
        else :
            return name
    else :
        return name






def audit_phone_number(phone_number,bad_number):
    m = phone_number_re.search(phone_number)
    if m:
        #good_number.append(phone_number)
        #return good_number
        pass
    else :
        
        bad_number.append(phone_number)

def is_phone_number(elem):
    return (elem.tag == "tag") and ("phone" in (elem.attrib['k']) or (elem.attrib['k'] == 'fax') )


def audit_number(filename):
    bad_number = []
    good_number = []
    updated_number = []
    imcomplete_number = []
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_number(tag):
                    
                    audit_phone_number(tag.attrib['v'],bad_number)
    return bad_number



def update_number(number):

    f = find_number_re.search(number)
    if f :
        updated_number = modify_number_re.sub('',f.group())
        return updated_number
    else :
        updated_number = number.replace('+','')
        return updated_number
       




def audit_post(code,bad_code) :
    m = good_code_re.search(code)
    if m :
        pass
        #return code
    else :
        bad_code.append(code)

def audit_post_code(filename) :
    
    bad_code = []
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way" :
            for tag in elem.iter("tag") :
                if is_post_code(tag):
                    audit_post(tag.attrib['v'],bad_code)             
    
    return bad_code

def is_post_code(elem) :
    return (elem.tag == "tag") and (elem.attrib['k'] == 'addr:postcode')
    
def update_post_code(code) :
    m = good_code_re.search(code)
    if m :
        updated_code = m.group().replace(' ','').upper()
        return updated_code
    else :
        updated_code = code.replace(' ','').upper()
        return updated_code
    


    
    


def audit_pro(province_type,province_types):
    if province_type not in pro_exp:
        province_types['Not BC'].add(province_type)
    else :
        province_types['BC'].add(province_type)
    return province_types


def is_province(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:province")


def audit_province(filename):

    province_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_province(tag):
                    audit_pro(tag.attrib['v'],province_types)
    return province_types, pro_map


def update_province(name, mapping):
    if name not in pro_exp :
        
        name = name.replace(name,mapping[name])
        return name
    else :

        return name


def date_type(date,good_date,bad_date):
    m = expected.search(date)
    if m :
        good_date.add(date)
    else :
        bad_date.add(date)
    return good_date,bad_date

def is_date(elem):
    return (elem.tag == "tag") and ("date" in elem.attrib['k'])


def audit_date(filename):
    good_date = set()
    bad_date = set()
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_date(tag):
                    good_date, bad_date = date_type(tag.attrib['v'],good_date,bad_date)

    return good_date, bad_date, mon_map


def update_date(date,mapping):
    m = month.search(date)
    if m :
        mon = m.group()
        if mon in mapping :
            date = date.replace(mon,mapping[mon])
            updated_date = re.sub(check,r"\g<year>-\g<other>",date)
            return updated_date
        else :
            return date
    else :
        updated_date = re.sub(check,r"\g<year>-\g<other>",date)
        return updated_date
                
        


def audit_height_(height,height_bad) :
    m = bad_height.search(height)
    if m :
        height_bad.append(height)
    else :
        pass
        
    

def is_height(elem):
    return (elem.tag == "tag") and ("height" in elem.attrib['k'])


def audit_height(filename):
 
    height_bad = []
    for event, elem in ET.iterparse(filename, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_height(tag):
                    audit_height_(tag.attrib['v'],height_bad)
                    

    return height_bad


def update_height(height):
    m = bad_height.search(height)
    if m :
        u = m.group()
        if u == 'ft':
            updated_height = height.replace(u,'').strip()
            updated_height = float(updated_height) * 0.3048
            return str(updated_height)
        else :
            updated_height = (height.replace(u,'').strip())
            return updated_height
    else:
        return height.strip()





def audit_is_in_type(is_in_name, is_in_types):
    m = is_in_re.search(is_in_name)
    if m :
        
        is_in_type = m.group()
        
        if is_in_types not in isin_exp :
            is_in_types[is_in_type].add(is_in_name)
    else : 
        pass
        # print(is_in_name)
    


def is_in(elem):
    return (elem.tag == "tag") and ('is_in' in elem.attrib['k'])


def audit_is_in(filename):

    is_in_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_in(tag):
                    audit_is_in_type(tag.attrib['v'],is_in_types)

    return is_in_types, isin_map


def update_is_in(name, mapping):
    if name.find(',') == -1 :
        #1
        m = is_in_re.search(name)
        if m:
            op = m.group()
            updated_name = name.replace(op,mapping[op]).replace(", ",",")
            return updated_name
        else :
            return name
    else :
        #2
        m = is_in_re.search(name)
        if m :
            # bc 
            op = m.group()
            updated_name = name.replace(op,mapping[op]).replace(", ",",")
            return updated_name
        else :
            try:
                updated_name = name.replace(", ",",")
                return updated_name
            # british
            except ValueError :
                updated_name = name
                return updated_name

    return name           
            


    
website_re = re.compile(r'https?://\S')

def bad_web(name,bad_webs):
    m = website_re.search(name)
    
    if not m :
        bad_webs.append(name)
    else :
        pass
    
    

def is_web(element) :
    return (element.tag == "tag") and (element.attrib['k'] in ["website","url"])

def update_web(value) :
    
    m = website_re.search(value)
    
    if not m :
        if 'http://' in value :
            value = value.replace(' ','')
            return value
        else :
            value = 'http://' + value
            return value
    else :
        return value
    

def audit_web(filename) :
    bad_webs = []
    
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way" :
            for tag in elem.iter("tag"):
                if is_web(tag):
                    bad_web(tag.attrib['v'],bad_webs)
                    
   
    return bad_webs
                    

