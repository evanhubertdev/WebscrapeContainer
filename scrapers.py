from selenium import webdriver
from selenium.webdriver.common.by import By
import json
from urllib.request import urlopen

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
    '''
    get URL for honda automobiles API
    '''
    url = "https://automobiles.honda.com/platform/api/v1/model-select/configuration/bap"

    '''
    open URL and load(s) into json object
    '''
    response = urlopen(url)
    json_object = json.loads(response.read())
    
    '''
    create list for formatted JSON string
    '''
    formattedData = {}
    formattedData['vehicles'] = []

    '''
    tempDict, sedanData, hatchbackData, minivanTruckData, and suvData are all lists which are appended to formattedData
    each holding their respective data in a json object
    '''
    tempDict = {}
    sedanData = {}
    sedanData['cars-Sedans'] = []
    hatchbackData = {}
    hatchbackData['cars-Hatchbacks'] = []
    minivanTruckData = {}
    minivanTruckData['minivan-truck'] = []
    suvData = {}
    suvData['crossover-and-suv'] = []

    '''
    only iterate over the number of models in the API
    '''
    length = len(json_object['Models'])
    i = 0
    while i < length:
        '''
        - start with sedan scraping (includes electric vehicles)
        - parse name, price, and mileage into the tempDict
        - make tempDict empty after appended to (carType)Data to make room for new car data
        - continue for hatchbacks, crossovers/suv, and minivan/truck
        '''
        if (json_object['Models'][i]['Category']['Id'] == "sedans" or json_object['Models'][i]['Category']['Id'] == "environmental-vehicles"):
            tempDict['name'] = json_object['Models'][i]['ModelName']
            '''
            Note about MSRP Formatting: 
            - Msrp from the API is in format 12345.67; the format below parses to be in correct currency format
            '''
            tempDict['price'] = "${:,.2f}".format(float(json_object['Models'][i]['Msrp']))

            '''
            Note about cityMileage and highwayMileage
            - environmental-vehicles includes the clarity fuel cell which does not have city/hwy mpg
            - Rather has electricRange. This is not included in the API, its range is still attached to the standard the mpg formatting
            - for other cars.
            - thus we have to check and see if its an electric car
            - if it is an electric car, we do not use city/hwy mpg, we use electricRange
            '''
            if (json_object['Models'][i]['Category']['Id'] != "environmental-vehicles"):
                a, b = json_object['Models'][i]['Mpg'].split('/', 1)
                tempDict['cityMileage'] = a
                tempDict['highwayMileage'] = b
            else:
                tempDict['electricRange'] = json_object['Models'][i]['Mpg']
            
            '''
            Note about URL:
            - The URL's are https://automobiles.honda.com/(CARMODELNAME)
            - The car model name, with spaces replaces to '-' and forced to lowercase, creates a valid URL
            '''
            tempDict['url'] = 'https://automobiles.honda.com/' + json_object['Models'][i]['ModelName'].replace(' ', '-').lower()

            sedanData['cars-Sedans'].append(tempDict)
            tempDict = {}
        elif (json_object['Models'][i]['Category']['Id'] == "hatchbacks"):
            tempDict['name'] = json_object['Models'][i]['ModelName']
            tempDict['price'] = "${:,.2f}".format(float(json_object['Models'][i]['Msrp']))
            a, b = json_object['Models'][i]['Mpg'].split('/', 1)
            tempDict['cityMileage'] = a
            tempDict['highwayMileage'] = b
            tempDict['url'] = 'https://automobiles.honda.com/' + json_object['Models'][i]['ModelName'].replace(' ', '-').lower()
            hatchbackData['cars-Hatchbacks'].append(tempDict)
            tempDict = {}
        elif (json_object['Models'][i]['Category']['Id'] == "crossovers-suv"):
            tempDict['name'] = json_object['Models'][i]['ModelName']
            tempDict['price'] = "${:,.2f}".format(float(json_object['Models'][i]['Msrp']))
            a, b = json_object['Models'][i]['Mpg'].split('/', 1)
            tempDict['cityMileage'] = a
            tempDict['highwayMileage'] = b

            '''
            Note about CR-V Hybrid
            - The CR-V hybrid isnt a stand-alone vehicle
            - rather it is a subset of the CR-V (its an option)
            - Thus, we have to hard code the link to the #features section of the cr-v page which includes information about the hybrid cr-v.
            - If it is not the CR-V hybrid, continue as usual
            '''
            if (json_object['Models'][i]['ModelName'] != "CR-V Hybrid"):
                tempDict['url'] = 'https://automobiles.honda.com/' + json_object['Models'][i]['ModelName'].replace(' ', '-').lower()
            else:
                tempDict['url'] = 'https://automobiles.honda.com/cr-v#features-hybrid'

            suvData['crossover-and-suv'].append(tempDict)
            tempDict = {}
        elif (json_object['Models'][i]['Category']['Id'] == "minivan-truck"):
            tempDict['name'] = json_object['Models'][i]['ModelName']
            tempDict['price'] = "${:,.2f}".format(float(json_object['Models'][i]['Msrp']))
            a, b = json_object['Models'][i]['Mpg'].split('/', 1)
            tempDict['cityMileage'] = a
            tempDict['highwayMileage'] = b
            tempDict['url'] = 'https://automobiles.honda.com/' + json_object['Models'][i]['ModelName'].replace(' ', '-').lower()
            minivanTruckData['minivan-truck'].append(tempDict)
        i+=1

    '''
    append each (carType)Data list to the formattedData json object
    '''
    formattedData['vehicles'].append(sedanData)
    formattedData['vehicles'].append(hatchbackData)
    formattedData['vehicles'].append(minivanTruckData)
    formattedData['vehicles'].append(suvData)

    '''
    return formattedData as string to scraperesults container
    '''
    return json.dumps(formattedData)

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