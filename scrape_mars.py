# Dependencies
from bs4 import BeautifulSoup
from splinter import Browser
import cssutils
import tweepy
import pandas as pd
import time
from config import consumer_key, consumer_secret, access_token, access_token_secret, weather_api_key

# Function to initialize Splinter browser
def init_browser():
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


# Function to scrape various sites for information on Mars
def scrape():
    # Empty dict to store info
    mars_info = {}

    # Navigating to NASA site and initializing browser
    browser = init_browser()
    nasa_url = 'https://mars.nasa.gov/news/'
    browser.visit(nasa_url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    # Scraping latest article and storing to variables
    latest_article = soup.find("div", "list_text")
    news_title = latest_article.find("div", class_="content_title").text
    news_p = latest_article.find("div", class_="article_teaser_body").text
    #print(news_title)
    #print(news_p)

    # Adding to dict
    mars_info["news_title"] = news_title
    mars_info["teaser"] = news_p

    # Navigating to JPL site
    jpl_url = "https://jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)

    # Scraping JPL Mars site for featured image
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    carousel = soup.find('div', class_= 'carousel_items')
    div_style = carousel.find('article')['style']
    style = cssutils.parseStyle(div_style)
    partial_url = style['background-image']
    #print(partial_url)

    # Cleaning up image url
    partial_url = partial_url.replace('url(', '').replace(')', '')
    featured_image_url = "https://jpl.nasa.gov" + partial_url
    #print(featured_image_url)

    # Adding to dict
    mars_info["featured_image_url"] = featured_image_url

    # Navigating to Twitter
    tweet_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(tweet_url)
    
    # Pulling latest tweet from @marswxreport
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    mars_weather = soup.find("p", class_="tweet-text").text
    print(mars_weather)

    # Adding to dict
    mars_info["mars_weather"] = mars_weather

    # Navigating to Mars facts site
    facts_url = "https://space-facts.com/mars/"
    browser.visit(facts_url)

    # Using pandas to scrape table
    facts = pd.read_html(facts_url)
    #print(facts)

    # Isolating df from list and minor clean-up
    facts_df = pd.DataFrame(facts[0])
    facts_df.columns=['Fact','Result']
    #facts_df.head()

    # Writing df to html table
    mars_table = facts_df.to_html(index=False, justify='left', classes='mars-table')
    mars_table = mars_table.replace('\n', ' ')
    #print(mars_table)

    # Adding to dict
    mars_info["mars_table"] = mars_table

    # Navigating to hemisphere image site
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)

    # Loop to scrape image info with time delay to account for browser navigation
    hemisphere_image_urls = []

    for i in range (4):
        time.sleep(5)
        images = browser.find_by_tag('h3')
        images[i].click()
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        partial_url = soup.find("img", class_="wide-image")["src"]
        image_title = soup.find("h2",class_="title").text
        image_url = 'https://astrogeology.usgs.gov'+ partial_url
        image_dict = {"title":image_title,"image_url":image_url}
        hemisphere_image_urls.append(image_dict)
        browser.back()    
    #print(hemisphere_image_urls)

    # Adding to dict
    mars_info["hemispheres"] = hemisphere_image_urls

    # Quit browser
    browser.quit

    return mars_info
