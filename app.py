from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime

headers = {
  'authority': 'emma.msrb.org',
  'accept': '*/*',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'content-type': 'application/json; charset=utf-8',
  'cookie': '__utmz=247245968.1686550781.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ga_X7VJ8QGMQ9=GS1.1.1686550781.1.1.1686550795.0.0.0; Disclaimer6=msrborg; acceptCookies=true; _ga=GA1.2.894476767.1686550782; _gid=GA1.2.96542170.1686556225; ASP.NET_SessionId=f2wyvlgrq3evlyh1dyzds3w2; __utma=247245968.246801298.1686550781.1686555180.1686633036.3; __utmc=247245968; _gat=1; __utmt=1; __utmb=247245968.10.10.1686633036; AWSALB=ONndevLvEs6Fjr2PLstb9sxLnnAlFvlA98LeeopP7yEJMZ4mVi5xXvrxCmQu9bZenpmJu89xChtq4oIu55CHgSPeMx4fHnYebx7iXzUHXcfl3igLmcxLk9bku+k3; AWSALBCORS=ONndevLvEs6Fjr2PLstb9sxLnnAlFvlA98LeeopP7yEJMZ4mVi5xXvrxCmQu9bZenpmJu89xChtq4oIu55CHgSPeMx4fHnYebx7iXzUHXcfl3igLmcxLk9bku+k3',
  'referer': 'https://emma.msrb.org/Security/Details/A1EDCE70803CFA3144A8D6DB4DC27FA4B',
  'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"',
  'sec-fetch-dest': 'empty',
#   'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
  'x-requested-with': 'XMLHttpRequest'
}
id = 'AAB9755FD985D7A302CB102D1384FDBDE'

current_datetime = datetime.datetime.now()
timestamp = int(current_datetime.timestamp() * 1000)
timestamp_str = str(timestamp)



response = requests.get(f"https://emma.msrb.org/Security/RatingsPartialView?cusip9={id}&_={timestamp_str}", headers=headers) 

html_data = response.text

soup = BeautifulSoup(html_data , 'html.parser')

agencies =['fitchRatings','krollRatings','moodysRatings','snpRatings']
Rating_data={}

for agency in agencies:
    fitch_div = soup.find('div', id=agency)
    fitch_data = fitch_div.find('table', class_='ratingDataGrid')

    if fitch_data==None:
        
        kroll_data = fitch_div.find('div', id=f'{agency}DisclaimerDiv') 
        if kroll_data==None :
            modified_agency = agency[:len(agency)-1]     #.replace('s', '')
            kroll_data = fitch_div.find('div', id=f'{modified_agency}DisclaimerDiv').text.strip()
            Rating_data[agency]=kroll_data
      
        else:
            kroll_data = fitch_div.find('div', id=f'{agency}DisclaimerDiv').text.strip()
            Rating_data[agency]=kroll_data
        
    else:
        rows = fitch_data.find_all('tr')
        nested_list = [[column.text.strip() for column in row.find_all('td')] for row in rows]
      
        paragraph=fitch_div.find('div', class_='col-lg-8 pull-left').text.strip()
        paragraph_data=paragraph.split()
        nested_list.append([f"{' '.join(paragraph_data)} {fitch_div.find('div', class_='col-lg-4 pull-left pr-0').text.strip()}"])
       
        Rating_data[agency]=nested_list


data_fram={}

for key, value in Rating_data.items():
    transformed_data = []
    
    if isinstance(value, list):
        for sublist in value:
            
            if len(sublist)==4:
              
                if sublist[1]:
                    transformed_data.append(f"{sublist[0]}:{sublist[1]}")
                else:
                    transformed_data.append(f"{sublist[0]}: - ")
                if sublist[3]:
                    transformed_data.append(f"{sublist[2]}:{sublist[3]}")
                else:
                    transformed_data.append(f"{sublist[2]}: - ")

            else:
                transformed_data.append(f"{sublist[0]}")
        data_fram[key]=';;'.join(transformed_data) 
    else:
        data_fram[key]=value 
        


df = pd.DataFrame.from_dict(data_fram, orient='index')

df = df.transpose()


df.to_csv('ratings.csv', index=False)

print("Data successfully converted and saved to 'ratings.csv'.")











