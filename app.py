import streamlit as st
import pandas as pd
import time
from moomoo.openapi.quote import QuoteContext
from moomoo.openapi.common import SubType
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

quote_ctx = QuoteContext(host='127.0.0.1', port=11111)
stock_list = ["TSLA.US", "AAPL.US", "NVDA.US"]

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"Telegram发送失败：{e}")

st.title("🚀 实时交易监控系统（Moomoo API）")
selected_stock = st.selectbox("选择股票", stock_list)
threshold = st.number_input("提醒阈值（$上涨）", min_value=0.1, value=1.0)
trigger_button = st.button("启动监控")

placeholder = st.empty()
price_history = []

if trigger_button:
    st.success("开始监控中...")
    quote_ctx.subscribe(selected_stock, [SubType.QUOTE])

    last_price = None

    def handler(data):
        nonlocal last_price
        current_price = data['last_price'][0]
        price_history.append(current_price)
        placeholder.line_chart(price_history[-30:])
        if last_price and (current_price - last_price >= threshold):
            msg = f"{selected_stock}上涨超过${threshold}，现价：${current_price:.2f}"
            send_telegram_msg(msg)
            st.warning(msg)
        last_price = current_price

    quote_ctx.set_handler(handler)

    while True:
        time.sleep(2)