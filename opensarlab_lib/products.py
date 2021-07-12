from datetime import date
import glob
import os
import re
import requests
import sys
from typing import List

from opensarlab_lib.edl import EarthdataLogin

from hyp3_sdk import asf_search, Batch

#########################
#  Hyp3v1 API Functions #
#########################


def get_hyp3_subscriptions(login: EarthdataLogin, group_id=None) -> dict:
    """
    Takes an EarthdataLogin object and returns a list of associated, enabled subscriptions
    Returns None if there are no enabled subscriptions associated with Hyp3 account.
    """

    assert type(login) == EarthdataLogin, 'Error: login must be an EarthdataLogin object'

    while True:
        subscriptions = login.api.get_subscriptions(enabled=True, group_id=group_id)
        try:
            if subscriptions['status'] == 'ERROR' and \
                  subscriptions['message'] == 'You must have a valid API key':
                creds = login.api.reset_api_key()
                login.api.api = creds['api_key']
        except (KeyError, TypeError):
            break
    subs = []
    if not subscriptions:
        if not group_id:
            print(f"Found no subscriptions for Hyp3 user: {login.username}")
        else:
            print(f"Found no subscriptions for Hyp3 user: {login.username}, in group: {group_id}")
    else:
        for sub in subscriptions:
            subs.append(f"{sub['id']}: {sub['name']}")
    return subs


def get_subscription_products_info(subscription_id: int, login: EarthdataLogin, group_id=None) -> list:

    assert type(subscription_id) == str, f'Error: subscription_id must be a string, not a {type(subscription_id)}'
    assert type(login) == EarthdataLogin, f'Error: login must be an EarthdataLogin object, not a {type(login)}'

    products = []
    page_count = 0
    while True:
        product_page = login.api.get_products(
            sub_id=subscription_id, page=page_count, page_size=100, group_id=group_id)
        try:
            if product_page['status'] == 'ERROR'and \
                  product_page['message'] == 'You must have a valid API key':
                creds = login.api.reset_api_key()
                login.api.api = creds['api_key']
                continue
        except (KeyError, TypeError):
            page_count += 1
            pass
        if not product_page:
            break
        for product in product_page:
            products.append(product)
    return products


def get_subscription_granule_names_ids(subscription_id: int, login: EarthdataLogin) -> dict:

    assert type(subscription_id) == str, f'Error: subscription_id must be a string, not a {type(subscription_id)}'
    assert type(login) == EarthdataLogin, f'Error: login must be an EarthdataLogin object, not a {type(login)}'

    jobs_list = login.api.get_jobs(sub_id=subscription_id)
    granules = dict()
    for job in jobs_list:
        granules.update({job['granule']: job['id']})
    return granules


def get_wget_cmd(url: str, login: EarthdataLogin) -> str:
    cmd = f"wget -c -q --show-progress --http-user={login.username} --http-password={login.password} {url}"
    return cmd


#########################
#  Hyp3v2 API Functions #
#########################

def get_RTC_projects(hyp3):
    return hyp3.my_info()['job_names']

def get_job_dates(jobs: List[str]) -> List[str]:
    dates = set()
    for job in jobs:
        for granule in job.job_parameters['granules']:
            dates.add(date_from_product_name(granule).split('T')[0])
    return list(dates)

def filter_jobs_by_date(jobs, date_range):
    remaining_jobs = Batch()
    for job in jobs:
        for granule in job.job_parameters['granules']:
            dt = date_from_product_name(granule).split('T')[0]
            acquisition_date = date(int(dt[:4]), int(dt[4:6]), int(dt[-2:]))
            if date_range[0] <= acquisition_date <= date_range[1]:
                remaining_jobs += job
                break
    return remaining_jobs

def get_paths_orbits(jobs):
    for job in jobs:
        granule_metadata = asf_search.get_metadata(job.job_parameters['granules'][0])
        job.path = granule_metadata['path']
        job.orbit_direction = granule_metadata['flightDirection']
    return jobs

def filter_jobs_by_path(jobs, paths):
    if 'All Paths' in paths:
        return jobs
    remaining_jobs = Batch()
    for job in jobs:
        if job.path in paths:
            remaining_jobs += job
    return remaining_jobs

def filter_jobs_by_orbit(jobs, orbit_direction):
    remaining_jobs = Batch()
    for job in jobs:
        if job.orbit_direction == orbit_direction:
            remaining_jobs += job
    return remaining_jobs


def get_vertex_granule_info(granule_name: str, processing_level: int) -> dict:
    """
    Takes a string granule name and int processing level, and returns the granule info as json.<br><br>
    preconditions:
    Requires AWS Vertex API authentification (already logged in).
    Requires a valid granule name.
    Granule and processing level must match.
    """
    assert type(granule_name) == str, 'Error: granule_name must be a string.'
    assert type(processing_level) == str, 'Error: processing_level must be a string.'

    vertex_API_URL = "https://api.daac.asf.alaska.edu/services/search/param"
    try:
        response = requests.post(
            vertex_API_URL,
            params=[('granule_list', granule_name), ('output', 'json'),
                    ('processingLevel', processing_level)]
        )
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        sys.exit(1)
    else:
        if len(response.json()) > 0:
            json_response = response.json()[0][0]
            return json_response
        else:
            print("get_vertex_granule_info() failed.\ngranule/processing level mismatch.")

def get_product_info(granules: dict, products_info: list, date_range: list) -> dict:
    paths = []
    directions = []
    urls = []
    vertex_API_URL = "https://api.daac.asf.alaska.edu/services/search/param"
    for granule_name in granules:
        dt = date_from_product_name(granule_name)
        if dt:
            dt = dt.split('T')[0]
        else:
            continue
        if date(int(dt[:4]), int(dt[4:6]), int(dt[-2:])) >= date_range[0]:
            if date(int(dt[:4]), int(dt[4:6]), int(dt[-2:])) <= date_range[1]:
                parameters = [('granule_list', granule_name), ('output', 'json')]
                try:
                    response = requests.post(
                        vertex_API_URL,
                        params=parameters,
                        stream=True
                    )
                except requests.exceptions.RequestException as e:
                    print(e)
                    sys.exit(1)
                json_response = None
                if response.json()[0]:
                    json_response = response.json()[0][0]
                local_queue_id = granules[granule_name]
                for p_info in products_info:
                    if p_info['local_queue_id'] == local_queue_id:
                        try:
                            paths.append(json_response['track'])
                            directions.append(json_response['flightDirection'])
                            urls.append(p_info['url'])
                        except TypeError:
                            print(f"TypeError: json_response for {granule_name}: {json_response}")
                            pass
                        break
    return {'paths': paths, 'directions': directions, 'urls': urls}

def date_from_product_name(product_name: str) -> str:
    regex = "\w[0-9]{7}T[0-9]{6}"
    results = re.search(regex, product_name)
    if results:
        return results.group(0)
    else:
        return None

def get_products_dates(products_info: list) -> list:
    dates = []
    for info in products_info:
        date_regex = "\w[0-9]{7}T[0-9]{6}"
        date_strs = re.findall(date_regex, info['granule'])
        if date_strs:
            for d in date_strs:
                dates.append(d[0:8])
    dates.sort()
    dates = list(set(dates))
    return dates

# get_products_dates_insar will be deprecated in the
# near future as it is now duplicted in get_products_dates
def get_products_dates_insar(products_info: list) -> list:
    dates = []
    for info in products_info:
        date_regex = "\w[0-9]{7}T[0-9]{6}"
        date_strs = re.findall(date_regex, info['granule'])
        if date_strs:
            for d in date_strs:
                dates.append(d[0:8])
    dates.sort()
    dates = list(set(dates))
    return dates

def get_polarity_from_path(path: str) -> str:
    """
    Takes a path to a HyP3 product containing its polarity in its filename
    Returns the polarity string or none if not found
    """
    path = os.path.basename(path)
    regex = "(v|V|h|H){2}"
    return re.search(regex, path).group(0)

def get_RTC_polarizations(base_path: str) -> list:
    """
    Takes a string path to a directory containing RTC product directories
    Returns a list of present polarizations
    """
    assert type(base_path) == str, 'Error: base_path must be a string.'
    assert os.path.exists(base_path), f"Error: select_RTC_polarization was passed an invalid base_path, {base_path}"
    paths = []
    pths = glob.glob(f"{base_path}/*/*.tif")
    if len(pths) > 0:
        for p in pths:
            filename = os.path.basename(p)
            polar_fname = re.search("^\w[\--~]{5,300}(_|-)(vv|VV|vh|VH|hh|HH|hv|HV).(tif|tiff)$", filename)
            if polar_fname:
                paths.append(polar_fname.string.split('.')[0][-2:])
    if len(paths) > 0:
        return list(set(paths))
    else:
        print(f"Error: found no available polarizations.")