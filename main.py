import json
import re
from pathlib import Path
from datetime import date, datetime

import streamlit as st

MONTHS_FR = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}

APP_TITLE = "🐷 Petit Cochon"
DATA_FILE = Path("petit_cochon_data.json")


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "participants": [],
        "events": []
    }


def save_data(data: dict) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def sort_events(events: list[dict]) -> list[dict]:
    return sorted(events, key=lambda e: e["date"])


def format_date_fr(date_str: str) -> str:
    dt = datetime.fromisoformat(date_str)
    return f"{dt.day:02d} {MONTHS_FR[dt.month]} {dt.year}"


def format_date_badge(date_str: str) -> tuple[str, str, str]:
    dt = datetime.fromisoformat(date_str)
    return (
        f"{dt.day:02d}",
        MONTHS_FR[dt.month].capitalize(),
        str(dt.year),
    )


def clean_note_text(value: str) -> str:
    text = str(value or "")
    text = re.sub(r"</?div[^>]*>", "", text, flags=re.IGNORECASE)
    text = text.replace("{notes_html}", "")
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def has_real_text(value: str) -> bool:
    return bool(re.search(r"[A-Za-zÀ-ÿ0-9]", str(value or "")))


def date_palette(index: int) -> tuple[str, str]:
    palettes = [
        ("#FFE7D6", "#7A2E1F"),
        ("#FDE2EC", "#8A3358"),
        ("#DFF1FF", "#1F5A7A"),
        ("#E7F6E7", "#2F6B3A"),
        ("#FFF1D6", "#7A531F"),
        ("#ECE4FF", "#5D3E8A"),
    ]
    return palettes[index % len(palettes)]


st.set_page_config(page_title="Petit Cochon", page_icon="🐷", layout="wide")

st.markdown(
    """
    <style>
    .pc-date-box {
        border-radius: 18px;
        padding: 16px 10px;
        text-align: center;
        font-weight: 700;
        margin-top: 6px;
    }
    .pc-day {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
    }
    .pc-month {
        margin-top: 6px;
        font-size: 0.95rem;
        font-weight: 700;
    }
    .pc-year {
        font-size: 0.9rem;
        opacity: 0.85;
        margin-top: 2px;
    }
    .pc-card-title {
        font-size: 1.35rem;
        font-weight: 800;
        margin-bottom: 0.35rem;
    }
    .pc-section-label {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #8f6b62;
        margin-top: 0.6rem;
        margin-bottom: 0.2rem;
    }
    .pc-chip {
        display: inline-block;
        background: #f7f7f9;
        border: 1px solid #e7e7ec;
        border-radius: 999px;
        padding: 0.28rem 0.7rem;
        margin: 0.15rem 0.35rem 0.15rem 0;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

image_col_left, image_col_center, image_col_right = st.columns([1, 2, 1])
with image_col_center:
    st.image("petit_cochon.png", width=260)

st.title(APP_TITLE)
st.caption("Planification des réunions dégustation de charcuterie")

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

if "participants" not in data:
    data["participants"] = []
if "events" not in data:
    data["events"] = []

for event in data["events"]:
    if "organizers" not in event:
        organizer_value = event.pop("organizer", None)
        event["organizers"] = [organizer_value] if organizer_value else []

    event["notes"] = clean_note_text(event.get("notes", ""))

st.sidebar.header("Administration")
page = st.sidebar.radio(
    "Navigation",
    [
        "Prochaines réunions",
        "Planifier une réunion",
        "Administrer les réunions",
        "Gérer les participants"
    ],
    index=0
)

# ===== Prochaines réunions =====
if page == "Prochaines réunions":
    st.markdown("## 🗓️ Prochaines réunions")
    st.caption("Les prochains rendez-vous gourmands de l'équipe")

    upcoming = [
        event for event in sort_events(data["events"])
        if event["date"] >= date.today().isoformat()
    ]

    if not upcoming:
        st.info("Aucune réunion planifiée pour le moment.")
    else:
        for idx, event in enumerate(upcoming):
            bg_color, text_color = date_palette(idx)
            day, month, year = format_date_badge(event["date"])
            notes = clean_note_text(event.get("notes", ""))

            with st.container(border=True):
                col_date, col_content = st.columns([1, 4])

                with col_date:
                    st.markdown(
                        f"""
                        <div class="pc-date-box" style="background:{bg_color}; color:{text_color};">
                            <div class="pc-day">{day}</div>
                            <div class="pc-month">{month}</div>
                            <div class="pc-year">{year}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_content:
                    st.markdown('<div class="pc-card-title">Lundi gras</div>', unsafe_allow_html=True)

                    st.markdown('<div class="pc-section-label">Organisateurs</div>', unsafe_allow_html=True)
                    if event.get("organizers"):
                        organizers_html = "".join(
                            f'<span class="pc-chip">🐷 {name}</span>'
                            for name in event["organizers"]
                        )
                        st.markdown(organizers_html, unsafe_allow_html=True)
                    else:
                        st.write("Aucun organisateur")

                    st.markdown('<div class="pc-section-label">Participants</div>', unsafe_allow_html=True)
                    if event.get("participants"):
                        participants_html = "".join(
                            f'<span class="pc-chip">{name}</span>'
                            for name in event["participants"]
                        )
                        st.markdown(participants_html, unsafe_allow_html=True)
                    else:
                        st.write("Aucun participant")

                    if notes and has_real_text(notes):
                        st.markdown('<div class="pc-section-label">Notes</div>', unsafe_allow_html=True)
                        st.info(f"📝 {notes}")

# ===== Planifier une réunion =====
elif page == "Planifier une réunion":
    st.subheader("Ajouter une réunion dégustation")

    participants = sorted(data["participants"])

    with st.form("add_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            event_date = st.date_input("Jour de la réunion", value=date.today())
            organizers = st.multiselect("Organisateurs", options=participants, default=[])

        with col2:
            selected_participants = st.multiselect(
                "Participants",
                options=participants,
                default=[]
            )
            notes = st.text_area(
                "Notes",
                placeholder="Ex. apporter saucisson, jambon, cornichons..."
            )

        submitted = st.form_submit_button("Créer la réunion")

        if submitted:
            if not organizers:
                st.error("Merci de sélectionner au moins un organisateur.")
            else:
                data["events"].append({
                    "date": event_date.isoformat(),
                    "organizers": organizers,
                    "participants": selected_participants,
                    "notes": clean_note_text(notes),
                    "created_at": datetime.now().isoformat(timespec="seconds")
                })
                data["events"] = sort_events(data["events"])
                save_data(data)
                st.success("Réunion créée avec succès.")

# ===== Administrer les réunions =====
elif page == "Administrer les réunions":
    st.subheader("Administrer les réunions")

    events = sort_events(data["events"])

    if not events:
        st.info("Aucune réunion à administrer.")
    else:
        for idx, event in enumerate(events):
            with st.expander(
                f"{format_date_fr(event['date'])} — {', '.join(event.get('organizers', [])) if event.get('organizers') else 'Sans organisateur'}",
                expanded=False
            ):
                with st.form(f"edit_event_{idx}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_date = st.date_input(
                            "Jour",
                            value=datetime.fromisoformat(event["date"]).date(),
                            key=f"date_{idx}"
                        )
                        new_organizers = st.multiselect(
                            "Organisateurs",
                            options=sorted(data["participants"]),
                            default=event.get("organizers", []),
                            key=f"org_{idx}"
                        )

                    with col2:
                        new_participants = st.multiselect(
                            "Participants",
                            options=sorted(data["participants"]),
                            default=event.get("participants", []),
                            key=f"participants_{idx}"
                        )
                        new_notes = st.text_area(
                            "Notes",
                            value=event.get("notes", ""),
                            key=f"notes_{idx}"
                        )

                    col_save, col_delete = st.columns(2)
                    save_clicked = col_save.form_submit_button("Enregistrer")
                    delete_clicked = col_delete.form_submit_button("Supprimer")

                    if save_clicked:
                        if not new_organizers:
                            st.error("Au moins un organisateur est obligatoire.")
                        else:
                            event["date"] = new_date.isoformat()
                            event["organizers"] = new_organizers
                            event["participants"] = new_participants
                            event["notes"] = clean_note_text(new_notes)
                            data["events"] = sort_events(data["events"])
                            save_data(data)
                            st.success("Réunion mise à jour.")

                    if delete_clicked:
                        data["events"].remove(event)
                        save_data(data)
                        st.warning("Réunion supprimée. Recharge la page si besoin.")

# ===== Gérer les participants =====
else:
    st.subheader("Gérer les participants")

    with st.form("add_participant_form", clear_on_submit=True):
        new_participant = st.text_input("Nom du participant")
        add_participant = st.form_submit_button("Ajouter")

        if add_participant:
            clean_name = normalize_name(new_participant)
            existing = {p.lower(): p for p in data["participants"]}

            if not clean_name:
                st.error("Merci de saisir un nom.")
            elif clean_name.lower() in existing:
                st.warning("Ce participant existe déjà.")
            else:
                data["participants"].append(clean_name)
                data["participants"] = sorted(data["participants"])
                save_data(data)
                st.success(f"{clean_name} a été ajouté.")

    st.divider()
    st.markdown("### Liste des participants")

    if not data["participants"]:
        st.info("Aucun participant enregistré.")
    else:
        for participant in sorted(data["participants"]):
            col_name, col_delete = st.columns([4, 1])
            col_name.write(participant)

            if col_delete.button("Supprimer", key=f"delete_{participant}"):
                data["participants"].remove(participant)

                for event in data["events"]:
                    if participant in event.get("participants", []):
                        event["participants"] = [p for p in event["participants"] if p != participant]
                    if participant in event.get("organizers", []):
                        event["organizers"] = [p for p in event["organizers"] if p != participant]

                save_data(data)
                st.warning(f"{participant} a été supprimé.")