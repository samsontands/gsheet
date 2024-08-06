import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from google.oauth2.service_account import Credentials


def setup_credentials():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
    )
    return gspread.authorize(credentials)

# Create a new sheet if it doesn't exist
def create_sheet_if_not_exists(client, sheet_name):
    try:
        sheet = client.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sheet = client.create(sheet_name)
        worksheet = sheet.sheet1
        worksheet.append_row(['Name', 'Age', 'City'])  # Add headers
    return sheet

# Load data from the sheet
def load_sheet_data(sheet):
    worksheet = sheet.sheet1
    data = worksheet.get_all_values()
    headers = data.pop(0)
    return pd.DataFrame(data, columns=headers)

# Save data back to the sheet
def save_sheet_data(sheet, df):
    worksheet = sheet.sheet1
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# Streamlit app
def main():
    st.title("Google Sheets Editor")

    client = setup_credentials()
    sheet_name = "StreamlitPOC"
    sheet = create_sheet_if_not_exists(client, sheet_name)

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

    # Edit existing rows
    st.subheader("Edit existing rows")
    row_index = st.number_input("Row index to edit", min_value=0, max_value=len(df)-1)
    col_name = st.selectbox("Column to edit", df.columns)
    new_value = st.text_input("New value")

    if st.button("Update Cell"):
        df.at[row_index, col_name] = new_value
        save_sheet_data(sheet, df)
        st.success("Cell updated successfully!")

    # Refresh data
    if st.button("Refresh Data"):
        df = load_sheet_data(sheet)
        st.dataframe(df)

if __name__ == "__main__":
    main()
