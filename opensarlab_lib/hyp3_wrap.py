from datetime import date
from typing import List

from hyp3_sdk import Batch

import asf_search as asf

from opensarlab_lib.product_name_parse import date_from_product_name

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
            aquistion_date = date(int(dt[:4]), int(dt[4:6]), int(dt[-2:]))
            if date_range[0] <= aquistion_date <= date_range[1]:
                remaining_jobs += job
                break
    return remaining_jobs

def get_paths_orbits(jobs):
    for job in jobs:
        granule_metadata = asf.granule_search(job.job_parameters['granules'])[0]
        job.path = granule_metadata.properties['pathNumber']
        job.orbit_direction = granule_metadata.properties['flightDirection']
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
