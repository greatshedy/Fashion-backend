from pydantic import BaseModel,EmailStr
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    age:int
    gender:Optional[str]=None
    phone:str
    message:list[str]=[]
    friends:list[str]=[]
    is_active:Optional[bool]=None
    profile_image:Optional[str]=None
  
class User2(BaseModel):
    email:EmailStr
    password:str
    brand:str
    gender:Optional[str]=None
    phone:str
    message:list[str]=[]
    friends:list[str]=[]
    is_active:Optional[bool]=None
    profile_image:Optional[str]=None
    name:str
    age:int
    description:str
    rating:int
    reviews:int
    collections:int
    since:int
    tag:list[str]=[]
    featured:bool=False
    location:str
    image:Optional[str]=None


class User3(BaseModel):
    email:EmailStr
    password:str
    gender:Optional[str]=None
    phone:str
    message:list[str]=[]
    friends:list[str]=[]
    is_active:Optional[bool]=None
    profile_image:Optional[str]=None
    name:str
    age:str


class Login(BaseModel):
    email:EmailStr
    password:str


class Products(BaseModel):
    name:str
    price:int
    designer:str 
    category:str
    image:str
    product_id:str
    Company_name:str
    rating:int
    featured:bool=False
    fabric:str
    size:list[str]=[]
    loction:str



class Self_measurement(BaseModel):
    chest:int
    waist:int
    hips:int
    height:int
    weight:int
    burst:int
    sholder:int
    neck:int
    user_id:str
    

class Professional_measurement(BaseModel):
    chest:int
    waist:int
    hips:int
    height:int
    weight:int
    burst:int
    sholder:int
    neck:int
    user_id:str

class CartPaymentRequest(BaseModel):
    user_id: str
    product_id: str

class PaymentRequest(BaseModel):
    user_id: str
    product_id: str
    payment_details: dict

class DeliveryRequest(BaseModel):
    user_id: str
    product_id: str
    delivery_details: dict