# How To Open Science: A Principle and Reproducibility Review of the Learning Analytics and Knowledge Conference

[![OSF DOI](https://img.shields.io/badge/OSF-10.17605%2Fosf.io%2F74bzs-blue)][doi]
[![Docker](https://img.shields.io/docker/automated/ahaim5357/10.17605-osf.io-74bzs)][container]

[*How To Open Science: A Principle and Reproducibility Review of the Learning Analytics and Knowledge Conference*][doi] is a project that conducts a peer review of full papers, short papers, and posters submitted to the 11th and 12th *International Conference on Learning Analytics* to analyze which Open Science principles and their subfields are met. Additionally, a reproducibility metric is performed to verify whether the numbers in the associated paper can be reproduced.

This project contains the preregistration and associated updates, the [Qualtrics][qualtrics] survey used, and the raw dataset. This project additionally provides a Python script, with an associated Docker container, to compile the raw dataset into a proper CSV format rather than the one Qualtrics uses.

## License

The content of this Open Science Foundation project is licensed under a [Creative Commons Attribute 4.0 International License][cl]. The data is also licensed as such as recommended by [Creative Commons][ccdata].

The software of this Open Science Foundation project is licensed under the [MIT License][sl]. This is to prevent distribution issues when using the source in other projects. You can read more about this [here][ccsoftware].

## Rebuttal

Each row in the provided dataset contains an associated explanation in a document that defends the reasoning behind the choices in the survey. Authors may choose to refute or update the status of their particular paper in relation to the defined Open Science Principles, Reproducibility, or relinking dead references in the [dynamic document][expdyn].

## Compiler Script

### Method 1: Docker

The [Docker Container][container] can be run using:

```bash
docker run -v ${PWD}:/app/data ahaim5357/10.17605-osf.io-74bzs:lak2023
```

You can also clone this repository, then run the following [Docker][docker] commands:

```bash
docker build -t <image_name> .
docker run -v ${PWD}:/app/data <image_name>
```

Where `image_name` can be specified to whatever identifier the user desires.

This will automatically download the compiled dataset, dataset documentation, explanations associated with each dataset, and the content/dataset license.

#### Environment Variables

There are two environment variables:

* `74BZS_RAW_DATASET` (default false): When true, will download the raw dataset onto the local machine if it's not already present. The dataset will be pulled regardless for compilation.
* `74BZS_DOCS` (default true): When true, will download the dataset documentation, explanations associated with each dataset, and the content/dataset license.

These can be added to the docker script via `-e <ENV_VAR>=<VALUE>`:

```bash
# Download the raw dataset but not the docs to the local machine
docker run -v ${PWD}:/app/data -e 74BZS_RAW_DATASET=true -e 74BZS_DOCS=false <image_name>
```

### Method 2: Python Environment

The compiler script is written in Python 3.9.5. You can install the required libraries using the `requirements.txt` provided:

```bash
pip install -r requirements.txt
```

> You may need to prefix the `pip` command with either `python -m` for Unix systems or `py -m` for Windows systems if `pip` was not properly installed onto the path.

Then navigate to the folder in your terminal and run `qualtrics_data_compiler.py`.

For Unix Systems (Linux, MacOS):

```bash
python3 ./qualtrics_data_compiler.py
```

For Windows Systems:

```pwsh
py ./qualtrics_data_compiler.py
```

#### Command Line Arguments

There are three command line arguments that can be specified after the script:

* `-h`/`--help`: Prints the command and what arguments it can take.
* `-r`/`--raw-dataset`: Downloads the raw dataset onto the local machine if it's not already present.
* `-n`/`--no-docs`: Will not download the supplemental documents with the compiled dataset.

For Unix Systems (Linux, MacOS):

```bash
# Download the raw dataset but not the docs to the local machine
python3 ./qualtrics_data_compiler.py -r -n
```

For Windows Systems:

```pwsh
# Download the raw dataset but not the docs to the local machine
py ./qualtrics_data_compiler.py -r -n
```

## Citation

```
@misc{Haim_Shaw_Heffernan_2022,
  title={LAK Peer Review of Open Science and Reproducibility},
  url={osf.io/74bzs},
  DOI={10.17605/OSF.IO/74BZS},
  publisher={OSF},
  author={Haim, Aaron and Shaw, Stacy T and Heffernan, Neil T, III},
  year={2022},
  month={Sep}
}
```


[qualtrics]: https://www.qualtrics.com/
[cl]: https://osf.io/4xhm9
[ccdata]: https://creativecommons.org/about/program-areas/open-data/
[sl]: ./LICENSE
[ccsoftware]: https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software
[expdyn]: https://docs.google.com/document/d/11ActHWD2EkAWm2olSWBUCf4VOV79Sh0YBp2d4vpEidQ/edit?usp=sharing
[container]: https://hub.docker.com/repository/docker/ahaim5357/10.17605-osf.io-74bzs
[docker]: https://www.docker.com/
[doi]: https://doi.org/10.17605/osf.io/74bzs
