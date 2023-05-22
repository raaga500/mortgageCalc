import streamlit as st
import math
import pandas as pd
import numpy as np
import ammortization as am

st. set_page_config(layout="wide")

#st.title("Mortgage Prepayment Calculator")
st.markdown("<h1 style='text-align: center;'>Mortgage Prepayment Calculator</h1>", unsafe_allow_html=True)

st.divider()
col1, col2 = st.columns(2)
with col1:
    ord_mrtg_amt = st.text_input("**Original Mortgage Amount**",value=212000).strip()
    org_mortg_term = st.text_input("Original Mortgage Term (in years)",value=15).strip()
    years_remaining = st.text_input("Years remaining",value=14).strip()
    interest_rate = st.text_input("Interest Rate",value=4).strip()
    add_principal_pmnt = st.text_input("Additional Principal Payment",value=176).strip()

    ord_mrtg_amt = float(ord_mrtg_amt)
    org_mortg_term = int(org_mortg_term)
    interest_rate = float(interest_rate)
    years_remaining = float(years_remaining)
    add_principal_pmnt = float(add_principal_pmnt)

    btn_pressed = st.button('Calculate')

st.divider()

def calculatePrepaymentNumbers(ord_mrtg_amt, interest_rate, years_remaining, add_principal_pmnt):
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

    result_dict = {}
    result_dict['monthlyPayment'] = monthlyPayment
    result_dict['newMonthlyPayment'] = newMonthlyPayment
    result_dict['monthSaved'] = monthSaved
    result_dict['totalInterestSaved'] = totalInterestSaved
    return result_dict

def getAmmortizationSchedule(ord_mrtg_amt, interest_rate, org_mortg_term):
    df = am.amortisation_schedule(ord_mrtg_amt,interest_rate/100.0,12,org_mortg_term)
    return df

if btn_pressed:
    result_dict = calculatePrepaymentNumbers(ord_mrtg_amt,interest_rate,years_remaining,add_principal_pmnt)
    with col2:
        st.write("")
        st.write("")
        df = getAmmortizationSchedule(ord_mrtg_amt,interest_rate,org_mortg_term)
        chart_data = df[['Balance','TotalPaid']]
        st.line_chart(chart_data)
        st.write('### Result:')
        col2_a, col2_b = st.columns(2)
        with col2_a:
            st.write(f"**Original Monthly Payment**: {round(result_dict['monthlyPayment'],2)}")
            st.write(f"**New Monthly Payment**: {round(result_dict['newMonthlyPayment'],2)}")
        with col2_b:
            st.write(f"**Months Saved**: {result_dict['monthSaved']}")
            st.write(f"**Interest Saved**: {round(result_dict['totalInterestSaved'],2)}")
        



#st.write(df)
