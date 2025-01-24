"""Module initialization
"""
from models.engine.storage import Storage

# This object handles the operation with the database
storage = Storage()

# Load the data from the database
storage.reload()
