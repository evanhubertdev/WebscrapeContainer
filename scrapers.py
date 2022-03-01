from selenium import webdriver
from selenium.webdriver.common.by import By
import json

def getDriver(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    driver.get(url)

    return driver

def scrapeCars():
    driver = getDriver("https://automobiles.honda.com/tools/build-and-price")

    carTypes = driver.find_elements(By.CLASS_NAME, "vehicle-sort-main-container")
    rawData = {}
    rawData['vehicles'] = []
    for carType in carTypes:
        carTypeString = carType.get_attribute("data-attribute")
        if carTypeString is not None:
            carSubtypes = carType.find_elements(By.CLASS_NAME, "vehicle-sort-sub-container")
            for carSubtype in carSubtypes:
                carSubtypeJson = {}
                # Try getting Car Subtype, may not exist
                try:
                    carSubtypeString = carSubtype.find_element(By.TAG_NAME, "h4").find_element(By.TAG_NAME, "div").find_element(By.TAG_NAME, "span").text
                except Exception:
                    carSubtypeString = None
                carSubtypeJsonString = carTypeString if carSubtypeString == None else carTypeString + "-" + carSubtypeString
                carSubtypeJson[carSubtypeJsonString] = []
                # Get Cars
                rowOfCars = carSubtype.find_element(By.CSS_SELECTOR, "div[class='cards clearfix']").find_elements(By.CSS_SELECTOR, "div[class='rzf-gry-card-row clearfix']")
                for row in rowOfCars:
                    cars = row.find_elements(By.CSS_SELECTOR, "article[class='rzf-gry rzf-gry-card-tile card vehicle']")
                    for car in cars:
                        carJson = {}
                        # Get Car Name
                        name = car.find_element(By.TAG_NAME, "h5").text
                        carJson['name'] = name
                        infoElements = car.find_element(By.CLASS_NAME, "rzf-gry-card-vehicle-info").find_elements(By.TAG_NAME, "div")
                        # Get Price
                        price = infoElements[0].find_element(By.TAG_NAME, "span").text
                        carJson['price'] = price
                        # Get Gas Mileage/Electric Range
                        combinedMilageList = infoElements[1].find_element(By.TAG_NAME, "span").text.split('/')
                        # Electic vehicles only list range, so if it only has 1 value, it's electric
                        if len(combinedMilageList) == 2:
                            cityMileage = combinedMilageList[0]
                            carJson['cityMileage'] = cityMileage
                            highwayMileage = combinedMilageList[1]
                            carJson['highwayMileage'] = highwayMileage
                        else:
                            electricRange = combinedMilageList[0]
                            carJson['electricRange'] = electricRange
                        
                        # Get Link
                        buildLink = car.find_element(By.CLASS_NAME, "rzf-gry-card-primary-ctas").find_element(By.CSS_SELECTOR, "a[class='m_cta is-on-light io-listener is-primary']").get_attribute("href")
                        carJson['url'] = buildLink

                        # Add to carSubtypeJson
                        carSubtypeJson[carSubtypeJsonString].append(carJson)
                rawData['vehicles'].append(carSubtypeJson)

    driver.close()
    return json.dumps(rawData)


def scrapeNews():
    driver = getDriver("https://global.honda/newsroom/")
    rawData = {}
    rawData['articles'] = []

    # Years
    while True:
        # Pages
        while True:
            newsList = driver.find_element(By.CLASS_NAME, "news_list")

            articles = newsList.find_elements(By.CLASS_NAME, "news_list__article")
            for article in articles:
                articleJson = {}
                div = article.find_element(By.CLASS_NAME, "news_list__contents")
                href = div.find_element(By.CLASS_NAME, "news_list__ttl").find_element(By.TAG_NAME, "a")
                title = href.text
                articleJson['title'] = title
                date = div.find_element(By.CLASS_NAME, "news_list__date").text
                articleJson['date'] = date
                url = href.get_attribute("href")
                articleJson['url'] = url

                rawData['articles'].append(articleJson)
            try:
                nextPageButton = driver.find_element(By.CSS_SELECTOR, "#PAGETOP > div > div.mainclm.parsys > div.global-layout-select.parbase.section > div > div > div > div > div.pT60 > nav > p.news_navi__next > a")
                nextPageButton.click()
            except Exception:
                years = driver.find_element(By.CSS_SELECTOR, "#PAGETOP > div > div.mainclm.parsys > div.global-localNavi.parbase.section > section > ul").find_elements(By.TAG_NAME, "li")
                for year in years:
                    if year.get_attribute("class") == "active":
                        activeYear = year
                        break
                break
        
        nextYear = years[years.index(activeYear) + 1].find_element(By.TAG_NAME, "a")
        if "More" in nextYear.text:
            break
        else:
            nextYear.click()
    # outputFile = open('output.txt', 'w')
    # print(json.dumps(rawData, indent=4), file=outputFile)
    # outputFile.close()
    
    driver.close()
    return json.dumps(rawData)