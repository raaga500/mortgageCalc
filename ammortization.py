import numpy as np
import pandas as pd


def PMT(rate, nper,pv, fv=0, type=0 ,ap=0):
    if rate!=0:
        pmt = (rate*(fv+pv*(1+ rate)**nper))/((1+rate*type)*(1-(1+ rate)**nper))
    else:
        pmt = (-1*(fv+pv)/nper)  
    return(pmt-ap)


def IPMT(rate, per, nper,pv, fv=0, type=0):
  ipmt = -( ((1+rate)**(per-1)) * (pv*rate + PMT(rate, nper,pv, fv=0, type=0)) - PMT(rate, nper,pv, fv=0, type=0))
  return(ipmt)


def PPMT(rate, per, nper,pv, fv=0, type=0,ap=0):
  ppmt = PMT(rate, nper,pv, fv=0, type=0, ap=ap) - IPMT(rate, per, nper, pv, fv=0, type=0)
  return(ppmt)

def amortisation_schedule(amount, annualinterestrate, paymentsperyear, years,adtnlPayment=0):

    df = pd.DataFrame({'Principal' :[PPMT(annualinterestrate/paymentsperyear, i+1, paymentsperyear*years, amount,ap=adtnlPayment) for i in range(paymentsperyear*years)],
                                 'Interest' :[IPMT(annualinterestrate/paymentsperyear, i+1, paymentsperyear*years, amount) for i in range(paymentsperyear*years)]})
    
    df['Instalment'] = df.Principal + df.Interest
    df['Balance'] = amount + np.cumsum(df.Principal)
    df['TotalPaid'] = amount  - df['Balance']
    return(df[df['Balance']>=0])

df = amortisation_schedule(50000, 0.085, 12, 6)