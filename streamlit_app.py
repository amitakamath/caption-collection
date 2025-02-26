import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import json
from PIL import Image
import requests
from io import BytesIO
import pandas as pd
import json

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
    image_list = json.load(open('data/chosen_100_train2017_0.json'))
    caption_length = 50

    st.title("Image Captioning App")
    st.write(" ")
    st.write(" ")
    st.markdown("**Input your Prolific ID below:**")
    user_id = st.text_input("Prolific ID")
    if not user_id:
        st.error("Please enter your User ID.")
    st.write(" ")

    st.write(" ")
    st.write(" ")
    st.write("**Below are 10 images. Write a description for each image, following these instructions:**")
    st.write("- Describe all the :blue[important parts] of the scene.")
    st.write("- :red[Do not] start the sentences with \"There is\".")
    st.write("- :red[Do not] describe unimportant details.")
    st.write("- :red[Do not] describe things that might have happened in the future or past.")
    st.write("- :red[Do not] describe what a person might say.")
    st.write("- :red[Do not] give people proper names.")
    st.write("- The sentences should contain at least :blue[{} words].".format(caption_length))
    st.write(" ")
    st.write("Note: The word counter may take a second to refresh as you type; click outside the text area to see the updated count.")
    st.write(" ")
    st.write(" ")
    st.write(" ")
    
    # Load uncaptioned images
    uncaptioned_df, sheet = get_uncaptioned_images()

    # You shouldn't reach here:
    if uncaptioned_df.empty:
        st.success("All images have been captioned! 🎉")
        return

    # Select an image that needs a caption
    image_row = uncaptioned_df.iloc[0]  # Take the first uncaptioned row
    image_ids = [image_row["ImageID{}".format(i)] for i in range(10)]
    captions = []

    for i in range(10):
        st.write("**Image {}:**".format(i+1))
        st.image('data/{}'.format(image_ids[i]), use_container_width=True)
        caption = st.text_area("Caption Image {}".format(i+1))
        st.write("Number of words: ", len(caption.split()))
        if len(caption.split()) < caption_length:
            # st.write(":red[Caption less than {} words!]".format(caption_length))
            st.error("Please enter a caption of at least {} words.".format(caption_length))
        captions.append(caption)

    if st.button("Submit Caption"):
        if user_id and sum([1 for c in captions if c and len(c.split()) >= caption_length]) == 10:
            save_caption_to_sheet(image_ids, user_id, captions, sheet)
            st.success("Captions submitted!")
            st.success("Your success code is **1234**. Copy and paste it in Prolific to complete this task.")
        else:
            st.error("Please enter your User ID and all captions of sufficient length before submitting.")
    

if __name__ == "__main__":
    main()
