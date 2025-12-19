# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
from snowflake.snowpark.context import get_active_session
st.title('My parents new healthy diner')

# Write directly to the app
st.title("Customize Your Smoothie 🥤")
st.write("Which fruits you want to customize smoothie!")

# Name input
name_on_order = st.text_input("Name on smoothie:")
st.write("The Name on Your smoothie is", name_on_order)

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options")

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe.select(col("FRUIT_NAME")).to_pandas()["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list and name_on_order:

    ingredients_string = ''
    for each_fruit in ingredients_list:
        ingredients_string += each_fruit + ' '

    my_insert_stmt = (
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        "VALUES ('" + ingredients_string + "', '" + name_on_order + "')"
    )

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st.text(smoothiefroot_response)

