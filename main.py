import re
import time
import logging
import asyncio
import json
import bs4
import aiohttp
from datetime import datetime
from urllib.parse import urlencode
from concurrent.futures import ProcessPoolExecutor

def extract_job_info(html):
    # creating a soup object with lxml parser
    soup = bs4.BeautifulSoup(html, "lxml") 
    # finding all h2 tags with class attribute named 'jobtitle'   
    jobs = soup.find_all('h2', class_="jobtitle")
    job_lists = []
    for job in jobs:
        job_data = {}
        job_data["position"] = job.a.get('title')
        job_data["page_url"] = f"{BASE_URL}{job.a.get('href')}"
        comp_loc = job.find_next_sibling('div')
        job_data["company_name"] = comp_loc.find('span', class_="company").text.strip()
        job_data["location"] = comp_loc.find('span', class_="location").text.strip()
        table = job.find_next_sibling('table')
        
        # salary data is not available for all jobs
        try:
            job_data["salary"] = table.find('span', class_="salary").text.strip()
        except AttributeError:
            job_data["salary"] = "NA"

        job_data["summary"] = table.find('span', class_="summary").text.strip()
        job_data["date"] = table.find('span', class_="date").text.strip()
        job_lists.append(job_data)
    return job_lists

def sort_by_starting_salary(salary_string):
    # from salary string finding the max and min salary
    sal = re.findall(r'[1-9][0-9]*', salary_string.replace(',',''))

    # if salary is per month then return the yearly starting salary
    # if salary is not given return 0
    # else return the yearly starting salary
    if salary_string.endswith('month'):
        return int(sal[0])*12
    elif salary_string=="NA":
        return 0
    else:
        return int(sal[0])

async def fetch_url(session, url, page_no):
    # getting the running loop
    loop = asyncio.get_running_loop()
    async with session.get(url) as resp:
        print(f"fetching page {page_no}...")
        html = await resp.text()
        print(f"extracting information from page {page_no}...")
        # cpu bound work sent to worker pool
        data = await loop.run_in_executor(None, extract_job_info, html)
        return jobs_data.extend(data)


async def run(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(urls):
            task = asyncio.ensure_future(fetch_url(session, url, i+1))
            tasks.append(task)
            
        responses = await asyncio.gather(*tasks)
    return responses

if __name__=="__main__":

    BASE_URL = "https://www.indeed.co.in"
    # here q for role and l is for location
    params = {"q":"software developer", "l":"Bengaluru"}

    # initializing the urls list with the first element
    # as the first urls takes no start parameter
    urls = [f"{BASE_URL}/jobs?{urlencode(params)}"]

    # each page consists of 10 search result
    for i in range(10, 1000, 10):
        params["start"] = str(i)
        urls.append(f"{BASE_URL}/jobs?{urlencode(params)}")
    
    # All jobs data will be stored in this list
    jobs_data = []

    # here we will use ProcessPooling to do the CPU bound work
    executor = ProcessPoolExecutor(max_workers=15)
    # creating the event loop
    loop = asyncio.get_event_loop()
    # setting the executor
    loop.set_default_executor(executor)
    future = asyncio.ensure_future(run(urls))
    loop.run_until_complete(future)

    print("Sorting the jobs data according to maximum statrting salary")
    data = sorted(jobs_data, key=lambda x:sort_by_starting_salary(x['salary']), reverse=True)
    jobs_dict = {f"{datetime.now()}": data}
    with open('jobs.json', 'w+') as fd:
        print("Writing json file in jobs.json file")
        json.dump(jobs_dict, fd)
