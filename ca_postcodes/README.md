### Step 0: Download ChromeDriver

1.  Download the latest ChromeDriver from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/#stable).
2.  Extract the downloaded ZIP file to a known location on your system (on the same folder as your project is recomended).

#### Step 0-1: On Mac only: Allow the ChromeDriver Execution
1. *Navigate to the location where you have chromedriver*:

```
cd /path/to/chromedriver
```

For example, to `./chromedriver-mac-arm64` on my specific MAC machine.

2. *Remove the quarantine attribute*:

```
xattr -d com.apple.quarantine chromedriver
```

### Step 1: Create a Virtual Environment

1.  **Navigate to your project directory**:

```
cd /path/to/your/project
```

2. **Create a virtual environment**:

```
python -m venv venv
```

Use `python3` in commands in MAC.

3.  **Activate the virtual environment**:
    
    -   On Windows:
        
        ```
        venv\Scripts\activate
        ```
        
    -   On macOS/Linux:
        
        ```
        source venv/bin/activate
        ```
        

### Step 2: Create a `requirements.txt` File

Create a `requirements.txt` file in your project directory and add the necessary dependencies:

```
selenium
psycopg2-binary
python-dotenv
```

### Step 3: Install Dependencies

With the virtual environment activated, install the dependencies listed in `requirements.txt`:

```
pip install -r requirements.txt
```

### Step 4: Verify Installation

Verify that the packages are installed correctly by listing installed packages:

```
pip list
```

You should see `selenium`, `psycopg2-binary`, and `python-dotenv` listed among the installed packages.

### Step 5: Running Your Script

Ensure your virtual environment is activated and then run your script:

```
python main.py
```

### Step 6: Troubleshooting 

Please note if you face we an error like the following, it means you need to download a newer version of `chromedriver` or on the other word update it. 

```bash
C:\Users\mahdi\Git\GitHub\Automated-US-Visa-Appointment-Finder>python main.py
Traceback (most recent call last):
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\main.py", line 748, in <module>
    driver = create_driver()
             ^^^^^^^^^^^^^^^
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\main.py", line 620, in create_driver
    driver = webdriver.Chrome(service=service, options=options)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\chrome\webdriver.py", line 45, in __init__
    super().__init__(
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\chromium\webdriver.py", line 66, in __init__
    super().__init__(command_executor=executor, options=options)
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 212, in 
__init__
    self.start_session(capabilities)
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 299, in 
start_session
    response = self.execute(Command.NEW_SESSION, caps)["value"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\remote\webdriver.py", line 354, in 
execute
    self.error_handler.check_response(response)
  File "C:\Users\mahdi\Git\GitHub\mrag-db-importers\ca_postcodes\venv\Lib\site-packages\selenium\webdriver\remote\errorhandler.py", line 229, 
in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 126
Current browser version is 128.0.6613.84 with binary path C:\Program Files\Google\Chrome\Application\chrome.exe
Stacktrace:
        GetHandleVerifier [0x00007FF694DDEEA2+31554]
        (No symbol) [0x00007FF694D57ED9]
        (No symbol) [0x00007FF694C1872A]
        (No symbol) [0x00007FF694C56ED2]
        (No symbol) [0x00007FF694C56008]
        (No symbol) [0x00007FF694C4FCC8]
        (No symbol) [0x00007FF694C4BB3B]
        (No symbol) [0x00007FF694C98794]
        (No symbol) [0x00007FF694C97DF0]
        (No symbol) [0x00007FF694C8CDD3]
        (No symbol) [0x00007FF694C5A33B]
        (No symbol) [0x00007FF694C5AED1]
        GetHandleVerifier [0x00007FF6950E8B1D+3217341]
        GetHandleVerifier [0x00007FF695135AE3+3532675]
        GetHandleVerifier [0x00007FF69512B0E0+3489152]
        GetHandleVerifier [0x00007FF694E8E776+750614]
        (No symbol) [0x00007FF694D6375F]
        (No symbol) [0x00007FF694D5EB14]
        (No symbol) [0x00007FF694D5ECA2]
        (No symbol) [0x00007FF694D4E16F]
        BaseThreadInitThunk [0x00007FFE0F3D7374+20]
        RtlUserThreadStart [0x00007FFE0FE7CC91+33]

```

