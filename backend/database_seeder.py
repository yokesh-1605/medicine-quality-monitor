"""
Database Seeder for Medicine Quality Monitor
Seeds MongoDB with sample medicines data
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import os
import random
from dotenv import load_dotenv
from pathlib import Path
import uuid

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Sample manufacturers with their reliability scores
MANUFACTURERS = [
    {"name": "PharmaCorp", "score": 9.5, "country": "USA"},
    {"name": "MediTech Industries", "score": 8.8, "country": "Germany"},
    {"name": "HealthFirst Labs", "score": 9.2, "country": "Switzerland"},
    {"name": "BioMed Solutions", "score": 8.5, "country": "UK"},
    {"name": "PharmaGlobal", "score": 7.8, "country": "India"},
    {"name": "MedLife Corp", "score": 9.0, "country": "Japan"},
    {"name": "GenericMeds Inc", "score": 7.2, "country": "China"},
    {"name": "EuroPharma", "score": 8.9, "country": "France"},
    {"name": "AsiaMed Ltd", "score": 6.5, "country": "Vietnam"},
    {"name": "CounterfeitCorp", "score": 3.2, "country": "Unknown"},  # Suspicious manufacturer
]

# Sample medicine types
MEDICINE_TYPES = [
    "Paracetamol 500mg", "Ibuprofen 200mg", "Amoxicillin 250mg", 
    "Aspirin 75mg", "Metformin 500mg", "Omeprazole 20mg",
    "Atorvastatin 20mg", "Losartan 50mg", "Amlodipine 5mg",
    "Ciprofloxacin 500mg", "Doxycycline 100mg", "Prednisone 5mg",
    "Insulin Glargine", "Salbutamol Inhaler", "Vitamin D3 1000IU",
    "Folic Acid 5mg", "Iron Sulfate 200mg", "Calcium Carbonate 500mg"
]

def generate_batch_id():
    """Generate a realistic batch ID"""
    prefix = random.choice(['MED', 'PHR', 'BTH', 'LOT'])
    number = random.randint(100000, 999999)
    suffix = random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])
    return f"{prefix}{number}{suffix}"

async def seed_medicines():
    """Seed the database with sample medicines"""
    print("Seeding medicines collection...")
    
    medicines = []
    
    for i in range(50):
        manufacturer = random.choice(MANUFACTURERS)
        medicine_name = random.choice(MEDICINE_TYPES)
        
        # Generate expiry date (some expired, some valid, some near expiry)
        if i < 5:  # 5 expired medicines
            expiry_date = datetime.now() - timedelta(days=random.randint(1, 365))
            status = "expired"
        elif i < 10:  # 5 near expiry medicines  
            expiry_date = datetime.now() + timedelta(days=random.randint(1, 30))
            status = "valid"
        elif i < 45:  # 35 valid medicines
            expiry_date = datetime.now() + timedelta(days=random.randint(31, 730))
            status = "valid"
        else:  # 5 fake medicines
            expiry_date = datetime.now() + timedelta(days=random.randint(100, 500))
            status = "fake"
        
        # Generate batch manufacturing date
        manufacturing_date = expiry_date - timedelta(days=random.randint(365, 1095))
        
        batch_id = generate_batch_id()
        
        medicine = {
            "_id": str(uuid.uuid4()),
            "batch_id": batch_id,
            "name": medicine_name,
            "manufacturer": manufacturer["name"],
            "manufacturer_score": manufacturer["score"],
            "manufacturer_country": manufacturer["country"],
            "expiry_date": expiry_date.isoformat(),
            "manufacturing_date": manufacturing_date.isoformat(),
            "status": status,
            "scan_count": random.randint(0, 15),
            "distinct_locations": random.randint(1, 5),
            "verification_history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        medicines.append(medicine)
    
    # Clear existing medicines
    await db.medicines.delete_many({})
    
    # Insert new medicines
    await db.medicines.insert_many(medicines)
    
    print(f"Successfully seeded {len(medicines)} medicines!")
    
    # Print some statistics
    valid_count = sum(1 for m in medicines if m['status'] == 'valid')
    expired_count = sum(1 for m in medicines if m['status'] == 'expired')
    fake_count = sum(1 for m in medicines if m['status'] == 'fake')
    
    print(f"Valid medicines: {valid_count}")
    print(f"Expired medicines: {expired_count}")
    print(f"Fake medicines: {fake_count}")

async def seed_admin_user():
    """Seed admin user for dashboard access"""
    print("Seeding admin user...")
    
    # Simple admin user (in production, hash the password!)
    admin_user = {
        "_id": str(uuid.uuid4()),
        "username": "admin",
        "password": "admin123",  # In production, this should be hashed
        "role": "admin",
        "created_at": datetime.now().isoformat()
    }
    
    # Clear existing admin users
    await db.admin_users.delete_many({"username": "admin"})
    
    # Insert admin user
    await db.admin_users.insert_one(admin_user)
    
    print("Admin user created: username=admin, password=admin123")

async def create_indexes():
    """Create database indexes for better performance"""
    print("Creating database indexes...")
    
    # Create index on batch_id for faster lookups
    await db.medicines.create_index("batch_id", unique=True)
    
    # Create index on logs timestamp for faster queries
    await db.logs.create_index("timestamp")
    
    # Create index on admin username
    await db.admin_users.create_index("username", unique=True)
    
    print("Database indexes created!")

async def main():
    """Main seeding function"""
    try:
        await seed_medicines()
        await seed_admin_user()
        await create_indexes()
        print("\n✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during database seeding: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())