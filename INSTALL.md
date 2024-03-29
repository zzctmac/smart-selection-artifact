# Artifact of Coverage Goal Selector for Combining Multiple Criteria in Search-Based Unit Test Generation

## 0. Prerequisite
To use the following artifact, you need to prepare a Unix-like (e.g., Ubuntu and Mac OS) computer with [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/). A fast way to install these two applications is to install [docker-desktop](https://www.docker.com/products/docker-desktop/), since `docker-desktop` contains both of them.

Note that 
1. Our Python script to analyze the experimental results require many computation costs. If it is feasible, please increase the cpu and memory limit to at least 6 core and 16 GB (more is better) in the Resources Tab of `docker-desktop` Preferences. Also, it requires 20+ GB storage space to store the original experimental data.
2. If you meet errors like `Got permission denied while trying to connect to the Docker daemon...` when running `docker` command, you need to run the command with `sudo`.
3. All the following commands (except for those commands run in the Docker images) need to be run in the base directory of the artifact (i.e., the directory contains this `INSTALL.md`).

## 1. Artifact for Methodology

### Install and Go into the running environment
First, use the following cmd to build the running environment:
```shell
docker build  -f Dockerfile.binary -t smart_selection_binary ./
```

Next, go into this Docker image:
```shell
docker run -it --rm smart_selection_binary /bin/bash
```

### Introduction

In the current folder when you go into the Docker image, you can see `evosuite-ss.jar` using `ls` command. It is the binary file that implements our proposed methodology in Section 3, smart selection. We implement smart selection atop Evosuite, an open-source search-based unit test generator.

We choose a Java class `com.lts.io.DirectoryScanner` to show how to use `evosuite-ss.jar`. `com.lts.io.DirectoryScanner` comes from `caloriecount`, a benchmark project of [SF100](https://www.evosuite.org/experimental-data/sf100/).

Smart selection is integrated into three state-of-the-art SBST (Search-Based Software Testing) algorithms in Evosuite. These algorithms aim to generate test cases for a specific Java class. As mentioned in Section 2.2, they are WS, MOSA, and DynaMOSA.

### Run

You can use the following command to experience smart selection with WS:
```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60 -Dsmart_combine=true -Dsmart_combine_remove_mutant_strategy=SUBSUMPTION -generateSuite -Dalgorithm=MONOTONIC_GA
```
Similarly, you can use the following commands to experience smart selection with MOSA and DynaMOSA one by one:
```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60 -Dsmart_combine=true -Dsmart_combine_remove_mutant_strategy=SUBSUMPTION -Dalgorithm=MOSA
```
```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60 -Dsmart_combine=true -Dsmart_combine_remove_mutant_strategy=SUBSUMPTION -Dalgorithm=DynaMOSA
```
You can see the statistical data using `cat evosuite-report/statistics.csv` command.

You can add `-Dsmart_combine_line_span={Number}` to change the lineThreshold (mentioned in Section 3.4), where `{Number}` should be a non-negative integer number.

Also, one can experience our main baseline, the original combination (mentioned in Section 2.3). It has been implemented in Evosuite.
The command to experience the original combination with WS is:
```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60 -generateSuite -Dalgorithm=MONOTONIC_GA
```
The commands to experience the original combination with MOSA and DynaMOSA are:
```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60  -Dalgorithm=MOSA
```

```shell
java -jar ./evosuite-ss.jar -class com.lts.io.DirectoryScanner -Dsearch_budget=60  -Dalgorithm=DynaMOSA
```

### End
After experiencing, you can enter `exit` to logout from this docker image.

## 2. Artifact for Evaluation Results

### Install the running environment

First, use the following cmd to build the running environment for the experimental result analysis:
```shell
docker build  -f Dockerfile.analysis -t smart_selection_analysis ./
```

### Introduction

The folder [experimental_data](./experimental_data) contains two types of data:
1. data_fo*zip (e.g., [data_fo1.zip](./experimental_data/data_fo1.zip)) : The zipped original data of our experimental results (We split the whole data into six zip files owing to the single-file capacity limit of GitHub).
2. result folders (e.g., [result-folder-rq-1](./experimental_data/result_folder-rq-1)) : The data used in tables and figures in the paper. We have already run our script to analyze and transform the original data to the result data. You can go to [Run Script](#ChapterRunScript) to do the analysis again or directly go to [Result Details](#ChapterDetails) to get more details.

<div id="ChapterRunScript"></div>

### Run Script

To run the script to do the analysis work, firstly, you need to unzip data zip files. For example, you can use the following command (or you can make it on your own):
```shell
unzip 'experimental_data/data_fo*zip' -d ./experimental_data
unzip 'experimental_data/b1*zip' -d ./experimental_data
unzip 'experimental_data/corr-data.zip' -d ./experimental_data
unzip 'experimental_data/efficient-test-data.zip' -d ./experimental_data
unzip 'experimental_data/bugs*zip' -d ./experimental_data
```

After they are unzipped (needs 20-30 minutes), there will be a `data_folder`, `b1`, `corr-data`, and `efficient-test-data` directories in `./experimental_data`. The *./experimental_data/data_folder* contains the results of the experiments of RQ1-3 and RQ6, the *./experimental_data/corr-data* contains the results of the experiments of RQ4, the *./experimental_data/efficient-test-data* contains the results of the experiments of RQ5, the *./experimental_data/b1* contains the results of the experiments of RQ7, and the *./experimental_data/bugs* contains the results of the experiments of RQ8, respectively. Each sub-folder (e.g., [*./experimental_data/data_folder/task-49224*](./experimental_data/data_folder/task-49224)) is the result of a single experiment. A single experiment means that run a specific strategy (e.g., smart selection and other baselines) on a specific Java class. We leverage it as an example to illustrate the result of a single experiment. The *results/sc-suite-sc-release1/o4_hadoop/org_apache_hadoop_thirdparty_com_google_common_collect_Cut/reports* stores the coverage statistical data. *sc-suite-sc-release1* represents the strategy (sc, i.e., smart selection), the algorithm (suite, i.e., Whole Suite Generation), and the jar release version (sc-release1). It includes:

1. Folder 1 to folder 37: Each folder contains *statistics.csv* that stores each time's coverage data. Since SBST is a nondeterministic technique, we repeat $30+7$ times. We only choose the first 30 times' data to be in the experimental analysis. But when we ran experiments, we repeated $37$ times to avoid potential manual involvements due to a few EvoSuite crashes. If there are one or two EvoSuite crashes in $30+7$ repeats, we still can get $30$ success results.
2. *order.csv*: This file is used to cope with one mistake when we wrote the analysis code. When we wrote code to iterate to read each coverage data, we used the `os.listdir` Python API. We assumed that this API returns a sorted file list, which is not true (see https://stackoverflow.com/questions/44532641/order-in-which-files-are-read-using-os-listdir). When we tested the analysis work in several machines, we found this mistake. To let different machines can recurrent the analysis result (used in the paper) of the original machine we used, we record the original file order in this file and added the related adaptations in the analysis code. In the meantime, we found that all *reports* folders share the same content in this file.


General Speaking, our analysis work can be divided into the following steps:
1. Read all the statistical coverage data and cluster it into several groups using algorithms and strategies. Due to the research question design, the groups in different algorithms would not be involved in the following comparison.
2. Use Vargha-Delaney $A_{ab}$ to compare different groups (e.g., smart selection and the original combination) in each algorithm.
3. Calculate each group's average coverage values.
4. Write the comparison results and average coverage values into the CSV files. Furthermore, draw the bar graph for the comparison results.


You only need to use the following command to begin the analysis work:
```shell
docker-compose up -d
```
This command deletes the existing result folders' content and runs four Docker services (with respect to four research questions), which is configured in [docker-compose.yml](./docker-compose.yml). Since the original data is huge, this process needs much time (nearly five hours for a MacBook Pro with Core i7  Quad-core and 16 GB memory). Hence, the above command uses `-d` to let it run in the background.

You can use `docker-compose logs` to view these services' logs and use `docker-compose ps` to check their states (`Up` means working and `Exit` means done).

After it is done, the content of result folders will be shown again.

In case of Docker crashes (it happened once on a Mac when we tested), you can restart docker-desktop (or Docker if you directly use it). Then you can use the following two commands to re-run the analysis work:
```shell
docker-compose rm -f
```
```shell
docker-compose up -d
```
By the way, if Docker crashes, you will get messages such as `502 Server Error for URL: http+docker...` when you type any docker/docker-compose commands.

<div id="ChapterDetails"></div>

### Result Details
We illustrate how the tables and figures in the manuscript come from:

Section 1:

- The data of Figure 1 come from last two rows of [suite_mean_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_big.csv). Note that since we cannot know the total exceptions in a Java class, we normalize the exception coverage (EC) values of two approaches (22.08 vs. 29.74) by dividing by the larger one.
  
Section 4.2:
- Figure 4 (a) is [suite_os.pdf](./experimental_data/result_folder-rq-1/suite_os.pdf). Its data come from [suite_os_detail.csv](./experimental_data/result_folder-rq-1/suite_os_detail.csv).
- Figure 4 (b) is [suite_os_small_classes.pdf](./experimental_data/result_folder-rq-1/suite_os_small_classes.pdf). Its data come from [suite_os_small_classes_detail.csv](./experimental_data/result_folder-rq-1/suite_os_small_classes_detail.csv).
- Figure 4 (c) is [suite_os_big_classes.pdf](./experimental_data/result_folder-rq-1/suite_os_big_classes.pdf). Its data come from [suite_os_big_classes_detail.csv](./experimental_data/result_folder-rq-1/suite_os_big_classes_detail.csv).
- The data of Table 4 (a) come from [suite_mean_overview.csv](./experimental_data/result_folder-rq-1/suite_mean_overview.csv). 
- The data of Table 4 (b) come from [suite_mean_overview_small.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_small.csv). 
- The data of Table 4 (c) come from [suite_mean_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_big.csv).
- The first row of Table 5 comes from [suite_mean_size_overview.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview.csv). The `CC(Average)` in the table is the average number of the latter eight numbers in the csv.
- The second row of Table 5 comes from [suite_mean_size_overview_small.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview_small.csv).
- The third row of Table 5 comes from [suite_mean_size_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview_big.csv).

Section 4.3:
- Figure 5 (a) is [mosa_os.pdf](./experimental_data/result_folder-rq-2/mosa_os.pdf). Its data come from [mosa_os_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_detail.csv).
- Figure 5 (b) is [mosa_os_small_classes.pdf](./experimental_data/result_folder-rq-2/mosa_os_small_classes.pdf). Its data come from [mosa_os_small_classes_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_small_classes_detail.csv).
- Figure 5 (c) is [mosa_os_big_classes.pdf](./experimental_data/result_folder-rq-2/mosa_os_big_classes.pdf). Its data come from [mosa_os_big_classes_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_big_classes_detail.csv).
- The data of Table 6 (a) come from [mosa_mean_overview.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview.csv). 
- The data of Table 6 (b) come from [mosa_mean_overview_small.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview_small.csv). 
- The data of Table 6 (c) come from [mosa_mean_overview_big.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview_big.csv).
- The first row of Table 7 comes from [mosa_mean_size_overview.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview.csv). 
- The second row of Table 7 comes from [mosa_mean_size_overview_small.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview_small.csv).
- The third row of Table 7 comes from [mosa_mean_size_overview_big.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview_big.csv).

Section 4.4:
- Figure 6 (a) is [dynamosa_os.pdf](./experimental_data/result_folder-rq-3/dynamosa_os.pdf). Its data come from [dynamosa_os_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_detail.csv).
- Figure 6 (b) is [dynamosa_os_small_classes.pdf](./experimental_data/result_folder-rq-3/dynamosa_os_small_classes.pdf). Its data come from [dynamosa_os_small_classes_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_small_classes_detail.csv).
- Figure 6 (c) is [dynamosa_os_big_classes.pdf](./experimental_data/result_folder-rq-3/dynamosa_os_big_classes.pdf). Its data come from [dynamosa_os_big_classes_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_big_classes_detail.csv).
- The data of Table 8 (a) come from [dynamosa_mean_overview.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview.csv). 
- The data of Table 8 (b) come from [dynamosa_mean_overview_small.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview_small.csv). 
- The data of Table 8 (c) come from [dynamosa_mean_overview_big.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview_big.csv).
- The first row of Table 9 comes from [dynamosa_mean_size_overview.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview.csv). 
- The second row of Table 9 comes from [dynamosa_mean_size_overview_small.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview_small.csv).
- The third row of Table 9 comes from [dynamosa_mean_size_overview_big.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview_big.csv).

Section 4.5:
- The data of Figure 7 and 8 come from the folder [suite](./experimental_data/result_folder-rq-4/suite). Take the pair (BC, LC) as an example. The sub-figure is [suite/1-branch-line.pdf](./experimental_data/result_folder-rq-4/suite/1-branch-line.pdf). Since the data pairs are too many (1600) to be shown, we sample 20% of the data to create this sub-figure. As a result, it may be slightly different in multiple runs. Its Pearson value is in [suite/1-branch-line-pearson.csv](./experimental_data/result_folder-rq-4/suite/1-branch-line-pearson.csv). The Pearson value is generated with the whole data.
- The data of Figure 9 and 10 come from  the folder [mosa](./experimental_data/result_folder-rq-4/mosa).


Section 4.6:
- Figure 11 (a) is [suite_lc_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/suite_lc_tmc_ec_oc_group.pdf). Its data come from [suite_lc_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/suite_lc_tmc_ec_oc_group_detail.csv).
- Figure 11 (b) is [mosa_lc_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/mosa_lc_tmc_ec_oc_group.pdf). Its data come from [mosa_lc_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/mosa_lc_tmc_ec_oc_group_detail.csv).
- Figure 11 (c) is [dynamosa_lc_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/dynamosa_lc_tmc_ec_oc_group.pdf). Its data come from [dynamosa_lc_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/dynamosa_lc_tmc_ec_oc_group_detail.csv).
- Figure 12 (a) is [suite_wm_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/suite_wm_tmc_ec_oc_group.pdf). Its data come from [suite_wm_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/suite_wm_tmc_ec_oc_group_detail.csv).
- Figure 12 (b) is [mosa_wm_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/mosa_wm_tmc_ec_oc_group.pdf). Its data come from [mosa_wm_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/mosa_wm_tmc_ec_oc_group_detail.csv).
- Figure 12 (c) is [dynamosa_wm_tmc_ec_oc_group.pdf](./experimental_data/result_folder-rq-5/dynamosa_wm_tmc_ec_oc_group.pdf). Its data come from [dynamosa_wm_tmc_ec_oc_group_detail.csv](./experimental_data/result_folder-rq-5/dynamosa_wm_tmc_ec_oc_group_detail.csv).

- The data of Table 10 (a) come from [group_suite_lc_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_suite_lc_tmc_ec_oc_mean_overview.csv) and [group_suite_wm_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_suite_wm_tmc_ec_oc_mean_overview.csv). The `Suite Size` comes from [group_suite_lc_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_suite_lc_tmc_ec_oc_mean_size_overview.csv) and [group_suite_wm_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_suite_wm_tmc_ec_oc_mean_size_overview.csv).
- The data of Table 10 (b) come from [group_mosa_lc_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_mosa_lc_tmc_ec_oc_mean_overview.csv) and [group_mosa_wm_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_mosa_wm_tmc_ec_oc_mean_overview.csv). The `mosa Size` comes from [group_mosa_lc_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_mosa_lc_tmc_ec_oc_mean_size_overview.csv) and [group_mosa_wm_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_mosa_wm_tmc_ec_oc_mean_size_overview.csv).
- The data of Table 10 (c) come from [group_dynamosa_lc_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_dynamosa_lc_tmc_ec_oc_mean_overview.csv) and [group_dynamosa_wm_tmc_ec_oc_mean_overview.csv](./experimental_data/result_folder-rq-5/group_dynamosa_wm_tmc_ec_oc_mean_overview.csv). The `dynamosa Size` comes from [group_dynamosa_lc_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_dynamosa_lc_tmc_ec_oc_mean_size_overview.csv) and [group_dynamosa_wm_tmc_ec_oc_mean_size_overview.csv](./experimental_data/result_folder-rq-5/group_dynamosa_wm_tmc_ec_oc_mean_size_overview.csv).

Section 4.7:
- Figure 13 (a) is [suite_rs.pdf](./experimental_data/result_folder-rq-6/suite_rs.pdf). Its data come from [suite_rs_detail.csv](./experimental_data/result_folder-rq-6/suite_rs_detail.csv).
- Figure 13 (b) is [mosa_rs.pdf](./experimental_data/result_folder-rq-6/mosa_rs.pdf). Its data come from [mosa_rs_detail.csv](./experimental_data/result_folder-rq-6/mosa_rs_detail.csv).
- Figure 13 (c) is [dynamosa_rs.pdf](./experimental_data/result_folder-rq-6/dynamosa_rs.pdf). Its data come from [dynamosa_rs_detail.csv](./experimental_data/result_folder-rq-6/dynamosa_rs_detail.csv).
- The data of Table 11 (a) come from [sub_suite_mean_overview.csv](./experimental_data/result_folder-rq-6/sub_suite_mean_overview.csv). The `Suite Size` comes from [sub_suite_mean_size_overview.csv](./experimental_data/result_folder-rq-6/sub_suite_mean_size_overview.csv).
- The data of Table 11 (b) come from [sub_mosa_mean_overview.csv](./experimental_data/result_folder-rq-6/sub_mosa_mean_overview.csv). The `Suite Size` comes from [sub_mosa_mean_size_overview.csv](./experimental_data/result_folder-rq-6/sub_mosa_mean_size_overview.csv).
- The data of Table 11 (c) come from [sub_dynamosa_mean_overview.csv](./experimental_data/result_folder-rq-6/sub_dynamosa_mean_overview.csv). The `Suite Size` comes from [sub_dynamosa_mean_size_overview.csv](./experimental_data/result_folder-rq-6/sub_dynamosa_mean_size_overview.csv).

Section 4.8:
- Figure 14's data collect from [suite_mean_overview.csv (2 min)](./experimental_data/result_folder-rq-1/suite_mean_overview.csv), [suite_budget_mean_5.csv](./experimental_data/result_folder-rq-1/suite_budget_mean_5.csv), [suite_budget_mean_8.csv](./experimental_data/result_folder-rq-1/suite_budget_mean_8.csv), and [suite_budget_mean_10.csv](./experimental_data/result_folder-rq-1/suite_budget_mean_10.csv).
- Figure 15's data collect from [mosa_mean_overview.csv (2 min)](./experimental_data/result_folder-rq-2/mosa_mean_overview.csv), [mosa_budget_mean_5.csv](./experimental_data/result_folder-rq-2/mosa_budget_mean_5.csv), [mosa_budget_mean_8.csv](./experimental_data/result_folder-rq-2/mosa_budget_mean_8.csv), and [mosa_budget_mean_10.csv](./experimental_data/result_folder-rq-2/mosa_budget_mean_10.csv).
- Figure 16's data collect from [dynamosa_mean_overview.csv (2 min)](./experimental_data/result_folder-rq-3/dynamosa_mean_overview.csv), [dynamosa_budget_mean_5.csv](./experimental_data/result_folder-rq-3/dynamosa_budget_mean_5.csv), [dynamosa_budget_mean_8.csv](./experimental_data/result_folder-rq-3/dynamosa_budget_mean_8.csv), and [dynamosa_budget_mean_10.csv](./experimental_data/result_folder-rq-3/dynamosa_budget_mean_10.csv).

Section 4.9:
- The data of Figure 17 and Table 12-14 collect from [result_folder-rq-8](./experimental_data/result_folder-rq-8)