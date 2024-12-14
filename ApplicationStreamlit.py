import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import pymysql

# Connect to the MySQL database using PyMySQL
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="RED_BUS_DATA"
)

# Create a cursor object
mycursor = mydb.cursor()

# Create a database if it does not exist
mycursor.execute("USE RED_BUS_DATA")

# Function to fetch data from the database
def fetch_data_from_sql(query, params=None):
    mycursor.execute(query, params)  # Pass parameters for safe query execution
    # Fetch the results
    result = mycursor.fetchall()
    
    # Get the column names
    columns = [desc[0] for desc in mycursor.description]
    
    # Convert the result to a pandas DataFrame
    df = pd.DataFrame(result, columns=columns)
    
    return df

# Set page configuration
st.set_page_config(
    page_title="Redbus",
    page_icon=":oncoming_bus:",
    layout="wide",  # "wide" for full-page layout
    initial_sidebar_state="auto"
)

# Styling for the page
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #F0F2F6;
            color: #333333;
        }
        
        .stApp {
            background-color: #F0F2F6;
        }

        .css-1d391kg {
            padding-top: 2rem;
        }

        h1 {
            color: #3B3B3B;
            font-size: 2.5rem;
            text-align: center;
        }
        
        .stSelectbox select {
            background-color: #F4F4F4;
            border: 1px solid #D1D1D1;
            border-radius: 4px;
            padding: 8px 10px;

        }

        .stDataFrame {
            margin-top: 20px;
            border: 1px solid #D1D1D1;
            border-radius: 8px;
            
            
        }

        .stCheckbox {
            color: #555555;
        }
        
        .sidebar-content {
            background-color: #e81e1e;
            color: white;
            padding-top: 20px;
        }

        .stSidebar .sidebar-content {
            background-color: #fcfafa;
            color: white;
        }
        
        .stSidebar {
            background-color: #fcfafa;
            color: white;
        }

        .stButton button {
            background-color: #007BFF;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 10px 15px;
            border: none;
        }

        .stButton button:hover {
            background-color: #0056b3;
        }
        
    </style>
""", unsafe_allow_html=True)

data = "https://i.pinimg.com/564x/04/6b/38/046b3884bbd9d16ba053a80c95b8f295.jpg"  # bus image link

# Sidebar menu and image
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=['Home', 'Government Buses', 'Route Details', 'Search Bus'],
        icons=['house-door-fill', 'truck-front-fill', 'database', 'search'],
        default_index=0,
        styles={
            "container": {'padding': '10px', 'background-color': '#ed3b3b'},
            "icon": {'color': "#FFFFFF", "font-size": "24px"},
            "nav-link": {'font-size': '18px', 'text-align': 'left', 'margin': '0px', '--hover-color': '#f57878', 'font-weight': 'bold', 'color': 'white'},
            "nav-link-selector": {'background-color': '#ed3b3b', 'font-weight': 'bold'}
        }
    )

    st.sidebar.image(data, use_container_width=True)  # Adjust image width

# Home page content
if selected == "Home":
    st.title(":red[RedBus] - India's No. 1 Online Bus Ticket Booking Site 🚌")
    
    # Query to get data (Modify based on your requirement)
    query2 = "SELECT DISTINCT region FROM redbus_govt_bus"
    
    # Fetch regions
    data2 = fetch_data_from_sql(query2)
    regions = data2['region'].tolist()  # Extract region column as list
    
    # Create a selectbox for selecting a region
    option = st.selectbox('Find All RTC Operator Directories', regions)
    
    # Display the selected region
    st.write('You selected:', option)

    query3 = "SELECT government_bus_name, links FROM redbus_govt_bus WHERE region = %s"
    
    # Fetch the bus names and links based on the selected region
    data3 = fetch_data_from_sql(query3, params=(option,))
    
    # Display the fetched data
    st.dataframe(data3)

elif selected == "Government Buses":
    query4 = "SELECT DISTINCT government_bus_name FROM redbus_govt_bus"

    # Fetch government bus name
    data4 = fetch_data_from_sql(query4)
    government_bus_name_list = data4['government_bus_name'].tolist()  # Extract government bus name column as list

    # Create a selectbox for selecting a region
    option1 = st.selectbox('Government Bus Name', government_bus_name_list)

    # Display the selected Government Bus Name
    st.write('You selected:', option1)

    # Use parameterized queries to avoid SQL injection
    query5 = "SELECT links FROM redbus_govt_bus WHERE government_bus_name = %s"
    
    # Fetch the bus names and links based on the selected region
    data5 = fetch_data_from_sql(query5, params=(option1,))

    # Display the fetched data
    st.write(data5['links'].tolist())

elif selected == "Route Details":
    query7 = "SELECT DISTINCT government_bus_name FROM redbus_route_details"

    # Fetch government bus name
    data7 = fetch_data_from_sql(query7)

    government_bus_name_list = data7['government_bus_name'].tolist()  # Extract government bus name column as list

    # Create a selectbox for selecting a region
    option2 = st.selectbox('Government Bus Name', government_bus_name_list)

    # Display the selected Government Bus Name
    st.write('You selected:', option2)

    # Use parameterized queries to avoid SQL injection
    query8 = "SELECT route_title, bus_fare_starts_from, route_link FROM redbus_route_details WHERE government_bus_name = %s"
    
    # Fetch the bus names and links based on the selected region
    data8 = fetch_data_from_sql(query8, params=(option2,))

    # Display the fetched data
    st.write(data8)

elif selected == "Search Bus":
    H=[]
    query9 = "SELECT DISTINCT route_title FROM redbus_bus_details"
    data9 = fetch_data_from_sql(query9)

    Route_title_list = data9['route_title'].tolist()  # Extract route titles as a list

    # Create a selectbox for selecting a route title
    option3 = st.selectbox('Route Title', Route_title_list)

    # Display the selected route title
    st.write('You selected:', option3)

    # Use parameterized queries to avoid SQL injection
    query10 = f"SELECT route_title, bus_id, route_link, travel_name, coach, start_time, start_bus_stand, duration, end_time, end_bus_stand,date, rating, persons, bus_fare, seats_left, windows FROM redbus_bus_details WHERE route_title = %s"
    
    # Fetch bus details based on the selected route title
    data10 = fetch_data_from_sql(query10, params=(option3,))

    # Initialize a list to store selected rows
    selected_rows = []

    # Add checkboxes for filtering rows
    for index, row in data10.iterrows():
        if st.checkbox(f"bus id {row['bus_id']}: route title {row['route_title']}", key=row['bus_id']):
            selected_rows.append(row)

    # Display the filtered data
    if selected_rows:
        filtered_data = pd.DataFrame(selected_rows)
        st.write(filtered_data)
    else:
        st.write("No buses selected.")
