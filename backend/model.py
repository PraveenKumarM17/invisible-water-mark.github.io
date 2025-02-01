# models.py

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['watermarkDB']

# Media collection
media_collection = db['media']

def create_media(media_id, email, file_path):
    """Insert a new media entry into the database."""
    media_entry = {
        'media_id': media_id,
        'email': email,
        'file': file_path
    }
    media_collection.insert_one(media_entry)

def get_media_by_id(media_id):
    """Retrieve media information by its unique media_id."""
    return media_collection.find_one({'media_id': media_id})

def get_all_media():
    """Retrieve all media entries."""
    return list(media_collection.find())

def delete_media(media_id):
    """Delete a media entry by its media_id."""
    result = media_collection.delete_one({'media_id': media_id})
    return result.deleted_count

def update_media(media_id, new_data):
    """Update media entry with new data (e.g., file path)."""
    result = media_collection.update_one(
        {'media_id': media_id},
        {'$set': new_data}
    )
    return result.modified_count
