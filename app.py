import pandas as pd
from datetime import date
import requests
import configparser
import pathlib

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

# load data
currencySymbol = pd.read_csv('./data/currency_shortcodes.csv')

# create a list of currency names
currency_list = currencySymbol['name'] + ' (' + currencySymbol['short_code'] + ')'
currency_list = currency_list.tolist()

# Current Date
today = date.today().strftime("%Y-%m-%d")

# Min Date
min_day = date.today() - pd.Timedelta(days=200)

# Start Date
start_day = date.today() - pd.Timedelta(days=30)

# Read Configuration File
parser = configparser.ConfigParser()
script_path = pathlib.Path(__file__).parent.resolve()
config_file = "configuration.conf"
parser.read(f"{script_path}/{config_file}")

# API Key
api_key = parser.get("api_config","api_key")


# About Content
def about_content():
    context = """
        # **Currency Trends and Exchange Calculator**

        
        ### About This Dashboard

        This dashboard is designed to provide users with a quick and easy way to view the current exchange rates and their variances of various currencies. It will display the selected currencies' exchange rates in a table format, along with the variance between the current rate and the previous rate over a specified time period. A line graph will also show the trends of these exchange rates. Additionally, users can use the exchange calculator to convert an amount from one currency to another.

        **_Please note that the exchange rates are updated hourly, and the historical data is available for the past 200 days._**

        ### Domain of Application for This Dashboard

        The purpose of this dashboard is to provide a user-friendly platform for users to interact with currency exchange data. It allows users to view historical trends of different currencies, which can be useful for financial analysis, trading in the foreign exchange market, or simply for individuals and businesses requirements to exchange currencies for travel or commerce purposes. In addition, the currency exchange calculator is a handy tool for anyone who needs to convert between different currencies.

        ### Setup Instructions

        
        **The dashboard is deployed on Shinyapps.io and can be accessed via the following link:**
        
        - **https://currencies-jingyi.shinyapps.io/currencies-dashboard/**

        To run this dashboard on your local machine, follow these steps:

        1. Clone the repository to your local machine.
        2. Run `uv venv` to create a virtual environment.
        3. Run `.venv\Scripts\activate` to activate the virtual environment.
        4. Run `uv pip install -r requirements.txt` to install the required packages.
        5. Run `Shiny run app.py` to start the dashboard.
        6. Open your web browser and navigate to http://localhost:8000 (or whatever port your console indicates the app is running on) to view the dashboard.

        ### Usage Examples
        
        - **Historical Data:** Select the base currency and one or more target currencies, then specify the date range. The dashboard will display a table and a plot of the historical exchange rates of the selected currencies. You can further refine the data displayed in the table and plot by using the "table currency" and "plot currency" selectors to choose which of the selected target currencies you want to include.

        **_Note that you need to select the "table currency" and "plot currency" after selecting more than one target currency, otherwise, the dashboard will display the data for the first target currency by default._**

        - **Currency Exchange Calculator:** Select the base currency and the target currency, and input the amount you want to convert. Click the "Compute" button and the dashboard will display the converted amount in the target currency.

        ### References
        - **Currency Beacon API:** Currency Beacon. (2023). Currency Beacon API. Retrieved from https://currencybeacon.com/
        """
    return context


app_ui = ui.page_navbar(
    ui.nav_panel("Historical Data",
                 ui.page_sidebar(
                    ui.sidebar(
                                ui.input_selectize("base","Base Currency", currency_list, selected="US Dollar (USD)"),
                                ui.input_selectize("target","Target Currencies", currency_list, selected="Euro (EUR)", multiple=True),
                                ui.input_date_range("dates", "Dates", start=start_day, end=today, max=today, min= min_day),
                                ui.output_ui("table_currency_selection"),
                                ui.output_ui("plot_currency_selection"),
                                width=350,
                                open="always"
                     ),
                    ui.output_plot("historical_plot"),
                    ui.hr(),
                    ui.output_data_frame("historical_table")),

                 ),

    ui.nav_panel("Currency Exchange Calculator",
                 ui.card(
                     ui.input_selectize("base_currency","From:", currency_list, selected="US Dollar (USD)"),
                     ui.input_selectize("target_currency","To:", currency_list, selected="Euro (EUR)"),
                     ui.input_numeric("amount", "Amount:", value=1),
                 ),
                 ui.card(
                    #  ui.output_text("exchange_value"),
                    ui.input_action_button("button", "Compute", width='300px'),
                    ui.output_ui("compute"),
                 )),
    ui.nav_panel("About",
                 ui.markdown(about_content())),
    title = "Currency Trends and Exchange Calculator",
    )

# requesting data from the API
def currency_timeseries(base, symbols, start_date, end_date):

    # Get the data from the API
    url = f'https://api.currencybeacon.com/v1/timeseries?api_key={api_key}&base={base}&start_date={start_date}&end_date={end_date}&symbols={symbols}'
    
    response = requests.get(url).json()

    # Extract the response data into a dataframe
    response_data = response['response']
    data_list = []

    for date, currencies in response_data.items():
        for currency, rate in currencies.items():
            data_list.append((date, currency, rate))

    df = pd.DataFrame(data_list, columns=['Date', 'Currency', 'Rate'])

    return df

# requesting calculator data from the API
def currency_calculator(base_currency, target_currency, amount):
    
        # Get the data from the API
        url = f'https://api.currencybeacon.com/v1/convert?api_key={api_key}&from={base_currency}&to={target_currency}&amount={amount}'
        
        response = requests.get(url).json()

        value = response['response']['value']
        amount = response['response']['amount']

        return value, amount


# setup server
def server(input: Inputs, output: Outputs, session: Session):
    def get_data():

        if not input.base() or input.base() == "" or input.target() is None or input.target() == "" or input.dates() is None or input.dates() == "":
            return pd.DataFrame(columns=['Date', 'Currency', 'Rate'])
        else:
            # Params
            base = input.base().split("(")[1].split(")")[0]

            target = input.target()
            target_list = [x.split("(")[1].split(")")[0] for x in target]
            target_str = ','.join(target_list)

            start_date = input.dates()[0]
            end_date = input.dates()[1]

            # Get the historical timeseries data
            df = currency_timeseries(base, target_str, start_date, end_date)
            return df
    

    @output
    @render.ui("table_currency_selection")
    def table_currency_selection():
        target_list = input.target()

        if not input.base() or input.base() == "" or not target_list or target_list == "" or not input.dates() or input.dates() == "":
            pass
        else:
            return ui.input_selectize("table_currency","Table Currency", target_list, selected=target_list[0], multiple=True)
    

    @render.data_frame("historical_table")
    def historical_table():
        return render.DataGrid(calculate_historical_table(), summary=False, height="3000px", width=1600)
    

    @reactive.Calc
    def calculate_historical_table():
        
        df = get_data()
        selected_currencies = [x.split("(")[1].split(")")[0] for x in input.table_currency()]

        df = df[df['Currency'].isin(selected_currencies)]
        df['Rate'] = df['Rate'].round(3)

        # The variance between the current rate and the previous rate
        df['Variance'] = df.groupby('Currency')['Rate'].diff()

        # Fill the first variance with 0
        df['Variance'] = df['Variance'].fillna(0)
        return df
    

    @output
    @render.ui("plot_currency_selection")
    def plot_currency_selection():
        target_list = input.target()

        if not input.base() or input.base() == "" or not target_list or target_list == "" or not input.dates() or input.dates() == "":
            pass
        else:
            return ui.input_selectize("plot_currency","Plot Currency", target_list, selected=target_list[0], multiple=True)
    

    @output
    @render.plot("historical_plot")
    def historical_plot():
        df = get_data()
        df["Date"] = pd.to_datetime(df["Date"])

        fig,ax = plt.subplots(figsize=(14, 5))

        selected_currencies = [x.split("(")[1].split(")")[0] for x in input.plot_currency()]
        selected_currencies_names = input.plot_currency()

        for currency in selected_currencies:
            df_currency = df[df['Currency'] == currency]
            ax.plot(df_currency['Date'], df_currency['Rate'], label=currency)

        if len(selected_currencies) > 1:
            ax.set_title(f'Historical Exchange Rates from {input.base()} to {", ".join(selected_currencies_names)}')
        else:
            ax.set_title(f'Historical Exchange Rates from {input.base()} to {selected_currencies_names[0]}')
        
        ax.set_ylabel('Currency Rate')
        ax.legend(df["Currency"].unique(), loc='upper left')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    
        plt.xticks(rotation=0)
        plt.tight_layout()

        return fig
    
    @output
    @render.ui
    @reactive.event(input.button)
    async def compute():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)
            
        base_currency = input.base_currency().split("(")[1].split(")")[0]
        target_currency = input.target_currency().split("(")[1].split(")")[0]
        amount = input.amount()

        value, amount = currency_calculator(base_currency, target_currency, amount)

        value = round(value, 2)

        context = f"Exchange Value: **{value} {target_currency}** for **{amount} {base_currency}**"
        return ui.markdown(context)


# run app
app = App(app_ui, server)
        