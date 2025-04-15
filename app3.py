"""
Created on Mon Sep 23 10:59:42 2024

@author: Carlos Leonardo Beltrán Ríos, Escuela de Física, UIS
"""
import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit as cf
import matplotlib.pyplot as plt

@st.cache_data
@st.cache_resource
def Vline(XY,V0,b1,b2,r1,r2,alfa):
    xp=XY[0,:]
    yp=XY[1,:]
    V2=V0/(((xp+b1)*1e-2)**2 +(yp*1e-2)**2)**r1
    V1=V0/(((xp-b2)*1e-2)**2 +(yp*1e-2)**2)**r2
    Veff=alfa*(V2-V1)
    return Veff

def Fiteo(nxy,Vz,p_ini):
    bounds=((9,0, 0, -3, -3,0),(11,12, 13, 3, 3,np.inf))
    best_val,cov=cf(Vline,nxy,Vz,p0=p_ini,
              bounds=bounds,method='trf',maxfev=5000)
    return best_val

def organizar(M): #organiza los datos para su uso
    row,col=np.shape(M)
   # print(row,col)
    V=M[:,0]
    XY=M[0:,1:]
    ind=np.argsort(V)
    V=V[ind]
    nXY=np.empty(np.shape(XY))
    for i in range(len(ind)):
        nXY[i,:]=XY[ind[i],:]

    row,col=np.shape(M)    
    filas=int(row*(col-1)/2)
    nXY=nXY.reshape(filas,2)

    Vz=[]
    for i in range(int(filas/row)):
        Vz=np.append(Vz,V)
    ind=np.argsort(Vz)
    Vz=Vz[ind]
    return Vz,nXY

def grafico1(nxpyp,best): #datos para construir
    V0,b1,b2,r1,r2,a=best
    x=nxpyp[0,:]
    y=0
    V=np.zeros(len(x))
    for j in range(len(x)):
        xj=x[j]
        y=0
        V2n=V0/(((xj+b1)*1e-2)**2 +(y*1e-2)**2)**r2
        V1n=V0/(((xj-b2)*1e-2)**2 +(y*1e-2)**2)**r1
        V[j]=a*(V2n-V1n)

    return V

def grafico2(nxpyp,best): #datos para construir campo E
    V0,b1,b2,r1,r2,a=best
    x=nxpyp[0,:]
    y=nxpyp[1,:]
    V=np.zeros((len(xp),len(yp)))
    for j in range(len(x)):
        for k in range(len(y)):
            V2n=V0/(((x[j]+b1)*1e-2)**2 +(y[k]*1e-2)**2)**r2
            V1n=V0/(((x[j]-b2)*1e-2)**2 +(y[k]*1e-2)**2)**r1
            V[k,j]=a*(V2n-V1n)
    return V

st.markdown("""
    <style>
        body {
            font-size:25px !important;
        }
        .big-font {
            font-size:50px !important;
        }
        .medium-font {
            font-size:30px !important;
        }
        .small-font {
            font-size:15px !important;
        }
    </style>
    """, unsafe_allow_html=True)
st.markdown('<p class="big-font">Equipotential Lines!</p>', unsafe_allow_html=True)
   
uploaded_file =  st.file_uploader("Choose a file", 
                                  type=['csv', 'xlsx', 'txt'])

if uploaded_file is not None:
    # Check the file type
    file_type = uploaded_file.type

    # Use the appropriate pandas function to read the file
    if file_type == "text/csv":
        df = pd.read_csv(uploaded_file,delimiter=';')
        
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        df = pd.read_excel(uploaded_file)
        data = pd.read_excel(uploaded_file, sheet_name=None)
        
        sheet_name = st.selectbox("Choose a sheet", list(data.keys()))
        
        df = data[sheet_name]
        
    elif file_type == "text/plain":
        df = pd.read_csv(uploaded_file, sep="\t")  # assuming tab-separated values

    # Use the dataframe in your app
  

df = df.dropna()  # Remove rows with missing values
    
datos=df.values #matrix de datos a trabajar
st.write(df) #muestra los datos de la hoja de excel,csv o txt
    
    

#descripción del modelo: ecuacion tipo latex
st.text('Physic model is given by')
st.latex(r'V=K\,V_0\left(\frac{1}{((x+b_1)^2+y^2)^{r_1}}-\frac{1}{(x-b_2)^2+y^2)^{r_2}}\right)')

st.text('Enter the experimental prameters for')
V0 = st.number_input('Parameter V0 (volts):')
b1 = st.number_input('Parameter b1(cm):')
b2 = st.number_input('Parameter b2(cm):')

st.text('Enter the initial values for')
K = st.number_input('Parameter K:')
r1 = st.number_input('Parameter r1:')
r2 = st.number_input('Parameter r2:')

#obtención de lo mejores valores para los parametros del modelo

Vz,XY=organizar(datos) #organiza en datos para graficar

p_ini=[V0,b1,b2,r1,r2,K]

best_val=Fiteo(XY.T,Vz,p_ini)
V0,b1,b2,r1,r2,a=best_val

st.text('Optimized paramters values are:')
st.write('V0=',"{:.3f}".format(V0))
st.write('b1=',"{:.3f}".format(b1))
st.write('b2=',"{:.3f}".format(b2))
st.write('r1=',"{:.3e}".format(r1))
st.write('r2=',"{:.3e}".format(r2))
st.write('K=',"{:.3f}".format(a))

#crear datos con los valores optimizados
xp=np.linspace(min(XY[:,0])-0.1,max(XY[:,0])+0.1,200)
yp=np.linspace(min(XY[:,1])-0.1,max(XY[:,1])+0.1,200)

yp0=np.zeros(len(xp))
nxpyp0=np.array([xp,yp0])
best_fun1=grafico1(nxpyp0,best_val)


fig, ax = plt.subplots(figsize=(3, 3))
ax.plot(datos[:,1],datos[:,0],'*',c='r',label='datos')
ax.plot(xp,best_fun1,ls='-',c='b',label='modelo')
ax.set_xlabel('x(cm)')
ax.set_ylabel('V(volts)')
ax.set_title('Fitted data for potential (y=0 line)')
ax.legend()
plt.show()
st.pyplot(fig)

#graficando las equipotenciales y el campo
fig1, ax1 = plt.subplots(figsize=(5, 5))
Vexp=datos[:,0]

#puntos experimentales
ax1.scatter(XY[:,0],XY[:,1])

#dibujar campo electrico
nxpyp=np.array([xp,yp])
Vp=grafico2(nxpyp, best_val)
Ey,Ex=np.gradient(-Vp)
# Ex=Ex/np.hypot(Ex,Ey)
# Ey=Ey/np.hypot(Ex,Ey)
x,y=np.meshgrid(xp,yp)
x=x[::20,::20]
y=y[::20,::20]
Ex=Ex[::20,::20]
Ey=Ey[::20,::20]
ax1.quiver(x,y,Ex,Ey) #grafica el campo

#dibujar equipotenciales

nlv=len(Vexp) #numero de niveles
levels=np.sort(Vexp)

CS = ax1.contour(xp,yp,Vp,nlv,levels=levels,colors='r')# Negative contours default to dashed.
ax1.clabel(CS,inline=True, fontsize=10)
ax1.set_xlabel('x(cm)')
ax1.set_ylabel('y(cm)')
ax1.set_title('Equipotential lines and Electric field')
ax1.legend()
plt.show()
st.pyplot(fig1)














