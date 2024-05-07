import pandas as pd
from datetime import date
import requests
import json

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

# load data
currencySymbol = pd.read_csv('./data/currency_shortcodes.csv')

# create a list of currency names
currency_list = currencySymbol['name'] + ' (' + currencySymbol['short_code'] + ')'
currency_list = currency_list.tolist()

# Current Date
today = date.today().strftime("%Y-%m-%d")

# Min Date
min_day = date.today() - pd.Timedelta(days=200)

# API Key
api_key = 'Jlv9nG6xEQHbF9MIY2NkzSasVOVe50I6'

app_ui = ui.page_navbar(
    ui.nav_panel("Historical Data",
                 ui.page_sidebar(
                    ui.sidebar(
                                ui.input_selectize("base","Base Currency", currency_list, selected="US Dollar (USD)"),
                                ui.input_selectize("target","Target Currencies", currency_list, selected="Euro (EUR)", multiple=True),
                                ui.input_date_range("dates", "Dates", start="2024-04-01", end=today, max=today, min= min_day),
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
    

    # @output
    # @render.text("exchange_value")
    # def exchange_value():
    #     base_currency = input.base_currency().split("(")[1].split(")")[0]
    #     target_currency = input.target_currency().split("(")[1].split(")")[0]
    #     amount = input.amount()

    #     value, amount = currency_calculator(base_currency, target_currency, amount)
    #     return f"Exchange Value: {value} {target_currency} for {amount} {base_currency}"



# run app
app = App(app_ui, server)
        