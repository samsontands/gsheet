import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Set up Google Sheets credentials
@st.cache_resource
def get_gspread_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(credentials)

# Load data from the sheet
@st.cache_data
def load_sheet_data(sheet):
    data = sheet.get_all_values()
    headers = data.pop(0)
    return pd.DataFrame(data, columns=headers)

# Save data back to the sheet
def save_sheet_data(sheet, df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Streamlit app
def main():
    st.title("Google Sheets Editor")

    # Replace this with your actual Google Sheet ID
    SHEET_ID = "your_sheet_id_here"
    
    client = get_gspread_client()
    sheet = client.open_by_key(SHEET_ID).sheet1

    st.write(f"Editing sheet: {sheet.spreadsheet.title}")
    st.write(f"Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")

    df = load_sheet_data(sheet)

    # Display the dataframe
    st.write("Current data:")
    st.dataframe(df)

    # Add new row
    st.subheader("Add new row")
    new_name = st.text_input("Name")
    new_age = st.number_input("Age", min_value=0, max_value=120)
    new_city = st.text_input("City")

    if st.button("Add Row"):
        new_row = pd.DataFrame([[new_name, new_age, new_city]], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)
        save_sheet_data(sheet, df)
        st.success("Row added successfully!")
        st.experimental_rerun()

    # Edit existing rows
    st.subheader("Edit existing rows")
    row_index = st.number_input("Row index to edit", min_value=0, max_value=len(df)-1 if not df.empty else 0)
    if not df.empty:
        col_name = st.selectbox("Column to edit", df.columns)
        new_value = st.text_input("New value")

        if st.button("Update Cell"):
            df.at[row_index, col_name] = new_value
            save_sheet_data(sheet, df)
            st.success("Cell updated successfully!")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
