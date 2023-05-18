import streamlit as st
import math


st.title("Mortgage Prepayment Calculator")
st.divider()

ord_mrtg_amt = st.text_input("**Original Mortgage Amount**").strip()
org_mortg_term = st.text_input("Original Mortgage Term (in years)").strip()
years_remaining = st.text_input("Years remaining").strip()
interest_rate = st.text_input("Interest Rate").strip()
add_principal_pmnt = st.text_input("Additional Principal Payment").strip()

ord_mrtg_amt = float(ord_mrtg_amt)
org_mortg_term = float(org_mortg_term)
interest_rate = float(interest_rate)
years_remaining = float(years_remaining)
add_principal_pmnt = float(add_principal_pmnt)

btn_pressed = st.button('Calculate')

st.divider()

if btn_pressed:
    numerator = ord_mrtg_amt * (interest_rate/1200 * math.pow((1 + interest_rate/1200), years_remaining*12))
    
    #st.write(numerator)

    denominator = (math.pow((1 + interest_rate/1200),years_remaining*12) - 1)
    #st.write(denominator)
    monthlyPayment = numerator/denominator
    newMonthlyPayment = monthlyPayment + add_principal_pmnt
    origTimePeriod = math.log(monthlyPayment/(monthlyPayment - ord_mrtg_amt * interest_rate/1200))/math.log(1+interest_rate/1200)
    newTimePeriod = math.log(newMonthlyPayment/(newMonthlyPayment - ord_mrtg_amt * interest_rate/1200))/math.log(1+interest_rate/1200)
    monthSaved = math.floor(origTimePeriod - newTimePeriod)
    origTotalPayment = monthlyPayment * years_remaining * 12
    
    newTotalPayment = newMonthlyPayment * newTimePeriod
    totalInterestSaved = origTotalPayment - newTotalPayment
    st.write('### Result:')
    st.write(f'**Original Monthly Payment**: {round(monthlyPayment,2)}')
    st.write(f'**New Monthly Payment**: {round(newMonthlyPayment,2)}')
    st.write(f'**Months Saved**: {monthSaved}')
    st.write(f'**Interest Saved**: {round(totalInterestSaved,2)}')