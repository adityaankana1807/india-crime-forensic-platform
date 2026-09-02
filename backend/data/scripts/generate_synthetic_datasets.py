"""
Generates synthetic multilingual crime-report and digital-forensic-evidence
datasets focused on India, used to train/demo the platform's NLP and
clustering models.

Real NCRB crime statistics (see ncrb_*.csv in ../raw/) are aggregate counts,
not free-text narratives, so this augments them with labeled, multilingual
synthetic report text spanning six of India's most widely spoken languages:
English, Hindi, Bengali, Marathi, Tamil and Telugu. Crime categories follow
NCRB / Indian Penal Code (IPC) terminology.

Run: python generate_synthetic_datasets.py
"""
import csv
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

random.seed(42)

OUT_DIR = Path(__file__).resolve().parent.parent / "synthetic"
OUT_DIR.mkdir(parents=True, exist_ok=True)

LANGS = ["en", "hi", "bn", "mr", "ta", "te"]

# Faker locale support for India: en_IN, hi_IN, bn_BD, ta_IN are available;
# Marathi/Telugu have no Faker locale, so they fall back to en_IN for
# names/cities while templates/vocabulary below remain authentically mr/te.
FAKER_LOCALES = {"en": "en_IN", "hi": "hi_IN", "bn": "bn_BD", "ta": "ta_IN", "mr": "en_IN", "te": "en_IN"}
FAKERS = {code: Faker(locale) for code, locale in FAKER_LOCALES.items()}

# Curated name pools used for Marathi/Telugu since Faker has no locale data for them.
MARATHI_NAMES = ["Rohan Deshmukh", "Sneha Joshi", "Amit Kulkarni", "Priya Patil", "Sanjay More",
                  "Anita Bhosale", "Vikram Shinde", "Swati Gaikwad", "Nikhil Jadhav", "Pooja Kale"]
TELUGU_NAMES = ["Venkatesh Reddy", "Lakshmi Naidu", "Suresh Rao", "Anitha Prasad", "Ravi Kumar",
                 "Padma Chowdary", "Srinivas Sharma", "Divya Reddy", "Kiran Babu", "Sowmya Rani"]

INDIAN_CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Pune",
                  "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Nagpur", "Indore", "Bhopal",
                  "Patna", "Kanpur", "Coimbatore", "Kochi", "Guwahati", "Chandigarh"]

WEAPONS = {
    "en": ["a knife", "a country-made pistol", "an iron rod", "a sickle"],
    "hi": ["एक चाकू", "एक कट्टा", "एक लोहे की रॉड", "एक हंसिया"],
    "bn": ["একটি ছুরি", "একটি দেশি পিস্তল", "একটি লোহার রড", "একটি কাস্তে"],
    "mr": ["एक चाकू", "एक कट्टा", "एक लोखंडी रॉड", "एक विळा"],
    "ta": ["ஒரு கத்தி", "ஒரு நாட்டு துப்பாக்கி", "ஒரு இரும்பு கம்பி", "ஒரு அரிவாள்"],
    "te": ["ఒక కత్తి", "ఒక దేశీ తుపాకీ", "ఒక ఇనుప రాడ్", "ఒక కొడవలి"],
}

ITEMS = {
    "en": ["a mobile phone", "gold jewellery", "a two-wheeler", "cash", "a laptop"],
    "hi": ["एक मोबाइल फोन", "सोने के गहने", "एक दोपहिया वाहन", "नकदी", "एक लैपटॉप"],
    "bn": ["একটি মোবাইল ফোন", "সোনার গহনা", "একটি দুই চাকার গাড়ি", "নগদ টাকা", "একটি ল্যাপটপ"],
    "mr": ["एक मोबाईल फोन", "सोन्याचे दागिने", "एक दुचाकी", "रोख रक्कम", "एक लॅपटॉप"],
    "ta": ["ஒரு மொபைல் போன்", "தங்க நகைகள்", "ஒரு இருசக்கர வாகனம்", "பணம்", "ஒரு லேப்டாப்"],
    "te": ["ఒక మొబైల్ ఫోన్", "బంగారు నగలు", "ఒక ద్విచక్ర వాహనం", "నగదు", "ఒక ల్యాప్‌టాప్"],
}

# crime_type -> per-language sentence templates ({name} {loc} {weapon} {item}).
TEMPLATES = {
    "theft": {
        "en": "{name} reported that {item} was stolen near {loc} while unattended.",
        "hi": "{name} ने बताया कि {loc} के पास {item} लावारिस हालत में चोरी हो गया।",
        "bn": "{name} জানিয়েছেন যে {loc} এর কাছে অরক্ষিত অবস্থায় {item} চুরি হয়ে গেছে।",
        "mr": "{name} ने सांगितले की {loc} जवळ {item} विनाकारण चोरीला गेले.",
        "ta": "{loc} அருகே கண்காணிப்பு இல்லாத நேரத்தில் {item} திருடப்பட்டதாக {name} தெரிவித்தார்.",
        "te": "{loc} సమీపంలో ఎవరూ లేనప్పుడు {item} దొంగిలించబడిందని {name} తెలిపారు.",
    },
    "burglary": {
        "en": "Suspect forced entry into a house near {loc} and took {item}, reported by {name}.",
        "hi": "संदिग्ध ने {loc} के पास एक घर में जबरन प्रवेश किया और {item} ले गया, {name} ने रिपोर्ट दर्ज कराई।",
        "bn": "সন্দেহভাজন {loc} এর কাছে একটি বাড়িতে জোর করে ঢুকে {item} নিয়ে গেছে, {name} অভিযোগ করেছেন।",
        "mr": "संशयिताने {loc} जवळील घरात जबरदस्तीने प्रवेश करून {item} नेले, {name} यांनी तक्रार नोंदवली.",
        "ta": "சந்தேக நபர் {loc} அருகே ஒரு வீட்டில் நுழைந்து {item} எடுத்துச் சென்றார், {name} புகார் அளித்தார்.",
        "te": "అనుమానితుడు {loc} సమీపంలోని ఇంట్లోకి బలవంతంగా ప్రవేశించి {item} తీసుకెళ్లాడు, {name} ఫిర్యాదు చేశారు.",
    },
    "robbery": {
        "en": "{name} was confronted by an armed suspect with {weapon} near {loc} and had {item} taken.",
        "hi": "{name} का सामना {loc} के पास {weapon} लिए एक सशस्त्र संदिग्ध से हुआ और {item} छीन लिया गया।",
        "bn": "{name} {loc} এর কাছে {weapon} নিয়ে একজন সশস্ত্র সন্দেহভাজনের মুখোমুখি হন এবং তার {item} ছিনতাই হয়।",
        "mr": "{name} यांची {loc} जवळ {weapon} घेतलेल्या सशस्त्र संशयिताशी गाठ पडली आणि {item} हिसकावले गेले.",
        "ta": "{loc} அருகே {weapon} ஏந்திய ஆயுதம் தாங்கிய சந்தேக நபரை {name} சந்தித்தார், {item} பறிக்கப்பட்டது.",
        "te": "{loc} సమీపంలో {weapon} పట్టుకున్న అనుమానితుడిని {name} ఎదుర్కొన్నారు, {item} లాక్కున్నారు.",
    },
    "dacoity": {
        "en": "A gang of armed men robbed a shop near {loc}, reported by {name}, a witness at the scene.",
        "hi": "हथियारबंद लोगों के एक गिरोह ने {loc} के पास एक दुकान लूट ली, घटनास्थल पर मौजूद गवाह {name} ने बताया।",
        "bn": "সশস্ত্র ব্যক্তিদের একটি দল {loc} এর কাছে একটি দোকান লুট করেছে, ঘটনাস্থলের সাক্ষী {name} জানিয়েছেন।",
        "mr": "सशस्त्र लोकांच्या टोळीने {loc} जवळील एका दुकानाची लूट केली, साक्षीदार {name} यांनी सांगितले.",
        "ta": "ஆயுதம் தாங்கிய நபர்கள் குழு {loc} அருகே ஒரு கடையை கொள்ளையடித்தனர், சாட்சி {name} தெரிவித்தார்.",
        "te": "సాయుధులైన వ్యక్తుల ముఠా {loc} సమీపంలోని దుకాణాన్ని దోచుకుంది, సాక్షి {name} తెలిపారు.",
    },
    "murder": {
        "en": "{name} was found deceased near {loc} with injuries consistent with {weapon}; a murder case was registered.",
        "hi": "{name} {loc} के पास मृत पाया गया, चोटें {weapon} से मेल खाती थीं; हत्या का मामला दर्ज किया गया।",
        "bn": "{name} {loc} এর কাছে মৃত অবস্থায় পাওয়া যায়, আঘাত {weapon} এর সাথে সামঞ্জস্যপূর্ণ; হত্যা মামলা রুজু হয়েছে।",
        "mr": "{name} {loc} जवळ मृतावस्थेत आढळले, जखमा {weapon} शी सुसंगत होत्या; खुनाचा गुन्हा दाखल करण्यात आला.",
        "ta": "{name} {loc} அருகே இறந்த நிலையில் காணப்பட்டார், காயங்கள் {weapon} உடன் பொருந்துகின்றன; கொலை வழக்கு பதிவு செய்யப்பட்டது.",
        "te": "{name} {loc} సమీపంలో మృతదేహంగా కనిపించారు, గాయాలు {weapon}తో సరిపోలుతున్నాయి; హత్య కేసు నమోదైంది.",
    },
    "kidnapping": {
        "en": "{name} was reported missing near {loc}; family suspects kidnapping for ransom.",
        "hi": "{name} {loc} के पास लापता बताया गया; परिवार को फिरौती के लिए अपहरण की आशंका है।",
        "bn": "{name} {loc} এর কাছে নিখোঁজ বলে জানানো হয়েছে; পরিবার মুক্তিপণের জন্য অপহরণের সন্দেহ করছে।",
        "mr": "{name} {loc} जवळ बेपत्ता झाल्याची तक्रार करण्यात आली; कुटुंबाला खंडणीसाठी अपहरणाची शंका आहे.",
        "ta": "{name} {loc} அருகே காணாமல் போனதாக தெரிவிக்கப்பட்டது; மீட்கும் தொகைக்காக கடத்தப்பட்டதாக குடும்பத்தினர் சந்தேகிக்கின்றனர்.",
        "te": "{name} {loc} సమీపంలో కనిపించకుండా పోయారని ఫిర్యాదు; విమోచన కోసం అపహరణ జరిగిందని కుటుంబం అనుమానిస్తోంది.",
    },
    "cybercrime": {
        "en": "{name} reported unauthorised access to their online banking account, traced to an IP linked to {loc}.",
        "hi": "{name} ने अपने ऑनलाइन बैंकिंग खाते में अनधिकृत पहुँच की सूचना दी, जो {loc} से जुड़े एक आईपी से जुड़ी थी।",
        "bn": "{name} তার অনলাইন ব্যাংকিং অ্যাকাউন্টে অননুমোদিত প্রবেশের অভিযোগ করেছেন, যা {loc} এর সাথে যুক্ত একটি আইপি থেকে হয়েছে।",
        "mr": "{name} यांनी त्यांच्या ऑनलाइन बँकिंग खात्यात अनधिकृत प्रवेश झाल्याची तक्रार केली, जी {loc} शी संबंधित आयपीवरून झाली.",
        "ta": "{name} தனது ஆன்லைன் வங்கிக் கணக்கில் அங்கீகரிக்கப்படாத அணுகல் இருந்ததாக புகார் அளித்தார், அது {loc} உடன் தொடர்புடைய ஐபியிலிருந்து வந்தது.",
        "te": "{name} తన ఆన్‌లైన్ బ్యాంకింగ్ ఖాతాలో అనధికార ప్రవేశం జరిగిందని ఫిర్యాదు చేశారు, ఇది {loc}కు సంబంధించిన ఐపీ నుండి వచ్చింది.",
    },
    "cheating_fraud": {
        "en": "{name} was deceived into transferring funds by a scammer posing as a vendor near {loc}.",
        "hi": "{name} को {loc} के पास एक विक्रेता बनकर धोखेबाज ने धन हस्तांतरित करने के लिए धोखा दिया।",
        "bn": "{name} কে {loc} এর কাছে একজন বিক্রেতা সেজে থাকা প্রতারক অর্থ স্থানান্তর করতে প্রতারিত করেছে।",
        "mr": "{name} यांना {loc} जवळ विक्रेता असल्याचे भासवून फसवणूक करणाऱ्याने पैसे हस्तांतरित करण्यास फसवले.",
        "ta": "{loc} அருகே விற்பனையாளர் போல் நடித்த மோசடி செய்பவரால் {name} பணத்தை மாற்ற ஏமாற்றப்பட்டார்.",
        "te": "{loc} సమీపంలో విక్రేతగా నటించిన మోసగాడు {name}ను నగదు బదిలీ చేయమని మోసం చేశాడు.",
    },
    "drug_trafficking": {
        "en": "Officers seized a consignment of narcotics near {loc} under the NDPS Act; investigation involves {name}.",
        "hi": "अधिकारियों ने एनडीपीएस अधिनियम के तहत {loc} के पास मादक पदार्थों की एक खेप जब्त की; जांच में {name} शामिल है।",
        "bn": "এনডিপিএস আইনের অধীনে কর্মকর্তারা {loc} এর কাছে মাদকদ্রব্যের একটি চালান জব্দ করেছেন; তদন্তে {name} জড়িত।",
        "mr": "अधिकाऱ्यांनी एनडीपीएस कायद्यांतर्गत {loc} जवळ अमली पदार्थांचा साठा जप्त केला; तपासात {name} यांचा समावेश आहे.",
        "ta": "என்டிபிஎஸ் சட்டத்தின் கீழ் {loc} அருகே போதைப்பொருள் கொள்முதலை அதிகாரிகள் பறிமுதல் செய்தனர்; விசாரணையில் {name} ஈடுபட்டுள்ளார்.",
        "te": "ఎన్‌డిపిఎస్ చట్టం కింద అధికారులు {loc} సమీపంలో మాదక ద్రవ్యాల సరుకును స్వాధీనం చేసుకున్నారు; దర్యాప్తులో {name} ప్రమేయం ఉంది.",
    },
    "crime_against_women": {
        "en": "{name} filed a complaint of harassment and stalking near {loc}, an investigation has been opened.",
        "hi": "{name} ने {loc} के पास उत्पीड़न और पीछा किए जाने की शिकायत दर्ज कराई, जांच शुरू कर दी गई है।",
        "bn": "{name} {loc} এর কাছে হয়রানি ও অনুসরণ করার অভিযোগ দায়ের করেছেন, তদন্ত শুরু হয়েছে।",
        "mr": "{name} यांनी {loc} जवळ छळ आणि पाठलाग केल्याची तक्रार नोंदवली, तपास सुरू करण्यात आला आहे.",
        "ta": "{loc} அருகே தொந்தரவு மற்றும் பின்தொடர்தல் குறித்து {name} புகார் அளித்தார், விசாரணை தொடங்கப்பட்டுள்ளது.",
        "te": "{loc} సమీపంలో వేధింపులు మరియు వెంబడించడంపై {name} ఫిర్యాదు చేశారు, దర్యాప్తు ప్రారంభమైంది.",
    },
    "extortion": {
        "en": "{name} reported receiving repeated threats demanding money near {loc}.",
        "hi": "{name} ने {loc} के पास बार-बार पैसे की मांग करने वाली धमकियां मिलने की सूचना दी।",
        "bn": "{name} {loc} এর কাছে বারবার অর্থ দাবি করে হুমকি পাওয়ার কথা জানিয়েছেন।",
        "mr": "{name} यांनी {loc} जवळ वारंवार पैशांची मागणी करणाऱ्या धमक्या मिळाल्याची तक्रार केली.",
        "ta": "{loc} அருகே பணம் கோரி மீண்டும் மீண்டும் மிரட்டல் வந்ததாக {name} தெரிவித்தார்.",
        "te": "{loc} సమీపంలో డబ్బు కోరుతూ పదేపదే బెదిరింపులు వచ్చాయని {name} తెలిపారు.",
    },
    "rioting": {
        "en": "A violent clash broke out near {loc} between two groups, {name} among those who filed a complaint.",
        "hi": "{loc} के पास दो गुटों के बीच हिंसक झड़प हुई, शिकायत दर्ज कराने वालों में {name} भी शामिल थे।",
        "bn": "{loc} এর কাছে দুটি দলের মধ্যে সহিংস সংঘর্ষ হয়েছে, অভিযোগকারীদের মধ্যে {name} ছিলেন।",
        "mr": "{loc} जवळ दोन गटांमध्ये हिंसक चकमक झाली, तक्रार करणाऱ्यांमध्ये {name} यांचा समावेश होता.",
        "ta": "{loc} அருகே இரு குழுக்களுக்கிடையே வன்முறை மோதல் வெடித்தது, புகார் அளித்தவர்களில் {name} ஒருவர்.",
        "te": "{loc} సమీపంలో రెండు గುంపుల మధ్య హింసాత్మక ఘర్షణ జరిగింది, ఫిర్యాదు చేసిన వారిలో {name} ఒకరు.",
    },
}

THREAT_BY_TYPE = {
    "theft": "low",
    "cheating_fraud": "medium",
    "cybercrime": "medium",
    "extortion": "medium",
    "rioting": "medium",
    "burglary": "medium",
    "crime_against_women": "high",
    "kidnapping": "high",
    "robbery": "high",
    "dacoity": "high",
    "drug_trafficking": "high",
    "murder": "critical",
}

CRIME_TYPES = list(TEMPLATES.keys())

THREAT_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}

# Behavioural / modus-operandi clusters used to link repeat-offender incident
# sequences: a suspect's incidents are drawn from one cluster so crime-type
# choice stays consistent (MO), while severity is allowed to drift upward
# over time (escalation) — the basis for the platform's behaviour-analysis module.
MO_CLUSTERS = {
    "property": ["theft", "burglary", "robbery", "dacoity"],
    "violent": ["robbery", "dacoity", "kidnapping", "murder"],
    "financial": ["cybercrime", "cheating_fraud", "extortion"],
    "narcotics": ["drug_trafficking"],
    "public_order": ["rioting"],
    "women_safety": ["crime_against_women"],
}


def random_name(lang: str, fkr: Faker) -> str:
    if lang == "mr":
        return random.choice(MARATHI_NAMES)
    if lang == "te":
        return random.choice(TELUGU_NAMES)
    return fkr.name()


def _closest_crime_type(cluster_types, target_ord):
    return min(cluster_types, key=lambda ct: abs(THREAT_ORDER[THREAT_BY_TYPE[ct]] - target_ord))


def _make_report_row(row_id, lang, crime_type, name, loc, date, suspect_id, mo_cluster, incident_index):
    fkr = FAKERS[lang]
    weapon = random.choice(WEAPONS[lang])
    item = random.choice(ITEMS[lang])
    text = TEMPLATES[crime_type][lang].format(name=name, loc=loc, weapon=weapon, item=item)
    return {
        "id": row_id,
        "language": lang,
        "text": text,
        "crime_type": crime_type,
        "threat_level": THREAT_BY_TYPE[crime_type],
        "location": loc,
        "date": date.isoformat(),
        "suspect_id": suspect_id,
        "mo_cluster": mo_cluster,
        "incident_index": incident_index,
    }


def gen_repeat_offender_sequences(num_suspects, start_id):
    """Generates linked multi-incident sequences per suspect with a consistent
    MO (crime-type cluster) and a mild escalation trend in severity over time —
    used by the behaviour-analysis module to detect MO consistency and
    escalating risk trajectories."""
    rows = []
    start = datetime(2024, 1, 1)
    row_id = start_id
    for s in range(num_suspects):
        suspect_id = f"SUSP-{s+1:04d}"
        lang = random.choice(LANGS)
        fkr = FAKERS[lang]
        name = random_name(lang, fkr)
        mo_cluster = random.choice(list(MO_CLUSTERS))
        cluster_types = MO_CLUSTERS[mo_cluster]
        home_city = random.choice(INDIAN_CITIES)
        other_cities = random.sample([c for c in INDIAN_CITIES if c != home_city], k=2)

        num_incidents = random.randint(3, 6)
        base_date = start + timedelta(days=random.randint(0, 500))
        severity = random.choice([0, 1])  # start low/medium, escalate over time
        cur_date = base_date

        for j in range(num_incidents):
            severity = min(3, severity + random.choice([0, 0, 1]))
            crime_type = _closest_crime_type(cluster_types, severity)
            loc = home_city if random.random() < 0.7 else random.choice(other_cities)
            rows.append(_make_report_row(
                f"SYN-{row_id:05d}", lang, crime_type, name, loc, cur_date,
                suspect_id, mo_cluster, j + 1,
            ))
            row_id += 1
            cur_date += timedelta(days=random.randint(7, 60))
    return rows, row_id


def gen_standalone_reports(n, start_id):
    rows = []
    start = datetime(2024, 1, 1)
    row_id = start_id
    for _ in range(n):
        lang = random.choice(LANGS)
        crime_type = random.choice(CRIME_TYPES)
        fkr = FAKERS[lang]
        name = random_name(lang, fkr)
        loc = random.choice(INDIAN_CITIES)
        date = start + timedelta(days=random.randint(0, 640), hours=random.randint(0, 23))
        rows.append(_make_report_row(
            f"SYN-{row_id:05d}", lang, crime_type, name, loc, date, "", "", 0,
        ))
        row_id += 1
    return rows


def gen_crime_reports(n=1200, repeat_offender_share=0.28):
    linked_rows, next_id = gen_repeat_offender_sequences(num_suspects=70, start_id=1)
    standalone_n = max(0, n - len(linked_rows))
    standalone_rows = gen_standalone_reports(standalone_n, next_id)
    rows = linked_rows + standalone_rows
    random.shuffle(rows)
    return rows


# Template index -> emotional_tone label, shared across languages (see TONE_LABELS).
TONE_LABELS = ["deceptive", "threatening", "neutral", "distressed"]

FORENSIC_SNIPPET_TEMPLATES = {
    "en": [
        "User contacted {name} at {email} regarding the shipment, transfer {item} to the account before {date}.",
        "Chat log: 'meet me near {loc} at 11pm, bring {weapon}, don't tell anyone.'",
        "Email header shows origin IP {ip}, forwarded to {email} on {date}.",
        "Message from {name}: 'I think I'm being followed near {loc}, I'm really scared, please help me.'",
    ],
    "hi": [
        "उपयोगकर्ता ने {email} पर {name} से शिपमेंट के बारे में संपर्क किया, {date} से पहले खाते में {item} भेजें।",
        "चैट लॉग: '{loc} के पास रात 11 बजे मिलो, {weapon} लाना, किसी को मत बताना।'",
        "ईमेल हेडर मूल आईपी {ip} दिखाता है, {date} को {email} पर अग्रेषित किया गया।",
        "{name} का संदेश: 'मुझे लगता है {loc} के पास कोई मेरा पीछा कर रहा है, मैं बहुत डरी हुई हूँ, कृपया मदद करें।'",
    ],
    "bn": [
        "ব্যবহারকারী চালানের বিষয়ে {email} এ {name} এর সাথে যোগাযোগ করেছেন, {date} এর আগে অ্যাকাউন্টে {item} পাঠান।",
        "চ্যাট লগ: '{loc} এর কাছে রাত ১১টায় দেখা করো, {weapon} নিয়ে এসো, কাউকে বলো না।'",
        "ইমেইল হেডারে মূল আইপি {ip} দেখা যাচ্ছে, {date} তারিখে {email} এ ফরওয়ার্ড করা হয়েছে।",
        "{name} এর বার্তা: 'আমার মনে হচ্ছে {loc} এর কাছে কেউ আমাকে অনুসরণ করছে, আমি খুব ভয় পাচ্ছি, দয়া করে সাহায্য করুন।'",
    ],
    "mr": [
        "वापरकर्त्याने शिपमेंटबाबत {email} वर {name} शी संपर्क साधला, {date} पूर्वी खात्यात {item} पाठवा.",
        "चॅट लॉग: '{loc} जवळ रात्री ११ वाजता भेट, {weapon} आण, कोणालाही सांगू नकोस.'",
        "ईमेल हेडरमध्ये मूळ आयपी {ip} दिसतो, {date} रोजी {email} वर फॉरवर्ड केले.",
        "{name} चा संदेश: 'मला वाटतंय {loc} जवळ कोणीतरी माझा पाठलाग करत आहे, मी खूप घाबरले आहे, कृपया मदत करा.'",
    ],
    "ta": [
        "பயனர் {name} உடன் {email} இல் அனுப்புகை குறித்து தொடர்பு கொண்டார், {date} க்கு முன் கணக்கிற்கு {item} அனுப்பவும்.",
        "அரட்டை பதிவு: '{loc} அருகே இரவு 11 மணிக்கு சந்திப்போம், {weapon} கொண்டு வா, யாரிடமும் சொல்லாதே.'",
        "மின்னஞ்சல் தலைப்பு மூல ஐபி {ip} ஐ காட்டுகிறது, {date} அன்று {email} க்கு அனுப்பப்பட்டது.",
        "{name} இன் செய்தி: '{loc} அருகே யாரோ என்னை பின்தொடர்வதாக நினைக்கிறேன், மிகவும் பயமாக இருக்கிறது, தயவுசெய்து உதவுங்கள்.'",
    ],
    "te": [
        "వినియోగదారు షిప్‌మెంట్ గురించి {email} వద్ద {name}ని సంప్రదించారు, {date} లోపు ఖాతాకు {item} పంపండి.",
        "చాట్ లాగ్: '{loc} దగ్గర రాత్రి 11 గంటలకు కలుద్దాం, {weapon} తీసుకురా, ఎవరికీ చెప్పకు.'",
        "ఇమెయిల్ హెడర్ మూల ఐపీ {ip} చూపిస్తుంది, {date} న {email}కు ఫార్వార్డ్ చేయబడింది.",
        "{name} నుండి సందేశం: '{loc} దగ్గర ఎవరో నన్ను వెంబడిస్తున్నారని అనిపిస్తోంది, చాలా భయంగా ఉంది, దయచేసి సహాయం చేయండి.'",
    ],
}


def gen_forensic_evidence(n=500):
    rows = []
    start = datetime(2024, 1, 1)
    for i in range(n):
        lang = random.choice(LANGS)
        fkr = FAKERS[lang]
        name = random_name(lang, fkr)
        email = fkr.email()
        loc = random.choice(INDIAN_CITIES)
        weapon = random.choice(WEAPONS[lang])
        item = random.choice(ITEMS[lang])
        ip = fkr.ipv4()
        date = (start + timedelta(days=random.randint(0, 640))).strftime("%Y-%m-%d")
        template_idx = random.randrange(len(TONE_LABELS))
        template = FORENSIC_SNIPPET_TEMPLATES[lang][template_idx]
        tone = TONE_LABELS[template_idx]
        text = template.format(name=name, email=email, loc=loc, weapon=weapon, item=item, ip=ip, date=date)
        evidence_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rows.append({
            "evidence_id": f"EVID-{i+1:05d}",
            "language": lang,
            "text": text,
            "source": random.choice(["chat_log", "email", "sms", "call_transcript"]),
            "emotional_tone": tone,
            "collected_date": date,
            "sha256": evidence_hash,
        })
    return rows


def gen_crime_hotspots(n=2000):
    # Synthetic geospatial clusters around major Indian metropolitan centers.
    centers = [
        (19.0760, 72.8777, "Mumbai"),
        (28.7041, 77.1025, "Delhi"),
        (12.9716, 77.5946, "Bengaluru"),
        (13.0827, 80.2707, "Chennai"),
        (22.5726, 88.3639, "Kolkata"),
        (17.3850, 78.4867, "Hyderabad"),
        (18.5204, 73.8567, "Pune"),
        (26.9124, 75.7873, "Jaipur"),
    ]
    rows = []
    start = datetime(2024, 1, 1)
    for i in range(n):
        lat_c, lon_c, city = random.choice(centers)
        lat = lat_c + random.gauss(0, 0.05)
        lon = lon_c + random.gauss(0, 0.05)
        crime_type = random.choice(CRIME_TYPES)
        date = start + timedelta(days=random.randint(0, 640))
        rows.append({
            "id": f"HOT-{i+1:05d}",
            "city": city,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "crime_type": crime_type,
            "threat_level": THREAT_BY_TYPE[crime_type],
            "date": date.date().isoformat(),
        })
    return rows


def write_csv(rows, filename):
    path = OUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {path}")


if __name__ == "__main__":
    write_csv(gen_crime_reports(1200), "crime_reports_multilingual.csv")
    write_csv(gen_forensic_evidence(500), "forensic_evidence_logs.csv")
    write_csv(gen_crime_hotspots(2000), "crime_hotspots.csv")
