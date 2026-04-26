#!/usr/bin/env python
# coding: utf-8

# In[2]:


from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter:
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, user, pwd):
        # Initializing the MongoClient. This helps to 
        # access the MongoDB databases and collections.
        # This is hard-wired to use the aac database, the 
        # animals collection, and the aac user.
        # Definitions of the connection string variables are
        # unique to the individual Apporto environment.
        #
        # Connection Variables
        #
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 31210
        DB = 'AAC'
        COL = 'animals'
        
        
        # Initialize Connection
        try:
            # Establish connection to MongoDB client
            self.client = MongoClient('mongodb://%s:%s@%s:%d' % (user,pwd,HOST,PORT))
            # Access specified client database
            self.database = self.client['%s' % (DB)]
            # Access specified collection within database
            self.collection = self.database['%s' % (COL)]
        # Connection error handling
        except pymongo.errors.ConnectionFailure as e:
            print("Error connecting to the MongoDB server::", e)

# Create method to insert new document into animals collection
    def create(self, data):
        if data is not None:
            try:
                # Insert data into animals collection (data should be a dictionary)
                self.database.animals.insert_one(data)
                # Returns True if successful
                return True
            
            # Error handling for insertion
            except Exception as e:
                print("An error occurred while attempting to add data ::", e)
                # Returns False if insertion is unsuccessful
                return False
        # Else raises exception due to empty data parameter
        else:
            raise Exception("Nothing to save, because data parameter is empty")

# Method to read documents from animals collection
    def read(self, query):
        if query is not None:
            #query database results
            results = self.database.animals.find(query)
            #set database query results as list
            resultList = list(results)
            #return list
            return resultList
        #if empty query is passed as parameter
        else:
            #empty query returns all animals
            results = self.database.animals.find({})
            #set query results as list
            resultList = list(results)
            #return list
            return results
            
# Method to update documents from animals collection            
    def update(self, query, data):
        # If no update query entered
        if query is None:
            raise Exception("Error: search parameter is empty.")
        # If no update data entered
        elif data is None:
            raise Exception("Nothing to update, because data parameter is empty.")
        else:
            # Use update_many call to update documents with data parameter based on query parameter
            results = self.database.animals.update_many(query,{ "$set": data})
            # return the number of documents that were modified
            return results.modified_count
        
# Method to delete documents from animals collection
    def delete(self, query):
        # If no delete query entered
        if query is None:
            raise Exception("Error: search parameter is empty.")
        else:
            # Use delete_many call to delete documents that match the query
            results = self.database.animals.delete_many(query)
            # return the number of documents deleted
            return results.deleted_count
        
            

