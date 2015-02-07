'''
Animal Logic Tech Test
Code by Arthur Terzis

Note: All classes saved in this one text file to keep things easy to email 
rather than splitting into seperate files
'''

import os, sys
from xml.dom.minidom import Document
from xml.dom.minidom import parse
import pickle
import pprint



class Contact(object):
    '''
        Base Data class for a list of contact information
    '''
    def __init__(self, firstName="", lastName="", address="", phone=""):
        self._firstName = firstName
        self._lastName = lastName
        self._address = address
        self._phone = phone
    
    def __repr__(self):
        return "Contact: %s %s,\nAddress: %s,\nPhone: %s" %(self._firstName, 
                                              self._lastName, 
                                              self._address, 
                                              self._phone)
        
    def getFirstName(self):
        return self._firstName
    
    def getlastName(self):
        return self._lastName
    
    def getAddress(self):
        return self._address

    def getPhone(self):
        return self._phone
        
    def setFirstName(self, firstName=None):
        if firstName != None:
            self._firstName = firstName
        else:
            print "No first name to set"
            
    def setLastName(self, lastName=None):
        if lastName != None:
            self._lastName = lastName
        else:
            print "No last name to set"
    
    def setAddress(self, address=None):
        if address != None:
            self._address = address
        else:
            print "No Address to set"

    def setPhone(self, phone=None):
        if phone != None:
            self._phone = phone
        else:
            print "No phone number found"


#===============================================================================
# I would put DataHandler, Reader and Writer Classes in a separate .py file 
#===============================================================================



class DataHandler(object):
    '''
    Base class for a data reader/writer
    '''
    def __init__(self, format="XML"):
        '''
        format = current format for export, either XML or Pickle currently supported
        '''
        self._format = format
        self._formats = ["XML", "pickle"]
        self._data = []
        self._filePath = None


    def setFormat(self, format):
        if format in self._formats:
            self._format = format
            return True
        else:
            print "%s is an unsupported format, setting to None" %format
            self._format = None
            return False
        
    def setData(self, data):
        if isinstance(data, list):
            self._data = data
        else:
            self._data = [data]
               
    def setFilePath(self, filePath):
        '''
        Note: Only tested on a windows machine - may not work on linux
        check to see if passed in directory exists
        '''
        platform = sys.platform
        if platform == "win32":
            slash = '\\'
        else:
            slash = '/'
        
        dir = filePath[:filePath.rfind(slash)]
        if os.path.exists(dir):
            self._filePath = filePath
            return self._filePath
        else:
            print "%s directory does not exist - Aborting" %dir
            return False

    def getData(self):
        return self._data
    
    def getFilePath(self):
        # returns the currently assigned filePath
        return self._filePath
   
    def getSupportedFormats(self):
       return self._formats
    
    def getCurrentFormat(self):
        return self._format
        
    def displayData(self):
        pprint.pprint(self._data)
        return True

    def displayDataCards(self):
        for data in self._data:
            print "#" * 10 + " Contact " + "#" *10
            print "%s, %s" %(data.getlastName().upper(), data.getFirstName())
            print "Address: %s" %data.getAddress()
            print "Phone: %s \n"  %data.getPhone()
        
        return True
    

class Reader(DataHandler):
    '''
    Reads data based on the contact class. 
    Currently supported formats: XML and Pickle
    '''
    def __init__(self, format="XML"):
        DataHandler.__init__(self, format)

    def deserialize(self, filePath=None):
        if filePath:
            self.setFilePath(filePath)
        
        if self._format in self._formats:
            if self._format == "XML":
                self._deserializeXML()
            else:
                self._deserializePickle()
            return self._data
        else:
            print "%s type serialising not supported" %self._format
            return False
        
    def _deserializeXML(self):
        # flush any existing data
        self._data = []
        addressBook = parse(self._filePath)   
        
        contacts = addressBook.getElementsByTagName("Contact")
        
        # sort through each contact and get the data
        for contact in contacts:
            tmp = Contact(contact.getAttribute("firstName"),contact.getAttribute("lastName"),
                          contact.getAttribute("address"),contact.getAttribute("phone"))
            
            self._data.append(tmp)

    def _deserializePickle(self):
        # flush any existing data
        self._data = []
        
        #read file
        data = open(self._filePath, "r")
        info = pickle.load(data)
        data.close()
        
        # re-populate the data
        for obj in info:
            tmp = Contact(obj.getFirstName(),obj.getlastName(),obj.getAddress(),obj.getPhone())
            self._data.append(tmp)
                


class Writer(DataHandler):
    '''
    Writes data based on the contact class. 
    Currently supported formats: XML and Pickle
    '''
    def __init__(self, format="XML"):
        DataHandler.__init__(self, format)        
        
        
    def serialize(self, data):
        self.setData(data)
                
        if self._format in self._formats:
            if self._format == "XML":
                return self._serializeXML()
            else:
                return self._serializePickle()
        else:
            print "%s serialising not supported" %self._format   
            return False
        
        
    def _serializeXML(self):
        '''
         Expects data to be a list of Contact Objects
        '''
        doc = Document()

        element = doc.createElement("AddressBook")
        doc.appendChild(element)
    
        for data in self._data:
            
            contact = doc.createElement("Contact")
            element.appendChild(contact)
            
            firstName = doc.createAttribute("firstName")
            firstName.nodeValue = data.getFirstName()
            
            lastName = doc.createAttribute("lastName")
            lastName.nodeValue = data.getlastName()
            
            address = doc.createAttribute("address")
            address.nodeValue = data.getAddress()
            
            phone = doc.createAttribute("phone")
            phone.nodeValue = data.getPhone()
            
            contact.setAttributeNode(firstName)
            contact.setAttributeNode(lastName)
            contact.setAttributeNode(address)
            contact.setAttributeNode(phone)
    
        data = open(self._filePath,"w")
        data.write(doc.toprettyxml())
        data.close()

        print "Contacts saved out as an XML file."
        return True
        
    def _serializePickle(self):
        data = open(self._filePath, "w")
        pickle.dump(self._data, data)
        data.close()
        
        print "Contacts Saved out as a Pickle File"
        return True


#===============================================================================
# UNIT TESTS
#===============================================================================
import unittest

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        # create some test data
        self.contact1 = Contact("John", "Snow","27 Allan Ave, Sydney", "0400333444")
        self.contact2 = Contact("Peter","Frost", "121 George St, Sydney", "98547123")
        self.contact3 = Contact("Alice", "Oniel", "112 President Ave, Melbourne", "356325647")
        # data list of Contacts
        self.data = [self.contact1, self.contact2, self.contact3]
        # test file locations
        self.xmlFile = "C:\Documents and Settings\HP_Owner\Desktop\\test\\addressBook.xml"
        self.pickleFile= "C:\Documents and Settings\HP_Owner\Desktop\\test\\addressBook.pkl"

        self.writer = Writer()
        self.reader = Reader()
        

    def test_WriteXML(self):
        # initial write out of a file in XML
        self.writer.setFormat("XML")
        self.writer.setFilePath(self.xmlFile)

        write = self.writer.serialize(data=self.data)
        self.assertTrue(write)

    def test_ReadXML(self):
        # read the xml file
        self.reader.setFormat("XML")
        self.reader.setFilePath(self.xmlFile)
        data = self.reader.deserialize()
        
        #check to see the same number of elements are returned
        self.assertEqual(len(data), len(self.data))
        
        print "XML DISPLAY"
        # And check that these functions run
        self.assertTrue(self.reader.displayData())
        self.assertTrue(self.reader.displayDataCards())

    def test_WritePickle(self):
        # initial write out of a pickle file
        self.writer.setFormat("pickle")
        self.writer.setFilePath(self.pickleFile)

        write = self.writer.serialize(data=self.data)
        self.assertTrue(write)

    def test_ReadPickle(self):
        # read the pickle file
        self.reader.setFormat("pickle")
        self.reader.setFilePath(self.pickleFile)
        data = self.reader.deserialize()
        
        #check to see the same number of elements are returned
        self.assertEqual(len(data), len(self.data))
        
        # And check that these functions run
        print "PICKLE DISPLAY"
        self.assertTrue(self.reader.displayData())
        self.assertTrue(self.reader.displayDataCards())

    def test_tryUnsupported(self):
        # check the writer for unsupported
        self.writer.setFormat("json")
        write = self.writer.serialize(data=self.data)
        self.assertFalse(write)
        # check the reader for unsupported
        self.reader.setFormat("json")
        read = self.reader.deserialize()
        self.assertFalse(read)
        
        # check to see when an incorrect file path is used
        self.writer.setFormat("XML")
        path = self.writer.setFilePath("C:\Documents and Settings\HP_Owner\Desktop\\fake\\temp.xml")
        self.assertFalse(path)

    
'''
Run the unit tests
'''
if __name__ == '__main__':
    unittest.main()


