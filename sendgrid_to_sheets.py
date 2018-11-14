import pandas as pd
from datetime import date
import calendar
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def category_decide(category_series):
    """Contains Category Dictionary and determins what category to assign a campaign
    """
    category_dic = { "MWF":"MWF", "Refund":"Refund","Promo": "National Promo",
                    "MWP":"Field Marketing Promo",
                    }
    return_list = []
    for row in list(category_series):
        for key in category_dic.keys():
            if key in row:
                return_list.append((category_dic[key]))
    return return_list
def mung_data(df):
    """
    Takes read in data frame and converts to needed columns
    """
    #Get every 8th one, which should be 'campaign total'
    total_df = df[df['Date'] == 'Campaign Total']
    # get the prior dates for the campaigns, index and subtract 7 for initial send date
    campaign_dates = (df[df['Date'] == 'Campaign Total'].index-7).values
    send_dates_list = df.iloc[campaign_dates]['Date'].tolist()
    send_dates = pd.to_datetime(send_dates_list)
    # Now we need to incorporate adding the day of the week
    day_names = [day.day_name() for day in send_dates]
    #A add in columns
    total_df['Date'] = send_dates.strftime('%m/%d/%Y')
    total_df['Day Of Week'] = day_names
    total_df['Category'] =  category_decide(total_df['Campaign Name'])
    # #Add in Old Columns with zero, maybe we'll use later
    total_df['Opens'] = ""
    total_df['Clicks'] = ""
    # # reoder columns just for matching up reading
    total_df = total_df[['Campaign Name','Date','Day Of Week','Category', 'Requests', 'Delivered','Opens','Unique Opens',
       'Clicks','Unique Clicks', 'Unsubscribes']]
    return total_df.values.tolist()

def open_worksheet():
    '''
    Utalize gspread to open the specific worksheet
    '''
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
                'client_secret.json',
                ['https://spreadsheets.google.com/feeds'])
    client = gspread.authorize(credentials)

    #Put in the specific google sheet URL to access. MUST BE SHARED WITH THE CLIENT ID FROM CREDENTIALS
    sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1pUiI-Bjhuv96P9kxs4ZYWtyqkbSryreLGCh-tof1Oto/edit?usp=sharing')
    worksheet = sheet.get_worksheet(0)
    return worksheet


if __name__ == '__main__':
    df = pd.read_csv('bulk_campaign_stats_export.csv',usecols=['Campaign Name','Date','Requests','Delivered','Unique Opens', 'Unique Clicks','Unsubscribes'])
    to_post = mung_data(df)
    worksheet = open_worksheet()
    for i in range(len(to_post)):
        worksheet.append_row(to_post[i],value_input_option='USER_ENTERED')
