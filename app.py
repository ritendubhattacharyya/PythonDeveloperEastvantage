from fastapi import FastAPI, Depends, HTTPException
import uvicorn
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, MetaData, inspect, update
from sqlalchemy import Table, Column, Integer, String, Float
from pydantic import BaseModel
import json
from math import radians, sin, cos, sqrt, atan2

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


address = Table(
    "address",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("street_no", String, nullable=False),
    Column("city", String, nullable=False),
    Column("state", String, nullable=False),
    Column("country", String, nullable=False),
    Column("coordinates_l1", Float, nullable=False),
    Column("coordinates_l2", Float, nullable=False),
)

metadata.create_all(bind=engine)


def haversine_distance(coord1, coord2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    
    # Calculate the change in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Calculate the distance
    distance = R * c
    
    return distance


@app.get('/')
def index():
    return "Hello World"


@app.get('/get_address')
def index(db: Session = Depends(get_db)):
    query = address.select()
    result = db.execute(query).fetchall()
    print(type(list(result[0])))
    final_list = []
    for i in result:
        data = {}
        data['id'] = i[0]
        data['street'] = i[1]
        data['city'] = i[2]
        data['state'] = i[3]
        data['country'] = i[4]
        data['l1'] = i[5]
        data['l2'] = i[6]
        final_list.append(data)

    return json.dumps(final_list)


@app.get("/addresses/filter/")
def filter_addresses(latitude: float, longitude: float, max_distance: float, db: Session = Depends(get_db)):
    # Reference coordinate
    reference_coord = (latitude, longitude)
    
    # Retrieve all addresses from the database
    query = address.select()
    result = db.execute(query)
    addresses = result.fetchall()
    
    # Filter addresses based on the given distance
    filtered_addresses = []
    for addr in addresses:
        # Calculate the distance between the reference coordinate and the address coordinate
        address_coord = (addr.coordinates_l1, addr.coordinates_l2)
        distance = haversine_distance(reference_coord, address_coord)
        
        # Check if the distance is within the specified maximum distance
        if distance <= max_distance:
            filtered_addresses.append(addr)
    final_list = []
    for i in filtered_addresses:
        data = {}
        data['id'] = i[0]
        data['street'] = i[1]
        data['city'] = i[2]
        data['state'] = i[3]
        data['country'] = i[4]
        data['l1'] = i[5]
        data['l2'] = i[6]
        final_list.append(data)
    return json.dumps(final_list)


class AddressCreate(BaseModel):
    street_no: str
    city: str
    state: str
    country: str
    coordinates_l1: float
    coordinates_l2: float


@app.post('/create')
def create_address(address_data: AddressCreate, db: Session = Depends(get_db)):
    new_address = address.insert().values(
        street_no=address_data.street_no,
        city=address_data.city,
        state=address_data.state,
        country=address_data.country,
        coordinates_l1=address_data.coordinates_l1,
        coordinates_l2=address_data.coordinates_l2
    )
    db.execute(new_address)
    db.commit()
    return {"message": "Address added successfully"}


class AddressUpdate(BaseModel):
    street_no: str = None
    city: str = None
    state: str = None
    country: str = None
    coordinates_l1: float = None
    coordinates_l2: float = None


@app.put("/update/{address_id}")
def update_address(address_id: int, address_data: AddressUpdate, db: Session = Depends(get_db)):
    # Prepare the values to be updated, filtering out None values
    update_data = {}
    address_data_dict = address_data.dict()
    for key, value in address_data_dict.items():
        if value is not None:
            update_data[key] = value

    if not update_data:
        raise HTTPException(status_code=401, detail="No fields to update")

    stmt = update(address).where(address.c.id == address_id).values(**update_data)
    result = db.execute(stmt)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address updated successfully"}


@app.delete("/delete/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    stmt = address.delete().where(address.c.id == address_id)
    result = db.execute(stmt)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Address not found")

    return {"message": "Address deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)