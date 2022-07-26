# Artifact of Selectively Combining Multiple Coverage Goals in Search-Based Unit Test Generation

## 0. Prerequisite
To use the following artifact, you need to prepare a Unix-like (e.g., Ubuntu and Mac OS) computer with [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/). A fast way to install these two applications is to install [docker-desktop](https://www.docker.com/products/docker-desktop/), since `docker-desktop` contains both of them.

Note that our Python script to analyze the experimental results require lots of memory. If it is feasible, please increase the memory limit to at least 8 GB (more is better) in the Resources Tab of `docker-desktop` Preferences.

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
1. [data_folder](./experimental_data/data_folder) : The original data of our experimental results.
2. result folders (e.g., [result-folder-rq-1](./experimental_data/result_folder-rq-1)) : The data used in tables and figures in the paper. We have already run our script to analyze and transform the original data to the result data. You can go to [Run Script](#Run Script) to do the analysis again or directly go to [Result Details](#Result Details) to get more details.

### Run Script

To run script to do the analysis work, you only need to use the following command:
```shell
docker-compose up -d
```
This command deletes the existing result folders' content and runs four Docker services (with respect to four research questions), which is configured in [docker-compose.yml](./docker-compose.yml). Since the original data is huge, this process needs much time (nearly three hours and a half for a MacBook Pro with Core i7  Quad-core and 16 GB memory). Hence, the above command uses `-d` to let it run in the background.

You can use `docker-compose logs` to view these services' logs and use `docker-compose ps` to check their states (`Up` means working and `Exit` means done).

After it is done, the content of result folders will be shown again.

### Result Details