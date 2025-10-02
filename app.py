import streamlit as st
import pandas as pd
import datetime
from decimal import Decimal
import plotly.express as px
import plotly.graph_objects as go
import io

# Page configuration
st.set_page_config(
    page_title="BusinessFin Pro - Multi-Company Accounting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .company-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class MultiCompanyAccounting:
    def __init__(self):
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state for both companies"""
        if 'companies' not in st.session_state:
            st.session_state.companies = {
                "company_1": {
                    "name": "Tech Solutions Ltd",
                    "transactions": [],
                    "accounts": self.create_chart_of_accounts(),
                    "color": "#1E88E5"
                },
                "company_2": {
                    "name": "Consulting Partners Ltd", 
                    "transactions": [],
                    "accounts": self.create_chart_of_accounts(),
                    "color": "#FF6B00"
                }
            }
    
    def create_chart_of_accounts(self):
        """Create standard chart of accounts"""
        return {
            # Assets (1000-1999)
            "1000": {"name": "Cash", "type": "asset", "balance": Decimal('0')},
            "1100": {"name": "Accounts Receivable", "type": "asset", "balance": Decimal('0')},
            "1200": {"name": "Inventory", "type": "asset", "balance": Decimal('0')},
            "1500": {"name": "Equipment", "type": "asset", "balance": Decimal('0')},
            "1600": {"name": "Vehicles", "type": "asset", "balance": Decimal('0')},
            
            # Liabilities (2000-2999)
            "2000": {"name": "Accounts Payable", "type": "liability", "balance": Decimal('0')},
            "2100": {"name": "VAT Payable", "type": "liability", "balance": Decimal('0')},
            "2500": {"name": "Bank Loan", "type": "liability", "balance": Decimal('0')},
            "2600": {"name": "Credit Card", "type": "liability", "balance": Decimal('0')},
            
            # Equity (3000-3999)
            "3000": {"name": "Owner's Capital", "type": "equity", "balance": Decimal('0')},
            "3900": {"name": "Retained Earnings", "type": "equity", "balance": Decimal('0')},
            "3950": {"name": "Current Year Earnings", "type": "equity", "balance": Decimal('0')},
            
            # Income (4000-4999)
            "4000": {"name": "Product Sales", "type": "income", "balance": Decimal('0')},
            "4100": {"name": "Service Revenue", "type": "income", "balance": Decimal('0')},
            "4200": {"name": "Consulting Income", "type": "income", "balance": Decimal('0')},
            
            # Expenses (5000-5999)
            "5000": {"name": "Cost of Goods Sold", "type": "expense", "balance": Decimal('0')},
            "5100": {"name": "Salary Expense", "type": "expense", "balance": Decimal('0')},
            "5200": {"name": "Rent Expense", "type": "expense", "balance": Decimal('0')},
            "5300": {"name": "Utilities Expense", "type": "expense", "balance": Decimal('0')},
            "5400": {"name": "Marketing Expense", "type": "expense", "balance": Decimal('0')},
            "5500": {"name": "Office Supplies", "type": "expense", "balance": Decimal('0')},
            "5600": {"name": "Travel Expense", "type": "expense", "balance": Decimal('0')},
            "5700": {"name": "Professional Fees", "type": "expense", "balance": Decimal('0')},
        }
    
    def record_transaction(self, company_id, date, description, entries, vat_rate=0.2):
        """Record a transaction with VAT support"""
        try:
            # Validate debits = credits
            total_debits = sum(Decimal(str(entry.get("debit", 0))) for entry in entries)
            total_credits = sum(Decimal(str(entry.get("credit", 0))) for entry in entries)
            
            if total_debits != total_credits:
                st.error(f"Accounting error: Debits ({total_debits}) ≠ Credits ({total_credits})")
                return False
            
            # Update account balances
            for entry in entries:
                account_num = entry["account"]
                if account_num in self.companies[company_id]["accounts"]:
                    account = self.companies[company_id]["accounts"][account_num]
                    if "debit" in entry:
                        account["balance"] += Decimal(str(entry["debit"]))
                    if "credit" in entry:
                        account["balance"] -= Decimal(str(entry["credit"]))
            
            # Add to transaction history
            transaction = {
                "id": len(self.companies[company_id]["transactions"]) + 1,
                "date": date,
                "description": description,
                "entries": entries.copy(),
                "vat_rate": vat_rate
            }
            
            self.companies[company_id]["transactions"].append(transaction)
            st.success("✅ Transaction recorded successfully!")
            return True
            
        except Exception as e:
            st.error(f"Error recording transaction: {str(e)}")
            return False
    
    def get_account_balance(self, company_id, account_type):
        """Get total balance for account type"""
        return sum(
            account["balance"] 
            for account in self.companies[company_id]["accounts"].values() 
            if account["type"] == account_type
        )
    
    def generate_balance_sheet(self, company_id):
        """Generate balance sheet data"""
        assets = self.get_account_balance(company_id, "asset")
        liabilities = self.get_account_balance(company_id, "liability")
        equity = self.get_account_balance(company_id, "equity")
        
        # Update current year earnings
        net_income = self.calculate_net_income(company_id)
        self.companies[company_id]["accounts"]["3950"]["balance"] = Decimal(str(net_income))
        equity += Decimal(str(net_income))
        
        return {
            "assets": float(assets),
            "liabilities": float(liabilities),
            "equity": float(equity),
            "check": assets == liabilities + equity
        }
    
    def calculate_net_income(self, company_id):
        """Calculate net income for the period"""
        revenue = self.get_account_balance(company_id, "income")
        expenses = self.get_account_balance(company_id, "expense")
        return float(revenue - expenses)
    
    def get_transaction_history(self, company_id):
        """Get transaction history as DataFrame"""
        transactions = []
        for tx in self.companies[company_id]["transactions"]:
            for entry in tx["entries"]:
                transactions.append({
                    "Date": tx["date"],
                    "Description": tx["description"],
                    "Account": f"{entry['account']} - {self.companies[company_id]['accounts'][entry['account']]['name']}",
                    "Debit": float(entry.get("debit", 0)),
                    "Credit": float(entry.get("credit", 0)),
                    "Company": self.companies[company_id]["name"]
                })
        return pd.DataFrame(transactions) if transactions else pd.DataFrame()

def main():
    st.markdown('<h1 class="main-header">🏢 BusinessFin Pro - Multi-Company Accounting</h1>', unsafe_allow_html=True)
    
    # Initialize accounting system
    accounting = MultiCompanyAccounting()
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose Module",
        ["Dashboard", "Record Transaction", "Financial Reports", "Transaction History", "Company Settings"]
    )
    
    # Dashboard
    if app_mode == "Dashboard":
        show_dashboard(accounting)
    
    # Record Transaction
    elif app_mode == "Record Transaction":
        record_transaction(accounting)
    
    # Financial Reports
    elif app_mode == "Financial Reports":
        show_financial_reports(accounting)
    
    # Transaction History
    elif app_mode == "Transaction History":
        show_transaction_history(accounting)
    
    # Company Settings
    elif app_mode == "Company Settings":
        show_company_settings(accounting)

def show_dashboard(accounting):
    st.header("📊 Business Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_id = "company_1"
        company = accounting.companies[company_id]
        st.markdown(f'<div class="company-card"><h3>🏭 {company["name"]}</h3></div>', unsafe_allow_html=True)
        
        # Key metrics
        balance_sheet = accounting.generate_balance_sheet(company_id)
        net_income = accounting.calculate_net_income(company_id)
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Assets", f"£{balance_sheet['assets']:,.2f}")
        with metric_col2:
            st.metric("Net Income", f"£{net_income:,.2f}")
        with metric_col3:
            equity_color = "normal" if balance_sheet['equity'] >= 0 else "inverse"
            st.metric("Owner's Equity", f"£{balance_sheet['equity']:,.2f}", delta=None, delta_color=equity_color)
        
        # Quick chart
        if balance_sheet['assets'] > 0:
            fig = go.Figure(data=[
                go.Bar(name='Assets', x=['Assets'], y=[balance_sheet['assets']], marker_color=company['color']),
                go.Bar(name='Liabilities', x=['Liabilities'], y=[balance_sheet['liabilities']], marker_color='#FF6B6B'),
                go.Bar(name='Equity', x=['Equity'], y=[balance_sheet['equity']], marker_color='#4ECDC4')
            ])
            fig.update_layout(title=f"{company['name']} - Financial Position", barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        company_id = "company_2"
        company = accounting.companies[company_id]
        st.markdown(f'<div class="company-card"><h3>🏭 {company["name"]}</h3></div>', unsafe_allow_html=True)
        
        # Key metrics
        balance_sheet = accounting.generate_balance_sheet(company_id)
        net_income = accounting.calculate_net_income(company_id)
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Total Assets", f"£{balance_sheet['assets']:,.2f}")
        with metric_col2:
            st.metric("Net Income", f"£{net_income:,.2f}")
        with metric_col3:
            equity_color = "normal" if balance_sheet['equity'] >= 0 else "inverse"
            st.metric("Owner's Equity", f"£{balance_sheet['equity']:,.2f}", delta=None, delta_color=equity_color)
        
        # Quick chart
        if balance_sheet['assets'] > 0:
            fig = go.Figure(data=[
                go.Bar(name='Assets', x=['Assets'], y=[balance_sheet['assets']], marker_color=company['color']),
                go.Bar(name='Liabilities', x=['Liabilities'], y=[balance_sheet['liabilities']], marker_color='#FF6B6B'),
                go.Bar(name='Equity', x=['Equity'], y=[balance_sheet['equity']], marker_color='#4ECDC4')
            ])
            fig.update_layout(title=f"{company['name']} - Financial Position", barmode='stack')
            st.plotly_chart(fig, use_container_width=True)
    
    # Consolidated view
    st.header("📈 Consolidated Overview")
    consol_assets = accounting.generate_balance_sheet("company_1")["assets"] + accounting.generate_balance_sheet("company_2")["assets"]
    consol_income = accounting.calculate_net_income("company_1") + accounting.calculate_net_income("company_2")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Combined Assets", f"£{consol_assets:,.2f}")
    with col2:
        st.metric("Combined Net Income", f"£{consol_income:,.2f}")
    with col3:
        st.metric("Total Transactions", 
                 f"{len(accounting.companies['company_1']['transactions']) + len(accounting.companies['company_2']['transactions'])}")

def record_transaction(accounting):
    st.header("💳 Record Transaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_choice = st.selectbox(
            "Select Company",
            ["company_1", "company_2"],
            format_func=lambda x: accounting.companies[x]["name"]
        )
        
        transaction_date = st.date_input("Transaction Date", datetime.date.today())
        description = st.text_input("Description", placeholder="e.g., Client payment, Office supplies purchase")
        
        # VAT setting (UK standard)
        vat_rate = st.selectbox("VAT Rate", [0.0, 0.2, 0.05], format_func=lambda x: f"{x*100}%")
    
    with col2:
        st.subheader("Transaction Entries")
        st.info("💡 Remember: Total Debits must equal Total Credits")
        
        # Dynamic entry form
        if 'entry_count' not in st.session_state:
            st.session_state.entry_count = 2
        
        entries = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for i in range(st.session_state.entry_count):
            st.markdown(f"**Entry {i+1}**")
            col_acc, col_debit, col_credit = st.columns([2, 1, 1])
            
            with col_acc:
                account_options = {
                    f"{num} - {acc['name']}": num 
                    for num, acc in accounting.companies[company_choice]["accounts"].items()
                }
                selected_account = st.selectbox(
                    f"Account {i+1}",
                    list(account_options.keys()),
                    key=f"acc_{i}"
                )
                account_num = account_options[selected_account]
            
            with col_debit:
                debit = st.number_input("Debit", min_value=0.0, step=100.0, key=f"debit_{i}")
            
            with col_credit:
                credit = st.number_input("Credit", min_value=0.0, step=100.0, key=f"credit_{i}")
            
            if debit > 0 or credit > 0:
                entry = {"account": account_num}
                if debit > 0:
                    entry["debit"] = debit
                    total_debits += Decimal(str(debit))
                if credit > 0:
                    entry["credit"] = credit
                    total_credits += Decimal(str(credit))
                entries.append(entry)
        
        # Add/remove entry buttons
        col_add, col_remove, _ = st.columns([1, 1, 2])
        with col_add:
            if st.button("➕ Add Entry"):
                st.session_state.entry_count += 1
                st.rerun()
        with col_remove:
            if st.button("➖ Remove Entry") and st.session_state.entry_count > 2:
                st.session_state.entry_count -= 1
                st.rerun()
    
    # Totals display
    st.markdown(f"**Totals:** Debits = £{float(total_debits):.2f} | Credits = £{float(total_credits):.2f}")
    
    if total_debits != total_credits:
        st.error(f"❌ Imbalance: £{float(abs(total_debits - total_credits)):.2f}")
    else:
        st.success("✅ Debits and Credits are balanced!")
    
    # Record transaction button
    if st.button("📝 Record Transaction", type="primary") and entries and description:
        if accounting.record_transaction(company_choice, transaction_date, description, entries, vat_rate):
            st.session_state.entry_count = 2  # Reset entry count
            st.rerun()

def show_financial_reports(accounting):
    st.header("📋 Financial Reports")
    
    report_type = st.selectbox("Select Report", ["Balance Sheet", "Income Statement", "Cash Flow"])
    company_choice = st.radio("Select Company", ["company_1", "company_2", "Consolidated"], 
                             format_func=lambda x: accounting.companies[x]["name"] if x in accounting.companies else x)
    
    if report_type == "Balance Sheet":
        show_balance_sheet(accounting, company_choice)
    elif report_type == "Income Statement":
        show_income_statement(accounting, company_choice)

def show_balance_sheet(accounting, company_choice):
    st.subheader("💰 Balance Sheet")
    
    if company_choice == "Consolidated":
        for company_id in ["company_1", "company_2"]:
            company = accounting.companies[company_id]
            balance_sheet = accounting.generate_balance_sheet(company_id)
            
            st.markdown(f"**{company['name']}**")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Assets**")
                assets = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "asset" and acc["balance"] != 0}
                for num, acc in assets.items():
                    st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
                st.write(f"**Total Assets: £{balance_sheet['assets']:,.2f}**")
            
            with col2:
                st.write("**Liabilities & Equity**")
                liabilities = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "liability" and acc["balance"] != 0}
                equity = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "equity" and acc["balance"] != 0}
                
                for num, acc in liabilities.items():
                    st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
                st.write(f"**Total Liabilities: £{balance_sheet['liabilities']:,.2f}**")
                
                for num, acc in equity.items():
                    st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
                st.write(f"**Total Equity: £{balance_sheet['equity']:,.2f}**")
            
            st.write(f"**Check: Assets = Liabilities + Equity: {balance_sheet['check']}**")
            st.markdown("---")
    else:
        company = accounting.companies[company_choice]
        balance_sheet = accounting.generate_balance_sheet(company_choice)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Assets**")
            assets = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "asset" and acc["balance"] != 0}
            for num, acc in assets.items():
                st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
            st.write(f"**Total Assets: £{balance_sheet['assets']:,.2f}**")
        
        with col2:
            st.write("**Liabilities & Equity**")
            liabilities = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "liability" and acc["balance"] != 0}
            equity = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "equity" and acc["balance"] != 0}
            
            st.write("**Liabilities**")
            for num, acc in liabilities.items():
                st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
            st.write(f"**Total Liabilities: £{balance_sheet['liabilities']:,.2f}**")
            
            st.write("**Equity**")
            for num, acc in equity.items():
                st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
            st.write(f"**Total Equity: £{balance_sheet['equity']:,.2f}**")
        
        st.success(f"**Accounting Equation Check: Assets = Liabilities + Equity: {balance_sheet['check']}**")

def show_income_statement(accounting, company_choice):
    st.subheader("📈 Income Statement")
    
    if company_choice == "Consolidated":
        total_revenue = 0
        total_expenses = 0
        
        for company_id in ["company_1", "company_2"]:
            company = accounting.companies[company_id]
            st.markdown(f"**{company['name']}**")
            
            revenue = sum(acc["balance"] for acc in company["accounts"].values() if acc["type"] == "income")
            expenses = sum(acc["balance"] for acc in company["accounts"].values() if acc["type"] == "expense")
            net_income = revenue - expenses
            
            st.write(f"Revenue: £{float(revenue):,.2f}")
            st.write(f"Expenses: £{float(expenses):,.2f}")
            st.write(f"**Net Income: £{float(net_income):,.2f}**")
            
            total_revenue += float(revenue)
            total_expenses += float(expenses)
            
            st.markdown("---")
        
        st.subheader("**Consolidated Results**")
        st.write(f"Total Revenue: £{total_revenue:,.2f}")
        st.write(f"Total Expenses: £{total_expenses:,.2f}")
        st.write(f"**Combined Net Income: £{total_revenue - total_expenses:,.2f}**")
    
    else:
        company = accounting.companies[company_choice]
        
        st.write("**Revenue**")
        revenue_accounts = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "income" and acc["balance"] != 0}
        total_revenue = Decimal('0')
        for num, acc in revenue_accounts.items():
            st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
            total_revenue += acc["balance"]
        
        st.write("**Expenses**")
        expense_accounts = {num: acc for num, acc in company["accounts"].items() if acc["type"] == "expense" and acc["balance"] != 0}
        total_expenses = Decimal('0')
        for num, acc in expense_accounts.items():
            st.write(f"{acc['name']}: £{float(acc['balance']):,.2f}")
            total_expenses += acc["balance"]
        
        net_income = total_revenue - total_expenses
        st.write(f"**Total Revenue: £{float(total_revenue):,.2f}**")
        st.write(f"**Total Expenses: £{float(total_expenses):,.2f}**")
        st.success(f"**Net Income: £{float(net_income):,.2f}**")

def show_transaction_history(accounting):
    st.header("📋 Transaction History")
    
    company_choice = st.selectbox(
        "Select Company",
        ["company_1", "company_2", "All Companies"],
        format_func=lambda x: accounting.companies[x]["name"] if x in accounting.companies else x,
        key="history_company"
    )
    
    if company_choice == "All Companies":
        df1 = accounting.get_transaction_history("company_1")
        df2 = accounting.get_transaction_history("company_2")
        df = pd.concat([df1, df2], ignore_index=True) if not df1.empty and not df2.empty else df1 if not df1.empty else df2
    else:
        df = accounting.get_transaction_history(company_choice)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"transaction_history_{datetime.date.today()}.csv",
                mime="text/csv",
            )
        with col2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Transactions')
            st.download_button(
                label="📥 Download as Excel",
                data=excel_buffer.getvalue(),
                file_name=f"transaction_history_{datetime.date.today()}.xlsx",
                mime="application/vnd.ms-excel",
            )
    else:
        st.info("No transactions recorded yet.")

def show_company_settings(accounting):
    st.header("⚙️ Company Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Company 1 Settings")
        new_name_1 = st.text_input("Company Name", value=accounting.companies["company_1"]["name"], key="name_1")
        accounting.companies["company_1"]["name"] = new_name_1
        
        st.write("**Current Accounts**")
        for num, acc in accounting.companies["company_1"]["accounts"].items():
            st.write(f"{num} - {acc['name']}: £{float(acc['balance']):,.2f}")
    
    with col2:
        st.subheader("Company 2 Settings")
        new_name_2 = st.text_input("Company Name", value=accounting.companies["company_2"]["name"], key="name_2")
        accounting.companies["company_2"]["name"] = new_name_2
        
        st.write("**Current Accounts**")
        for num, acc in accounting.companies["company_2"]["accounts"].items():
            st.write(f"{num} - {acc['name']}: £{float(acc['balance']):,.2f}")
    
    # Data management
    st.subheader("Data Management")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset Company 1 Data", type="secondary"):
            accounting.companies["company_1"]["transactions"] = []
            accounting.companies["company_1"]["accounts"] = accounting.create_chart_of_accounts()
            st.success("Company 1 data reset!")
            st.rerun()
    
    with col2:
        if st.button("🔄 Reset Company 2 Data", type="secondary"):
            accounting.companies["company_2"]["transactions"] = []
            accounting.companies["company_2"]["accounts"] = accounting.create_chart_of_accounts()
            st.success("Company 2 data reset!")
            st.rerun()
    
    # Export all data
    st.subheader("Backup & Export")
    if st.button("💾 Backup All Data", type="primary"):
        # Create a simplified backup of the data
        backup_data = {
            "export_date": str(datetime.datetime.now()),
            "companies": accounting.companies
        }
        
        # Convert to JSON for download
        import json
        from decimal import Decimal
        
        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return float(obj)
                return super(DecimalEncoder, self).default(obj)
        
        backup_json = json.dumps(backup_data, indent=2, cls=DecimalEncoder)
        
        st.download_button(
            label="📥 Download Backup",
            data=backup_json,
            file_name=f"accounting_backup_{datetime.date.today()}.json",
            mime="application/json",
        )

if __name__ == "__main__":
    main()