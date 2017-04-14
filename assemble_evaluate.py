from subprocess import Popen, PIPE


def call_process(command, new_dir=None):
    p = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, cwd=new_dir)
    stdout, stderr = p.communicate()
    stdout = stdout.decode()
    return stdout


if __name__ == '__main__':
    # Trinity commands
    call_process('mkdir trinity_assembly')
    call_process('Trinity --seqType fq --max_memory 100G --CPU 24 --output trinity_assembly --no_normalize_reads --full_cleanup --left subsamp-skewer-trimmed-pair1.fastq --right subsamp-skewer-trimmed-pair2.fastq > trinity.log')
    call_process('mv trinity_assembly.Trinity.fasta trinity.fasta')
    call_process('mv trinity.fasta trinity_assembly/')
    call_process('mv trinity.log trinity_assembly/')

    # BUSCO commands (for Trinity assembly)
    call_process('BUSCO.py -m tran --cpu 24 -l ~/busco/eukaryota_odb9 -o trinity -i trinity_assembly/trinity.fasta > busco.log')
    call_process('mv run_trinity trinity_busco')
    call_process('mv busco.log trinity_busco/')

    # TransRate commands (for Trinity assembly)
    call_process('transrate -o trinity_transrate -t 24 -a trinity_assembly/trinity.fasta --left subsamp-skewer-trimmed-pair1.fastq --right subsamp-skewer-trimmed-pair2.fastq > transrate.log')
    call_process('mv transrate.log trinity_transrate/')

    # SPAdes commands
    call_process('spades.py --rna --only-assembler --threads 24 --memory 100 -1 subsamp-skewer-trimmed-pair1.fastq -2 subsamp-skewer-trimmed-pair2.fastq -o spades_assembly')
    call_process('mv transcripts.fasta spades.fasta', 'spades_assembly/')

    # BUSCO commands (for SPAdes assembly)
    call_process('BUSCO.py -m tran --cpu 24 -l ~/busco/eukaryota_odb9 -o spades -i spades_assembly/spades.fasta > busco.log')
    call_process('mv run_spades spades_busco')
    call_process('mv busco.log spades_busco/')

    # TransRate commands (for SPAdes assembly)
    call_process('transrate -o spades_transrate -t 24 -a spades_assembly/spades.fasta --left subsamp-skewer-trimmed-pair1.fastq --right subsamp-skewer-trimmed-pair2.fastq > transrate.log')
    call_process('mv transrate.log spades_transrate/')
