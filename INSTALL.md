# Artifact of Selectively Combining Multiple Coverage Goals in Search-Based Unit Test Generation

## 0. Prerequisite
To use the following artifact, you need to prepare a Unix-like computer with [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/). A fast way to install these two applications is to install [docker-desktop](https://www.docker.com/products/docker-desktop/), since `docker-desktop` contains both of them.

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

