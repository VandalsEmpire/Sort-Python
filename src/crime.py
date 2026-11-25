"""Modelo dos registros de crime e leitura do CSV de entrada."""

import csv


class Crime:
    """Registro reduzido do dataset, ordenável pelo número DR_NO."""

    def __init__(
        self,
        dr_no: int,
        date_occ: str,
        area_name: str,
        crm_cd_desc: str,
        vict_age: int,
        location: str,
    ):
        self.dr_no = dr_no
        self.date_occ = date_occ
        self.area_name = area_name
        self.crm_cd_desc = crm_cd_desc
        self.vict_age = vict_age
        self.location = location

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


def _inteiro_ou_zero(valor):
    valor = valor.strip()
    return int(valor) if valor.isdigit() else 0


def carregar_crimes(caminho_csv: str) -> list:
    """Carrega os campos necessários para a ordenação a partir do CSV."""
    crimes = []
    with open(caminho_csv, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            dr_no_val = linha.get("DR_NO", "").strip()
            if not dr_no_val or not dr_no_val.isdigit():
                raise ValueError(
                    f"Registro {leitor.line_num}: DR_NO ausente ou inválido."
                )

            crimes.append(
                Crime(
                    dr_no=int(dr_no_val),
                    date_occ=linha.get("DATE OCC", ""),
                    area_name=linha.get("AREA NAME", ""),
                    crm_cd_desc=linha.get("Crm Cd Desc", ""),
                    vict_age=_inteiro_ou_zero(linha.get("Vict Age", "")),
                    location=linha.get("LOCATION", ""),
                )
            )
    return crimes
