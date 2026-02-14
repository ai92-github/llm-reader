# Webpage to LLM Ready Input Text

Pre-processing webpage before giving it as input to the LLM improves extraction/scraping accuracy especially if you want to extract website and image links, tables required for most scraping operations like scraping an e-commerce website.

Use this library to turn any webpage/url to LLM friendly text. Fully open source alternative to firecrawl and jina reader api.

You can also refer to my other repo [AI-web_scraper](https://github.com/m92vyas/AI-web_scraper) for direct scraping tools that will do `web search` and `scrapes multiple links` with `just a simple query`. It supports multiple LLMs, Web Search and Extracts Data as per your written instructions.

---

### Update for Old Users:

We have switched from Selenium to Playwright for concurrent web scraping support. Kindly install the required playwright dependencies as given below.

---

### Install:
```python
# install llm-reader
pip install git+https://github.com/m92vyas/llm-reader.git

# install playwright dependencies. we are using playwright for async/concurrent web scraping support.
playwright install  # to download browser.
playwright install-deps
```

### Import:
```python
from url_to_llm_text.get_html_text import get_page_source   # you can also use your own code or other services to get the page source
from url_to_llm_text.get_llm_input_text import get_processed_text   # pass html source text to get llm ready text
```

### Get processed LLM input text:

```python
url= <url_to_scrape>

# get html source text
# You can use your own function to get the html source text 

page_source = await get_page_source(url)

# get LLM ready input text from html source text

llm_text = await get_processed_text(page_source, url)
print(llm_text)

### or use asyncio ### 

# import asyncio
# url = <url_to_scrape>
# # creating a simple function here. View documentation for more parameter details.
# async def get_llm_ready_text(url: str) -> str:
#     page_source = await get_page_source(url)
#     llm_text = await get_processed_text(page_source, url)
#     return llm_text

# llm_text = asyncio.run(get_llm_ready_text(url))
# print(llm_text)
```

---

### Example Usage:

suppose we want to scrape the product name, main product page link, image link and price from the url "https://www.ikea.com/in/en/cat/corner-sofas-10671/" using any openai model.
```python
import requests
from url_to_llm_text.get_html_text import get_page_source
from url_to_llm_text.get_llm_input_text import get_processed_text

url = "https://www.ikea.com/in/en/cat/corner-sofas-10671/"

# get page html source text using this library function or any other means
page_source = await get_page_source(url)

# get llm ready text and pass the text to your LLM prompt template
llm_text = await get_processed_text(page_source, url)

# prompt template
prompt_format = """extract the product name, product link, image link and price for all the products given in the below webpage. The format should be:
{{
  "1": {{
        "Product Name": ,
        "Product Link": ,
        "Image Link": ,
        "Price":
        }},
  "2": {{
        "Product Name": ,
        ...
        }},
}}

webpage:
{llm_friendly_webpage_text}
"""

# calculate tokens and truncate the llm_text to fit your model context length and your requirements. sometimes you may need only initial part of the webpage.
# below we are manually truncating to 40000 characters. create a seperate function as per your need.
prompt = prompt_format.format(llm_friendly_webpage_text=llm_text[:40000])

api_key = <your openai api key>
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {api_key}"
}
payload = {
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": prompt
        }
  ]}],
  'seed': 0,
  "temperature": 0,
  "top_p": 0.001,
  # "max_tokens": 1024, # if you want to limit the output tokens. this may keep the output json structure incomplete.
  "n": 1,
  "frequency_penalty": 0, "presence_penalty": 0
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json()['choices'][0]['message']['content'])
```

```python
Output
{
    "1": {
        "Product Name": "SÖDERHAMN Corner sofa, 6-seat",
        "Product Link": "https://www.ikea.com/in/en/p/soederhamn-corner-sofa-6-seat-viarp-beige-brown-s69305895/",
        "Image Link": "https://www.ikea.com/in/en/images/products/soederhamn-corner-sofa-6-seat-viarp-beige-brown__0802771_pe768584_s5.jpg?f=xxs",
        "Price": "Rs.1,40,080"
    },
    "2": {
        "Product Name": "HOLMSUND Corner sofa-bed",
        "Product Link": "https://www.ikea.com/in/en/p/holmsund-corner-sofa-bed-borgunda-dark-grey-s49516894/",
        "Image Link": "https://www.ikea.com/in/en/images/products/holmsund-corner-sofa-bed-borgunda-dark-grey__1212713_pe910718_s5.jpg?f=xxs",
        "Price": "Rs.69,990"
    },
    "3": {
        "Product Name": "JÄTTEBO U-shaped sofa, 7-seat",
        "Product Link": "https://www.ikea.com/in/en/p/jaettebo-u-shaped-sofa-7-seat-with-chaise-longue-right-with-headrests-tonerud-grey-s39510618/",
        "Image Link": "https://www.ikea.com/in/en/images/products/jaettebo-u-shaped-sofa-7-seat-with-chaise-longue-right-with-headrests-tonerud-grey__1179836_pe896109_s5.jpg?f=xxs",
        "Price": "Rs.2,60,000"
    },
    "4": {
        "Product Name": "SÖDERHAMN Corner sofa, 4-seat",
        "Product Link": "https://www.ikea.com/in/en/p/soederhamn-corner-sofa-4-seat-with-open-end-tonerud-red-s09514420/",
        "Image Link": "https://www.ikea.com/in/en/images/products/soederhamn-corner-sofa-4-seat-with-open-end-tonerud-red__1213815_pe911323_s5.jpg?f=xxs",
        "Price": "Rs.98,540"
    },
    "5": {
        "Product Name": "JÄTTEBO Mod crnr sofa 2,5-seat w chaise lng",
        "Product Link": "https://www.ikea.com/in/en/p/jaettebo-mod-crnr-sofa-2-5-seat-w-chaise-lng-right-samsala-grey-beige-s09485173/",
        "Image Link": "https://www.ikea.com/in/en/images/products/jaettebo-mod-crnr-sofa-2-5-seat-w-chaise-lng-right-samsala-grey-beige__1109627_pe870119_s5.jpg?f=xxs",
        "Price": "Rs.1,32,000"
    },
    "6": {
        "Product Name": "JÄTTEBO Modular corner sofa, 6 seat",
        "Product Link": "https://www.ikea.com/in/en/p/jaettebo-modular-corner-sofa-6-seat-samsala-dark-yellow-green-s09485248/",
        "Image Link": "https://www.ikea.com/in/en/images/products/jaettebo-modular-corner-sofa-6-seat-samsala-dark-yellow-green__1109619_pe870109_s5.jpg?f=xxs",
        "Price": "Rs.2,06,000"
    },
    "7": {
        "Product Name": "SÖDERHAMN Corner sofa, 3-seat",
        "Product Link": "https://www.ikea.com/in/en/p/soederhamn-corner-sofa-3-seat-viarp-beige-brown-s09305884/",
        "Image Link": "https://www.ikea.com/in/en/images/products/soederhamn-corner-sofa-3-seat-viarp-beige-brown__0802711_pe768555_s5.jpg?f=xxs",
        "Price": "Rs.91,000"
    },
    ......}
```

---

### Documentation:
https://github.com/m92vyas/llm-reader/wiki/Documentation

---

### To Scrape and Crawl without getting Blocked:
- You can replace the `get_page_source` function with any paid API or use your own proxies or scraping setup to get the page source. e.g. you can use a pay-as-you-go option like [Scrappey](https://scrappey.com/?ref=rishi) to get page source without getting blocked and then pass the HTML to `get_processed_text` function to get LLM text for free.
- You can use [this guide](Cheaper_Alternative.md) to get an pay as you go option compared to subscription based solutions like Firecrawl.
- You can save in your subscription cost and also in downstream LLM usage cost.

---

### License:
This project is open-source and available under the MIT License.

---

### If you need OCR, Data Extraction, Table Extraction Solution:
Try out [ParseExtract](https://parseextract.com). Pay-As-you-Go Pricing, No Expiry, Accurate.

---

### To Redact your PDFs 100% locally:
Try out [RedactLocal](https://redactlocal.parseextract.com). 100% on device redactions. True redaction instead of just adding black bars.

---

### Support & Feedback:
- Share and consider giving a Star if you found this repo helpful.
- Open any issues or feature request.
- I'm available for full-time remote AI Engineer role.
- Also try out the other repo [AI-web_scraper](https://github.com/m92vyas/AI-web_scraper) and leave a Star there if you find it useful.
- Try out [ParseExtract](https://parseextract.com) for one stop API solution for OCR, Structured Data Extraction, Table Extraction for RAG, Agents, and other LLM Parsing / Extraction needs.
- Try out [RedactLocal](https://redactlocal.parseextract.com).
- Found this repo useful? You can do a one time sponsor [here](https://checkout.dodopayments.com/buy/pdt_HpJcB5tvN3euViX9c4v7M?quantity=1).
