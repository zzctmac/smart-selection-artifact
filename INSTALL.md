# Artifact of Selectively Combining Multiple Coverage Goals in Search-Based Unit Test Generation

## 0. Prerequisite
To use the following artifact, you need to prepare a Unix-like (e.g., Ubuntu and Mac OS) computer with [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/). A fast way to install these two applications is to install [docker-desktop](https://www.docker.com/products/docker-desktop/), since `docker-desktop` contains both of them.

Note that 
1. Our Python script to analyze the experimental results require many computation costs. If it is feasible, please increase the cpu and memory limit to at least 4 core/GB (more is better) in the Resources Tab of `docker-desktop` Preferences.
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

To run the script to do the analysis work, firstly, you need to unzip six zip files. For example, you can use the following command (or you can make it on your own):
```shell
unzip 'experimental_data/data_fo*zip' -d ./experimental_data
```

After they are unzipped, there will be a `data_folder` directory in `./experimental_data`. Then, you only need to use the following command to begin the analysis work:
```shell
docker-compose up -d
```
This command deletes the existing result folders' content and runs four Docker services (with respect to four research questions), which is configured in [docker-compose.yml](./docker-compose.yml). Since the original data is huge, this process needs much time (nearly three hours and a half for a MacBook Pro with Core i7  Quad-core and 16 GB memory). Hence, the above command uses `-d` to let it run in the background.

You can use `docker-compose logs` to view these services' logs and use `docker-compose ps` to check their states (`Up` means working and `Exit` means done).

After it is done, the content of result folders will be shown again.

<div id="ChapterDetails"></div>

### Result Details
We illustrate how the tables and figures in [the paper](./paper.pdf) come from:

Section 1:

- The data of Figure 1 comes from last two rows of [suite_mean_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_big.csv). Note that since we cannot know the total exceptions in a Java class, we normalize the exception coverage (EC) values of two approaches (22.08 vs. 29.74) by dividing by the larger one.
  
Section 4.2:
- Figure 4 (a) is [suite_os.pdf](./experimental_data/result_folder-rq-1/suite_os.pdf). Its data comes from [suite_os_detail.csv](./experimental_data/result_folder-rq-1/suite_os_detail.csv).
- Figure 4 (b) is [suite_os_small_classes.pdf](./experimental_data/result_folder-rq-1/suite_os_small_classes.pdf). Its data comes from [suite_os_small_classes_detail.csv](./experimental_data/result_folder-rq-1/suite_os_small_classes_detail.csv).
- Figure 4 (c) is [suite_os_big_classes.pdf](./experimental_data/result_folder-rq-1/suite_os_big_classes.pdf). Its data comes from [suite_os_big_classes_detail.csv](./experimental_data/result_folder-rq-1/suite_os_big_classes_detail.csv).
- The data of Table 2 (a) comes from [suite_mean_overview.csv](./experimental_data/result_folder-rq-1/suite_mean_overview.csv). 
- The data of Table 2 (b) comes from [suite_mean_overview_small.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_small.csv). 
- The data of Table 2 (c) comes from [suite_mean_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_overview_big.csv).
- The first row of Table 3 (a) comes from [suite_mean_size_overview.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview.csv). The `CC(Average)` in the table is the average number of the latter eight numbers in the csv.
- The second row of Table 3 (b) comes from [suite_mean_size_overview_small.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview_small.csv).
- The third row of Table 3 (c) comes from [suite_mean_size_overview_big.csv](./experimental_data/result_folder-rq-1/suite_mean_size_overview_big.csv).

Section 4.3:
- Figure 5 (a) is [mosa_os.pdf](./experimental_data/result_folder-rq-2/mosa_os.pdf). Its data comes from [mosa_os_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_detail.csv).
- Figure 5 (b) is [mosa_os_small_classes.pdf](./experimental_data/result_folder-rq-2/mosa_os_small_classes.pdf). Its data comes from [mosa_os_small_classes_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_small_classes_detail.csv).
- Figure 5 (c) is [mosa_os_big_classes.pdf](./experimental_data/result_folder-rq-2/mosa_os_big_classes.pdf). Its data comes from [mosa_os_big_classes_detail.csv](./experimental_data/result_folder-rq-2/mosa_os_big_classes_detail.csv).
- The data of Table 4 (a) comes from [mosa_mean_overview.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview.csv). 
- The data of Table 4 (b) comes from [mosa_mean_overview_small.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview_small.csv). 
- The data of Table 4 (c) comes from [mosa_mean_overview_big.csv](./experimental_data/result_folder-rq-2/mosa_mean_overview_big.csv).
- The first row of Table 5 (a) comes from [mosa_mean_size_overview.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview.csv). 
- The second row of Table 5 (b) comes from [mosa_mean_size_overview_small.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview_small.csv).
- The third row of Table 5 (c) comes from [mosa_mean_size_overview_big.csv](./experimental_data/result_folder-rq-2/mosa_mean_size_overview_big.csv).

Section 4.4:
- Figure 6 (a) is [dynamosa_os.pdf](./experimental_data/result_folder-rq-3/dynamosa_os.pdf). Its data comes from [dynamosa_os_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_detail.csv).
- Figure 6 (b) is [dynamosa_os_small_classes.pdf](./experimental_data/result_folder-rq-3/dynamosa_os_small_classes.pdf). Its data comes from [dynamosa_os_small_classes_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_small_classes_detail.csv).
- Figure 6 (c) is [dynamosa_os_big_classes.pdf](./experimental_data/result_folder-rq-3/dynamosa_os_big_classes.pdf). Its data comes from [dynamosa_os_big_classes_detail.csv](./experimental_data/result_folder-rq-3/dynamosa_os_big_classes_detail.csv).
- The data of Table 6 (a) comes from [dynamosa_mean_overview.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview.csv). 
- The data of Table 6 (b) comes from [dynamosa_mean_overview_small.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview_small.csv). 
- The data of Table 6 (c) comes from [dynamosa_mean_overview_big.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_overview_big.csv).
- The first row of Table 7 (a) comes from [dynamosa_mean_size_overview.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview.csv). 
- The second row of Table 7 (b) comes from [dynamosa_mean_size_overview_small.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview_small.csv).
- The third row of Table 7 (c) comes from [dynamosa_mean_size_overview_big.csv](./experimental_data/result_folder-rq-3/dynamosa_mean_size_overview_big.csv).

Section 4.5:
- Figure 7 (a) is [suite_rs.pdf](./experimental_data/result_folder-rq-4/suite_rs.pdf). Its data comes from [suite_rs_detail.csv](./experimental_data/result_folder-rq-4/suite_rs_detail.csv).
- Figure 7 (b) is [mosa_rs.pdf](./experimental_data/result_folder-rq-4/mosa_rs.pdf). Its data comes from [mosa_rs_detail.csv](./experimental_data/result_folder-rq-4/mosa_rs_detail.csv).
- Figure 7 (c) is [dynamosa_rs.pdf](./experimental_data/result_folder-rq-4/dynamosa_rs.pdf). Its data comes from [dynamosa_rs_detail.csv](./experimental_data/result_folder-rq-4/dynamosa_rs_detail.csv).
- The data of Table 8 (a) comes from [sub_suite_mean_overview.csv](./experimental_data/result_folder-rq-4/sub_suite_mean_overview.csv). The `Suite Size` comes from [sub_suite_mean_size_overview.csv](./experimental_data/result_folder-rq-4/sub_suite_mean_size_overview.csv).
- The data of Table 8 (b) comes from [sub_mosa_mean_overview.csv](./experimental_data/result_folder-rq-4/sub_mosa_mean_overview.csv). The `Suite Size` comes from [sub_mosa_mean_size_overview.csv](./experimental_data/result_folder-rq-4/sub_mosa_mean_size_overview.csv).
- The data of Table 8 (c) comes from [sub_dynamosa_mean_overview.csv](./experimental_data/result_folder-rq-4/sub_dynamosa_mean_overview.csv). The `Suite Size` comes from [sub_dynamosa_mean_size_overview.csv](./experimental_data/result_folder-rq-4/sub_dynamosa_mean_size_overview.csv).