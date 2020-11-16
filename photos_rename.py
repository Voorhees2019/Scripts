import os
import re


def get_file_src_name(path, filename):
    return os.path.join(path, filename)


def get_file_dst_name(path, filename):
    return os.path.join(path, ''.join([str(filename), '.jpg']))


def main(path):
    files_lst = os.listdir(path)

    # rename all the files, which names don't consist of numbers(new files),
    # into large_number_names to locate at the end of files_lst
    new_number_name = 100_000
    for file in files_lst:
        if not re.search(r'^(?!0)[0-9]+\.jpg', file):  # ^(?!0) -> searching for smth that starts not with 0
            os.rename(get_file_src_name(path, file), get_file_dst_name(path, new_number_name))
            new_number_name += 1

    # sort files_lst to leave behind already viewed photos
    files_lst = list(map(lambda x: int(x.replace('.jpg', '')), os.listdir(path)))
    files_lst = list(map(lambda x: str(x) + '.jpg', sorted(files_lst)))

    # main rename loop
    i = 1
    for file in files_lst:
        src = get_file_src_name(path, file)
        dst = get_file_dst_name(path, i)
        if os.path.exists(dst):
            i += 1
            continue
        os.rename(src, dst)
        i += 1
        print(f'file "{src}" renamed to "{dst}"')  # look after 4814


if __name__ == '__main__':
    dir_path = 'D:\\VOORHEES\\Pictures()'  # there were 4822 photos
    main(dir_path)
