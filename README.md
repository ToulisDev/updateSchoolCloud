# Python Script for School Login System
This script logs into a student's account on the school's login system by sending a POST request. Upon successful login, it searches for all registered subjects by finding all table-children HTML tags and provides a download link for every subject.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
To use this script, you need to have Python 3.x installed on your system along with the following packages:

- requests
- webbrowser
- bs4 (BeautifulSoup)
- getpass
- stdiomask
- pandas
- zipfile
- tqdm

You can install the required packages using pip by running the following command:

```sh
pip install -r requirements.txt
```
### Usage
To run the script, navigate to the directory containing the script and run the following command:

```sh
python updateSchoolCloud.py
```
You will be prompted to enter your login credentials. After successfully logging in, the script will search for all registered subjects and provide a download link for every subject.

### Authors
- ToulisDev - [GitHub Profile](https://github.com/ToulisDev)

### License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/ToulisDev/updateSchoolCloud/blob/main/LICENSE) file for details.
