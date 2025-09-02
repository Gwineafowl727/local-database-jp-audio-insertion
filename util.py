import os
import shutil
import random
import re


def copy_to_collection_media(original_audio_file_path: str, collection_media_path: str) -> str:
    """
    Copy and paste the file to the folder that lets Anki use it as audio for cards,
    then return the audio string that can be pasted into editor
    """
    original_audio_file_name = os.path.basename(original_audio_file_path)
    rand = str(random.randint(0, 999999999999))
    new_file_name = f"{rand}_{original_audio_file_name}"
    collection_media_path = "C:\\Users\\Tennyson (code)\\AppData\\Roaming\\Anki2\\User 1\\collection.media"
    path_for_card = os.path.join(collection_media_path, new_file_name)
    os.makedirs(os.path.dirname(path_for_card), exist_ok=True)
    shutil.copy(original_audio_file_path, path_for_card)
    return (f"[sound:{new_file_name}]", path_for_card)


def get_pitch_accent_notation(pronunciation: str, value: int) -> str:
    """Produces a new string where a slash in the kana string indicates the pitch"""
    if value == 0:
        return pronunciation
    else:
        v = 0
        new_string = pronunciation[0]
        for i in range(1, value):
            new_string += pronunciation[i]
            v = i
        new_string += "＼"
        for i in range(v + 1, len(pronunciation)):
            try:
                new_string += pronunciation[i]
            except:
                pass
        return new_string
    

def get_kana(furigana_field: str) -> str:
    """Produces a new string of just kana out of furigana fields like WordReading in JP Mining Note"""
        # Replace [reading] with just the reading
    result = re.sub(r'\[([^\]]+)\]', r'\1', furigana_field)
    
    # Remove any remaining kanji characters (CJK Unified Ideographs)
    result = re.sub(r'[\u4e00-\u9fff]', '', result)
    
    return result
 
