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
C:\Users\mahdi\Git\GitHub\Automated-US-Visa-Appointment-Finder>US_Visa_Appointment_Bot.exe
Traceback (most recent call last):
  File "US_Visa_Appointment_Bot.py", line 303, in <module>
    driver = create_driver()
             ^^^^^^^^^^^^^^^
  File "US_Visa_Appointment_Bot.py", line 156, in create_driver
    driver = Chrome(options=options)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "selenium\webdriver\chrome\webdriver.py", line 70, in __init__
  File "selenium\webdriver\chromium\webdriver.py", line 92, in __init__
  File "selenium\webdriver\remote\webdriver.py", line 275, in __init__
  File "selenium\webdriver\remote\webdriver.py", line 365, in start_session
  File "selenium\webdriver\remote\webdriver.py", line 430, in execute
  File "selenium\webdriver\remote\errorhandler.py", line 247, in check_response
selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 121
Current browser version is 123.0.6312.58 with binary path C:\Program Files\Google\Chrome\Application\chrome.exe
Stacktrace:
        GetHandleVerifier [0x00007FF605A55E42+3538674]
        (No symbol) [0x00007FF605674C02]
        (No symbol) [0x00007FF605525AEB]
        (No symbol) [0x00007FF60555C512]
        (No symbol) [0x00007FF60555B872]
        (No symbol) [0x00007FF605555106]
        (No symbol) [0x00007FF6055521C8]
        (No symbol) [0x00007FF6055994B9]
        (No symbol) [0x00007FF60558EE53]
        (No symbol) [0x00007FF60555F514]
        (No symbol) [0x00007FF605560631]
        GetHandleVerifier [0x00007FF605A86CAD+3738973]
        GetHandleVerifier [0x00007FF605ADC506+4089270]
        GetHandleVerifier [0x00007FF605AD4823+4057299]
        GetHandleVerifier [0x00007FF6057A5C49+720121]
        (No symbol) [0x00007FF60568126F]
        (No symbol) [0x00007FF60567C304]
        (No symbol) [0x00007FF60567C432]
        (No symbol) [0x00007FF60566BD04]
        BaseThreadInitThunk [0x00007FFFEEE27344+20]
        RtlUserThreadStart [0x00007FFFF03626B1+33]

[19088] Failed to execute script 'US_Visa_Appointment_Bot' due to unhandled exception!
```

