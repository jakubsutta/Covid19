#KNIHOVNY
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True

#TŘÍDA KRAJ
class Kraj:
    muzi = 0
    zeny = 0
    vek_muzi = 0
    vek_zeny = 0
    def __init__(self, name, code, type, coordinates):
        self.name = name
        self.code = code
        self.type = type
        self.coordinates = coordinates

#PŘIDÁVÁNÍ
    def pridat_nakazeneho(self, pohlavi, vek):
        if pohlavi == "M":
            self.muzi += 1
            self.vek_muzi += vek

        elif pohlavi == "Z":
            self.zeny += 1
            self.vek_zeny += vek

#JSON
    def get_json(self):
        pocet_nakazenych = self.muzi + self.zeny
        prumer_vek = (self.vek_zeny + self.vek_muzi)/pocet_nakazenych
        prumer_vek_zeny = self.vek_zeny / self.zeny
        prumer_vek_muzi = self.vek_muzi / self.muzi
        podil_muzu = self.muzi / pocet_nakazenych * 100
        vysl = {"celkem_nakazenych": pocet_nakazenych,
                    "prumerny_vek": round(prumer_vek,2),
                    "prumerny_vek_zeny": round(prumer_vek_zeny, 2),
                    "prumerny_vek_muzi": round(prumer_vek_muzi,2),
                    "muzi": round(podil_muzu, 2),
                    "zeny": round(100-podil_muzu, 2),
                    "code": self.code, "name": self.name}
        return vysl 
        
    def get_coordinates(self):
        vysledek = {"type": self.type, "coordinates": self.coordinates}
        return vysledek
    kraje=list()

#KRAJE ČR - JSON
#polygony - r = requests.get("http://arccr-arcdata.opendata.arcgis.com/datasets/6475ee085a0d498fb9075fd6320d16f2_8.geojson")
r = request.get("http://arccr-arcdata.opendata.arcgis.com/datasets/38f135cb51b347e09f2a65cdc8a06247_19.geojson")
r = r.json()
j = 0

#NAČTENÍ KRAJŮ
for i in range(len(r["features"])):
    kraje.append(Kraj(r["features"][i]["properties"]['NAZ_CZNUTS3'],r["features"][i]["properties"]['KOD_CZNUTS3'],
                      r["features"][i]["geometry"]["type"],r["features"][i]["geometry"]["coordinates"]))

#NAČTENÍ NEMOCNÝCH - COVID19 DATA
r = requests.get("https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.json")
r = r.json()
for clovek in r["data"]:
    k=0
    for kod in kraje:
        if kraje[k].code == clovek["KHS"]:
            x = k
            break
        else:
            k = k + 1

    kraje[x].pridat_nakazeneho(clovek["Pohlavi"], int(clovek["Vek"]))

#API1, FLASK
@app.route("/covid_kraje", methods=["GET"])
def covid_kraje():
    kraj = request.args.get("kraj", "0")
    k = 0
    for kod in kraje:
        if kraje[k].code == kraj:
            x = k
            nenalezeno = False
            break
        else:
            k = k + 1
            nenalezeno = True

    if nenalezeno:
        return "Chyba"
    else:
        result = kraje[x].get_json()
        result = jsonify(result)
        return result

#API2, FLASK
@app.route("/covid_kraje_json", methods=["GET"])
def covid_kraje_json():
    features = []
    i = 0
    for x in kraje:
        features.append({"type" : "Feature", "properties": kraje[i].get_json(), "geometry": kraje[i].get_coordinates()})
        i = i + 1
    results = {"type": "FeaturesCollection","features": features}
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)