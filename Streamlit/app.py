import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np

# Config
st.set_page_config(
    page_title="GetAround Dashboard",
    page_icon="💸 ",
    layout="wide"
)

st.title("GetAround Dashboard")

st.subheader('Les données')

@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_excel("./get_around_delay_analysis.xlsx")
    return df

# Load the data
data = load_data()

#len dataFrame
lenrental=len(pd.unique(data['rental_id']))
lencar=len(pd.unique(data['car_id']))

# Look the data
data_rows = data.head() # Filtering the dataframe.
st.dataframe(data_rows) # Displaying the dataframe.

st.markdown(f"""
      {lenrental} rentals ids and lignes \n
      {lencar} voitures \n
    """)

#Ensemble du dataset
st.title('Ensemble du dataset')

data['avance_checkout']=data["delay_at_checkout_in_minutes"]<=0
fig = px.pie(data['avance_checkout'], names='avance_checkout', title='Proportion de retard')
st.plotly_chart(fig,theme=None,use_container_width=True)

#Proportion du retard selon chekin type
st.subheader('Moyenne du retard selon chekin type')
sc=data.groupby(data['checkin_type'])["delay_at_checkout_in_minutes"].mean()
st.markdown(f"""
    * Moyenne retard voitures connectées: {round(sc[0])} min \n
    * Moyenne retard voitures non connectées: {round(sc[1])} min""")

#On s'interesse aux retards
df6=data.loc[data['avance_checkout']==False]
st.subheader(f"""On fait un filtre sur les retardataires""")

#On retire les outliers
df6=df6.drop(df6[df6.delay_at_checkout_in_minutes>500].index)
fig = px.box(df6, y="delay_at_checkout_in_minutes",title='Observation des retards')
st.plotly_chart(fig,theme=None,use_container_width=True)
sc6=df6.groupby(df6['checkin_type'])["delay_at_checkout_in_minutes"].mean()

st.markdown(f"""* Moyenne retard: {round(df6['delay_at_checkout_in_minutes'].mean())} min """)
st.markdown(f"""
    * Moyenne retard voitures connectées: {round(sc6[0])} min \n
    * Moyenne retard voitures non connectées: {round(sc6[1])} min""")

#Cancelling proportion
fig = px.pie(data['state'], names='state', title='Annulations en proportion')
st.plotly_chart(fig,theme=None,use_container_width=True)

#Les courses précédentes
st.title('Les courses précédentes')
id= 1841/21310
st.markdown(f"""
     La donnée n'est complétée que pour {"{:.0f}%".format(id*100)} des lignes""")

fig = px.box(data, y="time_delta_with_previous_rental_in_minutes",title='Temps restant sur la course précédente')
st.plotly_chart(fig)
st.text('Temps médian de 180 min')

st.subheader("Dataset fusionné pour avoir plus d'informations sur les courses précédentes")
#On fait un merge sur le dataset
df7 = pd.merge(data, data, how='inner', left_on = 'previous_ended_rental_id', right_on = 'rental_id')
#On n'affiche que les 15 premières lignes
df7r = df7.head(15)
st.dataframe(df7r)
st.text('dataset de 1841 lignes')

#Calcul du rapport entre le temps libre laissé entre la course précédente et la future course et le retard au check
st.subheader('Calcul du temps libre')
st.markdown("""Calcul d'un delta entre les colonnes ['time_delta_with_previous_rental_in_minutes_x'] et ['delay_at_checkout_in_minutes_y']""")
df7['temps_libre']=df7['time_delta_with_previous_rental_in_minutes_x']-df7['delay_at_checkout_in_minutes_y']

#Ajout de la colonne delta insufisant si le temps libre < au retard
df7['delta_insuffisant']=df7['temps_libre']<0

col1, col2 = st.columns(2)

with col1:
  fig = px.bar(df7['delta_insuffisant'], x="delta_insuffisant",color=df7["delta_insuffisant"])
  st.plotly_chart(fig,theme=None,use_container_width=True)

with col2:
  fig = px.pie(df7['delta_insuffisant'], names='delta_insuffisant', title="Proportion de courses avec un temps libre insuffisant")
  st.plotly_chart(fig,theme=None,use_container_width=True)

st.markdown("Pour 11,8% des courses il n'y a pas assez de temps libre")

fig = px.histogram(df7['delta_insuffisant'], x="delta_insuffisant", color=df7["state_x"],barnorm='percent',title='Annulations en proportion en fonction du time delta', text_auto=True)
st.plotly_chart(fig,theme=None,use_container_width=True)
st.markdown("Lorsque le delta est insuffisant il y a un peu plus plus d'annulations en proportion")


st.subheader("Calcul du retard moyen à la course suivante en fonction du temps libre laissé")
insuf=df7.groupby(df7['delta_insuffisant'])["delay_at_checkout_in_minutes_x"].mean()
st.markdown(f"""* Moyenne retard si le temps libre est suffisant:{round(insuf[0])}min""")
st.markdown(f"""* Moyenne retard si le temps libre est insuffisant:{round(insuf[1])}min""")

#Proportion de temps libre insuffisant si voiture connectée ou non
fig = px.histogram(df7['checkin_type_y'], x='checkin_type_y', color=df7['delta_insuffisant'],barnorm='percent',title="Proportion de temps libre insuffisant entre les voitures connectées et les non connectées",text_auto=True)
st.plotly_chart(fig,theme=None,use_container_width=True)


st.title("Les loueurs sur l'ensemble du dataset")

#Nombre de courses par voiture
st.subheader('Calcul du nombre moyen de courses par voiture')
nombre_locations_par_voiture=data.groupby(data['car_id'])["checkin_type"].count()
df2=pd.DataFrame(nombre_locations_par_voiture)
df2=df2.rename(columns={'checkin_type':'nombre_locations_par_voiture'})
fig = px.histogram(df2, x=df2["nombre_locations_par_voiture"],title="Nombre de locations par voitures")
st.plotly_chart(fig,theme=None,use_container_width=True)
#On retire du df valeurs en double...
df2['checkin_type']=data.groupby(data['car_id'])["checkin_type"].unique()
values=[['connect'],['mobile']]

col1, col2 = st.columns(2)

#Proportion de voitures réalisant plus de 5 courses
with col1:
   df3 = df2[df2.checkin_type.isin(values)]
   df3['courses_supp']=df3["nombre_locations_par_voiture"]>5
   fig = px.pie(df3['courses_supp'], names='courses_supp', title="Répartition des gros loueurs")
   st.plotly_chart(fig,theme=None,use_container_width=True)

#Proportion de voitures connectées
with col2:
   df3=df3.reset_index()
   fig = px.pie(df3['checkin_type'], names='checkin_type', title="Proportion de voitures connectées sur l'ensemble du dataset")
   st.plotly_chart(fig,theme=None,use_container_width=True)

#On crée nouvelle colonne dans le df car liste de liste...
df3['new_checkin_type']=[df3['checkin_type'][i][0] for i in range (len(df3['checkin_type']))]

#Pourcentage de gros loueurs en fonction du chekin type
fig = px.histogram(df3['new_checkin_type'], x=df3['new_checkin_type'], color=df3['courses_supp'],barnorm='percent',text_auto=True,title="Pourcentage de gros loueurs en fonction du chekin type")
st.plotly_chart(fig,theme=None,use_container_width=True)

st.markdown("""Il y a beaucoup plus de gros loueurs chez les voitures connectées,on observe également moins de retard parmi ces derniers\n
Imposer des contraintes de temps risque de pénaliser les voitures connectées. \n
Il serait judicieux d'imposer un minimum de temps entre 2 courses plus élévé pour les voitures non connectées que pour les voitures\n
connectées. Il y a un retard moyen de 80 minutes, la plupart des valeurs se situent entre 17 et 105 min \n
Le temps libre médian de 180 min, ma recommandation serait de laisser un temps libre entre 60 et 120 min\n
surtout pour les voitures non connectées.  """)