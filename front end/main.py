# Import modules
import pandas as pd
import streamlit as st
import numpy as np
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import yaml
import authenticator
import requests
import plotly.express as px
from streamlit_option_menu import option_menu


# Load configuration from YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# Authenticate user
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)
name, authentication_status, username = authenticator.login('Login', 'main')


# Establishing routes to login
if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Hi {name}!')
    st.write("Choose the section you want to review:")


    # Get data from API
    res = requests.get(
        "https://hmapi-dot-prefab-poetry-377916.oa.r.appspot.com/api/v1/master").json()
    dataframe = pd.DataFrame(res["result"])


    # Display filters on the sidebar
    st.sidebar.write("FILTERS")

    age_filtered_lst = st.sidebar.slider(
        "Customer Ages",
        0, 100, (20, 45)
    )

    news_lst = dataframe["fashion_news_frequency"].unique().tolist()

    news_filtered_lst = st.sidebar.multiselect(
        label="Customers News Frequency",
        options= news_lst,
        default= news_lst,
        key="fashion_news_frequency"
    )

    members_lst = dataframe["club_member_status"].unique().tolist()

    members_filtered_lst = st.sidebar.multiselect(
        label="Customers Member Status",
        options= members_lst,
        default= members_lst,
        key="club_member_status"
    )

    channel_dict = {"Online": 1, "Store": 2}
    channel_lst = list(channel_dict.keys())

    channel_filtered_lst = st.sidebar.multiselect(
        label="Sales Channel",
        options=channel_lst,
        default=channel_lst,
        key="multiselect_sales_channel"
    )

    sales_channel_ids = [channel_dict[c] for c in channel_filtered_lst]

    department_lst = dataframe["index_group_name"].unique().tolist()

    department_filtered_lst = st.sidebar.multiselect(
        label="Index Group",
        options=department_lst,
        default=department_lst,
        key="multiselect_department"
    )

    dates_lst = sorted(dataframe["t_dat"].unique().tolist())

    date_filtered_lst = st.sidebar.multiselect(
        label="Dates Sales",
        options=dates_lst,
        default=dates_lst,
        key="multiselect_dates"
    )


    # Apply filters to dataframe
    master_df = dataframe[(dataframe["age"] >= age_filtered_lst[0]) &
                    (dataframe["age"] <= age_filtered_lst[1]) &
                    (dataframe["sales_channel_id"].isin(sales_channel_ids)) &
                    (dataframe["index_group_name"].isin(department_filtered_lst)) &
                    (dataframe["fashion_news_frequency"].isin(news_filtered_lst)) &
                    (dataframe["club_member_status"].isin(members_filtered_lst)) &
                    (dataframe["t_dat"].isin(date_filtered_lst))
                    ]


    # Display menu to navigate the dashboard
    menu = option_menu(
        menu_title = None,
        options = ["How to use the dashboard?", "Sales per Article", "Customers", "Calendar Sales", "Department Sales", "Category Sales", "Color Sales"],
        default_index = 0,
        orientation = "vertical"
    )


    # INSTRUCTIONS SECTION
    if menu == "How to use the dashboard?":
        st.image("logo.png")
        st.write("""
        Welcome to our H&M Dashboard. Here you will be able to see your most important commercial kpis,
        in order to improve your business analysis.
        """)
        st.write("""
        Here are some recommendations to take advantage of the dashboard:
        * The left panel is for the filters and the log out. Whatever you filtered here, it will impact all the graphs and kpis of the different sections.
        * There are 6 different sections. In each of these sections, you will be able to see different charts and kpis according to that topic and the selected filters.
        * Finally, this is the first draft of the web application, so we are eager to here your suggestions. Please send us your recommendations to improve the webpage to: joseluis.zaballa@student.ie.edu 
        """)


    # FIRST SECTION
    if menu == "Sales per Article":
        # Define function to calculate KPI
        def calculate_sales(article_id):
            # Filter the master_df by the article_id
            article_df = master_df[master_df["article_id"] == article_id]
            # Calculate the total sales of the article
            total_sales = article_df["price"].sum()
            return total_sales

        # Streamlit app
        st.write("Introduce an article ID to know the specific dolar sales amount of this article. For example, the ID: 663713001 (Remember the selected filters affects this result).")

        # Sidebar with input field for article_id
        article_id = st.number_input("Enter article ID:", min_value=0, max_value=999999999, value=0, step=1)

        # Calculate and display the KPI
        total_sales = round (calculate_sales(article_id), 2)
        st.write(f"Total sales: ${total_sales}") 


    # SECOND SECTION
    if menu == "Customers":
        st.write("""
            In this section you will be able to find a chart that shows the number of customers, per age, 
            that bought merchandise in the selected filters. Then you will find 3 kpis:
            * Different Customers
            * Average age
            * Percentage of online customers, overall customers
            """)
        
        fig2 = px.bar(master_df.groupby(["age"])["customer_id"].count(),
            x=master_df.groupby(["age"])["customer_id"].count().index,
            y=master_df.groupby(["age"])["customer_id"].count().values,
            color_discrete_sequence=['red'])
        
        st.plotly_chart(fig2)

        num_customers = len(master_df["customer_id"])
        avg_age = np.mean(master_df["age"])
        online_customers = (len(master_df[master_df['sales_channel_id'].between(
            0.9, 1.1, inclusive=False)]) / len(master_df['sales_channel_id']))*100
        num_genders = master_df["club_member_status"].nunique()

        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            label="Number of different customers",
            value=num_customers,
        )

        kpi2.metric(
            label="Average age",
            value=round(avg_age, 2),
        )

        kpi3.metric(
            label="Percentage of Online Customers",
            value=round(online_customers, 2),
        )

        st.write("")


    # THIRD SECTION
    if menu == "Calendar Sales":
        st.write("""
            In this section you will be able to see the numbers of dolar sales per day for the selected filters.
            Then, you will find 2 kpis, one for the total sales, and one for the average sales per day of the selected range,
            with a small metric which indicated if that average sales is reaching the goal of $20 per day.
            """)
        
        fig3 = px.line(master_df.groupby(["t_dat"])["price"].sum(),
            x=master_df.groupby(["t_dat"])["price"].sum().index,
            y=master_df.groupby(["t_dat"])["price"].sum().values,
            color_discrete_sequence=['red'])

        st.plotly_chart(fig3)

        sales = np.sum(master_df["price"])
        days = master_df["t_dat"].nunique()
        avg_sales = sales / days

        kpi1, kpi2 = st.columns(2)

        kpi1.metric(
            label="Sales",
            value=round(sales, 2),
        )

        kpi2.metric(
            label="Average Sales per Day",
            value=round(avg_sales, 2),
            delta=round(avg_sales, 2)-20, #the -20 corresponds to the difference VS the goal (the hypothtical business goal is to have an average sales per day of 20)
        )

        st.write("")


    # FOURTH SECTION
    if menu == "Department Sales":
        st.write("""
            In this section you can see a graph with the dolar sales per department for the selected filters. 
            As well, you can see the kpi of the average sales of all deprtaments.
            """)

        fig4 = px.pie(master_df, values='price', names='index_name')
        st.plotly_chart(fig4)

        sales_dep = np.sum(master_df["price"])
        dep = master_df["index_name"].nunique()
        avg_dep_sales = round(sales_dep / dep, 2)

        kpi1 = st.container()
        with kpi1:
            st.metric(label="Average Department Sales", value=avg_dep_sales)

    # FIFTH SECTION
    if menu == "Category Sales":
        st.write("""
            In this section you can see a graph with the dolar sales per department for the selected filters. 
            As well, you can see the kpi of the average sales of all categories.
            """)

        fig5 = px.pie(master_df, values='price', names='garment_group_name')
        st.plotly_chart(fig5)

        sales_cat = np.sum(master_df["price"])
        category = master_df["garment_group_name"].nunique()
        avg_cat_sales = round(sales_cat / category, 2)

        kpi1 = st.container()
        with kpi1:
            st.metric(label="Average Category Sales", value=avg_cat_sales)

        st.write("")


    # SIXTH SECTION
    if menu == "Color Sales":
        st.write("""
            In this section you can see a graph with the dolar sales per department for the selected filters. 
            As well, you can see the kpi of the average sales of all colors.
            """)  

        fig6 = px.bar(
            master_df.groupby(["perceived_colour_master_name"])["price"].sum().reset_index().sort_values("price", ascending=True),
            x="price",
            y="perceived_colour_master_name",
            orientation="h",
            color_discrete_sequence=['red']
        )
        st.plotly_chart(fig6)

        sales_color = np.sum(master_df["price"])
        colors = master_df["perceived_colour_master_name"].nunique()
        avg_color_sales = round(sales_color / colors, 2)

        kpi1 = st.container()
        with kpi1:
            st.metric(label="Average Color Sales", value=avg_color_sales)

        st.write("")


elif authentication_status == False:
    st.error('Username/password is incorrect')
