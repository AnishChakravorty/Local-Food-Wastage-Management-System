#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px


# In[5]:


import warnings
warnings.filterwarnings("ignore")


# In[2]:


# ------------------------------
# DATABASE CONNECTION
# ------------------------------
def create_connection():
    return mysql.connector.connect(
        host="localhost",      # Change if different
        user="root",           # Your MySQL username
        password="root",  # Your MySQL password
        database="food_wastage_db" # Your DB name
    )

conn = create_connection()


# In[3]:


# ------------------------------
# HELPER FUNCTION
# ------------------------------
def run_query(query):
    return pd.read_sql(query, conn)


# In[4]:


# ------------------------------
# STREAMLIT UI
# ------------------------------
st.set_page_config(page_title="Food Wastage Management Dashboard", layout="wide")
st.title("📊 Food Wastage Management Dashboard")

st.markdown("This dashboard shows insights from the **Local Food Wastage Management System** using MySQL data.")


# In[6]:


# ==============================
# 1. Providers & Receivers by City
# ==============================
st.subheader("1️⃣ Providers & Receivers by City")
query1 = """
SELECT p.City, 
       COUNT(DISTINCT p.Provider_ID) AS Total_Providers, 
       COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM providers_data p
LEFT JOIN receivers_data r ON p.City = r.City
GROUP BY p.City;
"""
df1 = run_query(query1)
st.dataframe(df1)

fig1 = px.bar(df1, x="City", y=["Total_Providers", "Total_Receivers"], barmode="group", title="Providers vs Receivers by City")
st.plotly_chart(fig1, use_container_width=True)


# In[7]:


# ==============================
# 2. Provider Type Contribution
# ==============================
st.subheader("2️⃣ Provider Type Contribution")
query2 = """
SELECT f.Provider_Type, 
       SUM(f.Quantity) AS Total_Quantity
FROM food_listings_data f
GROUP BY f.Provider_Type
ORDER BY Total_Quantity DESC;
"""
df2 = run_query(query2)
st.dataframe(df2)
fig2 = px.pie(df2, names="Provider_Type", values="Total_Quantity", title="Contribution by Provider Type")
st.plotly_chart(fig2, use_container_width=True)


# In[8]:


# ==============================
# 3. Contact Info by City (Filter)
# ==============================
st.subheader("3️⃣ Contact Information of Providers by City")
cities = run_query("SELECT DISTINCT City FROM providers_data")["City"].tolist()
selected_city = st.selectbox("Select City", cities)
query3 = f"""
SELECT p.Name, p.Contact
FROM providers_data p
WHERE p.City = '{selected_city}';
"""
df3 = run_query(query3)
st.dataframe(df3)


# In[9]:


# ==============================
# 4. Receivers Who Claimed Most
# ==============================
st.subheader("4️⃣ Top Receivers by Food Claimed")
query4 = """
SELECT r.Name, 
       SUM(f.Quantity) AS Total_Claimed
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Name
ORDER BY Total_Claimed DESC;
"""
df4 = run_query(query4)
st.dataframe(df4)


# In[10]:


# ==============================
# 5. Total Quantity Available
# ==============================
st.subheader("5️⃣ Total Quantity Available")
query5 = "SELECT SUM(f.Quantity) AS Total_Food_Quantity FROM food_listings_data f;"
df5 = run_query(query5)
st.metric(label="Total Food Quantity", value=int(df5["Total_Food_Quantity"][0]))


# In[11]:


# ==============================
# 6. City with Highest Listings
# ==============================
st.subheader("6️⃣ City with Highest Listings")
query6 = """
SELECT f.Location, 
       COUNT(*) AS Total_Listings
FROM food_listings_data f
GROUP BY f.Location
ORDER BY Total_Listings DESC
LIMIT 1;
"""
df6 = run_query(query6)
st.dataframe(df6)


# In[12]:


# ==============================
# 7. Most Common Food Types
# ==============================
st.subheader("7️⃣ Most Common Food Types")
query7 = """
SELECT f.Food_Type, 
       COUNT(*) AS Count
FROM food_listings_data f
GROUP BY f.Food_Type
ORDER BY Count DESC;
"""
df7 = run_query(query7)
st.dataframe(df7)


# In[13]:


# ==============================
# 8. Claims per Food Item
# ==============================
st.subheader("8️⃣ Claims per Food Item")
query8 = """
SELECT c.Food_ID, 
       COUNT(*) AS Claim_Count
FROM claims_data c
GROUP BY c.Food_ID
ORDER BY Claim_Count DESC;
"""
df8 = run_query(query8)
st.dataframe(df8)


# In[14]:


# ==============================
# 9. Provider with Most Successful Claims
# ==============================
st.subheader("9️⃣ Provider with Most Successful Claims")
query9 = """
SELECT p.Name, 
       COUNT(*) AS Successful_Claims
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Successful_Claims DESC
LIMIT 1;
"""
df9 = run_query(query9)
st.dataframe(df9)


# In[15]:


# ==============================
# 10. Percentage of Claims by Status
# ==============================
st.subheader("🔟 Percentage of Claims by Status")
query10 = """
SELECT c.Status, 
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims_data), 2) AS Percentage
FROM claims_data c
GROUP BY c.Status;
"""
df10 = run_query(query10)
st.dataframe(df10)
fig10 = px.pie(df10, names="Status", values="Percentage", title="Claims Status Distribution")
st.plotly_chart(fig10, use_container_width=True)


# In[16]:


# ==============================
# 11. Avg Quantity Claimed per Receiver
# ==============================
st.subheader("1️⃣1️⃣ Average Quantity Claimed per Receiver")
query11 = """
SELECT r.Name, 
       ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
FROM claims_data c
JOIN receivers_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Name;
"""
df11 = run_query(query11)
st.dataframe(df11)


# In[17]:


# ==============================
# 12. Most Claimed Meal Type
# ==============================
st.subheader("1️⃣2️⃣ Most Claimed Meal Type")
query12 = """
SELECT f.Meal_Type, 
       COUNT(*) AS Claim_Count
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY f.Meal_Type
ORDER BY Claim_Count DESC;
"""
df12 = run_query(query12)
st.dataframe(df12)


# In[18]:


# ==============================
# 13. Total Donated by Each Provider
# ==============================
st.subheader("1️⃣3️⃣ Total Quantity Donated by Provider")
query13 = """
SELECT p.Name, 
       SUM(f.Quantity) AS Total_Donated
FROM food_listings_data f
JOIN providers_data p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC;
"""
df13 = run_query(query13)
st.dataframe(df13)


# In[19]:


# ==============================
# 14. City with Highest Pending Quantity
# ==============================
st.subheader("1️⃣4️⃣ City with Highest Pending Quantity")
query14 = """
SELECT f.Location, 
       SUM(f.Quantity) AS Pending_Quantity
FROM claims_data c
JOIN food_listings_data f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Pending'
GROUP BY f.Location
ORDER BY Pending_Quantity DESC
LIMIT 1;
"""
df14 = run_query(query14)
st.dataframe(df14)


# In[20]:


# ==============================
# 15. Food Type with Highest Near Expiry Unclaimed Stock
# ==============================
st.subheader("1️⃣5️⃣ Food Type with Highest Near Expiry Unclaimed Stock")
query15 = """
SELECT f.Food_Type, 
       COUNT(*) AS Near_Expiry_Unclaimed
FROM food_listings_data f
LEFT JOIN claims_data c ON f.Food_ID = c.Food_ID AND c.Status = 'Completed'
WHERE f.Expiry_Date <= DATE_ADD(CURDATE(), INTERVAL 2 DAY)
  AND (c.Claim_ID IS NULL OR c.Status != 'Completed')
GROUP BY f.Food_Type
ORDER BY Near_Expiry_Unclaimed DESC;
"""
df15 = run_query(query15)
st.dataframe(df15)



# In[21]:


# ------------------------------
st.success("✅ Dashboard Loaded Successfully!")


# In[ ]:




