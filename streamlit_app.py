import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import json
from PIL import Image
import requests
from io import BytesIO
import pandas as pd

# Function to connect to Google Sheets
def get_gsheet():
    credentials_data = st.secrets["google_sheets"]
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(credentials_data, scopes=scope)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(st.secrets["google_sheets"]["spreadsheet"]).sheet1
    return sheet

# Function to load images that need captions
def get_uncaptioned_images():
    sheet = get_gsheet()
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    # Filter for rows where 'Caption' is empty
    uncaptioned_df = df[df["Caption0"] == ""]
    return uncaptioned_df, sheet

# Function to update Google Sheet with user input
def save_caption_to_sheet_old(image_id, user_id, caption, sheet):
    cell = sheet.find(str(image_id))  # Find the row with this ImageID
    if cell:
        row_number = cell.row
        sheet.update_cell(row_number, 2, user_id)  # Update UserID column
        sheet.update_cell(row_number, 3, caption)  # Update Caption column

def save_caption_to_sheet(image_ids, user_id, captions, sheet):
    cell = sheet.find(str(image_ids[0]))  # Find the row with this ImageID
    if cell:
        row_number = cell.row
        sheet.update_cell(row_number, 11, user_id)  # Update UserID column
        for i, c in enumerate(captions):
            sheet.update_cell(row_number, 12+i, c)


# def save_caption_to_sheet(pid, image_id, caption):
#     sheet = get_gsheet()
#     sheet.append_row([pid, image_id, caption])  # Append caption to the sheet

def main():
    image_list = ["https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Felis_silvestris_silvestris_Luc_Viatour.jpg/1280px-Felis_silvestris_silvestris_Luc_Viatour.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/1/1d/Katzepasstauf_%282009_photo%3B_cropped_2022%29_%28cropped%29.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Chin_posing.jpg/1920px-Chin_posing.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/d/d5/Retriever_in_water.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Black_Labrador_Retriever_-_Male_IMG_3323.jpg/2560px-Black_Labrador_Retriever_-_Male_IMG_3323.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Felis_silvestris_silvestris_Luc_Viatour.jpg/1280px-Felis_silvestris_silvestris_Luc_Viatour.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/1/1d/Katzepasstauf_%282009_photo%3B_cropped_2022%29_%28cropped%29.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Chin_posing.jpg/1920px-Chin_posing.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/d/d5/Retriever_in_water.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Black_Labrador_Retriever_-_Male_IMG_3323.jpg/2560px-Black_Labrador_Retriever_-_Male_IMG_3323.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Felis_silvestris_silvestris_Luc_Viatour.jpg/1280px-Felis_silvestris_silvestris_Luc_Viatour.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/1/1d/Katzepasstauf_%282009_photo%3B_cropped_2022%29_%28cropped%29.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Chin_posing.jpg/1920px-Chin_posing.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/d/d5/Retriever_in_water.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Black_Labrador_Retriever_-_Male_IMG_3323.jpg/2560px-Black_Labrador_Retriever_-_Male_IMG_3323.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/4/4d/Cat_November_2010-1a.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Felis_silvestris_silvestris_Luc_Viatour.jpg/1280px-Felis_silvestris_silvestris_Luc_Viatour.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/1/1d/Katzepasstauf_%282009_photo%3B_cropped_2022%29_%28cropped%29.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Chin_posing.jpg/1920px-Chin_posing.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/d/d5/Retriever_in_water.jpg",
                  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Black_Labrador_Retriever_-_Male_IMG_3323.jpg/2560px-Black_Labrador_Retriever_-_Male_IMG_3323.jpg",
                  ]

    st.title("Image Captioning App")
    st.write("Input your Prolific ID below:")
    user_id = st.text_input("Prolific ID")

    st.write(" ")
    st.write("INSTRUCTIONS")
    st.write("INSTRUCTIONS")
    st.write("INSTRUCTIONS")
    st.write(" ")
    
    # Initialize session state for tracking user progress
    # if "caption_count" not in st.session_state:
    #     st.session_state.caption_count = 0

    # Stop users after 2 captions
    # if st.session_state.caption_count >= 2:
    #     st.success("You've reached your limit of 2 captions. Thank you for your contributions! 🎉")
    #     return
    
    # Load uncaptioned images
    uncaptioned_df, sheet = get_uncaptioned_images()

    if uncaptioned_df.empty:
        st.success("All images have been captioned! 🎉")
        return

    # Select an image that needs a caption
    image_row = uncaptioned_df.iloc[0]  # Take the first uncaptioned image
    image_ids = [image_row["ImageID{}".format(i)] for i in range(10)]
    # image_id = image_row["ImageID"]
    captions = []

    for i in range(10):
        st.write("Image {}:".format(i))
        st.image(image_list[image_ids[i]], use_container_width=True)
        caption = st.text_area("Caption Image {}".format(i))
        captions.append(caption)

    if st.button("Submit Caption"):
        if user_id and sum([1 for c in captions if c])==10:
            save_caption_to_sheet(image_ids, user_id, captions, sheet)
            st.success("Caption submitted and saved to Google Sheets!")
        else:
            st.warning("Please enter your User ID and all captions before submitting.")


    # Caption input
    # caption = st.text_area("Write your caption:")

    # if st.button("Submit Caption"):
    #     if user_id and caption:
    #         save_caption_to_sheet(image_id, user_id, caption, sheet)
    #         st.success("Caption submitted and saved to Google Sheets!")

    #         # Increment session count
    #         st.session_state.caption_count += 1
            
    #         st.rerun()  # Refresh to show the next image
    #     else:
    #         st.warning("Please enter your User ID and a caption before submitting.")

    # st.write("Caption the images below:")
    # st.write("Image 1:")
    # uploaded_file = Image.open(BytesIO(requests.get("https://media.4-paws.org/9/c/9/7/9c97c38666efa11b79d94619cc1db56e8c43d430/Molly_006-2829x1886-2726x1886-1920x1328.jpg").content))
    # st.image(uploaded_file, use_container_width=True)
    # caption1 = st.text_input("Write your caption for Image 1")

    # st.write("Image 2:")
    # uploaded_file = Image.open(BytesIO(requests.get("https://i.natgeofe.com/n/4f5aaece-3300-41a4-b2a8-ed2708a0a27c/domestic-dog_thumb_4x3.jpg").content))
    # st.image(uploaded_file, use_container_width=True)
    # caption2 = st.text_input("Write your caption for Image 2")

    # if st.button("Submit Caption"):
    #     if prolific_id and caption1 and caption2:
    #         save_caption_to_sheet(prolific_id, 1, caption1)
    #         save_caption_to_sheet(prolific_id, 2, caption2)
    #         st.success("Captions submitted and saved to Google Sheets!")
    #     else:
    #         st.warning("Please write your ID and all captions before submitting.")
    

if __name__ == "__main__":
    main()
