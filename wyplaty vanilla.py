import streamlit as st
import re

stopnie={
    "Kierownik":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"norma_delegacji":5,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":1},
    "Próbny Kierownik":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"norma_delegacji":5,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":0.5},

    "Menager":{"podstawa":2200000,"norma_kursow":15,"norma_godzin":10,"norma_delegacji":5,"zatrudnienie":50000,"kursy":300000,"godzina":120000,"procent":1},
    "Próbny Menager":{"podstawa":1700000,"norma_kursow":20,"norma_godzin":12,"norma_delegacji":5,"zatrudnienie":50000,"kursy":300000,"godzina":100000,"procent":1},

    "Dyrektor":{"podstawa":2700000,"norma_kursow":10,"norma_godzin":10,"norma_delegacji":0,"zatrudnienie":50000,"kursy":300000,"godzina":140000,"procent":1},
    "Próbny Dyrektor":{"podstawa":2200000,"norma_kursow":15,"norma_godzin":10,"norma_delegacji":0,"zatrudnienie":50000,"kursy":300000,"godzina":120000,"procent":1},

    "Profesjonalny Rekruter":{"podstawa":1700000,"norma_kursow":10,"norma_godzin":10,"norma_delegacji":10,"zatrudnienie":50000,"kursy":0,"godzina":55000,"procent":1},
    "Opiekun Rekruterów":{"podstawa":1700000,"norma_kursow":10,"norma_godzin":10,"norma_delegacji":10,"zatrudnienie":50000,"kursy":0,"godzina":55000,"procent":1}
}

def popraw_tekst(tekst):
    tekst=tekst.replace("\xa0"," ")
    tekst=tekst.replace("`","")
    tekst=tekst.replace("*","")
    tekst=tekst.replace("@","")
    tekst=re.sub(r"[ \t]+"," ",tekst)
    tekst=re.sub(r"\n+","\n",tekst)
    return tekst.strip()

def normalizuj(tekst):
    tekst=popraw_tekst(tekst).lower()
    znaki={"ą":"a","ć":"c","ę":"e","ł":"l","ń":"n","ó":"o","ś":"s","ź":"z","ż":"z"}
    for a,b in znaki.items():
        tekst=tekst.replace(a,b)
    return tekst

def formatuj(liczba):
    return f"{int(liczba):,}".replace(","," ")

def liczba_z_tekstu(wzor,tekst):
    tekst=popraw_tekst(tekst)
    x=re.search(wzor,tekst,re.IGNORECASE)
    if x:
        liczba=re.sub(r"\D","",x.group(1))
        if liczba!="":
            return int(liczba)
    return 0

def tekst_z_tekstu(wzor,tekst):
    tekst=popraw_tekst(tekst)
    x=re.search(wzor,tekst,re.IGNORECASE)
    if x:
        return x.group(1).strip()
    return ""

def znajdz_stopien(tekst):
    s=tekst_z_tekstu(r"Stopień\s*:\s*(.+)",tekst)
    s=normalizuj(s)

    probny=("probny" in s or "probnym" in s)
    kierownik="kierownik" in s
    dyrektor="dyrektor" in s
    menager=("menager" in s or "manager" in s or "menedzer" in s)
    rekruter="rekruter" in s
    profesjonalny="profesjonalny" in s
    opiekun="opiekun" in s

    if opiekun and rekruter:
        return "Opiekun Rekruterów"
    if profesjonalny and rekruter:
        return "Profesjonalny Rekruter"

    if probny and dyrektor:
        return "Próbny Dyrektor"
    if probny and menager:
        return "Próbny Menager"
    if probny and kierownik:
        return "Próbny Kierownik"

    if dyrektor:
        return "Dyrektor"
    if menager:
        return "Menager"
    if kierownik:
        return "Kierownik"

    return ""

def sprawdz_norme(kursy,godziny,delegacje,d):
    norma_ok=True
    powody=[]

    if kursy<d["norma_kursow"]:
        norma_ok=False
        powody.append("kursy")

    if godziny<d["norma_godzin"]:
        norma_ok=False
        powody.append("godziny")

    if d["norma_delegacji"]>0 and delegacje<d["norma_delegacji"]:
        norma_ok=False
        powody.append("delegacje")

    return norma_ok,powody

def oblicz(tekst):
    imie=tekst_z_tekstu(r"Imię\s*i\s*nazwisko\s*:\s*(.+)",tekst)
    kursy=liczba_z_tekstu(r"Ilość\s*kursów\s*:\s*([^\n]+)",tekst)
    godziny=liczba_z_tekstu(r"Ilość\s*godzin\s*:\s*([^\n]+)",tekst)
    delegacje=liczba_z_tekstu(r"Ilość\s*delegacji\s*:\s*([^\n]+)",tekst)
    zatrudnienia=liczba_z_tekstu(r"Ilość\s*zatrudnień\s*:\s*([^\n]+)",tekst)

    if zatrudnienia==0:
        zatrudnienia=liczba_z_tekstu(r"Ilość\s*przyprowadzeń\s*:\s*([^\n]+)",tekst)

    telefon=tekst_z_tekstu(r"Nr\.?\s*telefonu\s*:\s*(.+)",tekst)
    suma_podana=liczba_z_tekstu(r"Suma\s*:\s*([^\n]+)",tekst)

    stopien=znajdz_stopien(tekst)

    if stopien=="":
        return None,"Nie znaleziono stopnia."

    d=stopnie[stopien]

    podstawa=d["podstawa"]
    kwota_zatrudnienia=zatrudnienia*d["zatrudnienie"]

    nadmiar_kursow=max(0,kursy-d["norma_kursow"])
    premie_kursowe=nadmiar_kursow//20
    kwota_kursy=premie_kursowe*d["kursy"]

    nadgodziny=max(0,godziny-d["norma_godzin"])
    kwota_godziny=nadgodziny*d["godzina"]

    wynik_przed=podstawa+kwota_zatrudnienia+kwota_kursy+kwota_godziny
    wynik=wynik_przed*d["procent"]

    rozpiska=f"{formatuj(podstawa)} + {formatuj(kwota_zatrudnienia)} + ({nadmiar_kursow}→{formatuj(kwota_kursy)}) + ({nadgodziny}→{formatuj(kwota_godziny)})"

    if d["procent"]==0.5:
        rozpiska+=" ÷2"

    rozpiska+=" = "+formatuj(wynik)

    norma_ok,powody=sprawdz_norme(kursy,godziny,delegacje,d)

    dane={
        "imie":imie,
        "stopien":stopien,
        "kursy":kursy,
        "godziny":godziny,
        "delegacje":delegacje,
        "zatrudnienia":zatrudnienia,
        "telefon":telefon,
        "suma_podana":suma_podana,
        "wynik":wynik,
        "norma_ok":norma_ok,
        "powody":powody,
        "rozpiska":rozpiska
    }

    return dane,""

def podziel_na_osoby(tekst):
    tekst=popraw_tekst(tekst)
    czesci=re.split(r"(?=Imię\s*i\s*nazwisko\s*:)",tekst,flags=re.IGNORECASE)

    osoby=[]

    for czesc in czesci:
        if re.search(r"Imię\s*i\s*nazwisko\s*:",czesc,re.IGNORECASE) and re.search(r"Suma\s*:",czesc,re.IGNORECASE):
            osoby.append(czesc)

    return osoby

def sprawdz_wiele(tekst):
    osoby=podziel_na_osoby(tekst)
    wyniki=[]

    for osoba in osoby:
        dane,blad=oblicz(osoba)

        if blad!="":
            imie=tekst_z_tekstu(r"Imię\s*i\s*nazwisko\s*:\s*(.+)",osoba)
            wyniki.append({
                "imie":imie,
                "status":"incorrect",
                "powod":"błąd danych",
                "podana":0,
                "poprawna":0,
                "rozpiska":"nie dało się policzyć"
            })
        else:
            status="correct"
            powody=[]

            if int(dane["wynik"])!=int(dane["suma_podana"]):
                status="incorrect"
                powody.append("zła suma")

            if not dane["norma_ok"]:
                status="incorrect"
                powody.append("brak normy: "+", ".join(dane["powody"]))

            wyniki.append({
                "imie":dane["imie"],
                "status":status,
                "powod":", ".join(powody),
                "podana":dane["suma_podana"],
                "poprawna":dane["wynik"],
                "rozpiska":dane["rozpiska"]
            })

    return wyniki

st.title("Kalkulator wypłat Vanilla")

tryb=st.radio("Wybierz tryb:",["Jedna osoba","Sprawdź wiele osób"])

tekst=st.text_area("Wklej dane:",height=350)

if tryb=="Jedna osoba":
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
            st.write("Zatrudnienia / przyprowadzenia:",dane["zatrudnienia"])
            st.write("Telefon:",dane["telefon"])

            st.code(dane["rozpiska"])

            if dane["norma_ok"]:
                st.success("Norma wyrobiona")
            else:
                st.error("Norma niewyrobiona: "+", ".join(dane["powody"]))

            st.header("Wynagrodzenie: "+formatuj(dane["wynik"])+" $")

            if dane["suma_podana"]>0:
                if int(dane["wynik"])==int(dane["suma_podana"]):
                    st.success("Podana suma jest poprawna")
                else:
                    st.error("Podana suma jest błędna. Wpisano: "+formatuj(dane["suma_podana"])+" $")

if tryb=="Sprawdź wiele osób":
    if st.button("Sprawdź"):
        wyniki=sprawdz_wiele(tekst)

        if len(wyniki)==0:
            st.error("Nie znaleziono żadnych poprawnych bloków z danymi.")
        else:
            for w in wyniki:
                if w["status"]=="correct":
                    st.success(w["imie"]+" — correct")
                else:
                    st.error(w["imie"]+" — incorrect")

                st.code(w["rozpiska"])

                if w["status"]=="incorrect":
                    if w["powod"]!="":
                        st.caption("Powód: "+w["powod"])
                    if w["podana"]>0:
                        st.caption("Wpisano: "+formatuj(w["podana"])+" $")
