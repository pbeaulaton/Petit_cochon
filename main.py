import json
from pathlib import Path
from datetime import date, datetime

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

import streamlit as st

APP_TITLE = "🐷 Petit Cochon"
DATA_FILE = Path("petit_cochon_data.json")


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "participants": ["Alice", "Bob", "Charlie"],
        "events": []
    }


def save_data(data: dict) -> None:
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


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


st.set_page_config(page_title="Petit Cochon", page_icon="🐷", layout="wide")

image_col_left, image_col_center, image_col_right = st.columns([1, 2, 1])
with image_col_center:
    st.image("petit_cochon.jpg", width=260)

st.title(APP_TITLE)
st.caption("Planification des réunions dégustation de charcuterie")

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Ensure expected keys exist
if "participants" not in data:
    data["participants"] = []
if "events" not in data:
    data["events"] = []

for event in data["events"]:
    if "organizers" not in event:
        organizer_value = event.pop("organizer", None)
        event["organizers"] = [organizer_value] if organizer_value else []

# Sidebar
st.sidebar.header("Administration")
page = st.sidebar.radio(
    "Navigation",
    ["Prochaines réunions", "Réunions passées", "Planifier une réunion", "Administrer les réunions", "Gérer les participants"],
    index=0
)

# ===== Prochaines réunions =====
if page == "Prochaines réunions":
    st.markdown("## 🗓️ Prochaines réunions")
    st.caption("Les prochains rendez-vous gourmands de l'équipe")

    upcoming = [event for event in sort_events(data["events"]) if event["date"] >= date.today().isoformat()]
    if not upcoming:
        st.info("Aucune réunion planifiée pour le moment.")
    else:
        st.markdown(
            """
            <style>
            .pc-card {
                background: linear-gradient(135deg, #fff8f4 0%, #fffdfb 100%);
                border: 1px solid rgba(180, 120, 90, 0.18);
                border-radius: 22px;
                padding: 22px 24px;
                margin-bottom: 18px;
                box-shadow: 0 10px 30px rgba(120, 80, 60, 0.08);
            }
            .pc-grid {
                display: grid;
                grid-template-columns: 110px 1fr;
                gap: 20px;
                align-items: start;
            }
            .pc-date {
                background: linear-gradient(180deg, #ffeddc 0%, #ffd7bf 100%);
                border-radius: 18px;
                padding: 14px 10px;
                text-align: center;
                box-shadow: inset 0 1px 0 rgba(255,255,255,.65);
            }
            .pc-day {
                font-size: 2rem;
                font-weight: 800;
                line-height: 1;
                color: #7a2e1f;
            }
            .pc-month {
                margin-top: 6px;
                font-size: 0.95rem;
                font-weight: 700;
                color: #8b4a3a;
            }
            .pc-year {
                font-size: 0.9rem;
                color: #9c6a5d;
                margin-top: 2px;
            }
            .pc-title {
                font-size: 1.35rem;
                font-weight: 800;
                color: #2f3142;
                margin-bottom: 10px;
            }
            .pc-chips {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
                margin-bottom: 12px;
            }
            .pc-chip {
                display: inline-block;
                background: #ffffff;
                border: 1px solid rgba(90, 90, 120, 0.10);
                border-radius: 999px;
                padding: 6px 12px;
                font-size: 0.92rem;
                color: #3f4154;
            }
            .pc-label {
                font-size: 0.86rem;
                font-weight: 700;
                letter-spacing: 0.02em;
                text-transform: uppercase;
                color: #9a6a5d;
                margin-bottom: 4px;
            }
            .pc-notes {
                background: rgba(255,255,255,0.72);
                border-radius: 14px;
                padding: 12px 14px;
                color: #53566a;
                border: 1px dashed rgba(154, 106, 93, 0.22);
                margin-top: 6px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        for event in upcoming:
            day, month, year = format_date_badge(event["date"])
            organizers_html = "".join(
                [f'<span class="pc-chip">🐷 {name}</span>' for name in event.get("organizers", [])]
            ) or '<span class="pc-chip">Aucun organisateur</span>'
            participants_html = "".join(
                [f'<span class="pc-chip">{name}</span>' for name in event.get("participants", [])]
            ) or '<span class="pc-chip">Aucun participant</span>'
            notes_html = ""
            if event.get("notes"):
                import html
                safe_notes = html.escape(str(event.get("notes", "")).strip())
                if safe_notes:
                    st.markdown('<div class="pc-label">Notes</div>', unsafe_allow_html=True)
                    st.info(f"📝 {str(event.get('notes', '')).strip()}")

            st.markdown(
                f"""
                <div class="pc-card">
                    <div class="pc-grid">
                        <div class="pc-date">
                            <div class="pc-day">{day}</div>
                            <div class="pc-month">{month}</div>
                            <div class="pc-year">{year}</div>
                        </div>
                        <div>
                            <div class="pc-title">Lundi gras</div>
                            <div class="pc-label">Organisateurs</div>
                            <div class="pc-chips">{organizers_html}</div>
                            <div class="pc-label">Participants</div>
                            <div class="pc-chips">{participants_html}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ===== Réunions passées =====
elif page == "Réunions passées":
    st.markdown("## 🕰️ Réunions passées")
    st.caption("Les anciens rendez-vous gourmands de l'équipe")

    past_events = [event for event in sort_events(data["events"]) if event["date"] < date.today().isoformat()]
    if not past_events:
        st.info("Aucune réunion passée pour le moment.")
    else:
        for event in reversed(past_events):
            with st.container(border=True):
                st.markdown(f"### {format_date_fr(event['date'])}")
                st.markdown("**Lundi gras**")
                st.write(
                    f"**Organisateurs :** {', '.join(event.get('organizers', [])) if event.get('organizers') else 'Aucun organisateur'}"
                )
                st.write(
                    f"**Participants :** {', '.join(event.get('participants', [])) if event.get('participants') else 'Aucun participant'}"
                )
                if event.get("notes"):
                    st.info(f"📝 {str(event['notes']).strip()}")

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
            notes = st.text_area("Notes", placeholder="Ex. apporter saucisson, jambon, cornichons...")

        submitted = st.form_submit_button("Créer la réunion")

        if submitted:
            if not organizers:
                st.error("Merci de sélectionner au moins un organisateur.")
            else:
                data["events"].append({
                    "date": event_date.isoformat(),
                    "organizers": organizers,
                    "participants": selected_participants,
                    "notes": notes.strip(),
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
                            event["notes"] = new_notes.strip()
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
                save_data(data)
                st.warning(f"{participant} a été supprimé.")


