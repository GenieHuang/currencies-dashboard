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