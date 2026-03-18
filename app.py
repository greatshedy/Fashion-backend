from fastapi import FastAPI,HTTPException,status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import base64
from fastapi.responses import JSONResponse
from astrapy import DataAPIClient
from apscheduler.schedulers.background import BackgroundScheduler
from model import User,User2,User3,Login,Products,Self_measurement,Professional_measurement,CartPaymentRequest,PaymentRequest,DeliveryRequest
from utility import hashedpassword,verifyhash,generate_otp
from index import send_email

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Api_key = os.getenv("FASHION_DB_KEY")
client = DataAPIClient(Api_key)

db = client.get_database_by_api_endpoint(
  "https://5eb65b8d-272c-4691-a2b3-3c0bc4d3905a-us-east-2.apps.astra.datastax.com"
)

user_collection = db.create_collection("users")
designer_collection = db.create_collection("designers")
payment_collection = db.create_collection("payment")

try:
    product_collection = db.create_collection("products", definition={"indexing": {"deny": ["image"]}})
except Exception as e:
    db.drop_collection("products")
    product_collection = db.create_collection("products", definition={"indexing": {"deny": ["image"]}})

Self_measurement_collection = db.create_collection("self_measurement")
professional_measurement_collection = db.create_collection("professional_measurement")
print(f"Connected to Astra DB: {db.list_collection_names()}")

def ping_database():
    try:
        collections = db.list_collection_names()
        print(f"Database ping successful: {len(collections)} collections found")
    except Exception as e:
        print(f"Database ping failed: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(ping_database, 'interval', minutes=5)
scheduler.start()

@app.get("/")
def Home():
  return JSONResponse(content={"message":"Welcome To Fashion Api"})




#create Users endpoint
@app.post("/create_user")
def create_user(user: User):
  data= dict(user)
  print(data)
  data["password"] = hashedpassword(data["password"])
  userid = user_collection.insert_one(data).inserted_id
  
  return JSONResponse(content={"message":"user created sucessfully","user_id":userid},status_code=status.HTTP_201_CREATED)



#create designer endpoint
@app.post("/create_designer")
def create_designer(user: User2):
  data = dict(user)
  print(data)
  data["password"] = hashedpassword(data["password"])
  designerid = designer_collection.find_one({"email":data["email"]})
  # send_verification_email(data["email"], "Verify  Email" )

  if designerid:
    return JSONResponse(content={"message":"designer already exists"},status_code=status.HTTP_400_BAD_REQUEST)
  else:
    designerid = designer_collection.insert_one(data).inserted_id
    return JSONResponse(content={"message":"Designer created sucessfully",designerid:"designerid"},status_code=status.HTTP_201_CREATED)
  
  
#login users endpoint
@app.post("/login_user")
def login_user(login_user: Login):
  data = dict(login_user)
  print(data)
  user = user_collection.find_one({"email":data["email"]})
  if user:
    if verifyhash(user["password"],data["password"]):
      otp = generate_otp()
      user_collection.update_one({"email":data["email"]},{"$set":{"otp":otp}})
      html_content = f"<h2>Your Login OTP</h2><p>Your OTP is: <strong>{otp}</strong></p>"
      send_email(data["email"], "Verify Email", html_content)
      return JSONResponse(content={"message":"user verified sucessfully"},status_code=status.HTTP_200_OK)
    else:
      return JSONResponse(content={"message":"invalid password"},status_code=status.HTTP_401_UNAUTHORIZED)
  else:
    return JSONResponse(content={"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)



#login designer endpoint
@app.post("/login_designer")
def login_designer(login_designer:Login):
  data = dict(login_designer)
  print(data)
  designer = designer_collection.find_one({"email":data["email"]})
  if designer:
    if verifyhash(designer["password"],data["password"]):
      otp = generate_otp()
      designer_collection.update_one({"email":data["email"]}, {"$set":{"otp":otp}})
      html_content = f"<h2>Your Login OTP</h2><p>Your OTP is: <strong>{otp}</strong></p>"
      send_email(data["email"], "Verify Email", html_content)
      return JSONResponse(content={"message":"designer verified sucessfully"},status_code=status.HTTP_200_OK)
    else:
      return JSONResponse(content={"message":"invalid password"},status_code=status.HTTP_401_UNAUTHORIZED)
  else:
    return JSONResponse(content={"message":"designer not found"},status_code=status.HTTP_404_NOT_FOUND)



#verify users endpoint
@app.post("/verify_user")
def verify_user(user: dict):
  print(user)
  main_user = user_collection.find_one({"_id":user["_id"]})
  if main_user:
    if main_user["otp"] == user["otp"]:
      user_collection.update_one({"_id":user["_id"]},{"$set":{"is_active":True}})
      return JSONResponse(content={"message":"user verified sucessfully"},status_code=status.HTTP_200_OK)
    else:
      return JSONResponse(content={"message":"invalid otp"},status_code=status.HTTP_401_UNAUTHORIZED)
  else:
    return JSONResponse(content={"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


#verify designer endpoint
@app.post("/verify_designer")
def verify_designer(user: dict):
  print(user)
  main_designer = designer_collection.find_one({"_id":user["_id"]})
  if main_designer:
    if main_designer["otp"] == user["otp"]:
      designer_collection.update_one({"_id":user["_id"]},{"$set":{"is_active":True}})
      return JSONResponse(content={"message":"designer verified sucessfully"},status_code=status.HTTP_200_OK)
    else:
      return JSONResponse(content={"message":"invalid otp"},status_code=status.HTTP_401_UNAUTHORIZED)
  else:
    return JSONResponse(content={"message":"designer not found"},status_code=status.HTTP_404_NOT_FOUND)

#verify token endpoint
@app.post("/verify_token")
def verify_token(token:str):
  data = user_collection.find_one({"_id":token})
  if data:
    user_collection.update_one({"_id":token},{"$set":{"is_active":True}})
    return JSONResponse(content={"message":"token verified sucessfully"},status_code=status.HTTP_200_OK)
  else:
    return JSONResponse(content={"message":"token not found"},status_code=status.HTTP_404_NOT_FOUND)

 #verify designer endpoint
@app.post("/verify_token_designer")
def verify_token_designer(token:str):
  data = designer_collection.find_one({"_id":token})  
  if data:
    designer_collection.update_one({"_id":token},{"$set":{"is_active":True}})
    return JSONResponse(content={"message":"token verified sucessfully"},status_code=status.HTTP_200_OK)
  else:
    return JSONResponse(content={"message":"token not found"},status_code=status.HTTP_404_NOT_FOUND)


#search Endpoint
@app.post("/search")
def search(name:str,email:str):
  user = user_collection.find_one({"name":name, "email":email})
  if user:
    return JSONResponse(content={"message":"user found"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse(content={"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)

#active webusers
@app.post("/active_users")
def active_users(id:int):
  user = user_collection.find_one({"_id":id})
  if user:
    user_collection.update_one({"_id":id}, {"$set":{"is_active":True}})
    return JSONResponse(content={"message":"user Actiavted Sucessfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse(content={"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


#products endpoint
@app.post("/create_products")
def create_products(
    name: str = Form(...),
    price: int = Form(...),
    category: str = Form(...),
    product_id: str = Form(...),
    Company_name: str = Form(...),
    image: UploadFile = File(...),
    location:str=Form(...),
    fabric:str=Form(...),
    size:list[str]=Form(...),
    featured:bool=Form(...),
    rating:int=Form(...),
    designer:str=Form(...),
):
    try:
        # Read the image file and convert it to a base64 string
        image_content = image.file.read()
        base64_encoded = base64.b64encode(image_content).decode('utf-8')
        
        # Determine the content type (e.g., image/jpeg or image/png)
        content_type = image.content_type if image.content_type else "image/jpeg"
        
        # Create the data URL for the image
        image_data_url = f"data:{content_type};base64,{base64_encoded}"

        # Create the product dictionary
        data = {
            "name": name,
            "price": price,
            "category": category,
            "product_id": product_id,
            "Company_name": Company_name,
            "image": image_data_url, # Storing the base64 URL in the DB
            "location":location,
            "fabric":fabric,
            "size":size,
            "featured":featured,
            "rating":rating,
            "designer":designer,
        }
        
        print(data)
        inserted_id = product_collection.insert_one(data).inserted_id
        
        return JSONResponse(
            content={
                "message": "Product and image uploaded successfully", 
                "id": str(inserted_id),
                "image_data_url": image_data_url
            }, 
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        print(f"Error encoding image: {e}")
        return JSONResponse(
            content={"message": "Failed to process image"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@app.post("/user_self_measurement")
def user_self_measurement(measurement: Self_measurement):
    # Use model_dump() instead of the deprecated dict()
    data = measurement.model_dump()
    user_id = data["user_id"]

    # In AstraDB/MongoDB, _id is usually a string matching the inserted ID
    user = user_collection.find_one({"_id": user_id})
    if not user:
        return JSONResponse({"message": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)

    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"self_measurement": data}}
    )

    return JSONResponse({"message": "Self measurement added successfully"}, status_code=201)
@app.post("/professional_measurement")
def professional_measurement(measurement: Professional_measurement):

    # Use model_dump() instead of the deprecated dict()
    data = measurement.model_dump()
    user_id = data["user_id"]

    user = user_collection.find_one({"_id": user_id})

    if not user:
        return JSONResponse(
            content={"message": "User not found"},
            status_code=status.HTTP_404_NOT_FOUND
        )

    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"professional_measurement": data}}
    )

    return JSONResponse(
        content={"message": "This measurement was taken by a professional tailor"},
        status_code=status.HTTP_201_CREATED
    )

@app.put("/edit_user_profile/{user_id}")
def edit_user_profile(user_id: str, user: User):

    data = user.model_dump()

    existing_user = user_collection.find_one({"_id": user_id})
    if not existing_user:
        return JSONResponse({"message": "User not found"}, status_code=status.HTTP_404_NOT_FOUND)

    # NEVER allow updating _id
    if "_id" in data:
        del data["_id"]

    user_collection.update_one(
        {"_id": user_id},
        {"$set": data}
    )

    return JSONResponse(
        {"message": "User profile updated successfully"},
        status_code=status.HTTP_200_OK
    )


@app.post("/edit_designer_profile/{user_id}")
def edit_designer_proflile(user_id: str, user: User2):
  data = user.model_dump()
  print(data)
  existing_user = designer_collection.find_one({"_id": user_id})
  if existing_user:
    if "_id" in data:
        del data["_id"]
    designer_collection.update_one({"_id": user_id}, {"$set": data})
    return JSONResponse({"message":"user profile edited sucessfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user profile not found"},status_code=status.HTTP_404_NOT_FOUND)

@app.post("/add_to_cart")
def add_to_cart(user_id: str, product_id: str):
  user = user_collection.find_one({"_id": user_id})
  if user:
    user_collection.update_one({"_id": user_id},{"$set":{"cart": product_id}})
    return JSONResponse({"message":"product added to cart"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


@app.post("/payment")
def payment(request: PaymentRequest):
  user = user_collection.find_one({"_id": request.user_id})
  if user:
    # Save the payment details in the user's document
    user_collection.update_one(
        {"_id": request.user_id},
        {
            "$set": {"last_payment": request.payment_details},
            "$push": {"payments": request.model_dump()}
        }
    )
    return JSONResponse({"message":"payment done sucessfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)
    
@app.post("/delivery")
def delivery(request:DeliveryRequest):
  user = user_collection.find_one({"_id": request.user_id})
  if user:
    user_collection.update_one({"_id": request.user_id},{"$set":{"delivery": request.delivery_details}})
    return JSONResponse({"message":"delivery done sucessfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


@app.post("/logout_user/{user_id}")
def logout_user(user_id: str):
  user = user_collection.find_one({"_id": user_id})
  if user:
    user_collection.update_one({"_id": user_id}, {"$set": {"is_active": False}})
    return JSONResponse({"message": "user logged out successfully"}, status_code=status.HTTP_200_OK)
  else:
    return JSONResponse({"message": "user not found"}, status_code=status.HTTP_404_NOT_FOUND)


@app.post("/account_deactivation/{user_id}")
def account_deactivation(user_id: str):
  user = user_collection.find_one({"_id": user_id})
  
  if user:
    # Deactivate the user and mark the account as deactivated in a single update
    user_collection.update_one(
        {"_id": user_id},
        {"$set": {"is_active": False, "account_deactivated": True}}
    )
    return JSONResponse(
        content={"message": "user account deactivated successfully", "user_id": user_id},
        status_code=status.HTTP_200_OK
    )
  else:
    return JSONResponse(
        content={"message": "user not found"},
        status_code=status.HTTP_404_NOT_FOUND
    )


@app.post("/shopping_info/{user_id}")
def shopping_info(user_id:str, product_id:str):
  user = user_collection.find_one({"_id":user_id})
  if user:
    user_collection.update_one({"_id":user_id},{"$set":{"shopping_info":product_id}})
    return JSONResponse({"message":"shopping info added successfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)

@app.post("/edit_user_password/{user_id}")
def edit_user_password(user_id:str, password:str):
  user = user_collection.find_one({"_id":user_id})
  if user:
    hashed_pw = hashedpassword(password)
    user_collection.update_one({"_id":user_id},{"$set":{"password":hashed_pw}})
    return JSONResponse({"message":"password changed successfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)

@app.post("/edit_designer_password/{user_id}")
def edit_designer_password(user_id:str, password:str):
  user = designer_collection.find_one({"_id":user_id})
  if user:
    hashed_pw = hashedpassword(password)
    designer_collection.update_one({"_id":user_id},{"$set":{"password":hashed_pw}})
    return JSONResponse({"message":"password changed successfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


@app.post("/ratings/{user_id}")
def ratings(user_id:str, product_id:str, rating:int, review:str):
  user = user_collection.find_one({"_id":user_id})
  if user:
    user_collection.update_one({"_id":user_id},{"$set":{"rating":rating,"review":review}})
    return JSONResponse({"message":"rating added successfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)


@app.post("/location/{user_id}")
def location(user_id:str, location:str):
  user = user_collection.find_one({"_id":user_id})
  if user:
    user_collection.update_one({"_id":user_id},{"$set":{"location":location}})
    return JSONResponse({"message":"location added successfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"user not found"},status_code=status.HTTP_404_NOT_FOUND)

@app.get("/active_designers")
def active_designers():
  # Count the number of designers where is_active is True
  count = designer_collection.count_documents({"is_active": True})
  
  return JSONResponse(
      {"message": "success", "total_active_designers": count},
      status_code=status.HTTP_200_OK
  )


@app.get("/active_users")
def active_users():
  count = user_collection.count_documents({"is_active":True})
  return JSONResponse({"message":"success","total_active_users":count},status_code=status.HTTP_200_OK)

@app.post("/add_to_whislist{user_id}")
async def add_to_whislist(user_id:str,product_id:str):
  user = user_collection.find_one({"_id":user_id})
  if user:
    user_collection.update_one({"_id":user_id},{"$set":{"whislist":product_id}})
    return JSONResponse({"message":"product added to whislist succesfully"},status_code=status.HTTP_201_CREATED)
  else:
    return JSONResponse({"message":"product not found"},status_code=status.HTTP_404_NOT_FOUND)
