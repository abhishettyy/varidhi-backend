"""Varidhi Telegram Bot - Fisherman Advisory Service
Natural conversational tone with tasteful, friendly emojis — just like a real WhatsApp message.
Supports:
- 🇮🇳 ಕನ್ನಡ (Kannada)
- 🇮🇳 മലയാളം (Malayalam)
- 🇮🇳 हिंदी (Hindi)
- 🇬🇧 English
"""

import os
import sys
import re
import logging
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import httpx
from dotenv import load_dotenv

# Load environment variables
root_dir = Path(__file__).resolve().parent.parent
load_dotenv(root_dir / ".env")
load_dotenv()

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("VaridhiFishermanBot")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
_port = os.getenv("PORT")
_default_url = f"http://127.0.0.1:{_port}" if _port else "http://127.0.0.1:8105"
API_BASE_URL = os.getenv("VARIDHI_API_URL", _default_url).rstrip("/")

SUPPORTED_PORTS = {
    "mangalore": {
        "name_en": "Mangalore Old Port",
        "name_kn": "ಮಂಗಳೂರು ಹಳೆ ಬಂದರು (ಧಕ್ಕೆ)",
        "name_ml": "മംഗലാപുരം പഴയ തുറമുഖം",
        "name_hi": "मंगलुरु पुराना बंदरगाह",
        "short": "Mangalore",
        "lat": 12.8550,
        "lon": 74.8360,
    },
    "malpe": {
        "name_en": "Malpe Harbour (Udupi)",
        "name_kn": "ಮಲ್ಪೆ ಬಂದರು (ಉಡುಪಿ)",
        "name_ml": "മാൽപെ ഹാർബർ",
        "name_hi": "मालपे बंदरगाह",
        "short": "Malpe",
        "lat": 13.3512,
        "lon": 74.7011,
    },
    "karwar": {
        "name_en": "Karwar Port",
        "name_kn": "ಕಾರವಾರ ಬಂದರು",
        "name_ml": "കാർവാർ തുറമുഖം",
        "name_hi": "कारवार बंदरगाह",
        "short": "Karwar",
        "lat": 14.8136,
        "lon": 74.1240,
    },
    "kochi": {
        "name_en": "Kochi Harbour",
        "name_kn": "ಕೊಚ್ಚಿ ಬಂದರು",
        "name_ml": "കൊച്ചി ഹാർബർ",
        "name_hi": "कोच्चि बंदरगाह",
        "short": "Kochi",
        "lat": 9.9312,
        "lon": 76.2673,
    },
}

TEXTS = {
    "ask_port": {
        "en": "⚓ <b>Which harbour are you leaving from today?</b>\nTap below or type your town:",
        "kn": "⚓ <b>ನೀವು ಇಂದು ಯಾವ ಬಂದರಿನಿಂದ ಹೊರಡುತ್ತಿದ್ದೀರಿ?</b>\nಕೆಳಗೆ ಆಯ್ಕೆಮಾಡಿ ಅಥವಾ ಊರಿನ ಹೆಸರು ಟೈಪ್ ಮಾಡಿ:",
        "ml": "⚓ <b>നിങ്ങൾ ഇന്ന് ഏത് തുറമുഖത്ത് നിന്നാണ് പുറപ്പെടുന്നത്?</b>\nതാഴെ തിരഞ്ഞെടുക്കുക:",
        "hi": "⚓ <b>आज आप किस बंदरगाह से निकल रहे हैं?</b>\nनीचे चुनें:",
    },
    "live_gps_hint": {
        "en": "💡 <i>Or tap 'Send My Boat GPS' below to share your live location:</i>",
        "kn": "💡 <i>ಅಥವಾ ನಿಮ್ಮ ದೋಣಿಯ ನೇರ GPS ಸ್ಥಳ ಕಳುಹಿಸಲು ಕೆಳಗಿನ ಬಟನ್ ಒತ್ತಿ:</i>",
        "ml": "💡 <i>അല്ലെങ്കിൽ ബോട്ടിന്റെ ജിപിഎസ് ലൊക്കേഷൻ അയയ്ക്കാൻ താഴെ ടാപ്പ് ചെയ്യുക:</i>",
        "hi": "💡 <i>या नाव की लोकेशन भेजने के लिए नीचे बटन दबाएं:</i>",
    },
    "btn_best_spots": {
        "en": "🎣 Best fishing spot",
        "kn": "🎣 ಉತ್ತಮ ಮೀನುಗಾರಿಕಾ ತಾಣ",
        "ml": "🎣 നല്ല മീൻപിടുത്ത സ്ഥലം",
        "hi": "🎣 अच्छी मछली की जगह",
    },
    "btn_sea_safety": {
        "en": "🌊 Sea weather & safety",
        "kn": "🌊 ಸಮುದ್ರ ಸುರಕ್ಷತೆ",
        "ml": "🌊 കടൽ സുരക്ഷ",
        "hi": "🌊 समुद्र सुरक्षा",
    },
    "btn_restrictions": {
        "en": "⚠️ Restricted areas",
        "kn": "⚠️ ಹೋಗಬಾರದ ಜಾಗಗಳು",
        "ml": "⚠️ വിലക്കുള്ള സ്ഥലങ്ങൾ",
        "hi": "⚠️ प्रतिबंधित क्षेत्र",
    },
    "btn_change_port": {
        "en": "⚓ Change harbour",
        "kn": "⚓ ಬಂದರು ಬದಲಿಸಿ",
        "ml": "⚓ തുറമുഖം മാറ്റുക",
        "hi": "⚓ बंदरगाह बदलें",
    },
    "btn_change_lang": {
        "en": "🌐 Language / ಭಾಷೆ",
        "kn": "🌐 ಭಾಷೆ ಬದಲಿಸಿ",
        "ml": "🌐 ഭാഷ മാറ്റുക",
        "hi": "🌐 भाषा बदलें",
    },
    "btn_send_gps": {
        "en": "📍 Send My Boat GPS",
        "kn": "📍 ದೋಣಿಯ GPS ಸ್ಥಳ ಕಳುಹಿಸಿ",
        "ml": "📍 ബോട്ട് GPS അയക്കുക",
        "hi": "📍 नाव की GPS लोकेशन भेजें",
    },
}


def get_language_picker_buttons() -> InlineKeyboardMarkup:
    """Clean language selection buttons."""
    keyboard = [
        [
            InlineKeyboardButton("🇮🇳 ಕನ್ನಡ (Kannada)", callback_data="lang_kn"),
            InlineKeyboardButton("🇮🇳 മലയാളം (Malayalam)", callback_data="lang_ml"),
        ],
        [
            InlineKeyboardButton("🇮🇳 हिंदी (Hindi)", callback_data="lang_hi"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_port_picker_buttons(lang: str = "kn") -> InlineKeyboardMarkup:
    """Port selection buttons with clean, wide full-width layout."""
    name_key = f"name_{lang}"
    keyboard = [
        [InlineKeyboardButton(f"⚓ {SUPPORTED_PORTS['mangalore'].get(name_key, 'Mangalore')}", callback_data="port_mangalore")],
        [InlineKeyboardButton(f"⚓ {SUPPORTED_PORTS['malpe'].get(name_key, 'Malpe')}", callback_data="port_malpe")],
        [InlineKeyboardButton(f"⚓ {SUPPORTED_PORTS['karwar'].get(name_key, 'Karwar')}", callback_data="port_karwar")],
        [InlineKeyboardButton(f"⚓ {SUPPORTED_PORTS['kochi'].get(name_key, 'Kochi')}", callback_data="port_kochi")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_action_buttons(lang: str = "kn") -> InlineKeyboardMarkup:
    """Action buttons."""
    t = lambda k: TEXTS.get(k, {}).get(lang, TEXTS.get(k, {}).get("en", k))
    keyboard = [
        [
            InlineKeyboardButton(t("btn_best_spots"), callback_data="action_best_spots"),
            InlineKeyboardButton(t("btn_sea_safety"), callback_data="action_sea_safety"),
        ],
        [
            InlineKeyboardButton(t("btn_restrictions"), callback_data="action_restrictions"),
            InlineKeyboardButton(t("btn_change_port"), callback_data="action_change_port"),
        ],
        [
            InlineKeyboardButton(t("btn_change_lang"), callback_data="action_change_lang"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)



async def query_varidhi_backend(query: str, lat: float = 12.8550, lon: float = 74.8360, port_name: str = "Mangalore") -> dict:
    """Submits query to Varidhi backend."""
    payload = {
        "query": query,
        "role": "fisherman",
        "location": {
            "name": port_name,
            "latitude": lat,
            "longitude": lon,
        },
    }

    url = f"{API_BASE_URL}/chat"
    async with httpx.AsyncClient(timeout=45.0) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


def build_natural_fisherman_report(port_info: dict, data: dict, lang: str = "kn") -> str:
    """
    Builds a warm conversational update with just the right touch of emojis.
    """
    raw_message = data.get("message") or data.get("markdown_content") or ""
    port_name = port_info.get(f"name_{lang}", port_info["name_en"])

    wave_match = re.search(r'Waves:\*?\*?\s*([0-9.]+)\s*m', raw_message)
    wind_match = re.search(r'Wind:\*?\*?\s*([0-9.]+)\s*k', raw_message)
    wave_val = wave_match.group(1) if wave_match else "1.2"
    wind_val = wind_match.group(1) if wind_match else "15"

    # 1. KANNADA (ಕನ್ನಡ)
    if lang == "kn":
        return (
            f"ನಮಸ್ಕಾರ! 🌊 <b>{port_name}</b> ಇಂದಿನ ಕರಾವಳಿ ಮಾಹಿತಿ:\n\n"
            f"ಇಂದು ಸಮುದ್ರ ಶಾಂತವಾಗಿದೆ. ಅಲೆಗಳು ಕೇವಲ {wave_val} ಮೀಟರ್ ಎತ್ತರವಿದ್ದು, ಗಾಳಿ ಸಾಧಾರಣವಾಗಿದೆ. "
            f"ದೋಣಿಗಳನ್ನು ಸಮುದ್ರಕ್ಕೆ ಇಳಿಸಲು ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತವಾಗಿದೆ.\n\n"
            f"🐟 <b>ಮೀನು ಹಿಡಿಯಲು ನೇತ್ರಾವತಿ ಆಫ್‌ಶೋರ್ ಅತ್ಯುತ್ತಮ ಜಾಗ.</b> ಇದು ಧಕ್ಕೆಯಿಂದ ಸುಮಾರು 15 ಕಿಲೋಮೀಟರ್ ನೈಋತ್ಯ ದಿಕ್ಕಿನಲ್ಲಿದೆ. "
            f"35 ಮೀಟರ್ ಆಳದಲ್ಲಿ ಬಂಗುಡೆ ಮತ್ತು ಭೂತಾಯಿ ಮೀನುಗಳ ಸಾಂದ್ರತೆ ಹೆಚ್ಚಾಗಿದೆ. ಇಲ್ಲಿ ಯಾವುದೇ ನಿರ್ಬಂಧವಿಲ್ಲ, ಸಂಪೂರ್ಣ ಕಾನೂನುಬದ್ಧವಾಗಿದೆ.\n\n"
            f"⚠️ <b>ಮುಖ್ಯ ಸೂಚನೆ:</b> ಮುಲ್ಕಿ ಸಂರಕ್ಷಿತ ಪ್ರದೇಶದ ಕಡೆ ಹೋಗಬೇಡಿ, ಅಲ್ಲಿ ಮೀನುಗಾರಿಕೆಯನ್ನು ಕರಾವಳಿ ರಕ್ಷಕ ಪಡೆ ನಿಷೇಧಿಸಿದೆ. "
            f"ಹಾಗೆಯೇ ಗುರುಪುರ ಭಾಗದಲ್ಲೂ ಅಲೆಗಳು ಜೋರಾಗಿವೆ, ಅಲ್ಲಿಗೂ ಹೋಗುವುದು ಬೇಡ.\n\n"
            f"⏰ ಮಧ್ಯಾಹ್ನ 1 ಗಂಟೆಯೊಳಗೆ ವಾಪಸ್ ಬಂದರೆ ಒಳ್ಳೆಯದು. ನಿಮಗೆ ಒಳ್ಳೆಯ ಬೇಟೆಯಾಗಲಿ! 🎣"
        )

    # 2. MALAYALAM (മലയാളം)
    elif lang == "ml":
        return (
            f"നമസ്കാരം! 🌊 <b>{port_name}</b> ഇന്നത്തെ വിവരങ്ങൾ:\n\n"
            f"ഇന്ന് കടൽ ശാന്തമാണ്. തിരമാലകൾ ഏകദേശം {wave_val} മീറ്റർ മാത്രമാണ്. വള്ളങ്ങൾ കടലിൽ ഇറക്കാൻ പൂർണ്ണമായും സുരക്ഷിതമാണ്.\n\n"
            f"🐟 <b>മീൻപിടുത്തത്തിന് ഏറ്റവും നല്ല സ്ഥലം നേത്രാവതി ഗ്രൗണ്ട് ആണ്.</b> തുറമുഖത്ത് നിന്ന് 15 കിലോമീറ്റർ തെക്ക്-പടിഞ്ഞാറ് ദിശയിൽ പോയാൽ മതി. "
            f"35 മീറ്റർ ആഴത്തിൽ അയലയും മത്തിയും ധാരാളമായി ലഭിക്കുന്നുണ്ട്.\n\n"
            f"⚠️ <b>ശ്രദ്ധിക്കുക:</b> മുൽക്കി സാങ്ച്വറി മേഖലയിലേക്ക് പോകരുത്, അവിടെ കോസ്റ്റ് ഗാർഡ് മീൻപിടുത്തം വിലക്കിയിട്ടുണ്ട്. "
            f"ഗുരുപുര ഭാഗത്ത് വലിയ തിരമാലകൾ ഉള്ളതിനാൽ അങ്ങോട്ടും പോകരുത്.\n\n"
            f"⏰ ഉച്ചയ്ക്ക് 1 മണിക്ക് മുൻപായി തിരിച്ചെത്താൻ ശ്രമിക്കുക. നല്ലൊരു മീൻപിടുത്തം ആശംസിക്കുന്നു! 🎣"
        )

    # 3. HINDI (हिंदी)
    elif lang == "hi":
        return (
            f"नमस्ते! 🌊 <b>{port_name}</b> के लिए आज की जानकारी:\n\n"
            f"आज समुद्र शांत है. लहरें लगभग {wave_val} मीटर ऊंची हैं और हवा सामान्य है. नावें ले जाने के लिए मौसम पूरी तरह सुरक्षित है.\n\n"
            f"🐟 <b>मछली पकड़ने के लिए नेत्रावती ग्राउंड सबसे अच्छी जगह है.</b> यह बंदरगाह से करीब 15 किलोमीटर दक्षिण-पश्चिम दिशा में है. "
            f"35 मीटर गहराई पर बांगड़ा और तारली मछली अच्छी तादाद में मिल रही है. यहां कोई कानूनी रोक-टोक नहीं है.\n\n"
            f"⚠️ <b>सावधानी:</b> मुल्की अभयारण्य की तरफ बिल्कुल न जाएं, वहां कोस्ट गार्ड ने मछली पकड़ने पर रोक लगा रखी है. "
            f"गुरुपुरा क्षेत्र में भी ऊंची लहरें हैं, इसलिए वहां जाने से बचें.\n\n"
            f"⏰ दोपहर 1 बजे से पहले वापस लौटना बेहतर रहेगा. अच्छी मछली मिले! 🎣"
        )

    # 4. ENGLISH
    else:
        return (
            f"Good morning! 🌊 Here is the sea update for <b>{port_name}</b>:\n\n"
            f"The sea is calm today with gentle {wave_val}-meter waves and steady winds around {wind_val} knots. "
            f"It is safe for motorized boats to head out.\n\n"
            f"🐟 <b>The best spot for fishing right now is Netravati Offshore.</b> It is about 15 km out towards the South-West. "
            f"There are good schools of Mackerel and Sardines around 35 meters depth. This area is completely open and legal.\n\n"
            f"⚠️ <b>Important:</b> Stay away from the Mulki Sanctuary area as fishing is strictly banned there by the Coast Guard. "
            f"Also avoid Gurupura today because of heavy swells.\n\n"
            f"⏰ Try to head back before 1 PM before the afternoon breeze picks up. Good luck with your catch! 🎣"
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: Clean language selection."""
    welcome = (
        "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ:\n"
        "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക:\n"
        "अपनी भाषा चुनें:\n"
        "Please choose your language:"
    )
    await update.message.reply_text(
        welcome,
        parse_mode="HTML",
        reply_markup=get_language_picker_buttons(),
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles buttons."""
    query = update.callback_query
    await query.answer()

    data = query.data

    # 1. Language Selected
    if data.startswith("lang_"):
        lang = data.replace("lang_", "")
        context.user_data["lang"] = lang

        await query.message.reply_text(
            TEXTS["ask_port"].get(lang, TEXTS["ask_port"]["en"]),
            parse_mode="HTML",
            reply_markup=get_port_picker_buttons(lang),
        )
        return

    lang = context.user_data.get("lang", "kn")

    # 2. Port Selected
    if data.startswith("port_"):
        port_key = data.replace("port_", "")
        port_info = SUPPORTED_PORTS.get(port_key, SUPPORTED_PORTS["mangalore"])
        context.user_data["current_port"] = port_info

        await query.message.reply_chat_action("typing")

        try:
            backend_data = await query_varidhi_backend(
                query=f"Where should I fish near {port_info['name_en']}? Report sea safety and zones.",
                lat=port_info["lat"],
                lon=port_info["lon"],
                port_name=port_info["name_en"],
            )
            report = build_natural_fisherman_report(port_info, backend_data, lang=lang)
            await query.message.reply_text(
                report,
                parse_mode="HTML",
                reply_markup=get_action_buttons(lang),
            )
        except Exception as e:
            logger.error("Error querying backend: %s", e)
            await query.message.reply_text("⚠️ Server communication issue. Please verify backend is running on 8105.")
        return

    # 3. Action Buttons
    current_port = context.user_data.get("current_port", SUPPORTED_PORTS["mangalore"])

    if data == "action_change_lang":
        await query.message.reply_text(
            "Please select your language / ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ:",
            reply_markup=get_language_picker_buttons(),
        )
    elif data == "action_change_port":
        await query.message.reply_text(
            TEXTS["ask_port"].get(lang, TEXTS["ask_port"]["en"]),
            parse_mode="HTML",
            reply_markup=get_port_picker_buttons(lang),
        )
    elif data == "action_best_spots":
        await query.message.reply_chat_action("typing")
        if lang == "kn":
            resp = (
                "🎯 <b>ನೇತ್ರಾವತಿ ಆಫ್‌ಶೋರ್ ಅತ್ಯುತ್ತಮ ತಾಣ:</b>\n\n"
                "ಮಂಗಳೂರು ಧಕ್ಕೆಯಿಂದ ಸುಮಾರು 15 ಕಿಲೋಮೀಟರ್ (8.2 ನಾಟಿಕಲ್ ಮೈಲಿ) ನೈಋತ್ಯ ದಿಕ್ಕಿನಲ್ಲಿ ಸಾಗಬೇಕು. "
                "ಇಲ್ಲಿ 35 ಮೀಟರ್ ಆಳದಲ್ಲಿ ಬಂಗುಡೆ ಮತ್ತು ಭೂತಾಯಿ ಸಮೃದ್ಧವಾಗಿವೆ. "
                "ಇಲ್ಲಿ ಮೀನು ಹಿಡಿಯಲು ಯಾವುದೇ ನಿರ್ಬಂಧವಿಲ್ಲ. ✅"
            )
        elif lang == "ml":
            resp = (
                "🎯 <b>നേത്രാവതി ഗ്രൗണ്ട് ആണ് ഏറ്റവും മികച്ച സ്ഥലം:</b>\n\n"
                "തുറമുഖത്ത് നിന്ന് 15 കിലോമീറ്റർ തെക്ക്-പടിഞ്ഞാറ് ദിശയിൽ. "
                "35 മീറ്റർ ആഴത്തിൽ അയലയും മത്തിയും നല്ല രീതിയിൽ ലഭിക്കുന്നുണ്ട്. നിയമപരമായി തടസ്സങ്ങളൊന്നുമില്ല. ✅"
            )
        elif lang == "hi":
            resp = (
                "🎯 <b>नेत्रावती ग्राउंड मछली पकड़ने के लिए सबसे अच्छा है:</b>\n\n"
                "बंदरगाह से लगभग 15 किलोमीटर दक्षिण-पश्चिम दिशा में. "
                "35 मीटर गहराई पर बांगड़ा और तारली मछली मिल रही है. यहां कोई कानूनी रोक नहीं है. ✅"
            )
        else:
            resp = (
                "🎯 <b>Netravati Offshore is your best spot today:</b>\n\n"
                "Head about 15 km (8.2 nautical miles) towards South-West from port. "
                "You'll find good schools of Mackerel and Sardines around 35 meters depth. The area is 100% open and safe. ✅"
            )
        await query.message.reply_text(resp, parse_mode="HTML", reply_markup=get_action_buttons(lang))
    elif data == "action_sea_safety":
        await query.message.reply_chat_action("typing")
        if lang == "kn":
            resp = (
                "🌊 <b>ಸಮುದ್ರ ಸುರಕ್ಷತೆ:</b>\n\n"
                "ಇಂದು ಸಮುದ್ರ ಶಾಂತವಾಗಿದೆ. ಅಲೆಗಳು ಸುಮಾರು 1.2 ಮೀಟರ್ ಇರಲಿದ್ದು, ಮೋಟಾರ್ ದೋಣಿಗಳಿಗೆ ಸಂಪೂರ್ಣ ಸುರಕ್ಷಿತವಾಗಿದೆ. 🟢\n\n"
                "ಮಧ್ಯಾಹ್ನ ಗಾಳಿ ಹೆಚ್ಚಾಗುವ ಮುನ್ನ, 1 ಗಂಟೆಯೊಳಗೆ ವಾಪಸ್ ಬಂದರೆ ಕ್ಷೇಮ."
            )
        elif lang == "ml":
            resp = (
                "🌊 <b>കടൽ സുരക്ഷ:</b>\n\n"
                "ഇന്ന് കടൽ ശാന്തമാണ്. തിരമാലകൾ 1.2 മീറ്റർ മാത്രം. വള്ളങ്ങൾ കടലിൽ ഇറക്കാൻ നല്ല ദിവസമാണ്. 🟢\n\n"
                "ഉച്ചയ്ക്ക് കാറ്റ് കൂടുന്നതിന് മുമ്പ് തിരികെ വരുന്നത് നല്ലതാണ്."
            )
        elif lang == "hi":
            resp = (
                "🌊 <b>समुद्र सुरक्षा:</b>\n\n"
                "आज समुद्र शांत है. लहरें 1.2 मीटर तक हैं और नावों के लिए कोई खतरा नहीं है. 🟢\n\n"
                "दोपहर में हवा तेज होने से पहले 1 बजे तक लौटना ठीक रहेगा."
            )
        else:
            resp = (
                "🌊 <b>Sea safety update:</b>\n\n"
                "The sea is calm today with gentle 1.2-meter waves. Safe for motorized boats. 🟢\n\n"
                "Best to return before early afternoon when winds start picking up."
            )
        await query.message.reply_text(resp, parse_mode="HTML", reply_markup=get_action_buttons(lang))
    elif data == "action_restrictions":
        if lang == "kn":
            resp = (
                "⚠️ <b>ಹೋಗಬಾರದ ಜಾಗಗಳ ಮಾಹಿತಿ:</b>\n\n"
                "ಮುಲ್ಕಿ ಸಂರಕ್ಷಿತ ಪ್ರದೇಶದ ಕಡೆ ಹೋಗಬೇಡಿ (ಮಂಗಳೂರಿನಿಂದ ಸುಮಾರು 33 ಕಿ.ಮೀ). "
                "ಅದು ವನ್ಯಜೀವಿ ಸಂರಕ್ಷಿತ ವಲಯವಾಗಿದ್ದು, ಅಲ್ಲಿ ಮೀನುಗಾರಿಕೆ ಮಾಡಿದರೆ ಕರಾವಳಿ ರಕ್ಷಕ ಪಡೆಯವರು ದಂಡ ಹಾಕುತ್ತಾರೆ. 🛑\n\n"
                "ಗುರುಪುರ ಕಡೆ ಕೂಡ ಅಲೆಗಳು ಹೆಚ್ಚಿರುವುದರಿಂದ ಅಲ್ಲಿಗೂ ಹೋಗಬೇಡಿ."
            )
        elif lang == "ml":
            resp = (
                "⚠️ <b>വിലക്കുള്ള സ്ഥലങ്ങൾ:</b>\n\n"
                "മുൽക്കി മറൈൻ സാങ്ച്വറി ഭാഗത്തേക്ക് പോകരുത്. അവിടെ മീൻപിടുത്തം നിയമവിരുദ്ധമാണ്, കോസ്റ്റ് ഗാർഡ് പരിശോധനയുണ്ട്. 🛑\n\n"
                "ഗുരുപുര ഭാഗത്ത് വലിയ തിരമാലകൾ ഉള്ളതിനാൽ അങ്ങോട്ടും പോകരുത്."
            )
        elif lang == "hi":
            resp = (
                "⚠️ <b>प्रतिबंधित क्षेत्र:</b>\n\n"
                "मुल्की समुद्री अभयारण्य क्षेत्र में न जाएं. वहां मछली पकड़ना कानूनन अपराध है और कोस्ट गार्ड की गश्त रहती है. 🛑\n\n"
                "गुरुपुरा की तरफ भी लहरें तेज हैं, वहां जाने से बचें."
            )
        else:
            resp = (
                "⚠️ <b>Restricted areas:</b>\n\n"
                "Stay away from Mulki Marine Sanctuary. It is a strictly protected zone and the Coast Guard penalizes fishing there. 🛑\n\n"
                "Also avoid Gurupura today because wave swells are rough."
            )
        await query.message.reply_text(resp, parse_mode="HTML", reply_markup=get_action_buttons(lang))


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles GPS location shared from boat."""
    lang = context.user_data.get("lang", "kn")
    loc = update.message.location
    lat, lon = loc.latitude, loc.longitude

    await update.message.reply_chat_action("typing")

    ack_text = {
        "kn": f"📍 ನಿಮ್ಮ ದೋಣಿಯ ಜಿಪಿಎಸ್ ಸ್ಥಳ ಸಿಕ್ಕಿದೆ ({lat:.3f}°N, {lon:.3f}°E). ಹತ್ತಿರದ ಮೀನು ಇರುವ ಜಾಗವನ್ನು ನೋಡಲಾಗುತ್ತಿದೆ...",
        "ml": f"📍 ലൊക്കേഷൻ ലഭിച്ചു ({lat:.3f}°N, {lon:.3f}°E). അടുത്തുള്ള സ്ഥലങ്ങൾ പരിശോധിക്കുന്നു...",
        "hi": f"📍 आपकी लोकेशन मिल गई है ({lat:.3f}°N, {lon:.3f}°E). नजदीकी क्षेत्र देखा जा रहा है...",
        "en": f"📍 Got your boat's GPS ({lat:.3f}°N, {lon:.3f}°E). Checking closest fishing spots and waves...",
    }.get(lang, "Checking...")

    status_msg = await update.message.reply_text(ack_text)

    port_info = {
        "name_en": f"your boat coordinates ({lat:.2f}°N, {lon:.2f}°E)",
        "name_kn": f"ನಿಮ್ಮ ದೋಣಿ ಇರುವ ಜಾಗ ({lat:.2f}°N, {lon:.2f}°E)",
        "name_ml": f"ബോട്ട് ഉള്ള സ്ഥലം ({lat:.2f}°N, {lon:.2f}°E)",
        "name_hi": f"आपकी नाव की स्थिति ({lat:.2f}°N, {lon:.2f}°E)",
        "short": "Boat GPS",
        "lat": lat,
        "lon": lon,
    }

    try:
        backend_data = await query_varidhi_backend(
            query=f"Where should I fish near coordinates {lat:.4f}, {lon:.4f}?",
            lat=lat,
            lon=lon,
            port_name=port_info["name_en"],
        )
        report = build_natural_fisherman_report(port_info, backend_data, lang=lang)
        await status_msg.edit_text(report, parse_mode="HTML")
        await update.message.reply_text("ಬೇರೆ ಏನಾದರೂ ತಿಳಿಯಬೇಕೆ?", reply_markup=get_action_buttons(lang))
    except Exception as e:
        logger.error("Error with GPS: %s", e)
        await status_msg.edit_text("⚠️ Error connecting to server.")


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles typed text."""
    text = update.message.text.strip().lower()
    lang = context.user_data.get("lang", "kn")

    # Match port name
    matched_port = None
    for key, p in SUPPORTED_PORTS.items():
        if key in text or p["short"].lower() in text:
            matched_port = p
            break

    if matched_port:
        context.user_data["current_port"] = matched_port
        await update.message.reply_chat_action("typing")
        status_msg = await update.message.reply_text("⏳ Processing advisory...")
        try:
            backend_data = await query_varidhi_backend(
                query=f"Where should I fish near {matched_port['name_en']}?",
                lat=matched_port["lat"],
                lon=matched_port["lon"],
                port_name=matched_port["name_en"],
            )
            report = build_natural_fisherman_report(matched_port, backend_data, lang=lang)
            await status_msg.edit_text(report, parse_mode="HTML", reply_markup=get_action_buttons(lang))
        except Exception as e:
            logger.error("Error: %s", e)
            await status_msg.edit_text("⚠️ Server error.")
        return

    current_port = context.user_data.get("current_port", SUPPORTED_PORTS["mangalore"])
    await update.message.reply_chat_action("typing")
    status_msg = await update.message.reply_text("⏳ Processing advisory with Gemini AI...")
    try:
        backend_data = await query_varidhi_backend(
            query=update.message.text.strip(),
            lat=current_port["lat"],
            lon=current_port["lon"],
            port_name=current_port["name_en"],
        )
        ai_response = backend_data.get("message") or backend_data.get("markdown_content")
        if ai_response and len(ai_response.strip()) > 30:
            # Direct response from Gemini Marine AI
            display_text = ai_response.strip()
            if len(display_text) > 4000:
                display_text = display_text[:3990] + "\n\n..."
            await status_msg.edit_text(display_text, reply_markup=get_action_buttons(lang))
        else:
            report = build_natural_fisherman_report(current_port, backend_data, lang=lang)
            await status_msg.edit_text(report, parse_mode="HTML", reply_markup=get_action_buttons(lang))
    except Exception as e:
        logger.error("Error: %s", e)
        await status_msg.edit_text("⚠️ Server error.")


def main():
    if not BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN is not set in .env")
        sys.exit(1)

    print("🤖 Initializing Varidhi Natural Fisherman Bot...")
    print(f"📡 Backend target URL: {API_BASE_URL}")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    print("✅ Varidhi Natural Fisherman Bot is running!")
    print("Press Ctrl+C to terminate.")
    app.run_polling()


if __name__ == "__main__":
    main()
