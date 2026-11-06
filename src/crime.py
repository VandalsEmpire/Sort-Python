import csv

class Crime:
    def __init__(self, dr_no: int, date_occ: str, area_name: str, crm_cd_desc: str, vict_age: int, location: str):
        self.dr_no = dr_no
        self.date_occ = date_occ
        self.area_name = area_name
        self.crm_cd_desc = crm_cd_desc
        self.vict_age = vict_age
        self.location = location

    dr_no: int # Número do Registro Policial (Chave de ordenação) 
    date_occ: str # Data da ocorrência do crime 
    area_name: str # Nome da região/distrito policial 
    crm_cd_desc: str # Descrição da infração/crime
    vict_age: int # Idade da vítima 
    location: str # Endereço/Bloco aproximado da ocorrência

    def __lt__(self, other): 
        return self.dr_no < other.dr_no
    def __le__(self, other): 
        return self.dr_no <= other.dr_no
    def __gt__(self, other): 
        return self.dr_no > other.dr_no
    def __ge__(self, other): 
        return self.dr_no >= other.dr_no
    def __eq__(self, other): 
        if not isinstance(other, Crime): 
            return False 
        return self.dr_no == other.dr_no
    def __repr__(self): 
        return f"Crime(DR_NO={self.dr_no})"

def carregar_crimes(caminho_csv: str) -> list:
    crimes =[]
    with open(caminho_csv, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            dr_no_val = linha.get("DR_NO", "") 
            dr_no = int(dr_no_val) if dr_no_val and dr_no_val.isdigit() else 0 
                
            vict_age_val = linha.get("Vict Age", "") 
            vict_age = int(vict_age_val) if vict_age_val and vict_age_val.isdigit() else 0
            
            crime = Crime( 
                dr_no=dr_no, 
                date_occ=linha.get("DATE OCC", ""), 
                area_name=linha.get("AREA NAME", ""), 
                crm_cd_desc=linha.get("Crm Cd Desc", ""), 
                vict_age=vict_age, 
                location=linha.get("LOCATION", ""), 
                ) 
            crimes.append(crime) 
        return crimes