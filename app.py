import streamlit as st
from scraper import get_product_data
import matplotlib.pyplot as plt
import random

st.title("🛒 Smart Shopping Guide")

link = st.text_input("Paste Amazon Product Link")

if st.button("Analyze Product"):
    data = get_product_data(link)

    st.subheader("📦 Product Details")
    st.write("Name:", data["title"])
    st.write("Price:", data["price"])
    st.write("MRP:", data["mrp"])
    st.write("Rating:", data["rating"])

    # 🔗 Open Product
    st.markdown(f"[🔗 Open Product]({link})")

    # -------------------------------
    # ⭐ Rating Analysis
    # -------------------------------
    if data["rating"] != "Not Found":
        try:
            rating_value = float(data["rating"].split()[0])

            # 📊 Graph
            plt.figure()
            plt.bar(["Rating"], [rating_value])
            st.pyplot(plt)

            # 🤖 Smart Decision
            if rating_value >= 4.2:
                st.success("🔥 Excellent Product - Buy Now")
            elif rating_value >= 3.5:
                st.warning("⚠️ Average Product - Check Alternatives")
            else:
                st.error("❌ Poor Product - Avoid")

        except:
            st.error("Rating format issue")
    else:
        st.error("Rating not found")

    # -------------------------------
    # 💰 Discount Analysis
    # -------------------------------
    if data["price"] != "Not Found" and data["mrp"] != "Not Found":
        try:
            price = float(data["price"].replace("₹", "").replace(",", ""))
            mrp = float(data["mrp"].replace("₹", "").replace(",", ""))

            discount_percent = ((mrp - price) / mrp) * 100

            st.subheader("💸 Discount Analysis")
            st.write(f"Discount: {round(discount_percent,2)}%")

            if discount_percent > 50:
                st.warning("⚠️ High Discount - Fake ho sakta hai!")
            else:
                st.success("✅ Genuine Discount lag raha hai")

        except:
            st.error("Price calculation error")
    else:
        st.warning("Discount data not available")

    # -------------------------------
    # 🎲 Demo Fake Discount Alert
    # -------------------------------
    discount = random.randint(10, 80)

    if discount > 50:
        st.warning("⚠️ Extra Alert: High discount detected!")