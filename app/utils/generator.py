"""
Invoice data generator with intentional inconsistencies.
Generates realistic invoice data with various data quality issues.
"""

import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from faker import Faker

from app.models.schemas import EmailInvoice, InvoiceData


fake = Faker()


class InvoiceGenerator:
    """
    Generates invoice email data with intentional inconsistencies
    to simulate real-world data quality challenges.
    """
    
    def __init__(self, inconsistency_rate: float = 0.3):
        """
        Initialize the generator.
        
        Args:
            inconsistency_rate: Probability (0-1) of introducing inconsistencies
        """
        self.inconsistency_rate = inconsistency_rate
        self.message_counter = 1
        self.invoice_counter = 1001
        self.generated_messages: List[Dict[str, Any]] = []
        
    def generate_message_id(self) -> str:
        """Generate a unique message ID."""
        msg_id = f"msg_{self.message_counter:03d}"
        self.message_counter += 1
        return msg_id
    
    def generate_invoice_id(self) -> str:
        """Generate a unique invoice ID."""
        inv_id = f"INV-{self.invoice_counter}"
        self.invoice_counter += 1
        return inv_id
    
    def generate_amount(self) -> Any:
        """
        Generate invoice amount with potential inconsistencies.
        Returns: float, string, or invalid value
        """
        base_amount = round(random.uniform(100, 10000), 2)
        
        if random.random() < self.inconsistency_rate:
            inconsistency_type = random.choice([
                'string_with_symbol',
                'string_number',
                'text',
                'null',
                'negative'
            ])
            
            if inconsistency_type == 'string_with_symbol':
                return f"${base_amount:,.2f}"
            elif inconsistency_type == 'string_number':
                return str(base_amount)
            elif inconsistency_type == 'text':
                return random.choice([
                    "TWO THOUSAND",
                    "invalid_amount",
                    "TBD",
                    "N/A"
                ])
            elif inconsistency_type == 'null':
                return None
            elif inconsistency_type == 'negative':
                return -base_amount
        
        return base_amount
    
    def generate_datetime(self) -> Any:
        """
        Generate datetime with potential inconsistencies.
        Returns: ISO string, invalid string, or malformed datetime
        """
        base_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
        
        if random.random() < self.inconsistency_rate:
            inconsistency_type = random.choice([
                'invalid_format',
                'missing_timezone',
                'text',
                'null'
            ])
            
            if inconsistency_type == 'invalid_format':
                return base_date.strftime("%d/%m/%Y %H:%M")
            elif inconsistency_type == 'missing_timezone':
                return base_date.strftime("%Y-%m-%dT%H:%M:%S")
            elif inconsistency_type == 'text':
                return "invalid_datetime"
            elif inconsistency_type == 'null':
                return None
        
        return base_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def generate_currency(self) -> Optional[str]:
        """Generate currency code with potential missing values."""
        currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
        
        if random.random() < self.inconsistency_rate * 0.5:
            return None  # Missing currency
        
        return random.choice(currencies)
    
    def generate_vendor_name(self) -> str:
        """Generate realistic vendor name."""
        suffixes = ["Inc.", "Corp", "LLC", "Services", "Technologies", 
                   "Global", "Co.", "Solutions", "Innovations"]
        return f"{fake.company()} {random.choice(suffixes)}"
    
    def generate_invoice_data(self, include_extra_fields: bool = False) -> Dict[str, Any]:
        """
        Generate invoice data with potential inconsistencies.
        
        Args:
            include_extra_fields: Whether to include additional fields (schema drift)
        
        Returns:
            Dictionary representing invoice data
        """
        invoice_id = self.generate_invoice_id()
        amount = self.generate_amount()
        currency = self.generate_currency()
        date = fake.date_between(start_date="-30d", end_date="today").isoformat()
        vendor_name = self.generate_vendor_name()
        status = random.choice(["paid", "pending", "due", "overdue"])
        
        invoice_data: Dict[str, Any] = {}
        
        # Randomly omit critical fields
        if random.random() > self.inconsistency_rate * 0.3:
            invoice_data["invoice_id"] = invoice_id
        
        if random.random() > self.inconsistency_rate * 0.2:
            invoice_data["amount"] = amount
        
        if currency is not None:
            invoice_data["currency"] = currency
        
        invoice_data["date"] = date
        invoice_data["vendor_name"] = vendor_name
        
        if random.random() > 0.3:
            invoice_data["status"] = status
        
        # Schema drift: add new fields randomly
        if include_extra_fields or random.random() < 0.3:
            if random.random() < 0.4:
                due_date = fake.date_between(start_date="today", end_date="+60d")
                invoice_data["due_date"] = due_date.isoformat()
            
            if random.random() < 0.4:
                invoice_data["project_code"] = f"PROJ-{random.choice(['X', 'Y', 'Z'])}{random.randint(1, 9)}"
            
            if random.random() < 0.3:
                invoice_data["tax_amount"] = round(
                    float(amount if isinstance(amount, (int, float)) else 100) * 0.15, 
                    2
                )
            
            if random.random() < 0.2:
                invoice_data["approver"] = fake.email()
            
            if random.random() < 0.15:
                # Nested data structure
                num_items = random.randint(1, 3)
                invoice_data["line_items"] = [
                    {
                        "item": fake.word().capitalize(),
                        "quantity": random.randint(1, 20),
                        "rate": round(random.uniform(10, 500), 2)
                    }
                    for _ in range(num_items)
                ]
        
        return invoice_data
    
    def generate_email_invoice(self, force_duplicate: bool = False) -> Dict[str, Any]:
        """
        Generate a complete email invoice message.
        
        Args:
            force_duplicate: If True, return a duplicate of a previous message
        
        Returns:
            Dictionary representing an email with invoice data
        """
        if force_duplicate and self.generated_messages:
            # Return a duplicate of a previously generated message
            duplicate = random.choice(self.generated_messages).copy()
            return duplicate
        
        message_id = self.generate_message_id()
        invoice_data = self.generate_invoice_data()
        invoice_id = invoice_data.get("invoice_id", "UNKNOWN")
        amount = invoice_data.get("amount", "N/A")
        
        # Generate subject with variation
        subject_templates = [
            f"Invoice {invoice_id}",
            f"Invoice #{invoice_id}",
            f"URGENT: Invoice {invoice_id}",
            f"{invoice_id} Payment Request",
            f"{invoice_id} for Project {random.choice(['X', 'Y', 'Z'])}",
            "Invoice Notification",
        ]
        subject = random.choice(subject_templates)
        
        # Generate body
        body_templates = [
            f"Please find invoice {invoice_id} for ${amount} dated {invoice_data.get('date', 'N/A')}",
            f"Invoice {invoice_id} Amount: ${amount}",
            f"Invoice details: {invoice_id} for ${amount}",
            "Here's our invoice for services",
            f"Amount: ${amount}",
            f"Final invoice for project completion",
        ]
        body = random.choice(body_templates)
        
        sender = fake.email()
        received_at = self.generate_datetime()
        
        email_message = {
            "message_id": message_id,
            "subject": subject,
            "sender": sender,
            "received_at": received_at,
            "body": body,
            "invoice_data": invoice_data
        }
        
        # Store for potential duplication
        self.generated_messages.append(email_message)
        
        return email_message
    
    def generate_batch(self, count: int, duplicate_rate: float = 0.1) -> List[Dict[str, Any]]:
        """
        Generate a batch of invoice emails.
        
        Args:
            count: Number of invoices to generate
            duplicate_rate: Probability of generating duplicates
        
        Returns:
            List of email invoice dictionaries
        """
        batch = []
        
        for _ in range(count):
            force_duplicate = (
                random.random() < duplicate_rate and 
                len(self.generated_messages) > 0
            )
            email = self.generate_email_invoice(force_duplicate=force_duplicate)
            batch.append(email)
        
        return batch


# Global generator instance
generator = InvoiceGenerator()
