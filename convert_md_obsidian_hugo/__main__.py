import sys
import os
import argparse
import shutil
from convert_md_obsidian_hugo.logger import get_logger

description = 'Программа предназначена для преобразования mark down файла, подготовленного в Obsidian в формат для использования в hugo'

O_BEGIN_LINK = "[["
O_END_LINK = "]]"
O_SEPARATOR = "|"

O_BEGIN_IMAGE = "![["
O_END_IMAGE = "]]"

H_BEGIN_LINK_HINT = "["
H_END_LINK_HINT = "]"
H_BEGIN_LINK = "({{< "
H_END_LINK = " >}})"

H_BEGIN_IMAGE = '{{< figure src="/'
H_END_IMAGE = '" >}}'

H_CONVERTER_MARK = "@converter_mark"

obsidian_file = ""
hugo_file = ""

ext_pictures = ['.png', '.jpeg', '.jpg', '.tiff']

def convert_file(obsidian_file, hugo_file):
    file = open(obsidian_file)
    source_text = file.read()
    logger.info(f'Файл {obsidian_file} прочитан')

    flag = True

    # Преобразование картинок
    logger.info('Преобразование рисунков начато')
    while flag:
        o_begin_image_pos = source_text.find(O_BEGIN_IMAGE)
        if o_begin_image_pos != -1:
            o_end_image_pos = source_text.find(O_END_IMAGE, o_begin_image_pos)
            if o_end_image_pos != -1:
                image_name = source_text[o_begin_image_pos + 3:o_end_image_pos]
                old_string = source_text[o_begin_image_pos:o_end_image_pos + 2]
                source_text = source_text.replace(old_string, H_CONVERTER_MARK)
                new_string = H_BEGIN_IMAGE + image_name + H_END_IMAGE
                source_text = source_text.replace(H_CONVERTER_MARK, new_string)
                logger.info('Замена ссылки на рисунок выполнено')

        else:
            flag = False
    logger.info('Преобразование ссылок на рисунки выполнено')

    flag = True
    # Преобразование ссылок
    logger.info('Преобразование ссылок на другие файлы начато')
    while flag:
        o_begin_link_pos = source_text.find(O_BEGIN_LINK)
        if o_begin_link_pos != -1:
            o_end_link_pos = source_text.find(O_END_LINK)
            if o_end_link_pos != -1:
                o_separator_pos = source_text.find(O_SEPARATOR, o_begin_link_pos, o_end_link_pos)
                if o_separator_pos != -1:
                    h_link = source_text[o_begin_link_pos + 2:o_separator_pos]
                    h_link_text = source_text[o_separator_pos + 1:o_end_link_pos]
                else:
                    h_link = source_text[o_begin_link_pos + 2:o_end_link_pos]
                    h_link_text = h_link
                old_string = source_text[o_begin_link_pos:o_end_link_pos + 2]
                source_text = source_text.replace(old_string, H_CONVERTER_MARK)
                new_string = H_BEGIN_LINK_HINT + h_link_text + H_END_LINK_HINT + H_BEGIN_LINK + 'ref "' + h_link + '.md"' + H_END_LINK
                source_text = source_text.replace(H_CONVERTER_MARK, new_string)
                logger.info('Замена ссылки на файл выполнено')
        else:
            flag = False
    logger.info('Преобразование ссылок на другие файлы выполнено')
    dest_dir = os.path.split(hugo_file)[0]
    if not(os.path.isdir(dest_dir)):
        os.makedirs(dest_dir)
    dest_file = open(hugo_file, 'w+')
    dest_file.write(source_text)
    dest_file.close()
    logger.info(f'Файл {hugo_file} сохранен')


def convert_dir(obsidian_dir, hugo_dir):
    # Получение списка файлов, в том числе во вложенных каталогах
    # Для каждого файла: если файл имеет расширение md, то выполнить преобразование, иначе- скопировать его
    # Если файл является рисунком, то скопировать его в static

    for root, dirs, files in os.walk(obsidian_dir):
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            _, ext_file = os.path.splitext(file)
            if ext_file.lower() == '.md':
                src = os.path.join(root, file)
                dst = os.path.join(root.replace(obsidian_dir, hugo_dir+'/content'), file)
                convert_file(src, dst)
            elif ext_file.lower() in ext_pictures:
                src = os.path.join(root, file)
                dst_dir = hugo_dir+'/static'
                dst = os.path.join(dst_dir, file)
                if os.path.isdir(hugo_dir+'/static'):
                    shutil.copy(src, dst)
                else:
                    os.makedirs(dst_dir)
                    shutil.copy(src, dst)
                logger.info(f'Копирование изображения {src} в {dst}')
            else:
                src = os.path.join(root, file)
                dst_dir = root.replace(obsidian_dir, hugo_dir+'/content')
                dst = os.path.join(dst_dir, file)
                if os.path.isdir(dst_dir):
                    shutil.copy(src, dst)
                else:
                    os.makedirs(dst_dir)
                    shutil.copy(src, dst)
                logger.info(f'Копирование {src} в {dst}')


if __name__ == '__main__':
    logger = get_logger(__name__)
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument('-i', '--input-file', action='store', help='Входной md-файл')
    arg_parser.add_argument('-o', '--output-file', action='store', help='Выходной md-файл в формате hugo')
    arg_parser.add_argument('-id', '--input-dir', action='store', help='Входной каталог')
    arg_parser.add_argument('-od', '--output-dir', action='store', help='Целевой каталог')


    args = arg_parser.parse_args()
    if args.input_file:
        obsidian_file = args.input_file
        if args.input_dir:
            logger.info(f'Указаный параметры --input-file или --input-dir, более высокий приоритет имеет значение параметра -input-file')
        if not(args.output_file):
            logger.error('Указан параметр --input-file, но не указан параметр --output-file. Выполнение программы невозможно.')
            sys.exit()
    else:
        if not(args.input_dir):
            logger.error(f'Должен быть указан параметр --input-file или --input-dir')
            sys.exit()

    if args.output_file:
        hugo_file = args.output_file
        if args.output_dir:
            logger.info(f'Указаный параметры --output-file или --output-dir, более высокий приоритет имеет значение параметра -output-file')
        if not(args.input_file):
            logger.error('Указан параметр --output-file, но не указан параметр --input-file. Выполнение программы невозможно.')
            sys.exit()
    else:
        if not(args.output_dir):
            logger.error(f'Должен быть указан параметр --output-file или --output-dir')
            sys.exit()

    if args.input_dir:
        obsidian_dir = args.input_dir
        if args.input_file:
            logger.info(f'Указаный параметры --input-file или --input-dir, более высокий приоритет имеет значение параметра -input-file')
        if not(args.output_dir):
            logger.error('Указан параметр --input-dir, но не указан параметр --output-dir. Выполнение программы невозможно.')
            sys.exit()
    else:
        if not(args.input_file):
            logger.error(f'Должен быть указан параметр --input-file или --input-dir')
            sys.exit()

    if args.output_dir:
        hugo_dir = args.output_dir
        if args.output_file:
            logger.info(f'Указаный параметры --output-file или --output-dir, более высокий приоритет имеет значение параметра -output-file')
        if not(args.input_dir):
            logger.error('Указан параметр --output-dir, но не указан параметр --input-dir. Выполнение программы невозможно.')
            sys.exit()
    else:
        if not(args.output_file):
            logger.error(f'Должен быть указан параметр --output-file или --output-dir')
            sys.exit()
    
    
    if len(obsidian_file)>0 and len(hugo_file)>0:
        convert_file(obsidian_file, hugo_file)
    elif len(obsidian_dir)>0 and len(hugo_dir)>0:
        convert_dir(obsidian_dir, hugo_dir)
    else:
        logger.error('Не все значения пераметров переданы корректно')
        sys.exit()

    