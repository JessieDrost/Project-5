# ons wiskundige model 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


Afstandsmatrix = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name = "Afstandsmatrix" )
all_sheets = pd.read_excel("Connexxion data - 2024-2025.xlsx", sheet_name = None)
print("Beschikbare sheets in het bestand:", list(all_sheets.keys()))

# we hebben 2 tabellen dus die kunnen we zo laten zien:
Dienstregeling = all_sheets['Dienstregeling']
Afstandsmatrix = all_sheets['Afstandsmatrix']

print(Dienstregeling.head())
print(Afstandsmatrix.head())


max_cap = 300
SOH = [85, 95] #(even vragen)
oplaadtempo_90 = 450 
oplaadtempo_10 = 60

DCap_85 = max_cap * 0.85 #(255 kWh)(even vragen)
DCap_95 = max_cap * 0.95 #(285 kWh)(even vragen)
DCap = [DCap_85, DCap_95]
Overdag_90 = [DCap_85*0.9,DCap_95*0.9]
usage = [0.7,2.5] 

# Ik bereken hier de afstand in km
Afstandsmatrix["afstand in meters"] = Afstandsmatrix["afstand in meters"]/1000
# Hier hernoem ik de kolom.
Afstandsmatrix = Afstandsmatrix.rename(columns={'afstand in meters': 'afstand in km'})
# Ik wil laten zien dat alle waarde die NaN zijn materiaalritten zijn.
Afstandsmatrix["buslijn"] = Afstandsmatrix["buslijn"].fillna("materiaalrit")

# hoeveel km per uur moet je rijden?
# we hebben het aantal km en het aantal minuten.
# we moeten 1 kolomen aanmaken met max reistijd per uur.
# we moeten 1 kolom aanmaken met min reistijd per uur.
Afstandsmatrix["min reistijd in min"] = Afstandsmatrix["min reistijd in min"]/60
Afstandsmatrix["max reistijd in min"] = Afstandsmatrix["max reistijd in min"]/60
Afstandsmatrix = Afstandsmatrix.rename(columns={'min reistijd in min': 'min reistijd in uur'})
Afstandsmatrix = Afstandsmatrix.rename(columns={'max reistijd in min': 'max reistijd in uur'})

# we willen weten hoeveel km per uur een bus gemiddeld gaat.
Afstandsmatrix["max_speed"] = Afstandsmatrix["afstand in km"]/ Afstandsmatrix['min reistijd in uur'] 
Afstandsmatrix["min_speed"] = Afstandsmatrix["afstand in km"]/ Afstandsmatrix['max reistijd in uur'] 

# we willen weten hoeveel kwh je nodig hebt per rit:d
#Verbruik per km =  0.7-2.5 kWh 
Afstandsmatrix["max_energy"] = Afstandsmatrix["afstand in km"]* 2.5
Afstandsmatrix["min_energy"] = Afstandsmatrix["afstand in km"]* 0.7

# Ik ga ervan uit dat het aantal energie die je gebruikt en hoe snel je rijd linear is.
# de berekening doet het niet en ik begrijp niet waarom??? Kan je het me laten weten Yvonne? 

# busrit = van ehvapt naar ehvbst van 400 of andersom
# speed = gemiddelde km/uur
# Functie om het energieverbruik te berekenen
def calculate_energy(busrit, speed):
    if speed < busrit['min_speed']:
        energy_consumed = busrit['min_energy']
    elif speed > busrit['max_speed']:
        energy_consumed = busrit['max_energy']
    else:
        m = (busrit['max_energy'] - busrit['min_energy']) / (busrit['max_speed'] - busrit['min_speed'])  # richtingscoëfficiënt berekenen
        b = busrit['min_energy'] - m * busrit['min_speed'] #beginwaarde berekenen
        energy_consumed = m * speed + b # lineare lijn vormen

    percentage_hb = (energy_consumed / DCap_85*0.9) * 100  # hoeveel energie er maximaal leeg gaat in de accu  
    percentage_lb = (energy_consumed / DCap_95*0.9) * 100  # hoeveel energie er minimaal leeg gaat in de accu 
    return energy_consumed, percentage_lb, percentage_hb

# Gegevens voor de busrit en snelheid
busrit = 0  # Eerste rij
speed = 27  # Gemiddelde km/uur

# Bereken energieverbruik en percentage
energy_consumed, percentage_lb, percentage_hb = calculate_energy(df.iloc[busrit], speed)

#Definitie maken over de batterij gebruik? Lottes interpetatie 
def battery_usage(distance):
    """
    Je wilt de batterij gebruik per verschillende routes berekenen
    parameters: de afstand en de locaties
    Output: Batterij percentage na de rit
    """
    #Bereken de batterij gebruik voor de routes. Dus importeer de routes per km
    #De routes per km * met het verbruik 
    #Misschien de oplaad definitie met deze definitie eenmaken?
    #En dan de batterij = 100% - batterijgebruik
    #En dan miss later ervoor zorgen dat je de batterij kan laten opladen als die onder 10 komt? Fleur dit kan iemand anders desnoods ook doen. Anders heb je heel veel werk
#Zorg ervoor dat de batterij niet onder de 10% komt, overdag
def oplaad(battery, DCap):
    """
    Je wilt dat de definitie berekent wanneer je moet opladen
    Parameter: is de hoeveelheid batterij die je nog hebt
    Output: Nieuwe batterij percentage?
    """
    #Minimale batterijpercentage
    min_battery = 0.10*DCap #De batterij mag niet onder dit percentage komen
    max_battery = 0.90*DCap #Maximale batterij overdag
    oplaadtijd = 15
    opladen = oplaadtempo_90*oplaadtijd #Minimale oplaadtijd. Moet eigenlijk even kijken hoe ik het zonder cijfer doe
    if battery <= min_battery:
        new_battery = battery+opladen
        if new_battery>max_battery: #De batterij mag niet meer dan de 90% van de 85 of 95% opgeladen worden
            new_battery = max_battery
    else: 
        new_battery = battery 
    return new_battery

       



""""   
Overdag niet meer dan 90% opladen = 229,5 - 256,5 kWh -> staat in functie opladen 

Altijd tenminste 15 min achtereen worden opgeladen. -> staat ook in opladen

Veiligheidsmarge van ongeveer 10% van de SOH -> bus minimaal SOC (state of charge) waarde van 10%Veiligheidsmarge van ongeveer 10% van de SOH -> bus minimaal SOC (state of charge) waarde van 10%. Minimale hoeveelheid in accu = 25,5 -28,5 kWh -> staat ook in opladen

Verbruik per km =  0.7-2.5 kWh 

Idling verbruikt het 0.01 kWh (verbruik van bus in stilstand) 

Lijn 401 eerste rit vertrekt om 6:04 vanuit de airport (Apt) naar Eindhoven Centraal (bst). 401 laatste rit van Apt naar bst is om 00:31. Deze lijn zou klaar moeten zijn tussen de 00:53 en 00:56. 

Lijn 401 eerste rit vertrekt om 5:07 vanuit Eindhoven Centraal (bst) naar airport (Apt). 401 laatste rit van bst naar apt is om 00:09. Deze lijn zou klaar moeten zijn tussen de 00:31 en 00:33. 

Lijn 400 eerste rit vertrekt om 7:19 vanuit de airport (Apt) naar Eindhoven Centraal (bst). 400 laatste rit van Apt naar bst is om 20:46. Deze lijn zou klaar moeten zijn tussen de 21:07 en 21:09 

Lijn 400 eerste rit vertrekt om 06:52 vanuit Eindhoven Centraal (bst) naar airport (Apt). 401 laatste rit van bst naar apt is om 19:37. Deze lijn zou klaar moeten zijn tussen de 19:58 en 20:00.  
""""

