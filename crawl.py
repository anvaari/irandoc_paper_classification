from bs4 import BeautifulSoup as bs
import requests 
import pandas as pd
from datetime import date as dt

#Extract ID of article from link of it
def find_id(link):
    fa=link.find('fa')
    for i in range(fa-2,0,-1):
        if link[i]=='-':
            break
    return int(link[i+1:fa-1])
#Remove parenthese from name of Article 
def make_name_clear(name):
    if name.find('(')==-1:
        return name
    elif name[name.rfind('(' )+1].isdigit():
        return name[:name.rfind('(')]
    else:
        return name


        
#Input
pdf_dir='/home/anvaari/Learn/Hamtech/Text Classification/Data/PDFs/'
    
#Urls
main_site='https://jipm.irandoc.ac.ir/'
main_page=requests.get('https://jipm.irandoc.ac.ir/browse.php?&slct_pg_id=45&sid=1&slc_lang=fa',verify = False)

#Crawl First Page and extract links
soup=bs(main_page.text,'html.parser')
sec_links=soup.find_all('div',class_='yw_text_small persian')
sec_urls={} #URLs of each section of journal
for sec in sec_links:
    a_tag=sec.find_all('a')[-1]
    sec_urls[a_tag.text.strip('\n').strip()]=main_site+a_tag['href']
    
#Creat DataFrame
data=pd.DataFrame(columns=['Name','Date','Abstract','Content Type','Subject','Keywords','Authors','University','Url'])
data_en=pd.DataFrame(columns=['Name','Date','Abstract','Content Type','Subject','Keywords','Authors','University','Url'])

for url in sec_urls.values():
    sec_page=requests.get(url,verify=False)
    soup=bs(sec_page.text,'html.parser')
    art_links=soup.find_all('span',class_='abstract_title')
    for art in art_links:
        art_id=find_id(art.find('a')['href']) #Article ID
        #Download Pdfs
        pdf_url=main_site+art.find('a')['href'][:-4]+'pdf'
        pdf=requests.get(pdf_url,allow_redirects=True,verify=False)
        open(pdf_dir+'{}.pdf'.format(art_id), 'wb').write(pdf.content)
        #Add Url to DataFrame
        data.at[art_id,'Url']=main_site+art.find('a')['href']
        data_en.at[art_id,'Url']=main_site+art.find('a')['href']
        
        #Creat Soup ftom body of XML
        art_xml_url=main_site+'xml_out.php?a_id={}'.format(art_id)
        art_xml=requests.get(art_xml_url, verify=False)
        soup_xml=bs(art_xml.text,'lxml')
        art_data=soup_xml.find('articleset')
        #Name
        data.at[art_id,'Name']=make_name_clear(art_data.find('title_fa').get_text(strip=True))
        data_en.at[art_id,'Name']=art_data.find('title').get_text()
        #Date
        date_xml=soup_xml.find_all('pubdate')[1]
        date=pd.Series([date_xml.find('year').text,date_xml.find('month').text,date_xml.find('day').text]).astype(int)
        data.at[art_id,'Date']=dt(date[0],date[1],date[2])
        data_en.at[art_id,'Date']=dt(date[0],date[1],date[2])
        
        #Abstract
        abs_soup=bs(art_data.find('abstract_fa').get_text(),'html.parser')
        data.at[art_id,'Abstract']=abs_soup.get_text()
        data_en.at[art_id,'Abstract']=art_data.find('abstract').get_text()
        #Content Type
        data.at[art_id,'Content Type']=art_data.find('content_type_fa').get_text()
        data_en.at[art_id,'Content Type']=art_data.find('content_type').get_text()
        #Subjects
        data.at[art_id,'Subject']=art_data.find('subject_fa').get_text()
        data_en.at[art_id,'Subject']=art_data.find('subject').get_text()
        #Keywords
        data.at[art_id,'Keywords']=art_data.find('keyword_fa').get_text()
        data_en.at[art_id,'Keywords']=art_data.find('keyword').get_text()
        # Authors and Universities
        auth_list=art_data.find_all('author')
        auth_names=[]
        auth_names_en=[]
        auth_uni=[]
        auth_uni_en=[]
        for author in auth_list:
            name=''
            name_en=''
            name+=author.find('first_name_fa').get_text()+' '
            name+=author.find('last_name_fa').get_text()
            name_en+=author.find('first_name').get_text()+' '
            name_en+=author.find('last_name').get_text()
            auth_names.append(name)
            auth_names_en.append(name_en)
            auth_uni.append(author.find('affiliation_fa').get_text())
            auth_uni_en.append(author.find('affiliation').get_text())
        #add autor and universities to DataFrame
        data.at[art_id,'Authors']=auth_names
        data_en.at[art_id,'Authors']=auth_names_en
        data.at[art_id,'University']=auth_uni
        data_en.at[art_id,'University']=auth_uni_en
#data.to_excel('data.xlsx')
#data_en.to_excel('data_en.xlsx')