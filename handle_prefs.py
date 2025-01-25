import os
import json

from whisper.tokenizer import LANGUAGES, TO_LANGUAGE_CODE

USER_PREFS = json.load(open('user_prefs.json', 'r', encoding='utf-8'))

AVAILABLE_LANGUAGES = sorted(list(set(
    [x.title() for x in LANGUAGES.values()] +
    [x.title() for x in TO_LANGUAGE_CODE.keys()]
)))

default = os.path.join(os.path.expanduser("~"), ".cache")
download_root = os.path.join(os.getenv("XDG_CACHE_HOME", default), "whisper")
    
def check_model(model_name):
    return model_name + '.pt' in os.listdir(download_root)

def check_warn(pref_name: str, template_name: str, content: str):
    pref_name += '_insertion_symbol'
    template_name += '_template'
    output_name = template_name.split('_')[0]
    pref = USER_PREFS[pref_name]
    template = USER_PREFS[template_name]
    if pref not in template:
        msg = f'Warning: {pref_name} "{pref}" is not found in {template_name} "{template}". '
        msg += f'Output {output_name} files will not contain the {content}.'
        print(msg)

def validate(option: str):
    
    if option == 'output_dir':
        t = USER_PREFS['output_dir']
        if not os.path.exists(t):
            msg = f'Warning: "output_dir" is set to "{t}" which does not exist.\n'
            msg += 'This directory will be created upon running transcription.'
            print(msg)
            
    elif option in ('model', 'language'):
        if option == 'model':
            t = USER_PREFS['model']
            if not check_model(t):
                msg = f'Warning: "model" is set to "{t}" which has not been downloaded.\n'
                msg += 'You must navigate to "Download models" and download this model first.'
                print(msg)
        m, l = USER_PREFS['model'], USER_PREFS['language']
        if '.en' in m and l != 'English':
            msg = f'Warning: "model" is set to "{m}" which is English-only, '
            msg += f'but "language" is set to {l}.\n'
            msg += 'Whisper will assume all audio is English for this model selection.'
            print(msg)
        assert l in AVAILABLE_LANGUAGES # TODO remove
    
    elif option in ('text_template', 'text_insertion_symbol'):
        check_warn('text', 'text', 'transcribed text')
    elif option == 'segmentation_template':
        st = 'segmentation'
        check_warn('segment', st, 'segmented text')
        check_warn('start_time', st, 'segment start times')
        check_warn('end_time', st, 'segment end times')
    elif option == 'segment_insertion_symbol':
        check_warn('segment', st, 'segmented text')
    elif option == 'start_time_insertion_symbol':
        check_warn('start_time', st, 'segment start times')
    elif option == 'end_time_insertion_symbol':
        check_warn('end_time', st, 'segment end times')
    
def set_option(option: str, new_value):
    
    if option not in USER_PREFS:
        raise ValueError(f'Invalid option: {option}.')
    
    old_value = USER_PREFS[option]
    
    try:
        USER_PREFS[option] = new_value
        validate(option)
    except AssertionError as e:
        USER_PREFS[option] = old_value
        print(f'Warning: failed to update option {option} to {new_value}. Reason:')
        print(e + '\n')
    
    json.dump(
        USER_PREFS,
        open('user_prefs.json', 'w+', encoding='utf-8'),
        indent=4
    )
    
    msg = f'Updated "{option}" to "{new_value}". Saved successfully.\n'
    
if __name__ == "__main__":
    validate()