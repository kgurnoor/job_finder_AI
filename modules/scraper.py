# modules/scraper.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import re

BASE_URL = "https://www.herkey.com"
JOBS_URL = "https://www.herkey.com/jobs"
EVENTS_URL = "https://events.herkey.com/events"
SESSIONS_URL = "https://www.herkey.com/sessions"
MENTORSHIP_URL = "https://www.herkey.com/groups"

def scrape_jobs(query, work_mode=None, job_type=None):
    """Scrapes job listings for a list format."""

    url = f"{JOBS_URL}/search?"
    params = {}
    if work_mode:
        params['work_mode'] = work_mode
    if job_type:
        params['job_type'] = job_type
    if query:
        params['q'] = query

    if params:
        url += "&".join(f"{key}={value}" for key, value in params.items())

    job_listings = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        job_elements = soup.find_all('div', class_='MuiBox-root css-9452eu')  # Replace

        for job_element in job_elements:
            try:
                title_element = job_element.find('p', class_='MuiTypography-root MuiTypography-body1 css-1uqf52t')  # Replace
                title = title_element.text.strip() if title_element else "N/A"
                sanitized_title = quote(title) if title else "N/A"  # Sanitize for URL

                company_element = job_element.find('p', class_='MuiTypography-root MuiTypography-body2 css-1x1a4c1')  # Replace
                company = company_element.text.strip() if company_element else "N/A"

                location_element = job_element.find('p', class_='MuiTypography-root MuiTypography-body2 capitalize css-y9og3k')  # Replace
                location = location_element.text.strip() if location_element else "N/A"

                link = extract_job_link(job_element, title, BASE_URL)  # Use the link extraction function

                job_listings.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': link,
                })

            except Exception as e:
                print(f"Error extracting job data: {e}")
                continue
    except requests.exceptions.RequestException as e:
        print(f"Error scraping jobs: {e}")
    except Exception as e:
        print(f"Error parsing jobs: {e}")
    return job_listings

def extract_job_link(job_element, title, base_url):
    """Extracts the job link using various strategies."""

    link = "N/A"
    try:
        # 1. Try to find a direct link on the title
        title_link_element = job_element.find('a', class_='MuiTypography-root MuiTypography-body1 css-1uqf52t')  # Replace if different
        if title_link_element and title_link_element.has_attr('href'):
            link = urljoin(base_url, title_link_element['href'])
            return link

        # 2. Try to find a general "Apply" button link (if applicable)
        apply_button = job_element.find('a', class_='MuiButtonBase-root')  # Example - Replace if different
        if apply_button and apply_button.has_attr('href'):
            link = urljoin(base_url, apply_button['href'])
            if "/jobs/" in link:  # Basic check to see if it's a job link
                return link

        # 3. Try to extract the job ID and construct the link (Most reliable)
        job_id = extract_job_id(job_element)
        if job_id and title:
            sanitized_title = quote(title)
            link = f"{base_url}/jobs/{sanitized_title}/{job_id}"
            return link

    except Exception:
        pass  # If all methods fail, return "N/A"

    return link

def extract_job_id(job_element):
    """Extracts the job ID from the job listing HTML."""

    job_id = None
    try:
        # Examples (Adapt these to the actual HerKey HTML)
        # 1. From a data- attribute:
        # job_id_element = job_element.find('div', class_='job-card')
        # job_id = job_id_element.get('data-job-id')

        # 2. From the Easy Apply button URL:
        apply_button = job_element.find('a', class_='MuiButtonBase-root')  # Example
        if apply_button and apply_button.has_attr('href'):
            match = re.search(r'/jobs/.+?/(\d+)', apply_button['href'])
            if match:
                job_id = match.group(1)

        # 3. From a hidden input field:
        # hidden_input = job_element.find('input', {'type': 'hidden', 'name': 'job_id'})
        # job_id = hidden_input['value']

        # 4. If it's in a script tag (more complex):
        # script_tag = job_element.find('script', string=re.compile(r'jobId: (\d+)'))
        # if script_tag:
        #     match = re.search(r'jobId: (\d+)', script_tag.string)
        #     job_id = match.group(1)
    except Exception:
        pass  # If ID not found, return None
    return job_id

def scrape_events():
    """Scrapes events for a list format."""

    events_list = []
    try:
        response = requests.get(EVENTS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        event_elements = soup.find_all('div', class_='event-item')  # Example
        for event_element in event_elements:
            try:
                title = event_element.find('h3', class_='event-title').text.strip() if event_element.find('h3', class_='event-title') else "N/A"
                date = event_element.find('span', class_='event-date').text.strip() if event_element.find('span', class_='event-date') else "N/A"
                link_tag = event_element.find('a', class_='event-link')
                link = urljoin(EVENTS_URL, link_tag['href']) if link_tag and link_tag.has_attr('href') else "N/A"
                events_list.append({
                    'title': title,
                    'date': date,
                    'link': link
                })
            except Exception as e:
                print(f"Error extracting event data: {e}")
                continue
    except requests.exceptions.RequestException as e:
        print(f"Error scraping events: {e}")
    except Exception as e:
        print(f"Error parsing events: {e}")
    return events_list

def scrape_sessions():
    """Scrapes sessions for a list format."""

    sessions_list = []
    try:
        response = requests.get(SESSIONS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        session_elements = soup.find_all('div', class_='MuiBox-root css-1q1rcm9')  # Main session container
        for session_element in session_elements:
            try:
                title_element = session_element.find('a', class_='MuiTypography-root MuiTypography-inherit MuiLink-root MuiLink-underlineAlways css-140updn')
                link = urljoin(SESSIONS_URL, title_element['href']) if title_element and title_element.has_attr('href') else "N/A"
                title = title_element.text.strip() if title_element else "N/A"
                date_element = session_element.find('div', class_='MuiGrid-root MuiGrid-item MuiGrid-grid-xs-3 css-3bir93')
                date = date_element.text.strip() if date_element else "N/A"
                sessions_list.append({
                    'title': title,
                    'date': date,
                    'link': link
                })
            except Exception as e:
                print(f"Error extracting session data: {e}")
                continue
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sessions page: {e}")
    except Exception as e:
        print(f"Error parsing sessions page: {e}")
    return sessions_list

def scrape_mentorships():
    """Scrapes mentorship programs for a list format."""

    mentorships_list = []
    try:
        response = requests.get(MENTORSHIP_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        mentorship_elements = soup.find_all('div', class_='group-card')  # Example
        for mentorship_element in mentorship_elements:
            try:
                title = mentorship_element.find('h5', class_='group-title').text.strip() if mentorship_element.find('h5', class_='group-title') else "N/A"
                description = mentorship_element.find('p', class_='group-description').text.strip() if mentorship_element.find('p', class_='group-description') else "N/A"
                link_tag = mentorship_element.find('a', class_='group-link')
                link = urljoin(MENTORSHIP_URL, link_tag['href']) if link_tag and link_tag.has_attr('href') else "N/A"
                mentorships_list.append({
                    'title': title,
                    'description': description,
                    'link': link
                })
            except Exception as e:
                print(f"Error extracting mentorship data: {e}")
                continue
    except requests.exceptions.RequestException as e:
        print(f"Error scraping mentorships: {e}")
    except Exception as e:
        print(f"Error parsing mentorships: {e}")
    return mentorships_list

def scrape_relevant_data(query):
    """Scrapes relevant data based on the user's query."""

    query_lower = query.lower()

    work_mode = None
    job_type = None

    if "work from home" in query_lower:
        work_mode = "work-from-home"
    elif "hybrid" in query_lower:
        work_mode = "hybrid"
    elif "part-time" in query_lower:
        job_type = "part-time"
    elif "full-time" in query_lower:
        job_type = "full-time"

    if "jobs" in query_lower:
        return scrape_jobs(query, work_mode, job_type)
    elif "events" in query_lower:
        return scrape_events()
    elif "mentorship" in query_lower:
        return scrape_mentorships()
    elif "sessions" in query_lower:
        return scrape_sessions()
    else:
        return None