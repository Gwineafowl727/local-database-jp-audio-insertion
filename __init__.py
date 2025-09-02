from aqt import mw, gui_hooks
from aqt.utils import showInfo, qconnect
from aqt.qt import *
from .Selector import Selector
import json
import os
from .util import get_pitch_accent_notation, copy_to_collection_media


"""
to do:
-make sure it works on mac cuz god knows if i did the os module stuff right
-implement cross checking with kana fields to eliminate wrong audios from getting added
-make it possible to convert katakana words to hiragana so that they can be found (i.e. ヘラヘラ)
-make it possible to prefer nhk/shinmeikai only when multiple pitches are found, otherwise prefer other things
"""


def get_forvo_audio(word: str, profile_name) -> str:
    """Return string name of the forvo audio file path, or empty string if doesn't exist"""
    file_name = f"{word}.opus"
    file_path = os.path.join(parent_path, "forvo_files", profile_name, file_name)
    if os.path.isfile(file_path):
        return file_path
    else:
        return ""
    

def get_nhk_audio(word: str) -> list:
    """Return list of 2 lists: \n
    list 1: string name of NHK audio file path \n
    list 2: string of pitch accent notation for audio file of same index in list 1 \n
    return empty list if not found at all"""
    nhk_audio_folder = os.path.join(parent_path, "nhk16_files\\audio")
    try:
        index = nhk_map[word]
    except KeyError:
        return []
    entry = nhk_dict[index]
    accents_list = entry["accents"]

    audios_list = []
    pitch_list = []

    for a in accents_list:


        audios_list.append(os.path.join(nhk_audio_folder, a["soundFile"]))
        accent = a["accent"][0]
        pitch_list.append(get_pitch_accent_notation(accent["pronunciation"], accent["pitchAccent"]))
    return [audios_list, pitch_list]


def get_shinmeikai_audio(word: str) -> list:
    """Return list of 2 lists: \n
    list 1: string name of shinmeikai audio file path \n
    list 2: string of pitch accent notation for audio file of same index in list 1 \n
    return empty list if not found at all"""
    shinmeikai_audio_folder = os.path.join(parent_path, "shinmeikai8_files\\media")
    try:
        audio_name_list = shinmeikai_dict["headwords"][word]
    except:
        return []
    
    audios_list = []
    pitch_list = []

    for audio in audio_name_list:
        audios_list.append(os.path.join(shinmeikai_audio_folder, audio))
        pitch = shinmeikai_dict["files"][audio]["pitch_pattern"]
        if pitch[-1] == "━":
            pitch = pitch[0:-1]
        pitch_list.append(pitch)
    return [audios_list, pitch_list]
    

def load_dicts() -> None:
    """
    Loads the dictionaries as global variables only once user tries to do something with addon,\n
    as our other choice is to lag Anki for a second every time it opens.
    """
    global nhk_dict
    global nhk_map
    global shinmeikai_dict
    if nhk_dict is None:
        user_files_path = user_config["user_files_path"]
        nhk_json_path = os.path.join(user_files_path, "nhk16_files\\entries.json")
        shinmeikai_json_path = os.path.join(user_files_path, "shinmeikai8_files\\index.json")
        with open(nhk_json_path, "r") as file:
            nhk_dict = json.load(file)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        with open("nhk_map.json", "r") as file:
            nhk_map = json.load(file)

        with open(shinmeikai_json_path, "r") as file:
            shinmeikai_dict = json.load(file)


def fill_audio_field(add_to_card: list, field_name_list: list, note) -> None:
    """Helper function for placing the selected audio(s) into audio field."""

    note_type = note.model()
    note_type_name = note_type["name"]

    audio_string = ""
    for i, a in enumerate(add_to_card):
        audio_string += a
    
    num = 0
    for i, f in enumerate(field_name_list):
        if f == user_config["notetypes"][note_type_name][1]:
            num = i
            break
    note.fields[num] = audio_string
    try:
        note.flush()
    except:
        pass


def auto_select(note) -> None:
    """
    Uses the ordered priority set in config.json to autopick which audio source to use
    """
    load_dicts()

    # Gathering current note type and list of fields in note type
    note_type = note.model()

    note_type_name = note_type["name"]
    search_field = user_config["notetypes"][note_type_name][0]
    

    # Getting the word from the note
    fields_list = note_type["flds"]
    field_name_list = []
    for field_object in fields_list:
        field_name_list.append(field_object["name"])
    for i, field_name in enumerate(field_name_list):
        if field_name == search_field:
            index = i
    word = note.fields[index]

    search_priority_list = user_config["search_priority"]
    for source in search_priority_list:

        if source == "nhk16":
            nhk_list = get_nhk_audio(word)
            if not nhk_list:
                pass
            else:
                add_to_card = []
                for i, file_path in enumerate(nhk_list[0]):
                    add_to_card.append(copy_to_collection_media(file_path, user_config["collection_media_path"])[0])
                    if not user_config["include_all_pitches"]:
                        break
                fill_audio_field(add_to_card, field_name_list, note)
                return
                    

        elif source == "shinmeikai8":
            shinmeikai_list = get_shinmeikai_audio(word)
            if not shinmeikai_list:
                pass
            else:
                add_to_card = []
                for i, file_path in enumerate(shinmeikai_list[0]):
                    add_to_card.append(copy_to_collection_media(file_path, user_config["collection_media_path"])[0])
                    if not user_config["include_all_pitches"]:
                        break
                fill_audio_field(add_to_card, field_name_list, note)
                return


        else:
            file_path = get_forvo_audio(word, source)
            if file_path == "":
                continue
            else:
               add_to_card = []
               add_to_card.append(copy_to_collection_media(file_path, user_config["collection_media_path"])[0])
               fill_audio_field(add_to_card, field_name_list, note)
               return

    fill_audio_field([""], field_name_list, note)
    

def manual_select(editor) -> None:
    """
    Allows user to choose which available audios to add.
    """
    load_dicts()

    # Gathering editor's current note type and list of fields in note type
    editor_note = editor.note
    editor_note_type = editor_note.model()

    editor_note_type_name = editor_note_type["name"]
    search_field = user_config["notetypes"][editor_note_type_name][0]

    # Getting the word from the note
    fields_list = editor_note_type["flds"]
    field_name_list = []
    for field_object in fields_list:
        field_name_list.append(field_object["name"])
    for i, field_name in enumerate(field_name_list):
        if field_name == search_field:
            index = i
    word = editor_note.fields[index]

    strawberry_brown = get_forvo_audio(word, "strawberrybrown")
    poyotan = get_forvo_audio(word, "poyotan")
    kaoring = get_forvo_audio(word, "kaoring")
    akimoto = get_forvo_audio(word, "akimoto")
    skent = get_forvo_audio(word, "skent")
    
    

    audio_list = [strawberry_brown, poyotan, kaoring, akimoto, skent]
    text_list = ["strawberry_brown", "poyotan", "kaoring", "akimoto", "skent"]

    try:
        nhk_list = get_nhk_audio(word)
        nhk_audios = nhk_list[0]
        nhk_pitches = nhk_list[1]
    except:
        nhk_list = []
        nhk_audios = []
        nhk_pitches = []
    try:
        shinmeikai_list = get_shinmeikai_audio(word)
        shinmeikai_audios = shinmeikai_list[0]
        shinmeikai_pitches = shinmeikai_list[1]
    except:
        shinmeikai_list = []
        shinmeikai_audios = []
        shinmeikai_pitches = []

    for a in nhk_audios:
        audio_list.append(a)
    for p in nhk_pitches:
        text_list.append("NHK: " + p)
    for a in shinmeikai_audios:
        audio_list.append(a)
    for p in shinmeikai_pitches:
        text_list.append("Shinmeikai: " + p)

    # First copy over all the audios to collection.media in order to use aqt.sound's play
    all_audio_strings = []
    reduced_text_list = []
    collection_audio_file_path = []
    for file_path, name in zip(audio_list, text_list):
        if file_path == "":
            continue
        print(file_path)
        audio_tuple = copy_to_collection_media(file_path, user_config["collection_media_path"])
        all_audio_strings.append(audio_tuple[0])
        collection_audio_file_path.append(audio_tuple[1])
        reduced_text_list.append(name)

    user_answer = Selector(audio_list, text_list, collection_audio_file_path)
    user_answer = user_answer.exec()

    add_to_card = []


    for i, t in enumerate(reduced_text_list):
        if t in user_answer:
            add_to_card.append(all_audio_strings[i])
    note = False
    fill_audio_field(add_to_card, field_name_list, editor_note)
    editor.loadNote()


def auto_select_with_editor(editor):
    note = editor.note
    auto_select(note)
    editor.loadNote()


def add_editor_buttons(buttons, editor):
    """
    Add buttons to editor menu.
    """

    # get file paths for icons
    icon_auto_audio = os.path.join(script_dir, "auto_icon.png")
    icon_manual_audio = os.path.join(script_dir, "manual_icon.png")

    # editor button for autofilling audio based on preset priority
    autofill_button = editor.addButton(
        icon = icon_auto_audio,
        cmd = "local_db_jp_audio_insertion_auto",
        func = auto_select_with_editor,
        tip = "(Local Database JP Audio Insertion) insert audio, choosing by priority"
    )
    buttons.append(autofill_button)

    # editor button for manual selection of audio
    manual_button = editor.addButton(
        icon = icon_manual_audio,
        cmd = 'local_db_jp_audio_insertion_manual',
        func = manual_select,
        tip= "(Local Database JP Audio Insertion) insert audio, choose yourself"
    )
    buttons.append(manual_button)


def mass_autofill_jp_audio(browser):
    nids = browser.selectedNotes()
    if not nids:
        showInfo("No notes selected.")
        return
    for nid in nids:
        note = mw.col.getNote(nid)
        auto_select(note)
    showInfo(f"Autofilled JP audio for {len(nids)} notes.")


def append_to_browser_menu(browser, menu):
    # Add your option at the end of the context menu
    action = QAction("Autofill JP audio to note", browser)
    action.triggered.connect(lambda _, b=browser: mass_autofill_jp_audio(b))
    menu.addAction(action)



# Changing directory to script location to load config.json
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
with open("config.json", "r") as file:
    user_config = json.load(file)

# Initializing dict variables
nhk_dict = None
nhk_map = None
shinmeikai_dict = None

parent_path = "C:\\Users\\Tennyson (code)\\AppData\\Roaming\\Anki2\\addons21\\1045800357\\user_files"

gui_hooks.editor_did_init_buttons.append(add_editor_buttons)
gui_hooks.browser_will_show_context_menu.append(append_to_browser_menu)