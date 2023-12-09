import numpy as np
import numpy_financial as npf
from flask import Flask, request, jsonify

app = Flask(__name__)

class ApartmentInvestment:
    def __init__(self, unit_count, purchase_price, market_rent_per_unit, rent_growth_per_year, 
                 year_1_expense_ratio, expense_growth_per_year, capex_per_unit, exit_cap_rate):
        self.unit_count = unit_count
        self.purchase_price = purchase_price
        self.market_rent_per_unit = market_rent_per_unit
        self.rent_growth_per_year = rent_growth_per_year
        self.year_1_expense_ratio = year_1_expense_ratio
        self.expense_growth_per_year = expense_growth_per_year
        self.capex_per_unit = capex_per_unit
        self.exit_cap_rate = exit_cap_rate
    
    def calculate_irr(self):
        # Define variables and arrays to store calculations
        revenue = np.zeros(12)
        expenses = np.zeros(12)
        capex = np.zeros(12)
        net_operating_income = np.zeros(12)
        net_cash_flow = np.zeros(11)

        # Step 1: Year 1 Revenue
        revenue[1] = self.market_rent_per_unit * self.unit_count * 12
        # Step 2: Year 1 Expenses
        expenses[1] = revenue[1] * self.year_1_expense_ratio
        # Step 3: Grow Revenue and Expenses
        for year in range(2, 12):
            revenue[year] = revenue[year - 1] * (1 + self.rent_growth_per_year)
            expenses[year] = expenses[year - 1] * (1 + self.expense_growth_per_year)
        # Step 4: Net Operating Income
        net_operating_income = revenue - expenses
        # Step 5 and 6: CAPEX and growth
        capex[1] = self.capex_per_unit * self.unit_count
        for year in range(2, 12):
            capex[year] = capex[year - 1] * (1 + self.expense_growth_per_year)
        # Step 7: Net Cash Flow for Year 0 to Year 10
        net_cash_flow[0] = -self.purchase_price
        net_cash_flow[1:10] = net_operating_income[1:10] - capex[1:10]
        # Step 8: Add Reversion Value to Year 10 Cash Flow (calculated from Year 11 NOI)
        reversion_value = net_operating_income[11] / self.exit_cap_rate
        net_cash_flow[10] = net_operating_income[10] - capex[10] + reversion_value
        # Step 9: Calculate IRR
        irr = npf.irr(net_cash_flow)
        
        # Create a dictionary of all cash flows
        cash_flows_dict = {
        'revenue': revenue,
        'expenses': expenses,
        'capex': capex,
        'net_operating_income': net_operating_income,
        'net_cash_flow': net_cash_flow,

        }
        return irr#, cash_flows_dict

@app.route('/')
def test():
    return 'This route works!'


@app.route('/irr', methods=['GET'])
def irr():
    try:
        # Extracting parameters from the URL query string
        unit_count = int(request.args.get('unit_count', 0))
        purchase_price = float(request.args.get('purchase_price', 0.0))
        market_rent_per_unit = float(request.args.get('market_rent_per_unit', 0.0))
        rent_growth_per_year = float(request.args.get('rent_growth_per_year', 0.0))
        year_1_expense_ratio = float(request.args.get('year_1_expense_ratio', 0.0))
        expense_growth_per_year = float(request.args.get('expense_growth_per_year', 0.0))
        capex_per_unit = float(request.args.get('capex_per_unit', 0.0))
        exit_cap_rate = float(request.args.get('exit_cap_rate', 0.0))

        investment = ApartmentInvestment(unit_count, purchase_price, market_rent_per_unit,
                                         rent_growth_per_year, year_1_expense_ratio,
                                         expense_growth_per_year, capex_per_unit, exit_cap_rate)
        irr = investment.calculate_irr()

        response = {
            "IRR": irr
        }
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)


# HTML code for the table
html_table = """
<table border="1">
    <tr>
        <th>Parameter</th>
        <th>Description</th>
        <th>Example</th>
    </tr>
    <tr>
        <td>unit_count</td>
        <td>Number of units in the apartment.</td>
        <td>20</td>
    </tr>
    <tr>
        <td>purchase_price</td>
        <td>Total price for acquiring the property.</td>
        <td>1,000,000</td>
    </tr>
    <tr>
        <td>market_rent_per_unit</td>
        <td>Average expected rent per unit.</td>
        <td>1,200</td>
    </tr>
    <tr>
        <td>rent_growth_per_year</td>
        <td>Annual rent growth rate.</td>
        <td>3%</td>
    </tr>
    <tr>
        <td>year_1_expense_ratio</td>
        <td>Ratio of expenses to revenue in the first year.</td>
        <td>50%</td>
    </tr>
    <tr>
        <td>expense_growth_per_year</td>
        <td>Annual growth rate of expenses.</td>
        <td>2%</td>
    </tr>
    <tr>
        <td>capex_per_unit</td>
        <td>Annual capital expenditure per unit.</td>
        <td>500</td>
    </tr>
    <tr>
        <td>exit_cap_rate</td>
        <td>Cap rate for estimating the property's sale value.</td>
        <td>5%</td>
    </tr>
</table>
"""

# Display HTML table in Streamlit app
st.markdown(html_table, unsafe_allow_html=True)

