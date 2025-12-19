# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched
from snowflake.snowpark.context import get_active_session

# App title
st.title("Smoothie Orders 🥤")
st.write("Orders that need to be filled.")

session = get_active_session()

# Get only unfilled orders
orders_df = (
    session
    .table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
)

if orders_df.count() > 0:

    # Convert to pandas once
    orders_pd = orders_df.collect()

    st.dataframe(orders_pd, use_container_width=True)

    # Editable table (ORDER_FILLED as checkbox)
    edited_df = st.data_editor(
        orders_pd,
        use_container_width=True,
        num_rows="fixed"
    )

    if st.button("Submit"):
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(edited_df)

        try:
            og_dataset.merge(
                edited_dataset,
                og_dataset["ORDER_UID"] == edited_dataset["ORDER_UID"],
                [
                    when_matched().update({
                        "ORDER_FILLED": edited_dataset["ORDER_FILLED"]
                    })
                ]
            )
            st.success("Order(s) Updated! 👍")

        except Exception as e:
            st.error("Something went wrong ❌")
            st.write(e)

else:
    st.success("There are no pending orders right now 👍")
