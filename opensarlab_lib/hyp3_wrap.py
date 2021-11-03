from datetime import date
from typing import List, Tuple

from hyp3_sdk import Batch, HyP3

import asf_search as asf

from opensarlab_lib.product_name_parse import date_from_product_name

def get_job_dates(jobs: Batch) -> List[str]:
    """
    Takes: a Batch of HyP3 Jobs

    Returns: a list of string acquisition dates for Jobs in the Batch
    """
    dates = set()
    for job in jobs:
        for granule in job.job_parameters['granules']:
            dates.add(date_from_product_name(granule).split('T')[0])
    return list(dates)


def filter_jobs_by_date(jobs: Batch, date_range: List[date]) -> Batch:
    """
    Takes: a Batch of HyP3 Jobs and a list of two datetime.date
    objects, the minimum and maximum dates of a range.

    Returns: a filtered Batch of Jobs containing only Jobs falling within date_range
    """
    remaining_jobs = Batch()
    for job in jobs:
        for granule in job.job_parameters['granules']:
            dt = date_from_product_name(granule).split('T')[0]
            acquisition_date = date(int(dt[:4]), int(dt[4:6]), int(dt[-2:]))
            if date_range[0] <= acquisition_date <= date_range[1]:
                remaining_jobs += job
                break
    return remaining_jobs


def set_paths_orbits(jobs: Batch):
    """
    Takes: a Batch of HyP3 Jobs

    Looks up the path and orbit direction for each job and
    sets path and orbit_direction member variables for each Job object
    """
    for job in jobs:
        granule_metadata = asf.granule_search(job.job_parameters['granules'])[0]
        job.path = granule_metadata.properties['pathNumber']
        job.orbit_direction = granule_metadata.properties['flightDirection']


def filter_jobs_by_path(jobs: Batch, paths: Tuple[str]) -> Batch:
    """
    Takes: a Batch of HyP3 Jobs and a Tuple of string flight paths

    Returns: a filtered Batch containing only Jobs with flight paths in paths
    """
    if 'All Paths' in paths:
        return jobs
    remaining_jobs = Batch()
    for job in jobs:
        if job.path in paths:
            remaining_jobs += job
    return remaining_jobs

def filter_jobs_by_orbit(jobs: Batch, orbit_direction: str) -> Batch:
    """
    Takes: a Batch of HyP3 Jobs and a string orbit direction

    Returns: a filtered Batch containing only Jobs with the provided orbit direction
    """
    remaining_jobs = Batch()
    for job in jobs:
        if job.orbit_direction == orbit_direction:
            remaining_jobs += job
    return remaining_jobs
