"""
Builds a curated reference dataset of India's principal crime-investigation,
intelligence, financial-crime, narcotics, forensic-science and paramilitary
security agencies. Facts (establishment year, parent ministry, headquarters,
mandate) are drawn from each agency's public mandate; this is reference data,
not survey/statistical data, so it is compiled here rather than scraped.

Run: python build_agency_reference.py
"""
import csv
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "raw" / "indian_law_enforcement_agencies.csv"

AGENCIES = [
    ("Central Bureau of Investigation", "CBI", "Central Investigation", "Department of Personnel & Training (Cabinet Secretariat)", "New Delhi", 1963, "Corruption, economic offences, serious/organised crime; also India's INTERPOL National Central Bureau"),
    ("National Investigation Agency", "NIA", "Central Investigation", "Ministry of Home Affairs", "New Delhi", 2009, "Terrorism and offences affecting national security, created after the 2008 Mumbai attacks"),
    ("National Crime Records Bureau", "NCRB", "Crime Statistics & Records", "Ministry of Home Affairs", "New Delhi", 1986, "National crime statistics (Crime in India report), fingerprints, CCTNS crime database"),
    ("Narcotics Control Bureau", "NCB", "Narcotics", "Ministry of Home Affairs", "New Delhi", 1986, "Enforcement of the Narcotic Drugs and Psychotropic Substances (NDPS) Act"),
    ("Central Bureau of Narcotics", "CBN", "Narcotics", "Department of Revenue, Ministry of Finance", "Gwalior", 1950, "Licensing and control of licit narcotic drug cultivation and manufacture"),
    ("Enforcement Directorate", "ED", "Financial & Economic Crime", "Department of Revenue, Ministry of Finance", "New Delhi", 1956, "Enforcement of FEMA and the Prevention of Money Laundering Act (PMLA)"),
    ("Directorate of Revenue Intelligence", "DRI", "Financial & Economic Crime", "Central Board of Indirect Taxes & Customs, Ministry of Finance", "New Delhi", 1957, "Anti-smuggling and customs duty evasion intelligence"),
    ("Serious Fraud Investigation Office", "SFIO", "Financial & Economic Crime", "Ministry of Corporate Affairs", "New Delhi", 2003, "Investigation of corporate and white-collar fraud"),
    ("Central Economic Intelligence Bureau", "CEIB", "Financial & Economic Crime", "Department of Revenue, Ministry of Finance", "New Delhi", 1985, "Coordinates economic intelligence across enforcement agencies"),
    ("Financial Intelligence Unit - India", "FIU-IND", "Financial & Economic Crime", "Department of Revenue, Ministry of Finance", "New Delhi", 2004, "Receives, analyses and disseminates suspicious financial transaction reports"),
    ("Intelligence Bureau", "IB", "Intelligence", "Ministry of Home Affairs", "New Delhi", 1887, "Domestic intelligence gathering and counter-intelligence"),
    ("Research and Analysis Wing", "R&AW", "Intelligence", "Cabinet Secretariat", "New Delhi", 1968, "External intelligence gathering"),
    ("Indian Cyber Crime Coordination Centre", "I4C", "Cybercrime", "Ministry of Home Affairs", "New Delhi", 2020, "National coordination for cybercrime, operates the National Cyber Crime Reporting Portal"),
    ("Directorate of Forensic Science Services", "DFSS", "Forensic Science", "Ministry of Home Affairs", "New Delhi", 1988, "Apex body overseeing Central Forensic Science Laboratories nationwide"),
    ("Central Forensic Science Laboratory", "CFSL", "Forensic Science", "Directorate of Forensic Science Services, MHA", "New Delhi (+5 regional labs)", 1957, "Forensic examination of physical, biological, chemical and digital evidence"),
    ("National Forensic Sciences University", "NFSU", "Forensic Science", "Ministry of Home Affairs", "Gandhinagar", 2020, "Specialised forensic science education, training and research"),
    ("Bureau of Police Research and Development", "BPR&D", "Training & Coordination", "Ministry of Home Affairs", "New Delhi", 1970, "Police modernisation, research and training standards"),
    ("Sardar Vallabhbhai Patel National Police Academy", "SVPNPA", "Training & Coordination", "Ministry of Home Affairs", "Hyderabad", 1948, "Training of Indian Police Service (IPS) officers"),
    ("Central Reserve Police Force", "CRPF", "Paramilitary / Internal Security", "Ministry of Home Affairs", "New Delhi", 1939, "Internal security, counter-insurgency and law-and-order support to states"),
    ("Border Security Force", "BSF", "Paramilitary / Border Security", "Ministry of Home Affairs", "New Delhi", 1965, "Guards India's border with Pakistan and Bangladesh"),
    ("Central Industrial Security Force", "CISF", "Paramilitary / Critical Infrastructure", "Ministry of Home Affairs", "New Delhi", 1969, "Security of airports, metros and critical infrastructure installations"),
    ("Railway Protection Force", "RPF", "Specialised Police", "Ministry of Railways", "New Delhi", 1957, "Protection of railway property and passengers"),
    ("Government Railway Police", "GRP", "Specialised Police", "State Home Departments", "State-level", 1861, "Law-and-order and crime investigation on railway premises"),
    ("Delhi Police", "DP", "State/UT Police", "Ministry of Home Affairs (Union Territory)", "New Delhi", 1861, "General law enforcement for the National Capital Territory of Delhi"),
    ("Maharashtra Anti-Terrorism Squad", "Maharashtra ATS", "State Police - Specialised", "Maharashtra Home Department", "Mumbai", 1990, "Counter-terrorism investigation within Maharashtra"),
    ("Central Bureau of Investigation - Interpol Wing", "CBI-NCB Interpol", "International Liaison", "Department of Personnel & Training", "New Delhi", 1949, "India's INTERPOL National Central Bureau for cross-border case coordination"),
]


def main():
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "agency_name", "abbreviation", "category", "parent_ministry_or_department",
            "headquarters", "established_year", "primary_mandate",
        ])
        writer.writerows(AGENCIES)
    print(f"wrote {len(AGENCIES)} agencies -> {OUT_PATH}")


if __name__ == "__main__":
    main()
