import os
import shutil
from collections import defaultdict
from pathlib import Path
from utils.create_directories import create_directories
from utils.sha256 import sha256



def check_xml(xml_path: Path):

    with open(xml_path, 'r') as xml_file:
        xml_data = [line.strip() for line in xml_file.readlines()]

        # Master Switch
        check_features = ['<boolean name="36868"']

        check_result = all(any(feature in xml_line for xml_line in xml_data) for feature in check_features)

    return check_result



def copy_file(full_path: Path, target_dir: Path, file_name: str, file_extension: str, hashes: defaultdict[set], counts: defaultdict[int]):

    file_hash = sha256(full_path)

    if (file_name not in hashes[file_hash]):
        hashes[file_hash].add(file_name)

        name_repeat_count = counts[file_name] + 1
        counts[file_name] = name_repeat_count

        if (1 < name_repeat_count):
            file_name = f'{file_name}_{name_repeat_count}'

        shutil.copy2(full_path, f'{target_dir/file_name}{file_extension}')



def filter_irs_vdc_xml(input_dir: Path, output_dir: Path):

    filter_dir = output_dir/'filtered'
    irs_dir = filter_dir/'irs'
    vdc_dir = filter_dir/'vdc'
    xml_dir = filter_dir/'xml'
    create_directories([filter_dir, irs_dir, vdc_dir, xml_dir])

    irs_hashes = defaultdict(set)
    vdc_hashes = defaultdict(set)
    xml_hashes = defaultdict(set)

    irs_counts = defaultdict(int)
    vdc_counts = defaultdict(int)
    xml_counts = defaultdict(int)

    for root, _, files in os.walk(input_dir):
        root = Path(root)

        for file in files:
            full_path = root/file

            file_name = full_path.stem.strip()
            file_extension = full_path.suffix

            if (file_extension == '.irs'):
                copy_file(full_path, irs_dir, file_name, file_extension, irs_hashes, irs_counts)

            elif (file_extension == '.vdc'):
                copy_file(full_path, vdc_dir, file_name, file_extension, vdc_hashes, vdc_counts)

            elif (file_extension == '.xml'):

                check_result = check_xml(full_path)

                if (not check_result):
                    print(f'\nXML not for ViPER:\n{full_path}')

                else:
                    if (file_name in ['bt_a2dp', 'headset', 'speaker', 'usb_device']):
                        if (file_name == 'bt_a2dp'):
                            file_name = 'bluetooth'
                        elif (file_name == 'usb_device'):
                            file_name = 'usb'

                        new_file_name = f'{root.stem}{root.suffix}'.strip()

                        if (not (any(keyword in new_file_name.lower() for keyword in ['bluetooth', 'headset', 'speaker', 'usb']))):
                            new_file_name = f'{new_file_name}-{file_name}'

                    else:
                        new_file_name = file_name

                    copy_file(full_path, xml_dir, new_file_name, file_extension, xml_hashes, xml_counts)

    return(irs_dir, vdc_dir, xml_dir)
