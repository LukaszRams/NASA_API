# NASA Api for wallpapers

An application using the "EPIC DAILY "BLUE MARBLE" API" to download images of the earth, edit them 
and set them as a desktop background.

The application is equipped with automatic detection of incorrect files in the source folder, deleting them 
and if new data is available updating.


***Application created for educational purposes only***   

##### Thanks to <a href="https://epic.gsfc.nasa.gov/about/api" target="_blank">EPIC DAILY "BLUE MARBLE" API</a>


## Instruction
### Building

1. Go to the repository folder and create a new virtual environment

        >>> cd path\to\repository
        >>> python -m venv venv
        
2.  Activate the environment

        >>> venv\Scripts\activate.bat
        
3. Install packages from ***requirements.txt*** file

        >>> pip install -r requirements.txt
        
4. Build your application

        >>> pyinstaller -F --windowed --specpath=./nasaApi/build --workpath=./nasaApi/build --distpath=./nasaApi NASA_Api.py


### Launching

Go to the ***nasaApi*** folder and double-click on ***NASA_Api.exe***

*If you want the application to run automatically on startup, add it to the autostart*
