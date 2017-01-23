#!/usr/bin/env python
# -*- coding: utf-8 -*-



import xml.etree.cElementTree as ET
import pprint
import re
import datetime
from collections import defaultdict
import csv
import codecs
import cerberus
import schema

sample = "sample.osm"
source = ('/Users/watseob/Desktop/DataScience/Data/vancouver_canada.osm')

OSM_PATH = "sample.osm"
SOURCE = "/Users/watseob/Desktop/DataScience/Data/vancouver_canada.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\#?\b\S+\.?\s?$', re.IGNORECASE)


find_number_re = re.compile('\({0}\d{3}\){0}\)?[-.\s\)]{0,}\d{3}[-.\s\)]{0,}\d{4}')
modify_number_re = re.compile('\s|\.|-|\)')

good_code_re = re.compile('V[A-Z0-9]{2}\s?[A-Z0-9]{3}')

month = re.compile('[a-zA-Z]+')
check = re.compile(r"(?P<other>\b\d{0,4}[-./\s]?\d{1,2})[-./\s](?P<year>\d{4})")

good_height = re.compile('[a-zA-Z]+')

convert = re.compile('\d\.?\d?')
is_in_re = re.compile(r'[A-Z]{0,2}[-]?[A-Z]{2}')
website_re = re.compile(r'https?://\S')

str_exp = ["Street", "Avenue", "Boulevard","Broughton", "Drive", "Court", "Place", "Square", "Lane", "Road","Walk",
            "Drive", "South","Court","Alley","Esplanade","Jarvis","Jervis",'Connector',"Terminal","Nanaimo",
            "Trail", "Parkway", "Commons","East","Mews","Kingsway","West","Mall","Crescent","Way","Highway","Broadway"]

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
pro_map = {"BC" : "British Columbia",
           "B.C.": "British Columbia",
          "British-Columbia": "British Columbia",
          "ON" : "Ontario",
          "bc" : "British Columbia"}



mapping = {"January" : "1",
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

isin_exp = ["British Columbia", "Canada","North America"]

isin_map = {"BC": "British Columbia",
            "CA": "Canada",
            "NA": "North America",
            "UBC": "UBC",
            "CA-BC":"British Columbia,Canada"}



SCHEMA = schema.schema


NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  
    
    
    
    node_list = ['id','uid','version','lat','lon','timestamp','changeset','user']
    node_tag_list = ['key','value','type']
    
    way_list = ['id','user','uid','version','timestamp','changeset']
    way_nodes_list = ['node_id','position']
    way_tags_list = ['key','type','value']
    
    if element.tag == 'node':
        
        for elem in element.iter() :
            if elem.tag == 'node' :
                for key in node_list :
                    
                    try :
                        
                        if key == 'id':
                            node_attribs[key] = int(elem.attrib[key])
                        elif key == 'uid':
                            node_attribs[key] = int(elem.attrib[key])
                        elif key == 'lon' :
                            node_attribs[key] = float(elem.attrib[key])
                        elif key == 'lat' :
                            node_attribs[key] = float(elem.attrib[key])
                        elif key == 'changeset' :
                            node_attribs[key] = int(elem.attrib[key])
                        else :
                            node_attribs[key] = elem.attrib[key]
                    except :
                        if key == 'id':
                            node_attribs[key] = 000000
                        elif key == 'user':
                            node_attribs[key] = 'BLANK'
                        elif key == 'lon' :
                            node_attribs[key] = 0.0
                        elif key == 'lat' :
                            node_attribs[key] = 0.0
                        elif key == 'uid' :
                            node_attribs[key] = 0
                    
            elif elem.tag == 'tag' :
                tags_list = {}
                for k,v in elem.attrib.items():
                    #print k,v                   # -------------
                    m = problem_chars.search(v)
                    if m :
                        continue
                    tags_list['id'] = int(element.attrib['id'])
                    
                    tags_list['value'] = elem.attrib['v']
                    if ':' in elem.attrib['k'] :
                        tags_list['type'] = elem.attrib['k'].split(':')[0]
                        tags_list['key'] = elem.attrib['k'].split(':',1)[1]
                    else :
                        tags_list['type'] = 'regular'
                        tags_list['key'] = elem.attrib['k']
                tags.append(tags_list)
            else :
                pass
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        count = 0
        for elem in element.iter():
            
            if elem.tag == 'way' :
                for k, v in elem.items():
                    for key in way_list :
                    #id','user','uid','version','timestamp','changeset'
                        try :

                            if key == 'id':
                                way_attribs[key] = int(elem.attrib[key])
                            elif key == 'uid':
                                way_attribs[key] = int(elem.attrib[key])

                            elif key == 'changeset' :
                                way_attribs[key] = int(elem.attrib[key])
                            else :
                                way_attribs[key] = elem.attrib[key]
                        except :

                            print 'way error--------------'
            elif elem.tag == 'nd' :
                way_nodes_dic = {}
                
                for k, v in elem.items(): 
                    #print k, v
                    way_nodes_dic['position'] = count
                    way_nodes_dic['id'] = int(element.attrib['id'])
                    way_nodes_dic['node_id'] = int(v)
                    count += 1
                way_nodes.append(way_nodes_dic)
            elif elem.tag == 'tag' :
                way_tags_list = {}
                for k,v in elem.attrib.items():
                    #print k,v                   #-----------------
                    m = problem_chars.search(v) 
                    if m :
                        continue
                    way_tags_list['id'] = int(element.attrib['id'])
                    
                    way_tags_list['value'] = elem.attrib['v']
                    if ':' in elem.attrib['k'] :
                        way_tags_list['type'] = elem.attrib['k'].split(':')[0]
                        way_tags_list['key'] = elem.attrib['k'].split(':',1)[1]
                    else :
                        way_tags_list['type'] = 'regular'
                        way_tags_list['key'] = elem.attrib['k']
                tags.append(way_tags_list)
            else :
                pass
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    else :
        pass

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        validator = cerberus.Validator()

        
        
        for element in get_element(file_in, tags=('node', 'way')):
            for elem in element:
                if is_tag(elem) :
                    elem.attrib['k'] = update_key(elem.attrib['k'])
            for elem in element :
                if is_street_name(elem):
                    elem.attrib['v'] = update_street(elem.attrib['v'],str_map)
                elif is_phone_number(elem):
                    
                    elem.attrib['v'] = update_number(elem.attrib['v'])
                elif is_post_code(elem):
                     elem.attrib['v'] = update_post_code(elem.attrib['v'])
                elif is_province(elem):
                    updated_province = update_province(elem.attrib['v'], pro_map)
                    elem.attrib['v'] = updated_province
                elif is_date(elem):
                    elem.attrib['v'] = update_date(elem.attrib['v'])
                elif is_height(elem):
                    elem.attrib['v'] = update_height(elem.attrib['v'])
                elif is_in(elem):
                    elem.attrib['v'] = update_is_in(elem.attrib['v'],isin_map)
                elif is_web(elem):
                    elem.attrib['v'] = update_web(elem.attrib['v'])
                else :
                    pass
 
                    
                    
                    
                    
                    
                    
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


            
            
def is_tag(elem) :
    return elem.tag == 'tag'

def update_key(key) :

    if (not key.islower()) and (":" not in key):
        new_key = key.lower()
        return new_key
    else : 
        return key


def is_street_name(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")


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

def is_phone_number(elem):
    return (elem.tag == "tag") and ("phone" in (elem.attrib['k']) or (elem.attrib['k'] == 'fax') )

def update_number(number):
    f = find_number_re.search(number)
    if f :
        updated_number = modify_number_re.sub('',f.group())
        return updated_number
    else :
        return number.replace('+','')

def is_post_code(elem) :
    return (elem.tag == "tag") and (elem.attrib['k'] == 'addr:postcode')

def update_post_code(code) :
    m = good_code_re.search(code)
    if m :
        return m.group().replace(' ','').upper()
    else :
        return code.replace(' ','').upper()
        

def is_province(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:province")

def update_province(name, mapping):
    if name not in pro_exp :
        
        name = name.replace(name,mapping[name])
        return name
    else :

        return name
    
def is_date(elem):
    return (elem.tag == "tag") and ("date" in elem.attrib['k'])
    
def update_date(date):
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

def is_height(elem):
    return (elem.tag == "tag") and ("height" in elem.attrib['k'])    
    
    
def update_height(height):
    m = good_height.search(height)
    if m :
        u = m.group()
        if u == 'ft':
            updated_height = height.replace(u,'').strip()
            updated_height = float(updated_height) * 0.3048
            return str(updated_height)
        else :
            updated_height = float(height.replace(u,'').strip())
            return str(updated_height)
    else:
        return str(height.strip()) 

def is_in(elem):
    return (elem.tag == "tag") and ('is_in' in elem.attrib['k'])

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




if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(SOURCE, validate=True)