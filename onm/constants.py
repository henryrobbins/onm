# https://mint.intuit.com/mint-categories
MINT_EXPENSE_CATEGORIES = {
    "Income": ["Paycheck", "Investment", "Returned Purchase", "Bonus", "Interest Income", "Reimbursement", "Rental Income"],
    "Miscellaneous": ["Cash & ATM", "Check"],
    "Entertainment": ["Arts", "Music", "Movies & DVDs", "Newspaper & Magazines", "Amusement"],
    "Education": ["Tuition", "Student Loan", "Books & Supplies"],
    "Shopping": ["Clothing", "Books", "Electronics & Software", "Hobbies", "Sporting Goods"],
    "Personal Care": ["Laundry", "Hair", "Spa & Massage"],
    "Health & Fitness": ["Dentist", "Doctor", "Eye Care", "Pharmacy", "Health Insurance", "Gym", "Sports"],
    "Kids": ["Kids Activities", "Allowance", "Baby Supplies", "Babysitter & Daycare", "Child Support", "Toys"],
    "Food & Dining": ["Groceries", "Coffee Shops", "Fast Food", "Restaurants", "Alcohol & Bars", "Food Delivery"],
    "Gifts & Donations": ["Gift", "Charity"],
    "Investments": ["Deposit", "Withdrawal", "Dividend & Cap Gains", "Buy", "Sell"],
    "Bills & Utilities": ["Television", "Home Phone", "Internet", "Mobile Phone", "Utilities"],
    "Auto & Transport": ["Gas & Fuel", "Parking", "Service & Parts", "Auto Payment", "Auto Insurance", "Ride Share", "Public Transportation"],
    "Travel": ["Air Travel", "Hotel", "Rental Car & Taxi", "Vacation"],
    "Fees & Charges": ["Service Fee", "Late Fee", "Finance Charge", "ATM Fee", "Bank Fee", "Trade Commissions", "Loan Principal"],
    "Business Services": ["Advertising", "Office Supplies", "Printing", "Shipping", "Legal"],
    "Taxes": ["Federal Tax", "State Tax", "Local Tax", "Sales Tax", "Property Tax"],
    "Home": ["Home Supplies", "Home Improvement", "Home Insurance", "Home Services", "Mortgage & Rent", "Furnishings"]
}
MINT_CATEGORY_MAP = {e:f"{c}:{e}" for c, expenses in MINT_EXPENSE_CATEGORIES.items() for e in expenses}
MINT_CATEGORY_MAP.update({c:c for c in MINT_EXPENSE_CATEGORIES})
MINT_CATEGORY_MAP["Transfer"] = "Transfer"
MINT_CATEGORY_MAP["Transfer for Cash Spending"] = "Transfer"
MINT_CATEGORY_MAP["Credit Card Payment"] = "Credit Card Payment"
MINT_CATEGORY_MAP["Misc Expenses"] = "Miscellaneous"
MINT_CATEGORY_MAP["Uncategorized"] = "Uncategorized"
