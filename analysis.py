from os import walk
from subprocess import Popen, PIPE


def call_process(command, new_dir=None):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, cwd=new_dir)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    return stdout


def walk_reads(directory_path):
    directories = []
    file_list = []
    for dirpath, dirnames, filenames in walk(directory_path):
        if dirpath != directory_path:
            directories.append(dirpath)
            dir_files = []
            for file in filenames:
                dir_files.append(file)
            dir_files.sort()
            file_list.append(dir_files)
    return directories, file_list


def walk_read_subdir(directory_path):
    file_list = []
    for dirpath, dirnames, filenames in walk(directory_path):
        if dirpath == directory_path:
            file_list = filenames
    file_list.sort()
    return file_list


def subsample_reads():
    print('Subsampling read set {} of {}'.format((k + 1), num_read_sets))
    for readfile in skewer_read_files[k]:
        call_process('seqtk sample -s100 {} {} > subsamp-{}'.format(readfile, sampnum, readfile), read_directories[k])


if __name__ == '__main__':
    use_transfuse = False
    subsamp = True
    sampnum = 15000000

    downloads = []
    with open('read_links.txt', 'r') as f:
        for line in f:
            if (line[0] != '#') and (line[0] != '+'):
                downloads.append(line.rstrip())
    num_read_sets = int(len(downloads) / 2)

    call_process('mkdir reads')

    print('')
    counter = 1
    for link in downloads:
        if counter % 2 == 1:
            read_set = int((counter + 1) / 2)
            print('Downloading read set {} of {}'.format(read_set, num_read_sets))
            directory = 'pe_reads_{0:0>2}'.format(read_set)
            call_process('mkdir reads/{}'.format(directory))
        call_process('curl -LO --retry 5 {}'.format(link), 'reads/{}'.format(directory))
        counter += 1
    print('')

    read_directories, read_files = walk_reads('reads')
    cor_read_files = []
    skewer_read_files = []
    assembly_read_files = []

    for k in range(num_read_sets):
        read_files[k].sort()
        print('Running Rcorrector on read set {} of {}'.format((k + 1), num_read_sets))
        call_process('run_rcorrector.pl -1 {} -2 {} -k 32 -t 36'.format(read_files[k][0], read_files[k][1]), read_directories[k])
        files = walk_read_subdir(read_directories[k])
        file_group = []
        for file in files:
            if 'cor' in file:
                file_group.append(file)
        cor_read_files.append(file_group)
        cor_read_files[k].sort()
        print('Running skewer on read set {} of {}'.format((k + 1), num_read_sets))
        call_process('skewer -l 25 -m pe -o skewer -Q 2 -q 2 -t 36 -x /home/mcclintock/holsapple/trinity_analysis/TruSeq3-PE.fa {} {}'.format(cor_read_files[k][0], cor_read_files[k][1]), read_directories[k])
        files = walk_read_subdir(read_directories[k])
        file_group = []
        for file in files:
            if ('skewer' in file) and (file.endswith('fastq')):
                file_group.append(file)
        skewer_read_files.append(file_group)
        if subsamp:
            subsample_reads()
            files = walk_read_subdir(read_directories[k])
            file_group = []
            for file in files:
                if ('subsamp' in file) and (file.endswith('fastq')):
                    file_group.append(file)
            assembly_read_files.append(file_group)
        else:
            assembly_read_files.append(skewer_read_files[k])
        assembly_read_files[k].sort()

        print('Assembling with Trinity on read set {} of {}'.format((k + 1), num_read_sets))
        call_process('Trinity --seqType fq --max_memory 50G --CPU 36 --output trinity --no_normalize_reads --left {} --right {} > trinity.log'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
        call_process('mv trinity.log trinity/', read_directories[k])
        print('Running BUSCO on Trinity assembly for read set {} of {}'.format((k + 1), num_read_sets))
        call_process('BUSCO.py -m tran --cpu 36 -l ~/busco/eukaryota_odb9 -o busco_trinity -i trinity/Trinity.fasta > busco.log', read_directories[k])
        call_process('mv busco.log run_busco_trinity/', read_directories[k])
        print('Running transrate on Trinity assembly for read set {} of {}'.format((k + 1), num_read_sets))
        call_process('transrate -o transrate_trinity -t 36 -a trinity/Trinity.fasta --left {} --right {} > transrate.log'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
        call_process('mv transrate.log transrate_trinity/', read_directories[k])
        print('Assembling with SPAdes on read set {} of {}'.format((k + 1), num_read_sets))
        call_process('spades.py -o spades --rna --only-assembler --threads 36 --memory 50 -1 {} -2 {}'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
        print('Running BUSCO on SPAdes assembly for read set {} of {}'.format((k + 1), num_read_sets))
        call_process('BUSCO.py -m tran --cpu 36 -l ~/busco/eukaryota_odb9 -o busco_spades -i spades/transcripts.fasta > busco.log', read_directories[k])
        call_process('mv busco.log run_busco_spades/', read_directories[k])
        print('Running transrate on SPAdes assembly for read set {} of {}'.format((k + 1), num_read_sets))
        call_process('transrate -o transrate_spades -t 36 -a spades/transcripts.fasta --left {} --right {} > transrate.log'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
        call_process('mv transrate.log transrate_spades/', read_directories[k])

        if use_transfuse:
            print('Merging Trinity & SPAdes assemblies using transfuse for read set {} of {}'.format((k + 1), num_read_sets))
            call_process('transfuse -v -t 36 -i 0.98 -o transfuse.fasta -l {} -r {} -a spades/transcripts.fasta,trinity/Trinity.fasta > transfuse.log'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
            print('Running BUSCO on merged assemblies for read set {} of {}'.format((k + 1), num_read_sets))
            call_process('BUSCO.py -m tran --cpu 36 -l ~/busco/eukaryota_odb9 -o busco_transfuse -i transfuse.fasta > busco.log', read_directories[k])
            call_process('mv busco.log run_busco_transfuse/', read_directories[k])
            print('Running transrate on merged assemblies for read set {} of {}'.format((k + 1), num_read_sets))
            call_process('transrate -o transrate_transfuse -t 36 -a transfuse.fasta --left {} --right {} > transrate.log'.format(assembly_read_files[k][0], assembly_read_files[k][1]), read_directories[k])
            call_process('mv transrate.log transrate_transfuse/', read_directories[k])

        print('')
