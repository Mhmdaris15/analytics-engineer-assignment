"""
Database abstraction layer.
Provides a unified interface for both JSON file and MongoDB storage.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.core.config import settings


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    async def save_invoices(self, invoices: List[Dict[str, Any]]) -> bool:
        """Save a batch of invoices to the database."""
        pass
    
    @abstractmethod
    async def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Retrieve all invoices from the database."""
        pass
    
    @abstractmethod
    async def get_invoice_count(self) -> int:
        """Get the total count of invoices."""
        pass
    
    @abstractmethod
    async def clear_invoices(self) -> bool:
        """Clear all invoices from the database."""
        pass
    
    @abstractmethod
    async def close(self):
        """Close database connection."""
        pass


class JSONDatabase(DatabaseInterface):
    """JSON file-based database implementation."""
    
    def __init__(self, file_path: str):
        """
        Initialize JSON database.
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Ensure the JSON file and directory exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _read_data(self) -> List[Dict[str, Any]]:
        """Read data from JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_data(self, data: List[Dict[str, Any]]):
        """Write data to JSON file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def save_invoices(self, invoices: List[Dict[str, Any]]) -> bool:
        """Save invoices to JSON file."""
        try:
            existing_data = self._read_data()
            existing_data.extend(invoices)
            self._write_data(existing_data)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    async def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices from JSON file."""
        return self._read_data()
    
    async def get_invoice_count(self) -> int:
        """Get count of invoices in JSON file."""
        data = self._read_data()
        return len(data)
    
    async def clear_invoices(self) -> bool:
        """Clear all invoices from JSON file."""
        try:
            self._write_data([])
            return True
        except Exception as e:
            print(f"Error clearing JSON: {e}")
            return False
    
    async def close(self):
        """No-op for JSON database."""
        pass


class MongoDatabase(DatabaseInterface):
    """MongoDB database implementation."""
    
    def __init__(self, url: str, database: str, collection: str):
        """
        Initialize MongoDB connection.
        
        Args:
            url: MongoDB connection URL
            database: Database name
            collection: Collection name
        """
        self.client = AsyncIOMotorClient(url)
        self.db = self.client[database]
        self.collection = self.db[collection]
    
    async def save_invoices(self, invoices: List[Dict[str, Any]]) -> bool:
        """Save invoices to MongoDB."""
        try:
            if invoices:
                # Add timestamps
                for invoice in invoices:
                    invoice['_created_at'] = datetime.utcnow()
                
                result = await self.collection.insert_many(invoices)
                return len(result.inserted_ids) == len(invoices)
            return True
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return False
    
    async def get_all_invoices(self) -> List[Dict[str, Any]]:
        """Get all invoices from MongoDB."""
        try:
            cursor = self.collection.find({})
            invoices = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for invoice in invoices:
                if '_id' in invoice:
                    invoice['_id'] = str(invoice['_id'])
            
            return invoices
        except Exception as e:
            print(f"Error reading from MongoDB: {e}")
            return []
    
    async def get_invoice_count(self) -> int:
        """Get count of invoices in MongoDB."""
        try:
            return await self.collection.count_documents({})
        except Exception as e:
            print(f"Error counting MongoDB documents: {e}")
            return 0
    
    async def clear_invoices(self) -> bool:
        """Clear all invoices from MongoDB."""
        try:
            await self.collection.delete_many({})
            return True
        except Exception as e:
            print(f"Error clearing MongoDB: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection."""
        self.client.close()


class DatabaseFactory:
    """Factory for creating database instances."""
    
    @staticmethod
    def create_database() -> DatabaseInterface:
        """
        Create a database instance based on configuration.
        
        Returns:
            DatabaseInterface implementation
        """
        if settings.database_type == "mongodb":
            return MongoDatabase(
                url=settings.mongodb_url,
                database=settings.mongodb_database,
                collection=settings.mongodb_collection
            )
        else:
            return JSONDatabase(file_path=settings.json_storage_path)


# Global database instance
db: Optional[DatabaseInterface] = None


def get_database() -> DatabaseInterface:
    """
    Get the global database instance.
    Creates one if it doesn't exist.
    
    Returns:
        DatabaseInterface instance
    """
    global db
    if db is None:
        db = DatabaseFactory.create_database()
    return db
