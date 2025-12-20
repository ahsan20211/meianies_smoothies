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
cnx = st.connection("snowflake")
session = cnx.session()

# ------------------------------
# Fetch fruit options from Snowflake
# ------------------------------
my_dataframe = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_df = my_dataframe.to_pandas()

# Optional: show dataframe for debugging (like the tutorial)
# st.dataframe(fruit_df, use_container_width=True)
# st.stop()

# ------------------------------
# User inputs
# ------------------------------
name_on_order = st.text_input("Name on smoothie:")
st.write("The Name on Your smoothie is:", name_on_order)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# ------------------------------
# Display nutrition info per fruit
# ------------------------------
if ingredients_list:
    for fruit_chosen in ingredients_list:

        # Get SEARCH_ON value for selected fruit
        search_on_value = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].values[0]

        st.subheader(fruit_chosen + " Nutrition Information")

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on_value
        )

        if smoothiefroot_response.status_code == 200:
            st.dataframe(
                smoothiefroot_response.json(),
                use_container_width=True
            )
        else:
            st.error(f"Failed to fetch data for {fruit_chosen}")

# ------------------------------
# Submit order to Snowflake
# ------------------------------
if ingredients_list and name_on_order:
    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = (
        f"INSERT INTO smoothies.public.orders (ingredients, name_on_order) "
        f"VALUES ('{ingredients_string}', '{name_on_order}')"
    )

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")

# ------------------------------
# Example API call (demo section)
# ------------------------------
st.write("🍉 Example Fruit Info from API:")

response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")

if response.status_code == 200:
    sf_df = pd.DataFrame(response.json())
    st.dataframe(sf_df, use_container_width=True)
else:
    st.error("Failed to fetch data from SmoothieFroot API")
