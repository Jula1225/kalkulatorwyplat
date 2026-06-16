import streamlit as st
import re

stopnie={
    "Kierownik":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":1},
    "Menager":{"podstawa":2200000,"norma_kursow":15,"norma_godzin":10,"zatrudnienie":50000,"kursy":300000,"godzina":120000,"procent":1},
    "Dyrektor":{"podstawa":2700000,"norma_kursow":10,"norma_godzin":10,"zatrudnienie":50000,"kursy":300000,"godzina":140000,"procent":1},
    "Próbny Kierownik":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":0.5},
    "Próbny Menager":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":1}
}

def popraw_tekst(tekst):
    tekst=tekst.replace("\xa0"," ")
    tekst=re.sub(r"[ \t]+"," ",tekst)
    tekst=re.sub(r"\n+","\n",tekst)
    return tekst.strip()

def liczba_z_tekstu(wzor,tekst):
    tekst=popraw_tekst(tekst)
    x=re.search(wzor,tekst,re.IGNORECASE)
    if x:
        return int(x.group(1).replace(" ",""))
    return 0

def tekst_z_tekstu(wzor,tekst):
    tekst=popraw_tekst(tekst)
    x=re.search(wzor,tekst,re.IGNORECASE)
    if x:
        return x.group(1).strip()
    return ""

def znajdz_stopien(tekst):
    s=tekst_z_tekstu(r"Stopień\s*:\s*(.+)",tekst)
    s=popraw_tekst(s).lower()

    if "próbny kierownik" in s or "probny kierownik" in s:
        return "Próbny Kierownik"
    if "próbny menager" in s or "probny menager" in s or "próbny manager" in s or "probny manager" in s:
        return "Próbny Menager"
    if "dyrektor" in s:
        return "Dyrektor"
    if "menager" in s or "manager" in s:
        return "Menager"
    if "kierownik" in s:
        return "Kierownik"

    return ""

def formatuj(liczba):
    return f"{int(liczba):,}".replace(","," ")

def oblicz(tekst):
    imie=tekst_z_tekstu(r"Imię\s*i\s*nazwisko\s*:\s*(.+)",tekst)
    kursy=liczba_z_tekstu(r"Ilość\s*kursów\s*:\s*([\d ]+)",tekst)
    godziny=liczba_z_tekstu(r"Ilość\s*godzin\s*:\s*([\d ]+)",tekst)
    delegacje=liczba_z_tekstu(r"Ilość\s*delegacji\s*:\s*([\d ]+)",tekst)
    zatrudnienia=liczba_z_tekstu(r"Ilość\s*zatrudnień\s*:\s*([\d ]+)",tekst)
    telefon=tekst_z_tekstu(r"Nr\.?\s*Telefonu\s*:\s*(.+)",tekst)

    stopien=znajdz_stopien(tekst)

    if stopien=="":
        return None,"Nie znaleziono stopnia."

    d=stopnie[stopien]

    wynik=d["podstawa"]
    wynik+=zatrudnienia*d["zatrudnienie"]

    if kursy>d["norma_kursow"]:
        wynik+=((kursy-d["norma_kursow"])//20)*d["kursy"]

    if godziny>d["norma_godzin"]:
        wynik+=(godziny-d["norma_godzin"])*d["godzina"]

    wynik=wynik*d["procent"]

    dane={
        "imie":imie,
        "stopien":stopien,
        "kursy":kursy,
        "godziny":godziny,
        "delegacje":delegacje,
        "zatrudnienia":zatrudnienia,
        "telefon":telefon,
        "wynik":wynik
    }

    return dane,""

st.title("Kalkulator zarobków")

tekst=st.text_area("Wklej formularz pracownika:",height=300)

if st.button("Oblicz"):
    dane,blad=oblicz(tekst)

    if blad!="":
        st.error(blad)
    else:
        st.success("Obliczono wynagrodzenie")

        st.write("Imię i nazwisko:",dane["imie"])
        st.write("Stopień:",dane["stopien"])
        st.write("Kursy:",dane["kursy"])
        st.write("Godziny:",dane["godziny"])
        st.write("Delegacje:",dane["delegacje"])
        st.write("Zatrudnienia:",dane["zatrudnienia"])
        st.write("Telefon:",dane["telefon"])

        st.header("Wynagrodzenie: "+formatuj(dane["wynik"])+" $")