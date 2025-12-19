import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# ------------------------------
# Streamlit titles
# ------------------------------
st.title("My parents new healthy diner")
st.write("Customize Your Smoothie 🥤")
st.write("Which fruits you want to customize smoothie!")

# ------------------------------
# Snowflake connection
# ------------------------------
cnx = st.connection('snowflake')  # Make sure your connection is set in Streamlit Cloud
session = cnx.session()            # Create Snowflake session

# ------------------------------
# Fetch fruit options from Snowflake
# ------------------------------
my_dataframe = session.table("smoothies.public.fruit_options")
fruit_options = my_dataframe.select(col("FRUIT_NAME")).to_pandas()["FRUIT_NAME"].tolist()

# ------------------------------
# User inputs
# ------------------------------
name_on_order = st.text_input("Name on smoothie:")
st.write("The Name on Your smoothie is:", name_on_order)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen +  'Mutrition Information')
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/"+fruit_chosen
        )
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )


# ------------------------------
# Submit order to Snowflake
# ------------------------------
if ingredients_list and name_on_order:
    ingredients_string = ', '.join(ingredients_list)

    my_insert_stmt = (
        f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# ------------------------------
# Display fruit info from API
# ------------------------------
st.write("🍉 Example Fruit Info from API:")

response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

if response.status_code == 200:
    sf_df = pd.DataFrame(response.json())
    st.dataframe(sf_df, use_container_width=True)
else:
    st.error("Failed to fetch data from SmoothieFroot API")



