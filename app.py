#Import All Dependencies
import streamlit as st
import math
import pandas as pd
import numpy as np
import ammortization as am
import plotly.express as px
import plotly.graph_objects as go


#-------Charting helper Functions----------

#Function to show large result boxes at the top of the page
def show_gauge_meter(value,title,prefix=None):
    config = {'displayModeBar': False}
    fig = go.Figure(go.Indicator(
        #mode = "gauge+number",
        mode = "number",
        value = value,
        number = {'prefix': prefix, "font":{"size":80,"color":"black"}},
        title = {'text': title,"font":{"size":20,"color":"green"}},
        domain = {'x': [0, 1], 'y': [0, 1]}
        
    ))
    fig.update_layout(height=140)
    fig.update_layout(paper_bgcolor = "rgba(0,0,0,0)")
    return fig


#Function to create the main balance vs paid chart for new and old payment plan
def create_chart(df):
    fig = px.line(df, x=df.index, y=['orig_Balance','orig_TotalPaid','new_Balance','new_TotalPaid'])
    fig.update_layout(height=400)
    fig.update_layout(yaxis_range=[0,ord_mrtg_amt])
    fig.update_layout(xaxis_range=[0,org_mortg_term*12])
    fig.update_layout(xaxis_dtick=20)
    fig.update_layout(xaxis_title='Num of Months')
    fig.update_layout(yaxis_title='Loan Amount')
    return fig


#-------Ammortization Calculation Helper Functions---------------

#Function to calculate New and Old Monthly payment as implemented by me
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


#Function to call the Ammortization functions as downloaded from the internet
def getAmmortizationSchedule(ord_mrtg_amt, interest_rate, org_mortg_term,add_principal_pmnt):
    #Call assuming 12 payements per year, i.e. monthly payment schedule
    df = am.amortisation_schedule(ord_mrtg_amt,interest_rate/100.0,12,org_mortg_term,add_principal_pmnt)
    return df



#Layout
st. set_page_config(layout="wide")

#Title
st.markdown("<h1 style='text-align: center;'>Mortgage Prepayment Calculator</h1>", unsafe_allow_html=True)


#------Create empty result container  at the top of the page which will be populated after all the calculations
#Result container
st.divider()
result_container = st.container()
st.divider()


#----Divide the page into two columns below the main result display
col1, col2 = st.columns(2)


#Column 1 - Input Form
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
years_remaining = int(years_remaining)
add_principal_pmnt = float(add_principal_pmnt)



#Calculate results
result_dict = calculatePrepaymentNumbers(ord_mrtg_amt,interest_rate,years_remaining,add_principal_pmnt)

#Get original payments with no additional payment and original terms
df_original = getAmmortizationSchedule(ord_mrtg_amt,interest_rate,org_mortg_term,add_principal_pmnt=0)

#Split dataframe into past and remaining future payments
idx = ((org_mortg_term-years_remaining)*12) #TODO parameterize this

#past payments df
df_past = df_original.iloc[:idx]

#Get Last value of total paid from df_past
past_total_paid = df_past['TotalPaid'].iloc[-1]

#remaining payments df
df_remaining = df_original.iloc[idx:]

#Extract remaining balance from remaining payments df which will be input to the new payment schedule calculation
remaining_balance = df_remaining['Balance'].iloc[0]



#Column2 - Chart and Slider
#Show the chart and a slider to tweak the Additional Payment
with col2:
    graph_container = st.container()
    add_principal_pmnt = st.slider("**Addtional Payment Per month ($)**",min_value=0,max_value=3000,step=50,value=int(add_principal_pmnt))

    #Get payments with additional monthly payment and remaining balanace and terms
    df_new_remaining = getAmmortizationSchedule(remaining_balance,interest_rate,years_remaining,add_principal_pmnt)
    
    #Add past total paid to the df_new_remaining total paid
    df_new_remaining['TotalPaid'] = df_new_remaining['TotalPaid'] + past_total_paid
    
    #Rename the columns of the dataframe in order to concat with original df
    df_new_remaining.columns = [f'new_{col}' for col in df_new_remaining.columns]
  
    # TODO this part of the code needs to be changed to accomodate past payment and new payments in the graph
    result_dict = calculatePrepaymentNumbers(ord_mrtg_amt,interest_rate,years_remaining,add_principal_pmnt)
 
    #make the columns names for the past df same as the new remaining df so that both can be concatenated one below the other
    df_past.columns = df_new_remaining.columns

    #conct past payments df with new remaining payments df one below the other
    past_new_df = pd.concat([df_past,df_new_remaining],axis=0,ignore_index=True)

    #Rename columns of the original payment plan dataframe
    df_original.columns = [f'orig_{col}' for col in df_original.columns]

    #Concat original plan df with past and new concatenated df to have 4 time series in it
    df_concat = pd.concat([df_original,past_new_df],axis=1)

    #Extract out the 4 timeseries columns which need to be plotted on the chart
    chart_data = df_concat[['orig_Balance','orig_TotalPaid','new_Balance','new_TotalPaid']] #TODO change this df to append original payment plan fro past months with new payment plan for new months
    
    #Call charting helper function to configure the chart and get back the figure
    fig = create_chart(chart_data)

    #Call streamlit's plotly charting API and pass the figure from above call
    graph_container.plotly_chart(fig,use_container_width=True)



#Assign result variables
original_monthly_payment = round(df_concat['orig_Instalment'][0]*-1,2)
new_monthly_payment = round(original_monthly_payment + add_principal_pmnt,2)
months_saved = result_dict['monthSaved']
interest_saved = round(result_dict['totalInterestSaved'])

#Show results in result container
with result_container:

    col1, col2, col3, col4 = st.columns(4)
    #fig_gauge = show_gauge_meter(450)
    col1.plotly_chart(show_gauge_meter(original_monthly_payment,"Original Monthly Payment",prefix="$"),use_container_width=True,config = {'displayModeBar': False})
    col2.plotly_chart(show_gauge_meter(new_monthly_payment,"New Monthly Payment",prefix="$"),use_container_width=True,config = {'displayModeBar': False})
    col3.plotly_chart(show_gauge_meter(months_saved,"Months Saved"),use_container_width=True,config = {'displayModeBar': False})
    col4.plotly_chart(show_gauge_meter(interest_saved,"Interest Saved",prefix="$"),use_container_width=True,config = {'displayModeBar': False})


#Show one liner result summary at the bottom of the page
result_summary = f'You will save ${interest_saved} in total interest by paying additional ${add_principal_pmnt} monthly payment.'
st.markdown(f"<h2 style='text-align: center;'>{result_summary}</h1>", unsafe_allow_html=True)
st.divider()
