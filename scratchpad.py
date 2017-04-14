files = [['file1.fastq', 'file2.fastq', 'file2.corr.fastq', 'file1.corr.fastq'], ['file1.fastq', 'file2.fastq', 'file2.corr.fastq', 'file1.corr.fastq']]
print(files)
corr_files = []
for dir_files in files:
    file_group = []
    for file in dir_files:
        if 'corr' in file:
            file_group.append(file)
    corr_files.append(file_group)
print(corr_files)

# my_list = [[1, 4], [3, 2]]
# new_list = sum(my_list, [])
# print(new_list)

corr_files[1].sort()
print(corr_files)
