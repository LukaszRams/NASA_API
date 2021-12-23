# NASA Api for wallpapers

An application using the "EPIC DAILY "BLUE MARBLE" API" to download images of the earth, edit them 
and set them as a desktop background.

The application is equipped with automatic detection of incorrect files in the source folder, deleting them 
and if new data is available updating.

The software ultimately runs as a Windows service

***Application created for educational purposes only***   

##### Thanks to <a href="https://epic.gsfc.nasa.gov/about/api" target="_blank">EPIC DAILY "BLUE MARBLE" API</a>


## Instruction
### Building

1. Go to the repository folder and create a new virtual environment

        >>> cd path\to\repository
        >>> python -mvenv venv
        
2.  Activate the environment

        >>> venv\Scripts\activate.bat
        
3. Install packages from ***requirements.txt*** file

        >>> pip install -r requirements.txt
        
4. Build your service

        >>> python setup.py py2exe

### Installing

1. Copy the dist folder to a convenient location

2. Open the terminal and go to the folder

        >>> cd path\to\folder\dist

3. Install the service

        >>> main.exe -install

4. Set start-up mode (default is manual)

        >>> sc config nasaApi start=auto

5. Start the service

        >>> sc start nasaApi
    
If you want to configure the service in more detail, run:

    >>> services.msc
    
Find the ***NASA Api*** service, then double-click on it with the left mouse button