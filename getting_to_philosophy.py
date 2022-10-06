from bs4 import BeautifulSoup, NavigableString, Tag
import requests
import sys

def main():
    url = sys.argv[1]
    cur_hops=0
    MAX_HOPS = 100
    visited_urls = set()

    while cur_hops<=MAX_HOPS:
        #in each loop, if current URL is philosophy page we have finished successfully
        #else, find first valid link from current URL, if no link found, or the next URL has already been visited, we have finished unsuccessfully
        #else, we set URL to link found, increase counter, and continue loop
        print(url)
        visited_urls.add(url)
        body = requests.get(url).text
        soup = BeautifulSoup(body, "html.parser")
        title = soup.find(id="firstHeading")
        
        if title.text=="Philosophy":
            print(str(cur_hops)+ " hops")
            return
        
        link = find_first_link(soup)
        if not link:
            print("No link found on article page. Cannot explore any further.")
            return
        if link in visited_urls:
            print(link)
            print("Loop detected. Cannot find Philosophy.")
            return
        
        url=link
        cur_hops+=1
    #loop exited without finding philosophy
    print(f"Philosophy not found within {MAX_HOPS} hops. Exiting.")

def find_first_link(soup):
    #returns first link (string) found under element with class "mw-parser-output" or empty string if none found
    p = soup.find(id="mw-content-text").find(class_="mw-parser-output").find("p", recursive=False)
    while p:
        #Iterate over all p tags that are direct descendants of "mw-parser-output" class
        link = get_valid_link_from_p(p.descendants)
        if link:
            return link
        p = p.find_next_sibling("p", recursive=False)
    return ""

def get_valid_link_from_p(descendants):
    #returns first valid link (string) found in descendants of a <p> tag or empty string if none found
    parens=0
    for child in descendants:
        if isinstance(child, NavigableString):
            for char in child.string:
                if char=="(":
                    parens+=1
                if char==")":
                    parens-=1
        if isinstance(child, Tag) and has_valid_link(child, parens):
            #href is in format "/wiki/{article_name}" so we must prepend the rest of the URL
            return("https://en.wikipedia.org"+child.get("href"))
    return ""

def has_valid_link(child, parens):
    #returns boolean of whether child contains a valid link
    if parens!=0:
        #Child cannot be inside of parens
        return False
    
    if child.name!="a":
        #Child must be <a> tag
        return False

    class_list = child.get("class")
    if class_list and "new" in child.get("class"):
        #Cannot be a red link (link without corresponding page)
        return False
    
    link = child.get("href")
    if not link:
        #Child must have link
        return False
    split_link = link.split("/")
    if len(split_link)!=3 or split_link[1] != "wiki":
        #Child must be in format "/wiki/{article_name}"
        return False
    
    while(child):
        #Child and all ancestors must not be italicized or have "coordinates" as id
        if child.name=="i" or child.get("id")=="coordinates":
            return False
        child = child.parent
                
    return True

if __name__ == "__main__":
    main()

