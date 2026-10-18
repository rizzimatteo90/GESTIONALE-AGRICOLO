import os
import base64
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import streamlit as st

try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

st.set_page_config(page_title="Nicoli Rizzi - Servizi Agricoli e Forestali", layout="wide", initial_sidebar_state="collapsed")
DB_PATH = "gestionale_cantiere.db"
ADMIN_PASSWORD = "Billabong4e48"
CURRENT_YEAR = datetime.now().year


def img64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return ""

bg_path = next((p for p in ("sfondo.jpg", "IMG_8234.jpg") if os.path.exists(p)), None)
bg64 = img64(bg_path) if bg_path else ""
modulo_corrente = st.session_state.get("modulo_attivo", "HOME")
is_home = modulo_corrente == "HOME"
# La home mantiene la fotografia aziendale esistente; il modulo bilici usa una foto reale
# di cippato da Wikimedia Commons (licenza CC BY-SA 4.0, dettagli indicati nel modulo).
if bg64 and is_home:
    bg_css = f".stApp {{ background: linear-gradient(rgba(0,0,0,.48),rgba(0,0,0,.58)), url('data:image/jpeg;base64,{bg64}'); background-size:cover; background-position:center; background-attachment:fixed; }}"
elif modulo_corrente == "BILICI":
    bg_css = ".stApp { background: linear-gradient(rgba(20,24,20,.58),rgba(20,24,20,.72)), url('https://commons.wikimedia.org/wiki/Special:FilePath/Pile_of_wood_chips_Namibia.jpg?width=1600'); background-size:cover; background-position:center; background-attachment:fixed; color:#fff; }"
else:
    bg_css = ".stApp { background-color:#F9F6F0; color:#2C2C2C; }"
text_color = "#FFFFFF" if (is_home and bg64) or modulo_corrente == "BILICI" else "#2C2C2C"
shadow = "1px 1px 2px rgba(0,0,0,.8)" if (is_home and bg64) or modulo_corrente == "BILICI" else "none"
st.markdown(f"""
<style>
{bg_css}
[data-testid="stSidebar"] {{display:none;}}
h1,h2,h3,h4,h5,h6,p,[data-testid="stMarkdownContainer"] {{color:{text_color};}}
label {{color:{text_color}!important;font-weight:600!important;text-shadow:{shadow};}}
.logo-container {{width:100%;display:flex;align-items:center;justify-content:center;text-align:center;padding:8px 0 22px;box-sizing:border-box;background:transparent!important;}}
.logo-img {{display:block;width:min(92vw,650px)!important;max-width:650px!important;height:190px!important;object-fit:contain;background:transparent!important;mix-blend-mode:screen;}}
.logo-fallback {{color:#fff!important;font-size:clamp(42px,7vw,78px);line-height:1.05;font-weight:900;text-align:center;text-shadow:2px 2px 5px rgba(0,0,0,.8);}}
.st-key-home_modules {{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;}}
div.stButton>button[kind="primary"] {{background-color:#35483b!important;color:#fff!important;border:1px solid rgba(255,255,255,.55)!important;border-radius:16px!important;width:100%!important;min-height:0!important;height:auto!important;max-height:none!important;aspect-ratio:1/1!important;font-size:clamp(16px,1.7vw,22px)!important;font-weight:850!important;white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.15!important;box-shadow:0 6px 16px rgba(0,0,0,.24)!important;transition:all .2s ease-in-out!important;padding:14px!important;display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;text-shadow:0 2px 5px rgba(0,0,0,.9)!important;background-position:center!important;background-size:cover!important;}}
div.stButton>button[kind="primary"] p,div.stButton>button[kind="primary"] span {{color:#fff!important;width:100%!important;text-align:center!important;font-weight:850!important;text-shadow:0 2px 5px rgba(0,0,0,.95)!important;}}
div.stButton>button[kind="primary"]:hover {{border-color:#fff!important;transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(0,0,0,.38)!important;filter:brightness(1.08)!important;}}
.st-key-btn_rap button {{background-image:linear-gradient(0deg,rgba(15,25,17,.78),rgba(15,25,17,.08)),url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNTAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9InNreSIgeDI9IjAiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjZThlZWU4Ii8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjYjljOWIxIi8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImdyZWVuIiB4Mj0iMCIgeTI9IjEiPjxzdG9wIHN0b3AtY29sb3I9IiNhMWM5NTQiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiM0YjdiMmQiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjUwMCIgcng9IjI0IiBmaWxsPSJ1cmwoI3NreSkiLz48cGF0aCBkPSJNMCAzNjAgUTE4MCAzMzAgMzUwIDM2MiBUODAwIDM0MFY1MDBIMFoiIGZpbGw9IiM4ZmE3N2YiLz48cGF0aCBkPSJNMCA0MjUgUTE4MCAzOTUgMzYwIDQyNiBUODAwIDQxMFY1MDBIMFoiIGZpbGw9IiM3MThiNjEiLz48Y2lyY2xlIGN4PSIyNjAiIGN5PSIzNjUiIHI9IjkxIiBmaWxsPSIjMjAyOTIzIi8+PGNpcmNsZSBjeD0iMjYwIiBjeT0iMzY1IiByPSI2MCIgZmlsbD0iI2E5YjNhYSIvPjxjaXJjbGUgY3g9IjI2MCIgY3k9IjM2NSIgcj0iMzQiIGZpbGw9IiM1MzYwNTYiLz48Y2lyY2xlIGN4PSI2MTAiIGN5PSIzNzUiIHI9IjYyIiBmaWxsPSIjMjAyOTIzIi8+PGNpcmNsZSBjeD0iNjEwIiBjeT0iMzc1IiByPSIzOSIgZmlsbD0iI2E5YjNhYSIvPjxjaXJjbGUgY3g9IjYxMCIgY3k9IjM3NSIgcj0iMjIiIGZpbGw9IiM1MzYwNTYiLz48cGF0aCBkPSJNMTU2IDMzMkwxODMgMjQzTDMxOSAyMzFMMzgyIDI3N0w1MjAgMjgyTDU2MCAzMzBMNTYwIDM1M0gzNTRMMzMzIDMwNkgyMjFMMjEwIDM1M0gxNjBaIiBmaWxsPSJ1cmwoI2dyZWVuKSIgc3Ryb2tlPSIjMzU1YTI4IiBzdHJva2Utd2lkdGg9IjgiLz48cGF0aCBkPSJNMzIyIDIzM0wzNTAgMTQ1SDQ0OUw0ODQgMjc4SDM3MloiIGZpbGw9IiM0ZTdkMmQiIHN0cm9rZT0iIzM1NWEyOCIgc3Ryb2tlLXdpZHRoPSI4Ii8+PHBhdGggZD0iTTM2MiAxNTlINDMxTDQ1MiAyNDFIMzM5WiIgZmlsbD0iI2E5YzhkMiIgc3Ryb2tlPSIjMzQ0ZDUwIiBzdHJva2Utd2lkdGg9IjYiLz48cGF0aCBkPSJNNDUwIDE0Nkw0NjcgMTM2TDQ4MiAxNDVMNDkzIDI3Nkw0NzMgMjc4WiIgZmlsbD0iI2UxZTdkYyIvPjxyZWN0IHg9IjE5MCIgeT0iMjUyIiB3aWR0aD0iMTE1IiBoZWlnaHQ9IjE3IiByeD0iNSIgZmlsbD0iI2UwZThkYyIvPjxwYXRoIGQ9Ik01MTcgMjg5TDU3MiAyODlMNTk3IDMyMUw1NTMgMzMzWiIgZmlsbD0iI2Q4ZGVkNCIvPjxnIG9wYWNpdHk9Ii42NSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjMiPjxwYXRoIGQ9Ik01NSA5NUg3NDUiLz48cGF0aCBkPSJNNTUgMTA1SDc0NSIvPjwvZz48L3N2Zz4=)!important;}}
.st-key-btn_cal button {{background-image:linear-gradient(0deg,rgba(15,25,17,.78),rgba(15,25,17,.08)),url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNTAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4Mj0iMCIgeTI9IjEiPjxzdG9wIHN0b3AtY29sb3I9IiNlYWYxZjMiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNiZGNmZDMiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjUwMCIgcng9IjI0IiBmaWxsPSJ1cmwoI2JnKSIvPjxyZWN0IHg9IjE4MCIgeT0iODAiIHdpZHRoPSI0NDAiIGhlaWdodD0iMzQwIiByeD0iMjUiIGZpbGw9IiNmZmYiIHN0cm9rZT0iI2Q1ZTBlMSIgc3Ryb2tlLXdpZHRoPSI3Ii8+PHBhdGggZD0iTTE4MCAxMTBRMTgwIDgwIDIxMCA4MEg1OTBRNjIwIDgwIDYyMCAxMTBWMTU1SDE4MFoiIGZpbGw9IiM0MjZlNzgiLz48cGF0aCBkPSJNMjgwIDU4VjEwNU01MjAgNThWMTA1IiBzdHJva2U9IiM0MjZlNzgiIHN0cm9rZS13aWR0aD0iMTciIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxnIHN0cm9rZT0iI2RjZTVlNiIgc3Ryb2tlLXdpZHRoPSI1Ij48cGF0aCBkPSJNMjEwIDIxMEg1OTBNMjEwIDI3MEg1OTBNMjEwIDMzMEg1OTAiLz48cGF0aCBkPSJNMzA1IDE3MFYzOTBNNDAwIDE3MFYzOTBNNDk1IDE3MFYzOTAiLz48L2c+PGNpcmNsZSBjeD0iNTIwIiBjeT0iMjE0IiByPSIzNSIgZmlsbD0iI2Y1YzY1YiIvPjxnIHN0cm9rZT0iI2Y1YzY1YiIgc3Ryb2tlLXdpZHRoPSI3IiBzdHJva2UtbGluZWNhcD0icm91bmQiPjxwYXRoIGQ9Ik01MjAgMTYzVjE1MU01MjAgMjc3VjI2NU00NjkgMjE0SDQ1N001ODMgMjE0SDU3MU00ODQgMTc4TDQ3NSAxNjlNNTU2IDI2MEw1NjUgMjY5TTU1NiAxNzhMNTY1IDE2OU00ODQgMjYwTDQ3NSAyNjkiLz48L2c+PHBhdGggZD0iTTI0MiAyOTRDMjMyIDI2MSAyNTkgMjQ0IDI4MyAyNTJDMjk5IDIyMCAzNDcgMjMwIDM1MiAyNjJDMzgxIDI1OCAzOTYgMjkzIDM3NiAzMTBIMjY3QzI1MiAzMTAgMjQyIDMwMyAyNDIgMjk0WiIgZmlsbD0iIzdmYTViMCIvPjxjaXJjbGUgY3g9IjQzMCIgY3k9IjM1NSIgcj0iMTMiIGZpbGw9IiM0MjZlNzgiLz48Y2lyY2xlIGN4PSIzMzUiIGN5PSIyOTUiIHI9IjEwIiBmaWxsPSIjNDI2ZTc4Ii8+PC9zdmc+)!important;}}
.st-key-btn_bil button {{background-image:linear-gradient(0deg,rgba(15,25,17,.78),rgba(15,25,17,.08)),url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNTAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4Mj0iMCIgeTI9IjEiPjxzdG9wIHN0b3AtY29sb3I9IiNmMmVlZTUiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNkN2M4YWQiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0id29vZCIgeDI9IjAiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjZDliNzdlIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjOWI2ZDNjIi8+PC9saW5lYXJHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjgwMCIgaGVpZ2h0PSI1MDAiIHJ4PSIyNCIgZmlsbD0idXJsKCNiZykiLz48cmVjdCB4PSI4MCIgeT0iMTcwIiB3aWR0aD0iNTIwIiBoZWlnaHQ9IjE5MCIgcng9IjEzIiBmaWxsPSIjNTg2NDVlIi8+PHBhdGggZD0iTTEwNSAxOTNINTc1VjMyNkgxMDVaIiBmaWxsPSIjYmZjN2JlIi8+PHBhdGggZD0iTTExMCAyNDBMMTQzIDIwMkwxNzUgMjI5TDIwNyAxOTZMMjQwIDIzMEwyNzMgMjAzTDMwNiAyMzVMMzM5IDE5OEwzNzEgMjMyTDQwNiAyMDBMNDM4IDIzMUw0NzMgMjAzTDUwOCAyMzVMNTQxIDIwOUw1NzAgMjQxVjMyNkgxMTBaIiBmaWxsPSJ1cmwoI3dvb2QpIi8+PGcgZmlsbD0iIzgwNTkyZiI+PHBhdGggZD0iTTEzNSAyNDhsMTgtMTUgMTggMTYtMTYgMTV6TTIxMCAyNzZsMjEtMTcgMTcgMTYtMTkgMTZ6TTI4NCAyNDdsMTgtMTQgMjAgMTYtMTggMTR6TTM2MCAyNzhsMjAtMTYgMTggMTUtMTcgMTV6TTQzNSAyNDdsMTgtMTQgMTggMTUtMTcgMTV6TTUwNyAyNzhsMjAtMTYgMTggMTUtMTcgMTV6Ii8+PC9nPjxyZWN0IHg9IjYwMCIgeT0iMjQwIiB3aWR0aD0iMTA1IiBoZWlnaHQ9IjEyMCIgcng9IjkiIGZpbGw9IiM0MjY2NWEiLz48cGF0aCBkPSJNNjE1IDI0MEw2MzYgMTg0SDY4NEw3MDQgMjQwWiIgZmlsbD0iIzU2N2Q3MCIvPjxyZWN0IHg9IjY0MiIgeT0iMTk2IiB3aWR0aD0iMzUiIGhlaWdodD0iMjkiIHJ4PSI0IiBmaWxsPSIjYjdkMGQ0Ii8+PGNpcmNsZSBjeD0iMTgwIiBjeT0iMzY5IiByPSI0MiIgZmlsbD0iIzI1MmUyYSIvPjxjaXJjbGUgY3g9IjE4MCIgY3k9IjM2OSIgcj0iMjEiIGZpbGw9IiNhZWI4YjAiLz48Y2lyY2xlIGN4PSI2NDIiIGN5PSIzNjkiIHI9IjQyIiBmaWxsPSIjMjUyZTJhIi8+PGNpcmNsZSBjeD0iNjQyIiBjeT0iMzY5IiByPSIyMSIgZmlsbD0iI2FlYjhiMCIvPjxnIGZpbGw9IiM5YjZkM2MiPjxwYXRoIGQ9Ik0xNTAgMTIwbDIwLTIwIDI1IDE1LTEzIDI1ek0yMTQgMTM5bDE4LTIzIDI0IDEyLTE0IDI2ek0yNzUgMTEybDIwLTE4IDIzIDE0LTEyIDI0ek0zMzggMTM5bDE4LTIzIDI0IDEyLTE0IDI2ek00MDIgMTE2bDIwLTE5IDIzIDE1LTEyIDIzek00NjYgMTM5bDE4LTIyIDI0IDEyLTE0IDI1ek01MzAgMTE1bDIwLTE4IDIzIDE0LTEyIDI0eiIvPjwvZz48L3N2Zz4=)!important;}}
.st-key-btn_flotta button {{background-image:linear-gradient(0deg,rgba(15,25,17,.78),rgba(15,25,17,.08)),url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgNTAwIj48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImJnIiB4Mj0iMCIgeTI9IjEiPjxzdG9wIHN0b3AtY29sb3I9IiNlZGYwZWIiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNjYmQ1Y2IiLz48L2xpbmVhckdyYWRpZW50PjwvZGVmcz48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjUwMCIgcng9IjI0IiBmaWxsPSJ1cmwoI2JnKSIvPjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDI4MCAyNTApIj48cGF0aCBkPSJNMC0xNTBMMjYtMTUwTDM2LTEwOEw2OC05NEwxMDItMTIyTDEyMi0xMDJMOTQtNjhMMTA4LTM2TDE1MC0yNkwxNTAgMEwxMDggMTBMOTQgNDJMMTIyIDc2TDEwMiA5Nkw2OCA2OEwzNiA4MkwyNiAxMjVMMCAxMjVMLTEwIDgyTC00MiA2OEwtNzYgOTZMLTk2IDc2TC02OCA0MkwtODIgMTBMLTEyNSAwTC0xMjUtMjZMLTgyLTM2TC02OC02OEwtOTYtMTAyTC03Ni0xMjJMLTQyLTk0TC0xMC0xMDhaIiBmaWxsPSIjNjg4MzZlIiBzdHJva2U9IiMzNTVjNDIiIHN0cm9rZS13aWR0aD0iNyIvPjxjaXJjbGUgcj0iNjUiIGZpbGw9IiNlN2VkZTYiIHN0cm9rZT0iIzM1NWM0MiIgc3Ryb2tlLXdpZHRoPSI5Ii8+PGNpcmNsZSByPSIyNyIgZmlsbD0iIzY4ODM2ZSIvPjwvZz48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSg1NDUgMjUwKSByb3RhdGUoLTIzKSI+PHJlY3QgeD0iLTI1IiB5PSItMTQ1IiB3aWR0aD0iNTAiIGhlaWdodD0iMjkwIiByeD0iMjMiIGZpbGw9IiNiOWMyYmMiIHN0cm9rZT0iIzU2NjQ1YyIgc3Ryb2tlLXdpZHRoPSI5Ii8+PGNpcmNsZSBjeT0iLTExMCIgcj0iMzYiIGZpbGw9IiNkOWUwZGEiIHN0cm9rZT0iIzU2NjQ1YyIgc3Ryb2tlLXdpZHRoPSI5Ii8+PGNpcmNsZSBjeT0iMTEwIiByPSIzNiIgZmlsbD0iI2Q5ZTBkYSIgc3Ryb2tlPSIjNTY2NDVjIiBzdHJva2Utd2lkdGg9IjkiLz48cGF0aCBkPSJNLTI1LTExMEgyNU0tMjUgMTEwSDI1IiBzdHJva2U9IiM1NjY0NWMiIHN0cm9rZS13aWR0aD0iOSIvPjwvZz48ZyBmaWxsPSIjOGVhMzkyIiBvcGFjaXR5PSIuNSI+PGNpcmNsZSBjeD0iNjcwIiBjeT0iOTUiIHI9IjIwIi8+PGNpcmNsZSBjeD0iNzEwIiBjeT0iMTIwIiByPSIxMiIvPjxjaXJjbGUgY3g9IjEwNSIgY3k9IjM3NSIgcj0iMTYiLz48L2c+PC9zdmc+)!important;}}
div.stButton>button[kind="secondary"] {{background:#fff!important;color:#2C2C2C!important;border:1px solid #D0CBC3!important;border-radius:6px!important;font-weight:500!important;}}
div.stButton>button[kind="secondary"]:hover {{background:#F0EBE3!important;color:#000!important;}}
.streamlit-expanderHeader {{background:#F3EFE6;border-radius:6px;}}
@media(max-width:700px) {{
    [data-testid="stAppViewContainer"] .main .block-container {{padding: .25rem .35rem .25rem!important; max-width:100vw!important; overflow-x:hidden!important;}}
    .logo-container {{padding:0!important;margin:0!important;}}
    .logo-img {{width:92vw!important;height:clamp(58px,10vh,78px)!important;max-height:78px!important;}}
    .logo-fallback {{font-size:clamp(30px,8vw,46px)!important;}}
    .st-key-home_modules {{max-width:100%!important;margin-top:0!important;}}
    .st-key-home_modules [data-testid="stHorizontalBlock"] {{flex-wrap:nowrap!important;gap:.45rem!important;align-items:stretch!important;}}
    .st-key-home_modules [data-testid="column"] {{min-width:0!important;width:50%!important;flex:1 1 50%!important;padding:0 .12rem!important;}}
    .st-key-home_modules div[data-testid="stButton"] {{width:100%!important;}}
    div.stButton>button[kind="primary"] {{width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:1/1!important;font-size:clamp(10px,2.8vw,15px)!important;padding:5px!important;border-radius:10px!important;line-height:1.08!important;}}
    .stSelectbox,[data-testid="stSelectbox"] {{margin-bottom:.15rem!important;}}
    [data-testid="stMarkdownContainer"] p {{margin-bottom:.25rem!important;}}
    .stApp {{background-attachment:scroll!important;}}
}}
</style>
""", unsafe_allow_html=True)

# Database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS rapportini_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,data TEXT,utente TEXT,cliente TEXT,ore_totali REAL,note TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS dettagli_lavorazioni_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,rapportino_id INTEGER,ora_inizio TEXT,ora_fine TEXT,mezzo TEXT,descrizione TEXT,FOREIGN KEY(rapportino_id) REFERENCES rapportini_v3(id) ON DELETE CASCADE)""")
c.execute("""CREATE TABLE IF NOT EXISTS bilici_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,data_partenza TEXT,cliente TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS attrezzature_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT UNIQUE,tipo_conteggio TEXT,anno_riferimento INTEGER,valore_inizio_anno REAL)""")
c.execute("""CREATE TABLE IF NOT EXISTS manutenzioni_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,attrezzatura_id INTEGER,data TEXT,tipo TEXT,ore_km_al_momento REAL,eseguito_da TEXT,descrizione TEXT,costo REAL,FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature_v3(id))""")
c.execute("""CREATE TABLE IF NOT EXISTS utenti_app (id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL COLLATE NOCASE UNIQUE,creato_il TEXT DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

# Session state
for key, value in {"modulo_attivo":"HOME", "utente_corrente":"", "ruolo":"Operatore", "admin_autenticato":False, "num_righe_lavoro":1}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# L'URL può preselezionare un operatore già registrato, ma non concede privilegi.
try:
    nome_url = str(st.query_params.get("utente", "")).strip()
except Exception:
    nome_url = ""
if nome_url and not st.session_state.utente_corrente:
    c.execute("SELECT nome FROM utenti_app WHERE nome=? COLLATE NOCASE", (nome_url,))
    trovato = c.fetchone()
    if trovato:
        st.session_state.utente_corrente = trovato[0]

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# HOME
if st.session_state.modulo_attivo == "HOME":
    logo_file = next((p for p in ("logo.png", "logo.jpg", "IMG_7106.jpg") if os.path.exists(p)), None)
    if logo_file:
        logo_data = img64(logo_file)
        mime = "image/png" if logo_file.lower().endswith(".png") else "image/jpeg"
        st.markdown(f'<div class="logo-container"><img src="data:{mime};base64,{logo_data}" class="logo-img" alt="Logo Nicoli Rizzi"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-container"><div class="logo-fallback">NICOLI RIZZI</div></div>', unsafe_allow_html=True)

    c.execute("SELECT nome FROM utenti_app ORDER BY nome COLLATE NOCASE")
    utenti = [r[0] for r in c.fetchall()]
    opzioni = ["-- Seleziona operatore --"] + utenti + ["+ Registra nuovo operatore"]
    default = st.session_state.utente_corrente if st.session_state.utente_corrente in utenti else "-- Seleziona operatore --"
    # Su una nuova sessione, ripristina il nome salvato nell’URL anche nello stato del widget.
    if "selezione_utente_home" not in st.session_state:
        st.session_state["selezione_utente_home"] = default
    elif st.session_state.get("selezione_utente_home") not in opzioni:
        st.session_state["selezione_utente_home"] = default
    selezione = st.selectbox("Operatore:", opzioni, index=opzioni.index(default), key="selezione_utente_home")
    if selezione == "+ Registra nuovo operatore":
        with st.form("registra_operatore_form"):
            nuovo_nome = st.text_input("Nome e cognome del dipendente")
            registra = st.form_submit_button("Registra operatore")
        if registra:
            nome = " ".join(nuovo_nome.split())
            if not nome:
                st.error("Inserisci nome e cognome.")
            else:
                try:
                    c.execute("INSERT INTO utenti_app(nome) VALUES(?)", (nome,))
                    conn.commit()
                    st.session_state.utente_corrente = nome
                    st.query_params["utente"] = nome
                    st.rerun()
                except sqlite3.IntegrityError:
                    c.execute("SELECT nome FROM utenti_app WHERE nome=? COLLATE NOCASE", (nome,))
                    existing = c.fetchone()
                    st.session_state.utente_corrente = existing[0] if existing else nome
                    st.query_params["utente"] = st.session_state.utente_corrente
                    st.rerun()
    elif selezione == "-- Seleziona operatore --":
        st.session_state.utente_corrente = ""
    else:
        st.session_state.utente_corrente = selezione
        st.query_params["utente"] = selezione

    scelta_ruolo = st.selectbox("Ruolo:", ["Operatore", "Socio / Amministratore"], key="ruolo_scelto")
    if scelta_ruolo == "Socio / Amministratore":
        # La richiesta password compare SOLO dopo aver scelto Amministratore.
        if not st.session_state.admin_autenticato:
            with st.form("login_amministratore_form"):
                password = st.text_input("Password amministratore", type="password")
                login = st.form_submit_button("Accedi come amministratore")
            if login:
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_autenticato = True
                    st.session_state.ruolo = "Socio / Amministratore"
                    st.success("Accesso amministratore autorizzato.")
                    st.rerun()
                else:
                    st.session_state.admin_autenticato = False
                    st.session_state.ruolo = "Operatore"
                    st.error("Password non corretta. Accesso come operatore.")
        else:
            st.session_state.ruolo = "Socio / Amministratore"
            if st.button("Esci dall'account amministratore", key="logout_admin", type="secondary"):
                st.session_state.admin_autenticato = False
                st.session_state.ruolo = "Operatore"
                st.session_state.ruolo_scelto = "Operatore"
                st.rerun()
    else:
        # Selezionando Operatore non viene chiesta alcuna password.
        st.session_state.ruolo = "Operatore"
        st.session_state.admin_autenticato = False

    st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
    with st.container(key="home_modules"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            if st.button("RAPPORTINO GIORNALIERO ATTIVITÀ", key="btn_rap", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "RAPPORTINO"; st.rerun()
        with col2:
            if st.button("CALENDARIO E STORICO RAPPORTINI", key="btn_cal", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "CALENDARIO"; st.rerun()
        st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            if st.button("REGISTRO SPEDIZIONI BILICI CIPPATO", key="btn_bil", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "BILICI"; st.rerun()
        with col4:
            if st.button("GESTIONE PARCO MACCHINE E ATTREZZATURE", key="btn_flotta", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "FLOTTA"; st.rerun()
    st.markdown('<p style="text-align:center;font-weight:600;font-size:11px;margin-top:15px;text-shadow:1px 1px 3px #000">Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali Conto Terzi</p>', unsafe_allow_html=True)

# RAPPORTINO
elif st.session_state.modulo_attivo == "RAPPORTINO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Rapportino Giornaliero Attività")
    st.caption(f"Utente collegato: {st.session_state.utente_corrente or 'Nessun operatore selezionato'} ({st.session_state.ruolo})")
    with st.form("form_rapportino_v3"):
        d1, d2 = st.columns(2)
        with d1:
            data_rep = st.date_input("Data Lavorazione (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            cliente = st.text_input("Cliente", placeholder="Inserisci il nome del cliente")
        with d2:
            ore = st.number_input("Ore Totali Lavorate nella Giornata", min_value=0.0, step=0.5, value=8.0)
            note = st.text_area("Note / Osservazioni Generali", placeholder="Note complessive, consumo gasolio, condizioni meteo...")
        st.markdown("---"); st.subheader("Dettaglio Lavorazioni della Giornata")
        c.execute("SELECT nome FROM attrezzature_v3 ORDER BY nome")
        mezzi = [r[0] for r in c.fetchall()] + ["Altro / Inserimento Manuale"]
        lavori = []
        for i in range(st.session_state.num_righe_lavoro):
            st.markdown(f"**Lavorazione #{i+1}**")
            a,b,d,e = st.columns([1.3,1.3,3,3])
            with a: ora_in = st.time_input(f"Ora Inizio #{i+1}", value=datetime.strptime("07:30","%H:%M").time(), key=f"in_{i}")
            with b: ora_fi = st.time_input(f"Ora Fine #{i+1}", value=datetime.strptime("12:00","%H:%M").time(), key=f"fi_{i}")
            with d:
                m = st.selectbox(f"Mezzo / Attrezzatura #{i+1}", mezzi, key=f"m_{i}")
                mezzo = st.text_input(f"Specifica mezzo #{i+1}", key=f"mm_{i}", placeholder="es. Motosega Stihl 661") if m == "Altro / Inserimento Manuale" else m
            with e: descr = st.text_input(f"Descrizione Attività #{i+1}", key=f"desc_{i}", placeholder="es. Cippatura ramaglie")
            lavori.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), mezzo, descr))
        salva = st.form_submit_button("Salva Rapportino Completo")
    if st.button("Aggiungi un'altra riga di lavoro", type="secondary"):
        st.session_state.num_righe_lavoro += 1; st.rerun()
    if salva:
        if not st.session_state.utente_corrente:
            st.error("Seleziona o registra prima il tuo nome nella Home."); st.stop()
        data_fmt = data_rep.strftime("%d/%m/%Y")
        c.execute("INSERT INTO rapportini_v3(data,utente,cliente,ore_totali,note) VALUES(?,?,?,?,?)", (data_fmt,st.session_state.utente_corrente,cliente,ore,note))
        rap_id = c.lastrowid
        c.executemany("INSERT INTO dettagli_lavorazioni_v3(rapportino_id,ora_inizio,ora_fine,mezzo,descrizione) VALUES(?,?,?,?,?)", [(rap_id,*x) for x in lavori])
        conn.commit(); st.session_state.num_righe_lavoro = 1; st.success(f"Rapportino registrato con successo in data {data_fmt}!")

# CALENDARIO / STORICO
elif st.session_state.modulo_attivo == "CALENDARIO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Calendario & Storico Rapportini")
    admin = st.session_state.ruolo == "Socio / Amministratore" and st.session_state.admin_autenticato
    if not admin:
        st.info(f"Visualizzazione rapportini inseriti da: **{st.session_state.utente_corrente}**")
        df = pd.read_sql_query("SELECT * FROM rapportini_v3 WHERE utente=? ORDER BY id DESC", conn, params=(st.session_state.utente_corrente,))
    else:
        st.success("Vista Amministratore: monitoraggio completo dell'attività aziendale.")
        df = pd.read_sql_query("SELECT * FROM rapportini_v3 ORDER BY id DESC", conn)
    tab_cal, tab_lista = st.tabs(["Vista Calendario Mensile", "Elenco Dettagliato & Modifica"])
    with tab_cal:
        st.subheader("Calendario delle Attività")
        events=[]
        if not df.empty:
            for _,r in df.iterrows():
                try:
                    dt=datetime.strptime(str(r["data"]),"%d/%m/%Y")
                    # Nel calendario il titolo dell'evento è il nome dell'operatore che ha inserito il rapportino.
                    events.append({"title":str(r["utente"] or "Operatore"),"start":dt.strftime("%Y-%m-%d"),"allDay":True,"backgroundColor":"#587a55","borderColor":"#587a55","textColor":"#ffffff"})
                except (ValueError,TypeError):
                    pass
        # Mantiene la data selezionata anche se si aggiorna la pagina o si torna al modulo.
        if "giorno_calendario_selezionato" not in st.session_state:
            try:
                st.session_state.giorno_calendario_selezionato = date.fromisoformat(str(st.query_params.get("giorno", date.today().isoformat())))
            except (ValueError, TypeError):
                st.session_state.giorno_calendario_selezionato = date.today()
        if "vista_calendario" not in st.session_state:
            st.session_state.vista_calendario = "dayGridMonth"
        if st.session_state.vista_calendario == "dayGridDay":
            if st.button("← Torna alla vista mensile", key="torna_calendario_mese", type="secondary"):
                st.session_state.vista_calendario = "dayGridMonth"
                st.rerun()
        cal_state = {}
        if HAS_CALENDAR:
            vista_attuale = st.session_state.vista_calendario
            cal_state = calendar(
                events=events,
                options={
                    "headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth,timeGridWeek,timeGridDay"},
                    "initialView":vista_attuale,
                    "initialDate":st.session_state.giorno_calendario_selezionato.isoformat(),
                    "navLinks":True,
                    "locale":"it",
                    "firstDay":1,
                    "height":"auto",
                    "contentHeight":"auto",
                    "dayMaxEvents":True,
                    "fixedWeekCount":False,
                    "nowIndicator":True,
                    "buttonText":{"today":"Oggi","month":"Mese","week":"Settimana","day":"Giorno"},
                },
                callbacks=["dateClick", "eventClick"],
                key=f"cal_view_{vista_attuale}"
            ) or {}
            # Clic su una casella vuota o su un evento: apre i rapportini di quel giorno.
            try:
                callback = cal_state.get("callback")
                if callback == "dateClick":
                    data_click = cal_state.get("dateClick", {}).get("date")
                elif callback == "eventClick":
                    data_click = cal_state.get("eventClick", {}).get("event", {}).get("start")
                else:
                    data_click = None
                if data_click:
                    st.session_state.giorno_calendario_selezionato = date.fromisoformat(str(data_click)[:10])
                    # Sincronizza anche il widget data prima che venga creato in questo rerun.
                    st.session_state["giorno_rapportini"] = st.session_state.giorno_calendario_selezionato
                    st.session_state.vista_calendario = "dayGridDay"
                    st.query_params["giorno"] = st.session_state.giorno_calendario_selezionato.isoformat()
                    st.rerun()
            except (ValueError, TypeError, AttributeError):
                pass
        else:
            st.warning("Il calendario interattivo richiede la dipendenza streamlit-calendar. Verifica che sia inclusa in requirements.txt e ridistribuisci l'app.")
        st.caption("Clicca direttamente su un giorno del calendario, oppure su un nome operatore, per aprire la giornata selezionata.")
        st.markdown("---")
        st.subheader("Rapportini della giornata selezionata")
        giorno_data = st.date_input("Giorno", value=st.session_state.giorno_calendario_selezionato, format="DD/MM/YYYY", key="giorno_rapportini")
        st.session_state.giorno_calendario_selezionato = giorno_data
        st.query_params["giorno"] = giorno_data.isoformat()
        giorno=giorno_data.strftime("%d/%m/%Y")
        if admin: c.execute("SELECT * FROM rapportini_v3 WHERE data=? ORDER BY id DESC",(giorno,))
        else: c.execute("SELECT * FROM rapportini_v3 WHERE data=? AND utente=? ORDER BY id DESC",(giorno,st.session_state.utente_corrente))
        rapporti=c.fetchall()
        if rapporti:
            st.markdown(f"#### Rapportini del **{giorno}**")
            for rap in rapporti:
                rid,rd,ru,rc,ro,rn=rap
                with st.expander(f"{ru} · Cliente: {rc or '—'} · Ore: {ro}h"):
                    st.write(f"**Operatore:** {ru}"); st.write(f"**Cliente:** {rc or ''}"); st.write(f"**Ore lavorate:** {ro} ore"); st.write(f"**Note:** {rn or 'Nessuna nota inserita'}")
                    det=pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?",conn,params=(rid,))
                    if not det.empty: st.dataframe(det,use_container_width=True)
        else:
            st.info(f"Nessun rapportino presente per la data {giorno}.")
    with tab_lista:
        if not admin:
            st.info("La modifica e l'eliminazione dei rapportini sono riservate all'amministratore autorizzato.")
        elif not df.empty:
            st.dataframe(df,use_container_width=True); st.markdown("---"); st.subheader("Gestione / Modifica / Eliminazione Rapportino")
            rid=st.selectbox("Seleziona ID Rapportino:",df["id"].tolist()); row=df[df["id"]==rid].iloc[0]
            with st.expander(f"Modifica Scheda #{rid}"):
                with st.form("form_edit_rap_v3"):
                    nc=st.text_input("Cliente",value=row["cliente"] or ""); no=st.number_input("Ore Totali",min_value=0.0,value=float(row["ore_totali"] or 0)); nn=st.text_area("Note",value=row["note"] or "")
                    x,y=st.columns(2)
                    with x: aggiorna=st.form_submit_button("Aggiorna Rapportino")
                    with y: elimina=st.form_submit_button("Elimina Rapportino")
                    if aggiorna:
                        c.execute("UPDATE rapportini_v3 SET cliente=?,ore_totali=?,note=? WHERE id=?",(nc,no,nn,rid)); conn.commit(); st.success("Rapportino aggiornato."); st.rerun()
                    if elimina:
                        c.execute("DELETE FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?",(rid,)); c.execute("DELETE FROM rapportini_v3 WHERE id=?",(rid,)); conn.commit(); st.warning("Rapportino eliminato."); st.rerun()
        else: st.info("Non ci sono rapportini da visualizzare.")

# BILICI
elif st.session_state.modulo_attivo == "BILICI":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Registro Spedizioni Bilici Cippato")
    st.markdown("<style>[data-testid='stForm'],[data-testid='stDataFrame'],[data-testid='stAlert']{background:rgba(255,255,255,.94);border-radius:12px;padding:10px;color:#25332a;} [data-testid='stDataFrame'] *{color:#25332a;}</style>", unsafe_allow_html=True)
    with st.expander("Registra Nuova Partenza Bilico",expanded=True):
        with st.form("form_bilico_v3",clear_on_submit=True):
            a,b=st.columns(2)
            with a: data_p=date.today(); data_p=st.date_input("Data di Partenza (GG/MM/AAAA)",data_p,format="DD/MM/YYYY")
            with b: cliente_b=st.text_input("Cliente / Destinazione",placeholder="Nome cliente o impianto")
            invia=st.form_submit_button("Registra Partenza Bilico")
            if invia:
                if not cliente_b.strip(): st.error("Inserisci il cliente o la destinazione.")
                else:
                    fmt=data_p.strftime("%d/%m/%Y"); c.execute("INSERT INTO bilici_v3(data_partenza,cliente) VALUES(?,?)",(fmt,cliente_b.strip())); conn.commit(); st.success(f"Partenza bilico registrata per '{cliente_b.strip()}' in data {fmt}.")
    dfb=pd.read_sql_query("SELECT data_partenza AS 'Data Partenza',cliente AS 'Cliente' FROM bilici_v3 ORDER BY id DESC",conn)
    st.subheader("Storico Partenze Bilici")
    if not dfb.empty: st.dataframe(dfb,use_container_width=True)
    else: st.info("Nessuna partenza registrata nel sistema.")
    st.caption("Foto di cippato: Deutsche Gesellschaft für Internationale Zusammenarbeit (GIZ), Wikimedia Commons · CC BY-SA 4.0 · https://commons.wikimedia.org/wiki/File:Pile_of_wood_chips_Namibia.jpg")

# FLOTTA
elif st.session_state.modulo_attivo == "FLOTTA":
    st.button("Torna alla Home",on_click=torna_home,type="secondary")
    st.title("Gestione Parco Macchine & Attrezzature")
    if st.session_state.ruolo != "Amministratore" or not st.session_state.admin_autenticato:
        st.warning("La gestione del parco macchine e del registro manutenzioni è riservata a soci e amministratore autorizzati.")
    else:
        t1,t2=st.tabs(["Schede Mezzi & Ore Inizio Anno","Registro Manutenzioni"])
        with t1:
            st.subheader("Aggiungi Mezzo o Attrezzatura alla Flotta")
            with st.form("form_attrezzatura_v3",clear_on_submit=True):
                a,b,d,e=st.columns(4)
                with a: nome_m=st.text_input("Nome / Modello Mezzo",placeholder="es. Valtra S400")
                with b: tipo=st.selectbox("Unità di Misura",["Ore","Chilometri"])
                with d: anno=st.number_input("Anno Registrazione",min_value=2000,max_value=2100,value=CURRENT_YEAR,step=1)
                with e: valore=st.number_input(f"Ore/Km a Inizio Anno ({int(anno)})",min_value=0.0,step=10.0)
                salva_m=st.form_submit_button("Salva Mezzo")
                if salva_m:
                    if not nome_m.strip(): st.error("Inserisci il nome del mezzo.")
                    else:
                        try:
                            c.execute("INSERT INTO attrezzature_v3(nome,tipo_conteggio,anno_riferimento,valore_inizio_anno) VALUES(?,?,?,?)",(nome_m.strip(),tipo,int(anno),valore)); conn.commit(); st.success("Mezzo registrato."); st.rerun()
                        except sqlite3.IntegrityError: st.error("Esiste già un mezzo con questo nome.")
            dfa=pd.read_sql_query("SELECT nome AS 'Mezzo',tipo_conteggio AS 'Unità di Misura',anno_riferimento AS 'Anno Riferimento',valore_inizio_anno AS 'Valore Inizio Anno' FROM attrezzature_v3 ORDER BY nome",conn)
            st.subheader("Flotta Aziendale"); st.dataframe(dfa,use_container_width=True)
        with t2:
            st.subheader("Registra Manutenzione / Intervento")
            c.execute("SELECT id,nome FROM attrezzature_v3 ORDER BY nome"); att=c.fetchall()
            if att:
                mappa={r[1]:r[0] for r in att}; mezzo_man=st.selectbox("Seleziona Mezzo",list(mappa.keys()))
                with st.form("form_manutenzione_v3",clear_on_submit=True):
                    a,b=st.columns(2)
                    with a:
                        data_man=st.date_input("Data Intervento (GG/MM/AAAA)",date.today(),format="DD/MM/YYYY")
                        tipo_man=st.selectbox("Tipo Intervento",["Tagliando / Ordinaria","Riparazione Straordinaria","Sostituzione Lame / Catene / Ingrassaggio"])
                        ore_man=st.number_input("Ore/Km della Macchina al momento del lavoro",min_value=0.0,step=5.0)
                    with b:
                        eseguito=st.text_input("Eseguito Da",placeholder="Meccanico interno / officina")
                        costo=st.number_input("Costo Sostenuto (€)",min_value=0.0,step=10.0)
                        descr=st.text_area("Dettaglio Lavori Svolti e Pezzi Sostituiti")
                    salva_man=st.form_submit_button("Salva Manutenzione")
                    if salva_man:
                        fmt=data_man.strftime("%d/%m/%Y")
                        c.execute("INSERT INTO manutenzioni_v3(attrezzatura_id,data,tipo,ore_km_al_momento,eseguito_da,descrizione,costo) VALUES(?,?,?,?,?,?,?)",(mappa[mezzo_man],fmt,tipo_man,ore_man,eseguito.strip(),descr.strip(),costo)); conn.commit(); st.success("Manutenzione registrata."); st.rerun()
                dfm=pd.read_sql_query("SELECT m.data AS 'Data',a.nome AS 'Mezzo',m.tipo AS 'Tipo Intervento',m.ore_km_al_momento AS 'Ore/Km',m.eseguito_da AS 'Eseguito Da',m.descrizione AS 'Descrizione',m.costo AS 'Costo (€)' FROM manutenzioni_v3 m JOIN attrezzature_v3 a ON m.attrezzatura_id=a.id ORDER BY m.id DESC",conn)
                st.subheader("Storico Manutenzioni"); st.dataframe(dfm,use_container_width=True)
            else: st.warning("Aggiungi prima un mezzo nella scheda 'Schede Mezzi & Ore Inizio Anno'.")

conn.close()
