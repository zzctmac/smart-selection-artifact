from setuptools import setup, find_packages

setup(
    name="sc",
    packages=find_packages("src"),
    package_dir={'': 'src'},
    scripts=['bin/ec', 'bin/sc_overview', "bin/ss_analysis", "bin/sr_overview", "bin/smart_selection_analysis"
             , "bin/smart_size_show", "bin/ss_group_overview", "bin/correlation_analysis",
             "bin/bug_analysis"],
    package_data={
        "sc": ["share/data/artifacts/*.csv"],
    },
)
