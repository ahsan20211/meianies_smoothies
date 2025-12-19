import streamlit as st
from snowflake.snowpark.functions import col

# Streamlit titles
st.title('My parents new healthy diner')
st.write("Customize Your Smoothie 🥤")
st.write("Which fruits you want to customize smoothie!")

# Snowflake connection
cnx = st.connection('snowflake')  # Make sure you already set your Snowflake connection in Streamlit Cloud
session = cnx.session()            # Create the session first

# Fetch data from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The Name on Your smoothie is", name_on_order)

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.select(col("FRUIT_NAME")).to_pandas()["FRUIT_NAME"].tolist(),
    max_selections=5
)

# Insert order into Snowflake
if ingredients_list and name_on_order:
    ingredients_string = ' '.join(ingredients_list)

    my_insert_stmt = (
        f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

# Example API call
import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response.text)
