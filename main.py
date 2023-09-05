import streamlit as st
import pandas as pd
import requests
import base64

# Function to use the madewithlove htaccess tester API
def test_url_with_htaccess(url, htaccess_content):
    api_url = "https://htaccess.madewithlove.com/api"

    payload = {
        "url": url,
        "htaccess": htaccess_content,
        "serverVariables": {}
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        return response.json()

    except ValueError:  # This will catch JSON decoding errors
        st.warning(f"Invalid response for URL: {url}")
        st.write(response.text)  # Display the actual response for debugging
        return {}



def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


# Streamlit Interface
st.title("URLs & .htaccess Tester")

# Start the form
with st.form(key='files_form'):
    uploaded_csv = st.file_uploader("Upload CSV file with URLs", type=["csv"])
    uploaded_htaccess = st.file_uploader("Upload .htaccess file", type=["htaccess"])

    # Add a submit button for the form
    submit_button = st.form_submit_button(label='Run Test')

if submit_button:
    if uploaded_csv and uploaded_htaccess:
        # Read the uploaded files
        urls_df = pd.read_csv(uploaded_csv)
        htaccess_content = uploaded_htaccess.read().decode()

        with st.expander("Your htaccess File:"):
            st.code(htaccess_content)

        # Create a column to store results
        urls_df['Result URL'] = ""
        urls_df['Status Code'] = ""
        urls_df['Messages'] = ""

        for index, row in urls_df.iterrows():
            result = test_url_with_htaccess(row['url'], htaccess_content)

            # Use the key directly without get() since we're certain it exists, otherwise catch KeyError
            try:
                urls_df.at[index, 'Result URL'] = result['output_url']
                urls_df.at[index, 'Status Code'] = result['output_status_code']

                # Collecting all the messages from the "lines" into one column
                messages = ' | '.join([line['message'] for line in result['lines']])
                urls_df.at[index, 'Messages'] = messages
            except KeyError:
                st.error(f"Unexpected response format for URL: {row['url']}")
                st.write(result)  # Display the actual result for debugging

        # Display results
        st.write(urls_df)
        download_link_text = "Download the results as CSV"
        st.markdown(download_link(urls_df, 'results.csv', download_link_text), unsafe_allow_html=True)

    else:
        st.write("Please upload both CSV and .htaccess files to test.")