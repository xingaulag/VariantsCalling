#Trimmomatic for cutting down low quality bases
$ for sp in {1..100}; do
> java -jar trimmomatic-0.39.jar PE -threads 8 -phred33 -trimlog log.txt
/home/thanh/Desktop/gatk/work/sample/100KHV/VT${sp}_R1.fastq.gz
/home/thanh/Desktop/gatk/work/sample/100KHV/VT${sp}_R2.fastq.gz
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_paired_1.fastq.gz
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_unpaired_1.fastq.gz
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_paired_2.fastq.gz
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_unpaired_2.fastq.gz
ILLUMINACLIP:adapters/TruSeq3-PE-2.fa:2:30:3:1:true LEADING:20 TRAILING:20 SLIDINGWINDOW:3:15 AVGQUAL:20 MINLEN:100;
> done


# Mapping to hg38  for
$ for sp in {1..100}; do
> bwa mem -t 4 -M -R "@RG\tID:100PGx\tSM:VT$"{sp}"\tPL:illumina\tLB:lib1\tPU:unit1"
/home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta #ref form GATK resource bundle
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_paired_1.fastq.gz
/home/thanh/Desktop/gatk/work/QC/VT${sp}_QC_paired_2.fastq.gz |samtools view -bS -o /home/thanh/Desktop/gatk/work/map38/VT${sp}_map.bam;
> done

#Markduplicate by picard
$ java -jar picard.jar MarkDuplicates
I=/home/thanh/Desktop/gatk/work/map38/VT${sp}_map.bam
O=/home/thanh/Desktop/gatk/work/dup38/VT${sp}_marked.bam
M=/home/thanh/Desktop/gatk/work/dup38/Dup${sp}.txt ASO=queryname #assume sorting order query name

$ java -jar picard.jar SortSam
I=/home/thanh/Desktop/gatk/work/dup38/VT${sp}_marked.bam
O=/home/thanh/Desktop/gatk/work/dup38/VT${sp}_sorted.bam SORT_ORDER=coordinate #required for next step

#Base Recalibration by gatk4
$ gatk BaseRecalibrator
-I /home/thanh/Desktop/gatk/work/dup38/VT${sp}_sorted.bam
-R /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta
--known-sites /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.dbsnp138.vcf
-O /home/thanh/Desktop/gatk/work/nm.recal38/VT${sp}_data.table

$ gatk ApplyBQSR
-R /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta
-I /home/thanh/Desktop/gatk/work/dup38/VT${sp}_sorted.bam
--bqsr-recal-file /home/thanh/Desktop/gatk/work/s.recal38/VT${sp}_data.table
-O /home/thanh/Desktop/gatk/work/s.recal38/reVT${sp}.bam

#Variants calling (Haplotypecaller) (note: require minimun 8G for running)
#GVCF
$ java -jar -Xmx2g /home/thanh/Desktop/gatk/work/gatk/gatk-package-4.1.4.1-local.jar HaplotypeCaller
-R /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta
-I /home/thanh/Desktop/gatk/work/s.recal38/rdVT${sp}.bam
-L /home/thanh/Desktop/gatk/work/CDS100genes.list.bed #capturekit as bad format
-O /home/thanh/Desktop/gatk/work/vcf38/VT${sp}.g.vcf.gz -ERC GVCF

#SNPs (for running pharmcat)
$ java -jar -Xmx2g /home/thanh/Desktop/gatk/work/gatk/gatk-package-4.1.4.1-local.jar HaplotypeCaller
-R /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta
-I /home/thanh/Desktop/gatk/work/s.recal38/rdVT${sp}.bam
-L /home/thanh/Desktop/gatk/work/CDS100genes.list.bed #replace this capture kit to one form pharmcat
-O /home/thanh/Desktop/gatk/work/vcf38/VT${sp}.vcf.gz -output-mode EMIT_ALL_ACTIVE_SITES

$ java -jar -Xmx2g /home/thanh/Desktop/gatk/work/gatk/gatk-package-4.1.4.1-local.jar HaplotypeCaller -R /home/thanh/Desktop/gatk/work/refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta -I /home/thanh/Desktop/gatk/work/s.recal38/rdVT1.bam -L /home/thanh/Desktop/gatk/work/pgx.interval.file.list -O /home/thanh/Desktop/gatk/work/vcf38/testpc.VT1.vcf.gz --output-mode EMIT_ALL_ACTIVE_SITES

#Joint Cohort
#consolidate gVCF (prepare for faster joint cohort)
$ java -jar -Xmx2g /home/thanh/Desktop/gatk/work/gatk/gatk-package-4.1.4.1-local.jar GenomicsDBImport
-V vcf38/VT1.vcf.gz  -V vcf38/VT2.g.vcf.gz -V vcf38/VT3.g.vcf.gz -V vcf38/VT4.g.vcf.gz -V vcf38/VT5.g.vcf.gz -V vcf38/VT6.g.vcf.gz -V vcf38/VT7.g.vcf.gz -V vcf38/VT8.g.vcf.gz -V vcf38/VT9.g.vcf.gz -V vcf38/VT10.g.vcf.gz -V vcf38/VT11.g.vcf.gz  -V vcf38/VT12.g.vcf.gz -V vcf38/VT13.g.vcf.gz -V vcf38/VT14.g.vcf.gz -V vcf38/VT15.g.vcf.gz -V vcf38/VT16.g.vcf.gz -V vcf38/VT17.g.vcf.gz -V vcf38/VT18.g.vcf.gz -V vcf38/VT19.g.vcf.gz -V vcf38/VT20.g.vcf.gz -V vcf38/VT21.g.vcf.gz  -V vcf38/VT22.g.vcf.gz -V vcf38/VT23.g.vcf.gz -V vcf38/VT24.g.vcf.gz -V vcf38/VT25.g.vcf.gz -V vcf38/VT26.g.vcf.gz -V vcf38/VT27.g.vcf.gz -V vcf38/VT28.g.vcf.gz -V vcf38/VT29.g.vcf.gz -V vcf38/VT30.g.vcf.gz -V vcf38/VT31.g.vcf.gz  -V vcf38/VT32.g.vcf.gz -V vcf38/VT33.vcf.gz -V vcf38/VT34.vcf.gz -V vcf38/VT35.g.vcf.gz -V vcf38/VT36.g.vcf.gz -V vcf38/VT37.g.vcf.gz -V vcf38/VT38.g.vcf.gz -V vcf38/VT39.g.vcf.gz -V vcf38/VT40.g.vcf.gz -V vcf38/VT41.g.vcf.gz  -V vcf38/VT42.g.vcf.gz -V vcf38/VT43.g.vcf.gz -V vcf38/VT44.g.vcf.gz -V vcf38/VT45.g.vcf.gz -V vcf38/VT46.g.vcf.gz -V vcf38/VT47.g.vcf.gz -V vcf38/VT48.g.vcf.gz -V vcf38/VT49.g.vcf.gz -V vcf38/VT50.g.vcf.gz -V vcf38/VT51.g.vcf.gz  -V vcf38/VT52.g.vcf.gz -V vcf38/VT53.g.vcf.gz -V vcf38/VT55.g.vcf.gz -V vcf38/VT56.g.vcf.gz -V vcf38/VT57.g.vcf.gz -V vcf38/VT58.g.vcf.gz -V vcf38/VT59.g.vcf.gz -V vcf38/VT60.g.vcf.gz -V vcf38/VT61.vcf.gz  -V vcf38/VT62.g.vcf.gz -V vcf38/VT63.g.vcf.gz -V vcf38/VT64.g.vcf.gz -V vcf38/VT65.g.vcf.gz -V vcf38/VT66.g.vcf.gz -V vcf38/VT67.g.vcf.gz -V vcf38/VT68.g.vcf.gz -V vcf38/VT69.g.vcf.gz -V vcf38/VT70.g.vcf.gz -V vcf38/VT71.g.vcf.gz  -V vcf38/VT72.g.vcf.gz -V vcf38/VT73.g.vcf.gz -V vcf38/VT74.g.vcf.gz -V vcf38/VT75.g.vcf.gz -V vcf38/VT76.g.vcf.gz -V vcf38/VT77.g.vcf.gz -V vcf38/VT78.g.vcf.gz -V vcf38/VT79.g.vcf.gz -V vcf38/VT80.g.vcf.gz -V vcf38/VT81.g.vcf.gz -V vcf38/VT82.g.vcf.gz -V vcf38/VT83.g.vcf.gz -V vcf38/VT84.g.vcf.gz -V vcf38/VT85.g.vcf.gz -V vcf38/VT86.g.vcf.gz -V vcf38/VT87.g.vcf.gz -V vcf38/VT88.g.vcf.gz -V vcf38/VT89.g.vcf.gz -V vcf38/VT90.g.vcf.gz -V vcf38/VT91.g.vcf.gz  -V vcf38/VT92.g.vcf.gz -V vcf38/VT93.g.vcf.gz -V vcf38/VT94.g.vcf.gz -V vcf38/VT95.g.vcf.gz -V vcf38/VT96.g.vcf.gz -V vcf38/VT97.g.vcf.gz -V vcf38/VT98.g.vcf.gz -V vcf38/VT99.g.vcf.gz -V vcf38/VT100.g.vcf.gz -V vcf38/VT54.g.vcf.gz
--genomicsdb-workspace-path consolidate38
-L CDS100genes.list.bed #capture kit

$ java -jar gatk/gatk-package-4.1.4.1-local.jar GenotypeGVCFs
-R refgen/resources-broad-hg38-v0-Homo_sapiens_assembly38.fasta
-V gendb://consolidate38 #workspace from previous step
-O 100KHV.vcf

####Got error in this fucking step -_-
Em gởi mng slides e sẽ nói cuối tuần này. Em đang làm Variants Calling follow GATK best practice. Với em có chạy 1 số tools variants annotation.
