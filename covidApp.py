import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import base64



st.title('Simple Covid-19 Tracker')
st.sidebar.header('User Input Features')
country_enter = st.sidebar.text_input('Name of Country', 'Egypt').title()



# Collecting and Curing data from external links
@st.cache
def covid(country):
    cases = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    deaths = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    recoverd = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')
    cases = cases[cases['Country/Region'] == country].drop(['Province/State', 'Lat', 'Long', 'Country/Region'], 1).transpose()
    cases = cases.reset_index()
    cases = cases.rename(columns={cases.columns[0]:'date', cases.columns[1]:'Cases'})
    deaths = deaths[deaths['Country/Region'] == country].drop(['Province/State', 'Lat', 'Long', 'Country/Region'], 1).transpose()
    deaths = deaths.reset_index()
    deaths = deaths.rename(columns={deaths.columns[0]:'date', deaths.columns[1]:'Deaths'})
    recoverd = recoverd[recoverd['Country/Region'] == country].drop(['Province/State', 'Lat', 'Long', 'Country/Region'], 1).transpose()
    recoverd = recoverd.reset_index()
    recoverd = recoverd.rename(columns={recoverd.columns[0]:'date', recoverd.columns[1]:'Recoverd'})
    covid_data = pd.concat([cases, deaths['Deaths'], recoverd['Recoverd']], 1)
    covid_data['date'] = pd.to_datetime(covid_data['date'])
    every_day_data = covid_data[['Cases', 'Deaths', 'Recoverd']].diff().dropna()
    every_day_data = pd.concat([covid_data['date'], every_day_data], 1)
    every_day_data.dropna(inplace=True)
    return every_day_data


# Getting the country name
try:
    data = covid(country_enter)
    st.write(f'This table contains Covid-19 data of {country_enter}')
    st.dataframe(data[::-1])
except Exception:
    st.info(f'No data for {country_enter}')

# Function to save the data generated in csv or txt file
def filedownload(df, dl_type, name):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/{dl_type};base64,{b64}" download="Covid-19 {name} of {country_enter}.{dl_type}">Download {name} as {dl_type} file</a>'
    return href

st.markdown(filedownload(data, 'CSV', 'Table'), unsafe_allow_html=True)


#Plotting data
plot_what = st.sidebar.selectbox('Select what to be plotted',
    ('Cases', 'Deaths', 'Recoverd'))

try:
    from_date = st.sidebar.text_input('Starting date', '2020-08-03')
    to_date = st.sidebar.text_input('Ending date', '2020-09-30')
    plot_rang_data = data[(data['date'] >= from_date) & (data['date'] <= to_date)]

    def plot_me(start, end):
        # plot_rang = data[(data['date'] >= from_date) & (data['date'] <= to_date)]
        fig, ax = plt.subplots(figsize=(9,5))
        ax.plot(
            plot_rang_data['date'],
            plot_rang_data[plot_what],
            label=f'Numbers of Covid-19 {plot_what}'
        )
        ax.set(xlabel="Date",
            ylabel= f"Number of {plot_what} per day",
            title=f"Covid-19 {plot_what} in {country_enter} from {from_date} till {to_date}")
        # ax.axvline(pd.Timestamp(recover_peak_day), color='r', label= f'The day with highest recoverd number in {country}\n{recover_peak_day}')
        ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45)
        plt.grid()
        return fig, ax

    fig, ax = plot_me(from_date, to_date)
    st.pyplot(fig)
except Exception:
    st.info('Invalid Date Input, Please Input a Date in a Right Form,"YYYY-MM-DD".eg 2017-12-10')


if st.button('Show Report'):
    report_data = {
        'Total Cases' : np.sum(data.Cases),
        'Total Deaths' : np.sum(data.Deaths),
        'Total Recoverd' : np.sum(data.Recoverd),
        'The Max number of Case occured in a day' : np.max(data.Cases),
        'Day of Max number of Cases' : data.loc[data.Cases == np.max(data.Cases), 'date'].to_string().split()[1],
        'The Max number of Deaths occured in a day' : np.max(data.Deaths),
        'Day of Max number of Deaths' : data.loc[data.Deaths == np.max(data.Deaths), 'date'].to_string().split()[1],
        'The Max number of Recoverd occured in a day' : np.max(data.Recoverd),
        'Day of Max number of Recoverd' : data.loc[data.Recoverd == np.max(data.Recoverd), 'date'].to_string().split()[1],
        'The Sum of Cases in the selected range' : np.sum(plot_rang_data.Cases),
        'The Sum of Deaths in the selected range' : np.sum(plot_rang_data.Deaths),
        'The Sum of Recoverd in the selected range' : np.sum(plot_rang_data.Recoverd),
        'The Max number of Cases in the selected Range' : np.max(plot_rang_data.Cases),
        'The Max number of Deaths in the selected Range' : np.max(plot_rang_data.Deaths),
        'The Max number of Recoverd in the selected Range' : np.max(plot_rang_data.Recoverd),
    }
    df = pd.DataFrame.from_dict(report_data, orient='index')
    df.reset_index(inplace=True)
    df.index += 1
    df = df.rename(columns={0: 'Number', 'index':'Data'})
    st.table(df)
    st.markdown(filedownload(df, 'TXT', 'Report'), unsafe_allow_html=True)
    st.markdown(filedownload(plot_rang_data, 'CSV', f'Covid-19 Data of range {from_date} to {to_date}'), unsafe_allow_html=True)