from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import uuid
from pymongo import MongoClient
from datetime import datetime
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = FastAPI()

templates = Jinja2Templates(directory="templates")

client = MongoClient('mongodb+srv://swasthikp03:swasthik@swasthikprabhu.fabhbaq.mongodb.net/')
db = client['twitter_trends']
collection = db['trends']

def scrape_twitter_trends():
    options = webdriver.ChromeOptions()
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://httpbin.org/ip")
        ip_data = driver.find_element(By.TAG_NAME, "pre").text
        ip_address = json.loads(ip_data)["origin"]

        driver.get("https://twitter.com/login")
        time.sleep(5)

        username = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        username.send_keys("swasthikp04@gmail.com")
        username.send_keys(Keys.RETURN)
        time.sleep(15)

        password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password.send_keys("SwasthiK@2024")
        password.send_keys(Keys.RETURN)

        time.sleep(5)

        driver.get("https://twitter.com/home")
        time.sleep(5)

        trends = driver.find_elements(By.XPATH, "//div[@data-testid='tweetText']//span[@class='css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3']")[:5]
        trend_names = [trend.text for trend in trends]

        return trend_names, ip_address

    except Exception as e:
        print("Error:", e)
        return [], "No Proxy"

    finally:
        driver.quit()

def store_in_mongodb(trend_names, ip_address):
    unique_id = str(uuid.uuid4())
    record = {
        "unique_id": unique_id,
        "trend1": trend_names[0] if len(trend_names) > 0 else "N/A",
        "trend2": trend_names[1] if len(trend_names) > 1 else "N/A",
        "trend3": trend_names[2] if len(trend_names) > 2 else "N/A",
        "trend4": trend_names[3] if len(trend_names) > 3 else "N/A",
        "trend5": trend_names[4] if len(trend_names) > 4 else "N/A",
        "date_time": datetime.now(),
        "ip_address": ip_address
    }

    collection.insert_one(record)
    return unique_id

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/run-script")
async def run_script():
    trend_names, ip_address = scrape_twitter_trends()
    unique_id = store_in_mongodb(trend_names, ip_address)

    record = collection.find_one({"unique_id": unique_id})

    if record is None:
        return JSONResponse({"error": "Record not found"}, status_code=404)

    return JSONResponse({
        "date_time": record["date_time"].strftime("%Y-%m-%d %H:%M:%S"),
        "unique_id": record["unique_id"],
        "trend1": record["trend1"],
        "trend2": record["trend2"],
        "trend3": record["trend3"],
        "trend4": record["trend4"],
        "trend5": record["trend5"],
        "ip_address": record["ip_address"]
    })

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)