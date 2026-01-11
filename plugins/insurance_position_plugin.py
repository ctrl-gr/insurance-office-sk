from typing import Annotated
from semantic_kernel.functions import kernel_function
from pymongo import MongoClient
from datetime import datetime
import os

class insurance_position_plugin:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.conditions_collection = None
        self.connected = False
    
    def _connect(self):
        """Internal method to establish database connection."""
        if self.connected:
            return True
        
        try:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            if not connection_string:
                return False
            
            self.client = MongoClient(connection_string)
            self.client.admin.command('ping')
            
            self.db = self.client[os.getenv("DB_NAME")]
            self.collection = self.db[os.getenv("COLLECTIONS")]
            self.conditions_collection = self.db["policy_conditions"]
            self.connected = True
            return True
        except Exception as e:
            self.connected = False
            return False
    
    def _get_conditions_by_category(self, category: str) -> str:
        """Internal method to get conditions from database by category."""
        if not self._connect():
            return ""
        
        try:
            result = self.conditions_collection.find_one({
                "category": {"$regex": f"^{category}$", "$options": "i"}
            })
            if result and "name_conditions" in result:
                return result["name_conditions"]
            return ""
        except Exception as e:
            return e
    
    @kernel_function(
        name="get_next_policy_exp",
        description="Gets the next insurance expiration date from the database. Returns the insurance policy that will expire soonest.",
    )
    def get_next_expire(self) -> str:
        """Gets the next insurance expiration date."""
        if not self._connect():
            return "Error: Cannot connect to database. Please check your MongoDB connection string in the .env file."
        
        try:
            current_date = datetime.now()
            
            result = self.collection.find_one(
                {"expiration_date": {"$gte": current_date}},
                sort=[("expiration_date", 1)]
            )
            
            if not result:
                return "No upcoming insurance expirations found in the database."
            
            exp_date = result['expiration_date']
            policy_holder = result.get('policy_holder', 'Unknown')
            policy_type = result.get('policy_type', 'Unknown')
            provider = result.get('provider', 'Unknown')
            guarantees = result.get('guarantees', 'Unknown')
            conditions = result.get('conditions', 'Unknown')
            
            days_until = (exp_date - current_date).days
            
            return f"Next expiration:\n- Policy holder: {policy_holder}\n- Type: {policy_type}\n- Provider: {provider}\n- Guarantees: {guarantees}\n- Expiration Date: {exp_date.strftime('%Y-%m-%d')}\n- Days until expiration: {days_until}\n- Conditions edition: {conditions}"
        
        except Exception as e:
            return f"Error retrieving expiration date: {str(e)}"
    
    @kernel_function(
        name="list_all_insurances",
        description="Lists all insurance policies in the database with their expiration dates and their guarantees.",
    )
    def list_all_insurances(self) -> str:
        """Lists all insurance policies."""
        if not self._connect():
            return "Error: Cannot connect to database. Please check your MongoDB connection string."
        
        try:
            insurances = list(self.collection.find().sort("expiration_date", 1))
            
            if not insurances:
                return "No insurance policies found in the database."
            
            result = f"Found {len(insurances)} insurance policies:\n\n"
            
            for idx, ins in enumerate(insurances, 1):
                policy_holder = ins.get('policy_holder', 'Unknown')
                policy_type = ins.get('policy_type', 'Unknown')
                provider = ins.get('provider', 'Unknown')
                guarantees = ins.get('guarantees', 'Unknown')
                exp_date = ins.get('expiration_date', 'Unknown')
                conditions = ins.get('conditions', 'Unknown')
                
                if isinstance(exp_date, datetime):
                    exp_str = exp_date.strftime('%Y-%m-%d')
                    days_until = (exp_date - datetime.now()).days
                    status = "Expired" if days_until < 0 else f"{days_until} days left"
                else:
                    exp_str = str(exp_date)
                    status = "Unknown"
                
                result += f"{idx}. {policy_holder} ({policy_type})\n"
                result += f"   Provider: {provider}\n"
                result += f"   Guarantees: {guarantees}\n"
                result += f"   Expires: {exp_str} ({status})\n"
                result += f"   Conditions: {conditions}\n/n"
            
            return result
        
        except Exception as e:
            return f"Error listing insurances: {str(e)}"
    
    @kernel_function(
        name="add_insurance",
        description="Adds a new insurance policy to the database. Requires policy holder, type, provider, guarantees and expiration date (YYYY-MM-DD format).",
    )
    def add_insurance(
        self,
        policy_holder: Annotated[str, "Name of the insurance policy holder"],
        policy_type: Annotated[str, "Type of insurance (e.g., Car, Injuries, Home)"],
        provider: Annotated[str, "Insurance provider/company name"],
        guarantees: Annotated[str, "Policy guarantees"],
        expiration_date: Annotated[str, "Expiration date in YYYY-MM-DD format"],
    ) -> str:
        """Adds a new insurance policy to the database."""
        if not self._connect():
            return "Error: Cannot connect to database. Please check your MongoDB connection string."
        
        try:
            exp_date = datetime.strptime(expiration_date, "%Y-%m-%d")
            
            conditions = self._get_conditions_by_category(policy_type)
            
            insurance_doc = {
                "policy_holder": policy_holder,
                "policy_type": policy_type,
                "provider": provider,
                "guarantees": guarantees,
                "expiration_date": exp_date,
                "conditions": conditions,
                "created_at": datetime.now()
            }
            
            result = self.collection.insert_one(insurance_doc)
            
            return f"Successfully added insurance policy for '{policy_holder}' with conditions {conditions} (ID: {result.inserted_id})"
        
        except ValueError:
            return "Error: Invalid date format. Please use YYYY-MM-DD format (e.g., 2026-12-31)"
        except Exception as e:
            return f"Error adding insurance: {str(e)}"
    
    @kernel_function(
        name="get_db_status",
        description="Returns the connection status and basic information about the insurance database.",
    )
    def get_db_status(self) -> str:
        """Returns database connection status and info."""
        if not self._connect():
            return "Database Status: Not Connected\nPlease check your MONGODB_CONNECTION_STRING in the .env file."
        
        try:
            count = self.collection.count_documents({})
            return f"Database Status: Connected\nDatabase: insurance_db\nCollection: insurances\nTotal policies: {count}"
        except Exception as e:
            return f"Database Status: Connected but error occurred: {str(e)}"
