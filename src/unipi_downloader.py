#Imported Libraries
try:
    import sys,os
    import requests, webbrowser
    import errno, stat, shutil, re
    from bs4 import BeautifulSoup
    from getpass import getpass
    import stdiomask
    import pandas
    import zipfile
    from tqdm import tqdm
except ImportError as e:
    print("Error: Failed to import module {}".format(e.name))
    print("Please make sure that the module is installed and try again.")
    input("Press Enter key to continue . . .")
    sys.exit(1)

with requests.Session() as s:
    
    url = ''
    
    def initializeConnection():
        originalSite = 'https://aristarchus.ds.unipi.gr/'
        responseSite = s.get(originalSite+'modules/auth/cas.php')
        global url 
        url = str(responseSite.url)
        login()
    
    def login():
        USERNAME = input('Username: ')
        PASSWORD = stdiomask.getpass()

        response = s.get(url)
        content = str(response.content)

        ###Getting Params###

        soup = BeautifulSoup(content, 'html.parser')
        exSoup = soup.find('input',{'name':'execution'}).get('value')
        idSoup = soup.find('input',{'name':'_eventId'}).get('value')
        
        EXECUTION =  exSoup
        ID = idSoup

        ####################
        
        
        login_headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="97", "Google Chrome";v="97"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://sso.unipi.gr',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': url,
        'Accept-Language': 'el-GR,el;q=0.9,en;q=0.8'
    }
        payload = {'username':USERNAME, 
                    'password':PASSWORD,
                    'execution':EXECUTION,
                    '_eventId':ID}
        print("Trying to Connect...")
        response = s.post(url, data=payload, headers = login_headers)
        searchText = 'alert alert-danger'
        strContentOfRe = response.text
        
        if searchText in strContentOfRe:
            print('Check your credentials and try again!\n')
            login()
        else:
            print('Login successful!\n')
            findAllSubjects()



    def findAllSubjects():
        mySubjectsPage = s.get('https://aristarchus.ds.unipi.gr/main/my_courses.php')
        pd = pandas.read_html(mySubjectsPage.text)
        df = pd[0]
        listdf = df.iloc[:,0].values.tolist()

        #Listing every Subject name and Subject Code
        listOfSubjects = []
        listOfSubjectsCode = []
        listOfSubjectQuarter = []
        for x in range(len(listdf)):
            selString = listdf[x]
            findingCharInd = selString.index(']')
            findingLastInd = selString.rfind('(')
            startInd = findingCharInd + 15
            endInd = findingLastInd - 1
            strSubject = selString[startInd:endInd]
            listOfSubjects.append(strSubject)

            endCodeInd = selString.rfind(')')
            startCodeInd = endCodeInd - 3
            strCode = selString[startCodeInd:endCodeInd]
            listOfSubjectsCode.append(strCode)

            endQuartInd = selString.index(']')
            strQuarter = selString[:endQuartInd]
            ###Check what quarter is the subject and add the quarter number to List
            if "Α" in strQuarter or "A" in strQuarter:
                listOfSubjectQuarter.append("1")
            elif "Β" in strQuarter:
                listOfSubjectQuarter.append("2")
            elif "Γ" in strQuarter:
                listOfSubjectQuarter.append("3")
            elif "Δ" in strQuarter:
                listOfSubjectQuarter.append("4")
            elif "Ε" in strQuarter:
                listOfSubjectQuarter.append("5")
            elif "ΣΤ" in strQuarter:
                listOfSubjectQuarter.append("6")
            elif "Ζ" in strQuarter:
                listOfSubjectQuarter.append("7")
            elif "Η" in strQuarter:
                listOfSubjectQuarter.append("8")
            else:
                print('Could Not pass string:'+strQuarter)
                listOfSubjectQuarter.append("0")

        downloadQuarter = -1
        while int(downloadQuarter) < 0 or int(downloadQuarter) > 8:
            try:
                downloadQuarter = input('Please select which Quarter of subjects you want to download (1-8), if you want all of them type \'0\': ' )
                int(downloadQuarter)
            except ValueError:
                downloadQuarter = -1
                print("That's not an integer!\n")
        if downloadQuarter != 0:
            downloadFiles(listOfSubjects, listOfSubjectsCode, listOfSubjectQuarter, selQuarter=downloadQuarter)
        else:
            downloadFiles(listOfSubjects, listOfSubjectsCode, listOfSubjectQuarter)
        

    
    def downloadFiles(lstSubjects, lstSubjCode, lstSubjQuart, **selectedQuarter):
        for x in range(len(lstSubjects)):
            if(lstSubjQuart[x] is not str(selectedQuarter['selQuarter']) and int(selectedQuarter['selQuarter']) != 0):
                continue
            print('Starting Download:')
            print('Downloading '+str(x+1)+'/'+str(len(lstSubjects))+' files...')
            downloadUrl = 'https://aristarchus.ds.unipi.gr/modules/document/index.php?course=DS-COURSES-SEM'+str(lstSubjCode[x])+'&download=/'
            #Original Demo Url: https://aristarchus.ds.unipi.gr/modules/document/index.php?course=DS-COURSES-SEM145&download=/
            if(downloadZip(downloadUrl,lstSubjects[x])):
                print('Extracting Zip File...')
                extractZip(lstSubjects[x], lstSubjQuart[x])
                removeZip(lstSubjects[x])
            
        

    def downloadZip(zipUrl,zipName):
        print('Downloading...')
        zipFile = s.get(zipUrl, stream=True)
        
        Content_Type = {value for key, value in zipFile.headers.items() if key == 'Content-Type'}
        zipCheckFile = 'application/zip'

        if (zipCheckFile in Content_Type):
            total_size_in_bytes= int(zipFile.headers.get('content-length', 0))
            block_size = 1024 #1 Kibibyte
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(zipName+".zip",'wb') as f:
                for data in zipFile.iter_content(block_size):
                    progress_bar.update(len(data))
                    f.write(data)
                f.close()
            progress_bar.close()
            print('Download Finished!')
            return 1
        else:
            print('Zip File doesnt exist')
            return 0

    def handleRemoveReadonly(func, path, exc):
        excvalue = exc[1]
        if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
            os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
            func(path)
        else:
            raise

    def extractZip(zipName, quartInd):
        with zipfile.ZipFile('./'+zipName+'.zip', 'r') as zip_ref:
            for member in tqdm(zip_ref.infolist(), desc='Extracting '):
                try:
                    zip_ref.extract(member, './'+quartInd+'° εξάμηνο/'+zipName)
                except zipfile.error as e:
                    print(e)
                except FileExistsError as fee:
                    findingFileName = fee
                    fstring = str(findingFileName)
                    result = re.search('\'(.*)\'',fstring)
                    originalFile = result.group(1)
                    originalFile = originalFile.replace('\\\\','\\')
                    shutil.rmtree(originalFile, ignore_errors=False, onerror=handleRemoveReadonly)
                    zip_ref.extract(member, './'+quartInd+'° εξάμηνο/'+zipName)
    
    def removeZip(zipName):
        try:
            os.remove(zipName+'.zip')
        except OSError as e:
            print('Error'+e)
            pass

    if __name__ == '__main__' :
        initializeConnection()
    
