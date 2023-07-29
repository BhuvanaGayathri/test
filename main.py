from fastapi import FastAPI, File, UploadFile, HTTPException,Form
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from chat import get_completion_from_messages,collect_messages_text,update_menu_context
import os
import shutil
import uuid
import pandas as pd


app = FastAPI()

# Define the path where the logos will be saved on the server
LOGO_DIR = "./static/logos/"  # Update the directory path as needed

# Define the path where temporary files will be stored
TEMP_DIR = "./temp/"  # Update the directory path as needed

# Define the path where restaurant names will be stored
RESTAURANT_DIR = "./restaurants/"  # Update the directory path as needed

# Mount the "static" directory to serve static files (including index.html)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create the "restaurants" directory if it doesn't exist
os.makedirs(RESTAURANT_DIR, exist_ok=True)


class Message(BaseModel):
    content: str

@app.post("/chat")
async def chat(message: Message):
    user_message = message.content
    # user_phone_number = "RECEIVER_PHONE_NUMBER_WITH_COUNTRY_CODE"
    
    response = collect_messages_text(user_message)

    return {"message": response}

@app.post("/upload/logo/")
async def upload_logo(logo: UploadFile = File(...), restaurant_name: str = Form(...)):
    try:
        # Create the "logos" directory if it doesn't exist
        os.makedirs(LOGO_DIR, exist_ok=True)

        # Generate a unique filename for the uploaded logo
        unique_logoname = f"{str(uuid.uuid4())}_{logo.filename}"

        # Save the uploaded image to the "logos" directory with the unique filename
        file_path = os.path.join(LOGO_DIR, unique_logoname)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)

        # Return the logo URL in the response
        logo_url = f"/static/logos/{unique_logoname}"  # Use the correct URL

        # Store the restaurant name in a separate text file
        restaurant_file_path = os.path.join(RESTAURANT_DIR, f"{str(uuid.uuid4())}_restaurant.txt")
        with open(restaurant_file_path, "w") as restaurant_file:
            restaurant_file.write(restaurant_name)

        return {"message": "Logo uploaded successfully.", "logo_url": logo_url, "restaurant_name": restaurant_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/upload/data/")
# async def upload_data(data_file: UploadFile = File(...)):
#     try:
#         # Create the "temp" directory if it doesn't exist
#         os.makedirs(TEMP_DIR, exist_ok=True)

#         # Generate a unique filename for the uploaded logo
#         unique_filename = f"{data_file.filename}"

#         # Create a temporary directory inside "temp" to save the uploaded data file
#         temp_dir = os.path.join(TEMP_DIR,unique_filename)
#         os.makedirs(temp_dir, exist_ok=True)

#         # Save the uploaded data file to the temporary directory with the original filename
#         file_path = os.path.join(temp_dir, data_file.filename)
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(data_file.file, buffer)
            
#         # Read the data from the uploaded file (supports Excel and CSV formats)
#         if data_file.filename.endswith(".csv"):
#             df = pd.read_csv(file_path)
#         elif data_file.filename.endswith((".xls", ".xlsx")):
#             df = pd.read_excel(file_path)
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format. Only CSV, Excel (XLS/XLSX) files are supported.")

#         # Convert the data to a list of dictionaries for sending to the client
#         data_list = df.to_dict(orient="records")

#         menu_file_path = "./menu.csv"  # Path to the menu file in the root directory
#         df.to_csv(menu_file_path, index=False)

#         return {"message": "Data uploaded successfully.", "data": data_list}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload/data/")
async def upload_data(data_file: UploadFile = File(...)):
    try:
        # Create the "temp" directory if it doesn't exist
        os.makedirs(TEMP_DIR, exist_ok=True)

        # Generate a unique filename for the uploaded logo
        unique_filename = f"{data_file.filename}"

        # Create a temporary directory inside "temp" to save the uploaded data file
        temp_dir = os.path.join(TEMP_DIR, unique_filename)
        os.makedirs(temp_dir, exist_ok=True)

        # Save the uploaded data file to the temporary directory with the original filename
        file_path = os.path.join(temp_dir, data_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(data_file.file, buffer)

        # Read the data from the uploaded file (supports Excel and CSV formats)
        if data_file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif data_file.filename.endswith((".xls", ".xlsx")):
            df = pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400,
                                detail="Unsupported file format. Only CSV, Excel (XLS/XLSX) files are supported.")

        # Convert the data to a list of dictionaries for sending to the client
        data_list = df.to_dict(orient="records")

        # Update the menu content in the 'context' variable after CSV upload
        menu_file_path = "./menu.csv"  # Path to the menu file in the root directory
        df.to_csv(menu_file_path, index=False)
        update_menu_context(menu_file_path)

        return {"message": "Data uploaded successfully.", "data": data_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



