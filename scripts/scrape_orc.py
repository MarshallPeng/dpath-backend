from bs4 import BeautifulSoup
import requests
import re

from service.FirebaseService import FirebaseService
import urls


def get_course(url):

    # Set up
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    main = soup.find("div", {"id": "main"})
    course_info = {}

    # get Title number and description
    current = main.next_element.next_element.next_element
    course_num = current.text.replace(" ", '')  # course number
    title = current.next_element.next_element.strip()    # Title
    description = main.next_element.next_sibling.text.strip()   # description

    course_info['courseNumber'] = course_num
    course_info['title'] = title
    course_info['description'] = description

    # Find where instructor header is and get text after it
    category = main.find('h3', text=re.compile('Instructor'))
    if category is not None:
        course_info['instructors'] = category.next_element.next_element.strip()
    else:
        course_info['instructors'] = ""

    # find Cross Listed courses and get text after it
    category = main.find('h3', text=re.compile('Cross Listed Courses'))
    if category is not None:
        if hasattr(category.next_element.next_element, 'text'):
            course_info['xlist'] = category.next_element.next_element.text.strip()
        else:
            course_info['xlist'] = str(category.next_element)

    else:
        course_info['xlist'] = ""

    # Find Distributives text and get text after it
    category = main.find('h3', text=re.compile('Distributive and/or World Culture'))
    if category is not None:
        course_info['distributives'] = str(category.next_element.next_element)
    else:
        course_info['distributives'] = ""

    # Find Prerequisite section and get text after it.
    # This one is different because of a ton of <a> headers in text.
    category = main.find('h3', text=re.compile('Prerequisite'))
    if category is not None and hasattr(category, 'name') and category.name == 'h3':
        content = ""
        cur_pos = category.next_element.next_element

        while not hasattr(cur_pos, 'name') or (cur_pos.name != 'h3' and cur_pos.name != 'div'):
            if hasattr(cur_pos, 'text'):
                content += cur_pos.text
            else:
                content += str(cur_pos)
            cur_pos = cur_pos.next_sibling

        course_info['prerequisites'] = content
    else:
        course_info['prerequisites'] = ""

    # determine when course is offered.
    category = main.find('h3', text=re.compile('Offered'))
    if category is not None:
        course_info['offered'] = str(category.next_element.next_element)
    else:
        course_info['offered'] = ""

    return course_info


def get_all_course_urls_for_dept(url):
    """
    scrape all links on courses page for department.
    :param url:
    :return:
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    link_list = soup.find("ul", {"class": "sc-child-item-links"}).find_all("a")
    return [urls.base_url + link.get('href') for link in link_list]

if __name__ == '__main__':
    row_number = 0
    firebaseService = FirebaseService()
    for dept_url in [urls.biol_url, urls.cosc_url, urls.econ_url, urls.engs_url, urls.govt_url, urls.hist_url]:
        urls = get_all_course_urls_for_dept(dept_url)

        for url in urls:
            try:
                course_info = get_course(url)
                course_info['row_number'] = row_number

                # Change COSC1 to COSC01 so that firebase orders it properly.
                if len(course_info['courseNumber']) == 5:
                    course_info['courseNumber'] = course_info['courseNumber'][:-1] + "0" + course_info['courseNumber'][-1:]
                firebaseService.set_course_info(course_info)
            except BaseException as error:
                print error.message
            row_number += 1