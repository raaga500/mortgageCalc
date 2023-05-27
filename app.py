import streamlit as st
import math
import pandas as pd
import numpy as np
import ammortization as am
# from PIL import Image
import plotly.express as px
import locale
locale.setlocale( locale.LC_ALL, '' )

#Helper functions
def create_chart(df):
    fig = px.line(df, x=df.index, y=['orig_Balance','orig_TotalPaid','new_Balance','new_TotalPaid'])
    fig.update_layout(height=400)
    fig.update_layout(yaxis_range=[0,ord_mrtg_amt])
    fig.update_layout(xaxis_range=[0,org_mortg_term*12])
    fig.update_layout(xaxis_dtick=20)
    fig.update_layout(xaxis_title='Num of Months')
    fig.update_layout(yaxis_title='Loan Amount')
    return fig

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

def getAmmortizationSchedule(ord_mrtg_amt, interest_rate, org_mortg_term,add_principal_pmnt):
    df = am.amortisation_schedule(ord_mrtg_amt,interest_rate/100.0,12,org_mortg_term,add_principal_pmnt)
    return df



#Layout
st. set_page_config(layout="wide")

#Title
st.markdown("<h1 style='text-align: center;'>Mortgage Prepayment Calculator</h1>", unsafe_allow_html=True)

#Result container
st.divider()
result_container = st.container()
st.divider()

#Input Form
col1, col2 = st.columns(2)
with col1:
    with st.form("mortgage_prepay_form"):
        ord_mrtg_amt = st.text_input("**Original Mortgage Amount**",value=212000).strip()
        org_mortg_term = st.text_input("**Original Mortgage Term (in years)**",value=15).strip()
        years_remaining = st.text_input("**Years remaining**",value=14).strip()
        interest_rate = st.text_input("**Interest Rate(%)**",value=4).strip()
        add_principal_pmnt = st.text_input("**Additional Monthly Principal Payment($)**",value=175).strip()
        #add_principal_pmnt = st.slider("Addtional Payment Per month",min_value=0,max_value=3000,step=50)
        #add_principal_pmnt=0
        submitted = st.form_submit_button("**Submit**")

#Datatype conversion
ord_mrtg_amt = float(ord_mrtg_amt)
org_mortg_term = int(org_mortg_term)
interest_rate = float(interest_rate)
years_remaining = float(years_remaining)
add_principal_pmnt = float(add_principal_pmnt)



#Calculate results
result_dict = calculatePrepaymentNumbers(ord_mrtg_amt,interest_rate,years_remaining,add_principal_pmnt)
df_original = getAmmortizationSchedule(ord_mrtg_amt,interest_rate,org_mortg_term,add_principal_pmnt=0)
df_original.columns = [f'orig_{col}' for col in df_original.columns]


#Show the chart and a slider to tweak the Additional Payment
with col2:
    graph_container = st.container()
    add_principal_pmnt = st.slider("**Addtional Payment Per month ($)**",min_value=0,max_value=3000,step=50,value=int(add_principal_pmnt))
    result_dict = calculatePrepaymentNumbers(ord_mrtg_amt,interest_rate,years_remaining,add_principal_pmnt)
    df_new = getAmmortizationSchedule(ord_mrtg_amt,interest_rate,org_mortg_term,add_principal_pmnt)
    df_new.columns = [f'new_{col}' for col in df_new.columns]
    df_concat = pd.concat([df_original,df_new],axis=1)

    chart_data = df_concat[['orig_Balance','orig_TotalPaid','new_Balance','new_TotalPaid']]
    fig = create_chart(chart_data)
    graph_container.plotly_chart(fig,use_container_width=True)

#Assign result variables
original_monthly_payment = round(df_concat['orig_Instalment'][0]*-1,2)
new_monthly_payment = round(original_monthly_payment + add_principal_pmnt,2)
months_saved = result_dict['monthSaved']
interest_saved = round(result_dict['totalInterestSaved'])

#Show results in result container
with result_container:
    col2_a, col2_b = st.columns(2)
    with col2_a:
        st.write(f"**Original Monthly Payment** : ${original_monthly_payment}")
        #st.write(original_monthly_payment)
        st.write(f"**New Monthly Payment**: ${new_monthly_payment}")
    with col2_b:
        st.write(f"**Months Saved**: {months_saved}")
        st.write(f"**Interest Saved**: ${interest_saved}")

result_summary = f'You will save {locale.currency(interest_saved, grouping=True)} in total interest by paying additional ${add_principal_pmnt} monthly payment.'
st.markdown(f"<h2 style='text-align: center;'>{result_summary}</h1>", unsafe_allow_html=True)
st.divider()

st.write(df_concat)
# st.write(df_concat['new_Interest'].sum())
# st.write(df_concat['orig_Interest'].sum())
# st.write(result_dict['totalInterestSaved'])
# st.write(result_dict['monthSaved'])

# time_diff_in_months = (org_mortg_term - years_remaining)*12
# time_diff_in_months
# df_concat.loc[time_diff_in_months-1:]

# st.write(df_original)
# st.write(df_new)
# st.write(df_concat)